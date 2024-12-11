from pymongo import MongoClient
from urllib.parse import quote_plus


class MongoDBClient:
    def __init__(
        self, db_name, collection_name, user, password, host="localhost", port=27017
    ):
        uri = f"mongodb://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/"
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create(self, data):
        """Create a new document in the collection"""
        return self.collection.insert_one(data).inserted_id

    def read(self, query):
        """Read documents from the collection"""
        return list(self.collection.find(query))

    def update(self, query, new_values):
        """Update documents in the collection"""
        return self.collection.update_many(query, {"$set": new_values})

    def delete(self, query):
        """Delete documents from the collection"""
        return self.collection.delete_many(query)
