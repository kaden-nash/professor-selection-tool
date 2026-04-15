import json, os
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

class MongoUploader:
    def __init__(self):
        load_dotenv()
        self.db = MongoClient(os.getenv("MONGO_URI"))[os.getenv("MONGO_DB")] # type: ignore

    def upload_professor_scores(self, file_path: str):
        with open(file_path, "r") as f:
            data = json.load(f)
        ops = [
            UpdateOne({"id": item["id"]}, {"$set": item}, upsert=True)
            for item in data
        ]
        collection = os.getenv("MONGO_COLLECTION_PROFESSORS")
        try:
            self.db[collection].bulk_write(ops, ordered=False) # type: ignore
        except BulkWriteError as e:
            print(e.details)

    def upload_global_statistics(self, file_path: str):
        with open(file_path, "r") as f:
            data = json.load(f)
        collection = os.getenv("MONGO_COLLECTION_STATISTICS")
        self.db[collection].update_one( # type: ignore
            {"_id": "global_stats"},
            {"$set": data},
            upsert=True
        )