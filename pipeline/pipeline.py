from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from config.config import OPENAI_API_KEY, MODEL_NAME
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class AnimeRecommendationPipeline:
    def __init__(self, persist_dir="chroma_db"):
        try:
            logger.info("Initializing Recommendation Pipeline")

            vector_builder = VectorStoreBuilder(csv_path="", persist_dir=persist_dir)

            # Pass the vector_builder instance (which has query_similar method)
            # instead of the raw collection
            self.recommender = AnimeRecommender(vector_builder, OPENAI_API_KEY, MODEL_NAME)

            logger.info("Pipeline initialized successfully...")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline {str(e)}")
            raise CustomException("Error during pipeline initialization", e)
        
    def recommend(self,query:str) -> str:
        try:
            logger.info(f"Received a query {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Recommendation generated successfully...")
            return recommendation
        except Exception as e:
            logger.error(f"Failed to get recommendation {str(e)}")
            raise CustomException("Error during getting recommendation" , e)
        


        