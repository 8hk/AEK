import pymongo
from pymongo import MongoClient
import os

client = MongoClient(
    host=os.environ.get("MONGO_DB_HOST", " ") + ":" + os.environ.get("MONGO_DB_PORT", " "),
    # <-- IP and port go here
    serverSelectionTimeoutMS=3000,  # 3 second timeout
    username=os.environ.get("MONGO_DB_USERNAME", " "),
    password=os.environ.get("MONGO_DB_PASSWORD", " "),
)

db = client[os.environ.get("MONGO_INITDB_DATABASE", " ")]
annotation_detail_column = db["annotation"]
# annotation_detail_column.drop_indexes()
annotation_detail_column.create_index([('indexed', pymongo.TEXT)], name='search_index_')
for index in annotation_detail_column.list_indexes():
    print(index)
print(annotation_detail_column.list_indexes())

