from flask import Flask, jsonify
import os
from pymongo import MongoClient
from elasticsearch import Elasticsearch

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
ELASTICSEARCH_URI = os.getenv("ELASTICSEARCH_URI", "http://localhost:9200")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client.testdb
mongo_collection = mongo_db.testcollection

es = Elasticsearch(ELASTICSEARCH_URI, verify_certs=False)


@app.route('/mongo', methods=['GET'])
def mongo_endpoint():
    test_doc = {"message": "Hello from Mongo!"}
    mongo_collection.insert_one(test_doc)
    doc = mongo_collection.find_one({"message": "Hello from Mongo!"})
    return jsonify({"mongo_message": doc.get("message", "No message")})


@app.route('/es', methods=['GET'])
def es_endpoint():
    # Index a document in Elasticsearch
    es.index(index="testindex", document={"message": "Hello from Elasticsearch!"})
    # Search for it
    res = es.search(index="testindex", query={"match_all": {}})
    hits = res['hits']['hits']
    messages = [hit['_source']['message'] for hit in hits]
    return jsonify({"es_messages": messages})


@app.route('/combined', methods=['GET'])
def combined_endpoint():
    mongo_doc = {"message": "Combined Service Message"}
    insert_result = mongo_collection.insert_one(mongo_doc)

    mongo_result = mongo_collection.find_one({"_id": insert_result.inserted_id})

    es_doc = {
        "message": mongo_result["message"],
        "mongo_id": str(mongo_result["_id"])
    }

    es.index(index="combined_index", document=es_doc)

    es_result = es.search(index="combined_index", query={
        "match": {
            "message": "Combined Service Message"
        }
    })

    return jsonify({
        "mongo_result": mongo_result.get("message", "No MongoDB message"),
        "elasticsearch_result": [hit['_source'] for hit in es_result['hits']['hits']],
        "service_status": {
            "mongodb": "active" if mongo_result else "error",
            "elasticsearch": "active" if es_result['hits']['hits'] else "error"
        }
    })


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Hello from Python App!",
        "available_endpoints": ["/mongo", "/es", "/combined"]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
