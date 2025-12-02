from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)


def build_mongo_uri():
    # Prefer full URI if provided
    full_uri = os.getenv("MONGODB_URI")
    if full_uri:
        return full_uri

    # Otherwise construct from pieces (recommended in k8s with Secrets/ConfigMaps)
    user = os.getenv("MONGO_USERNAME", "")
    pwd = os.getenv("MONGO_PASSWORD", "")
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    auth_db = os.getenv("MONGO_AUTH_DB", "admin")
    # Example: mongodb://user:pass@mongodb:27017/flask_db?authSource=admin
    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}:{port}/?authSource={auth_db}"
    else:
        # unauthenticated fallback for local Part 1
        return f"mongodb://{host}:{port}/"


# Connect once at startup
client = MongoClient(build_mongo_uri())
db_name = os.getenv("MONGO_DB", "flask_db")
db = client[db_name]
collection = db["data"]


@app.route("/")
def index():
    return f"Welcome to the Flask app! The current time is: {datetime.now()}"


@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        payload = request.get_json(silent=True)
        
        if payload is None:
            return jsonify({"error": "Invalid JSON body - could not parse"}), 400
        
        if not isinstance(payload, dict) or len(payload) == 0:
            return jsonify({"error": "Invalid JSON body - empty or not dict"}), 400
            
        collection.insert_one(payload)
        return jsonify({"status": "Data inserted"}), 201

    # GET
    docs = list(collection.find({}, {"_id": 0}))
    return jsonify(docs), 200


if __name__ == "__main__":
    # Local Part 1 run
    app.run(host="0.0.0.0", port=5000)