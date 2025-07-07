from constants import *
from log import logger
from typing import Any
from pymongo import MongoClient
from dataclasses import dataclass
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from constants import MONGO_CONNECT_URL, MONGO_DB_NAME


@dataclass
class MongoTemplate:
    @staticmethod
    def create_moongo_client() -> MongoClient:
        try:
            return MongoClient(MONGO_CONNECT_URL)
        except ConnectionFailure:
            logger.error("ERROR! Connecting to Mongo DB Failed !!")    

    @staticmethod
    def close_mongo_client(client: MongoClient):
        try:
            client.close()
            logger.log("Closed the mongo_client")
        except Exception as e:
            logger.error(f"Got an exception while closing mongo_client {e}")
        return
    
    @staticmethod
    def check_db_existence(client: MongoClient, database_name: str) -> bool:
        try:
            if database_name in client.list_database_names():
                return client.get_database(database_name)
        except Exception as e:
            logger.error(f"No such db found in the list")
            return None

    @staticmethod
    def check_collection_existence(database: Database, collection_name: str) -> bool:
        try:
            if collection_name in database.list_collection_names():
                return database[collection_name]
        except Exception as e:
            logger.error(f"No such collection found in the db")
            return None
    
    @staticmethod
    def add_new_task(collection: Collection, query) -> bool:
        """
            It will log the task into the specified collection
        """
        return collection.insert_one(query).inserted_id

mongo_client = MongoTemplate.create_moongo_client()
mongo_db = MongoTemplate.check_db_existence(mongo_client, MONGO_DB_NAME)
