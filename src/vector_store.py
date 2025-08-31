import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

class VectorStoreBuilder:
    def __init__(self, csv_path: str, persist_dir: str = "chroma_db"):
        self.csv_path = csv_path
        self.persist_dir = persist_dir
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = "anime_collection"
    
    def _simple_chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100):
        """Simple text chunking with overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence end
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:  # If we find a period in the latter part
                end = start + last_period + 1
                chunks.append(text[start:end])
                start = end - overlap
            else:
                chunks.append(chunk)
                start = end - overlap
        
        return chunks

    def build_and_save_vectorstore(self):
        # Load CSV data
        df = pd.read_csv(self.csv_path, encoding='utf-8')
        
        # Create collection
        try:
            collection = self.client.get_collection(self.collection_name)
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        collection = self.client.create_collection(self.collection_name)
        
        # Process and add documents with chunking
        documents = []
        ids = []
        metadatas = []
        
        for idx, row in df.iterrows():
            # Extract key info (assuming CSV has 'combined_info' or similar structure)
            text = ' '.join([str(value) for value in row.values if pd.notna(value)])
            
            # Try to extract anime title from the text (assuming it starts with "Title:")
            anime_title = "Unknown"
            if "Title:" in text:
                title_part = text.split("Title:")[1].split("Overview:")[0].strip()
                anime_title = title_part
            
            # Create chunks
            chunks = self._simple_chunk_text(text)
            
            # Add each chunk as a separate document with metadata
            for chunk_idx, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{idx}_{chunk_idx}")
                metadatas.append({
                    "anime_id": str(idx),
                    "anime_title": anime_title,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks)
                })
        
        # Add to collection
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def load_vector_store(self):
        try:
            collection = self.client.get_collection(self.collection_name)
            return collection
        except:
            raise Exception(f"Collection {self.collection_name} not found. Please build the vector store first.")
    
    def query_similar(self, query: str, n_results: int = 5):
        collection = self.load_vector_store()
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        return {
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0] if 'metadatas' in results else None,
            'distances': results['distances'][0] if 'distances' in results else None
        }



