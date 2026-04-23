import os

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

class MongoUploader:
    """Sends data to mongoDB."""

    def __init__(self):
        load_dotenv()
        self.db = MongoClient(os.getenv("MONGO_URI"))[os.getenv("MONGO_DB")] # type: ignore
    
    def upload_professor_scores(self, data: list):
        if not data:
            return

        valid_ids = [item["id"] for item in data]
        print("Upserting professor data...")
        ops = [
            UpdateOne({"id": item["id"]}, {"$set": item}, upsert=True)
            for item in data
        ]
        
        collection_name = os.getenv("MONGO_COLLECTION_PROFESSORS")
        collection = self.db[collection_name] # type: ignore

        try:
            collection.bulk_write(ops, ordered=False)
            result = collection.delete_many({"id": {"$nin": valid_ids}})
            print(f"Purged {result.deleted_count} stale professors.")
            
        except BulkWriteError as e:
            print(e.details)

    def upload_global_statistics(self, data: dict):
        """Uploads global statistics."""
        collection = os.getenv("MONGO_COLLECTION_STATISTICS")
        self.db[collection].update_one( # type: ignore
            {"_id": "global_stats"},
            {"$set": data},
            upsert=True
        )