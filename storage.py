import json
import os
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from src.config.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        
        if self.storage_type == "firebase":
            try:
                # Initialize Firebase
                if not firebase_admin._apps:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {str(e)}")
                self.storage_type = "local"
                
        # Ensure local storage directory exists
        if self.storage_type == "local":
            os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)

    async def save_research_results(self, research_id: str, data: Dict[str, Any]) -> bool:
        """
        Save research results to storage
        """
        try:
            if self.storage_type == "firebase":
                # Save to Firebase
                doc_ref = self.db.collection("research_results").document(research_id)
                doc_ref.set(data)
            else:
                # Save to local storage
                file_path = os.path.join(settings.LOCAL_STORAGE_PATH, f"research_{research_id}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving research results: {str(e)}")
            return False

    async def get_research_results(self, research_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve research results from storage
        """
        try:
            if self.storage_type == "firebase":
                # Retrieve from Firebase
                doc_ref = self.db.collection("research_results").document(research_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None
            else:
                # Retrieve from local storage
                file_path = os.path.join(settings.LOCAL_STORAGE_PATH, f"research_{research_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return None
        except Exception as e:
            logger.error(f"Error retrieving research results: {str(e)}")
            return None

    async def save_synthesis(self, research_id: str, synthesis_data: Dict[str, Any]) -> bool:
        """
        Save synthesis results to storage
        """
        try:
            if self.storage_type == "firebase":
                # Save to Firebase
                doc_ref = self.db.collection("syntheses").document(research_id)
                doc_ref.set(synthesis_data)
            else:
                # Save to local storage
                file_path = os.path.join(settings.LOCAL_STORAGE_PATH, f"synthesis_{research_id}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(synthesis_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving synthesis: {str(e)}")
            return False 