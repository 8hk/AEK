import json
import os
import uuid
from datetime import datetime

from elasticsearch import Elasticsearch, helpers
from pymongo import MongoClient
import nltk

client = MongoClient(
    host=os.environ.get("MONGO_DB_HOST", " ") + ":" + os.environ.get("MONGO_DB_PORT", " "),
    # <-- IP and port go here
    serverSelectionTimeoutMS=3000,  # 3 second timeout
    username=os.environ.get("MONGO_DB_USERNAME", " "),
    password=os.environ.get("MONGO_DB_PASSWORD", " "),
)

db = client[os.environ.get("MONGO_INITDB_DATABASE", " ")]
class ElasticSearchHandler(object):


    def __init__(self):
        self.already_inserted_detailed_article_id_list = []
        self.annotation_detail_column = db["annotated_article_ids"]

        self.get_detailed_article_ids_from_db()
        print("total ",len(self.already_inserted_detailed_article_id_list),"articles will be processed")
        self.start_importing()

    def bulk_json_data(self,json_list, _index, doc_type):
        for json in json_list:
            if '{"index"' not in json:
                yield {
                    "_index": _index,
                    "_type": doc_type,
                    "_id": uuid.uuid4(),
                    "_source": json
                }

    def get_detailed_article_ids_from_db(self):
        query = {}
        column = db["annotated_article_ids"]
        document = column.find(query)
        for x in document:
            list_item = dict(x)
            if list_item["id"] not in self.already_inserted_detailed_article_id_list:
                self.already_inserted_detailed_article_id_list.append(list_item["id"])

    def article_details_query(self, article_id):
        mongo_query = {}
        mongo_query["id"] = article_id
        document = self.annotation_detail_column.find(mongo_query)
        for x in document:
            list_item = dict(x)
            article_json = {
                "authors": list_item["author_list"],
                "keywords": list_item["top_three_keywords"],
                "abstract": list_item["abstract"].lower(),
                "article_date": list_item["article_date"],
                "article_id": list_item["id"],
                "_created": datetime.now()
            }
            del document
            del list_item
            return article_json

    def start_importing(self):
        article_json = []
        elastic = Elasticsearch(hosts=["es01"])
        while self.already_inserted_detailed_article_id_list:
            article_json.append(self.article_details_query(self.already_inserted_detailed_article_id_list.pop()))
        response =helpers.bulk(elastic, self.bulk_json_data(article_json, "test6", "doc"))
        print("\nRESPONSE:", response)
        print("op finished")



if __name__ == "__main__":
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    print("op started")

    handler=ElasticSearchHandler()

    finish_time = now.strftime("%H:%M:%S")
    print("start time: ", start_time)
    print("finish time: ", finish_time)
