from typing import Dict, Any, Set
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API Keys
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Research Agent Configuration
    MAX_RESEARCH_DEPTH: int = int(os.getenv("MAX_RESEARCH_DEPTH", "3"))
    MAX_URLS_PER_SEARCH: int = int(os.getenv("MAX_URLS_PER_SEARCH", "5"))
    CACHE_EXPIRY_MINUTES: int = int(os.getenv("CACHE_EXPIRY_MINUTES", "60"))
    
    # Storage Configuration
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "data")
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS: Dict[str, Any] = {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_api_keys()
        self._load_firebase_credentials()
    
    def _validate_api_keys(self):
        """Validate that required API keys are set"""
        if not self.TAVILY_API_KEY:
            logger.warning("TAVILY_API_KEY is not set. The research functionality will not work.")
        elif not self.TAVILY_API_KEY.startswith('tvly-'):
            logger.warning("TAVILY_API_KEY format appears invalid. It should start with 'tvly-'")
            
        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set. The synthesis functionality will not work.")
    
    def _load_firebase_credentials(self):
        """Load Firebase credentials if using Firebase storage"""
        if self.STORAGE_TYPE == "firebase":
            creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if not creds_path:
                logger.warning("FIREBASE_CREDENTIALS_PATH not set. Defaulting to local storage.")
                self.STORAGE_TYPE = "local"
            elif not os.path.exists(creds_path):
                logger.warning(f"Firebase credentials file not found at {creds_path}. Defaulting to local storage.")
                self.STORAGE_TYPE = "local"
            else:
                try:
                    import json
                    with open(creds_path, 'r') as f:
                        self.FIREBASE_CREDENTIALS = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading Firebase credentials: {str(e)}")
                    self.STORAGE_TYPE = "local"
    
    # Common words to filter out in keyword extraction
    COMMON_WORDS: Set[str] = {
        "about", "above", "after", "again", "against", "all", "and", "any",
        "are", "because", "been", "before", "being", "below", "between",
        "both", "but", "by", "could", "did", "does", "doing", "down",
        "during", "each", "few", "for", "from", "further", "had", "has",
        "have", "having", "her", "here", "hers", "herself", "him", "himself",
        "his", "how", "into", "its", "itself", "just", "more", "most",
        "myself", "nor", "not", "now", "off", "once", "only", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "she", "should", "some", "such", "than", "that", "the", "their",
        "theirs", "them", "themselves", "then", "there", "these", "they",
        "this", "those", "through", "too", "under", "until", "very", "was",
        "way", "were", "what", "when", "where", "which", "while", "who",
        "whom", "why", "with", "would", "you", "your", "yours", "yourself",
        "yourselves"
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
settings = Settings() 