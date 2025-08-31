from openai import OpenAI
from src.prompt_template import get_anime_prompt

class AnimeRecommender:
    def __init__(self, vector_store, api_key: str, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.vector_store = vector_store
        self.prompt_template = get_anime_prompt()

    def get_recommendation(self, query: str):
        # Get more results for better selection
        search_results = self.vector_store.query_similar(query, n_results=15)
        similar_docs = search_results['documents']
        metadatas = search_results['metadatas']
        distances = search_results['distances']
        
        # Group chunks by anime with relevance scores
        anime_chunks = {}
        for doc, metadata, distance in zip(similar_docs, metadatas or [{}] * len(similar_docs), distances or [1.0] * len(similar_docs)):
            anime_id = metadata.get('anime_id', 'unknown')
            anime_title = metadata.get('anime_title', 'Unknown')
            
            if anime_id not in anime_chunks:
                anime_chunks[anime_id] = {
                    'title': anime_title,
                    'chunks': []
                }
            
            # Store chunk with its relevance score (lower distance = higher relevance)
            anime_chunks[anime_id]['chunks'].append({
                'text': doc,
                'relevance': 1.0 - distance  # Convert distance to relevance score
            })
        
        # Calculate adaptive thresholds based on score distribution
        all_relevances = []
        for anime_data in anime_chunks.values():
            all_relevances.extend([c['relevance'] for c in anime_data['chunks']])
        
        all_relevances.sort(reverse=True)
        
        # Dynamic threshold calculation
        if len(all_relevances) > 5:
            # Use top 80th percentile as high relevance threshold
            high_threshold = all_relevances[int(len(all_relevances) * 0.2)]
            # Use median as minimum threshold
            min_threshold = all_relevances[len(all_relevances) // 2]
        else:
            # Fallback for small result sets
            high_threshold = all_relevances[0] * 0.8 if all_relevances else 0.5
            min_threshold = all_relevances[-1] if all_relevances else 0.3
        
        # Smart selection: balance relevance and diversity
        selected_chunks = []
        anime_count = 0
        max_anime = 5
        
        # Sort anime by their best chunk relevance
        anime_by_relevance = sorted(anime_chunks.items(), 
                                  key=lambda x: max([c['relevance'] for c in x[1]['chunks']]), 
                                  reverse=True)
        
        for anime_id, anime_data in anime_by_relevance:
            if anime_count >= max_anime:
                break
                
            # Sort chunks by relevance for this anime
            sorted_chunks = sorted(anime_data['chunks'], key=lambda x: x['relevance'], reverse=True)
            
            # Adaptive chunk selection based on relative relevance
            selected_anime_chunks = []
            
            for i, chunk in enumerate(sorted_chunks):
                # Always take the most relevant chunk if it meets minimum threshold
                if i == 0 and chunk['relevance'] >= min_threshold:
                    selected_anime_chunks.append(chunk['text'])
                # Take additional chunks if they're in top tier (up to 3 total)
                elif chunk['relevance'] >= high_threshold and len(selected_anime_chunks) < 3:
                    selected_anime_chunks.append(chunk['text'])
                # Take one more if there's a small gap to the best chunk (continuity)
                elif (len(selected_anime_chunks) > 0 and 
                      len(selected_anime_chunks) < 2 and
                      chunk['relevance'] >= sorted_chunks[0]['relevance'] * 0.85):
                    selected_anime_chunks.append(chunk['text'])
                else:
                    break
            
            if selected_anime_chunks:  # Only include if we have relevant chunks
                combined_chunks = " ".join(selected_anime_chunks)
                selected_chunks.append(f"[{anime_data['title']}]: {combined_chunks}")
                anime_count += 1
        
        context = "\n\n".join(selected_chunks)
        
        # Format the prompt with context and query
        prompt = self.prompt_template.format(context=context, question=query)
        
        # Make direct API call to OpenAI
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content