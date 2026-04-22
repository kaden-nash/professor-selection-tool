import os
import json
import pytest
from unittest.mock import Mock, patch, mock_open
from pymongo.errors import BulkWriteError

from src.knightrate.professor_scoring.send_to_db import MongoUploader

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DB": "test_db",
        "MONGO_COLLECTION_PROFESSORS": "prof_col",
        "MONGO_COLLECTION_STATISTICS": "stat_col"
    }):
        yield

@pytest.fixture
def mock_mongo_client():
    with patch("knightrate.professor_scoring.send_to_db.MongoClient") as mock_client:
        yield mock_client

@pytest.fixture
def mock_dotenv():
    with patch("knightrate.professor_scoring.send_to_db.load_dotenv") as mock_ld:
        yield mock_ld

def test_mongo_uploader_init(mock_env, mock_mongo_client, mock_dotenv):
    uploader = MongoUploader()
    mock_dotenv.assert_called_once()
    mock_mongo_client.assert_called_once_with("mongodb://localhost:27017")
    # Verify that it accesses the database using the MONGO_DB name
    assert uploader.db == mock_mongo_client.return_value["test_db"]

def test_upload_professor_scores_success(mock_env, mock_mongo_client, mock_dotenv):
    uploader = MongoUploader()
    
    mock_data = [{"id": "prof_1", "name": "John"}, {"id": "prof_2", "name": "Jane"}]
    uploader.upload_professor_scores(mock_data)
    
    # Check bulk_write call
    mock_collection = uploader.db["prof_col"]
    mock_collection.bulk_write.assert_called_once()
    
    # We can inspect the operations passed to bulk_write
    call_args = mock_collection.bulk_write.call_args
    ops = call_args[0][0]  # The first argument (the list of UpdateOne)
    assert len(ops) == 2
    from pymongo import UpdateOne
    assert isinstance(ops[0], UpdateOne)
    
    assert call_args[1]["ordered"] is False

def test_upload_professor_scores_bulk_write_error(mock_env, mock_mongo_client, mock_dotenv, capsys):
    uploader = MongoUploader()
    
    mock_data = [{"id": "prof_1", "name": "John"}]
    
    mock_collection = uploader.db["prof_col"]
    # Simulate a bulk write error
    mock_collection.bulk_write.side_effect = BulkWriteError({"writeErrors": [{"errmsg": "Duplicate key"}]})
    
    uploader.upload_professor_scores(mock_data)
        
    # Standard output should contain the error details printed
    captured = capsys.readouterr()
    assert "writeErrors" in captured.out
    assert "Duplicate key" in captured.out

def test_upload_global_statistics_success(mock_env, mock_mongo_client, mock_dotenv):
    uploader = MongoUploader()
    
    mock_data = {"average_overall": 4.5}
    uploader.upload_global_statistics(mock_data)
    
    mock_collection = uploader.db["stat_col"]
    mock_collection.update_one.assert_called_once_with(
        {"_id": "global_stats"},
        {"$set": mock_data},
        upsert=True
    )
