import os
import requests
import sys
from pymongo import MongoClient
import time

print("Starting Synch Service...")
mongo_uri = os.getenv("MONGO_URI","mongodb://synchuser:synchuser@mongo:27017/messagesdb?authSource=messagesdb")
members_url=os.getenv("MEMBERS_URL","https://november7-730026606190.europe-west1.run.app/messages/")
interval=int(os.getenv("SYNC_INTERVAL","120"))
api_embeddings_url=os.getenv("EMBEDDINGS_URL","http://localhost:11434/api/embeddings")
api_embedding_name=os.getenv("EMBEDDINGS_NAME","mxbai-embed-large")


retries=10
delay=2


print("Starting the Synch Script")
print("mongo_uri:%s" %(mongo_uri))
print("members_url:%s"%(members_url))
print("interval:%s" %(interval))

def get_remote_message_count(url=members_url, timeout=15) -> int:

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params={"limit": 0}, timeout=timeout)
            r.raise_for_status()
            return int(r.json().get("total", 0))
        except requests.exceptions.RequestException as e:
            if attempt == retries:
                raise
            print(f"get_remote_message_count failed ({attempt}/{retries}): {e}; retrying in {delay}s")
            time.sleep(delay)


print("Gettig DB Connection")
client = MongoClient(mongo_uri)
db = client.get_default_database()


def get_embedding(text: str):
    resp = requests.post(
        api_embeddings_url,
        json={
            "model": api_embedding_name,
            "prompt": text,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["embedding"]  # list[float]

def get_message_count(db, key="global") -> int:
    cnt = db.message.count_documents({})
    return cnt


def get_messages(skip,limit):
    r = requests.get(members_url,params={"skip":skip,"limit":limit})
    r.raise_for_status()
    messages = r.json()
    return messages


def synch():
    print("Synching")
    message_count = get_message_count(db)
    
    print("Message Count: %d" %(message_count))
    remote_message_count = get_remote_message_count()
    print("Remote Message Count %d" %(remote_message_count))
    
    skip  = message_count
    limit = remote_message_count - message_count 

    if(message_count == remote_message_count):
        print("No new messages!")
        print("System exiting")
        return

    messages=[]
    for attempt in range(1, retries + 1):
        try:
            messages_json=get_messages(skip,limit)
        except Exception as e:
            if attempt == retries:
                raise
            print(f"get_remote_message_count failed ({attempt}/{retries}): {e}; retrying in {delay}s")
            time.sleep(delay)

    
    items=messages_json.get("items")
    for m in items:
        text=m["message"]
        print("Getting embedding for %s" %(text))
        embedding = get_embedding(text)
        print(embedding)
        m["embedding"] = embedding

    print("inserting items into the database")
    db.message.insert_many(items)


time.sleep(240)
while True:
    synch()
    time.sleep(interval)
