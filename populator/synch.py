import os
import requests
import sys
from pymongo import MongoClient


mongo_uri = os.getenv("MONGO_URL","mongodb://root:example@localhost:27017/messagesdb?authSource=admin")
members_url=os.getenv("MEMBERS_URL","https://november7-730026606190.europe-west1.run.app/messages/")
interval=int(os.getenv("SYNC_INTERVAL","120"))

print("Starting the Synch Script")
print("mongo_uri:%s" %(mongo_uri))
print("members_url:%s"%(members_url))
print("interval:%s" %(interval))


client = MongoClient(mongo_uri)
db = client.get_default_database()
#ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def get_message_count(db, key="global") -> int:
    cnt = db.message.count_documents({})
    return cnt


def get_remote_message_count(url=members_url, timeout=15) -> int:
    print(url)
    r = requests.get(url, params={"limit": 0}, timeout=timeout)
    r.raise_for_status()
    return int(r.json().get("total", 0))

def get_messages(skip,limit):
    r = requests.get(members_url,params={"skip":skip,"limit":limit})
    r.raise_for_status()
    messages = r.json()
    return messages


message_count = get_message_count(db)
print("Message Count: %d" %(message_count))
remote_message_count = get_remote_message_count()
print("Remote Message Count %d" %(remote_message_count))
skip  = message_count
limit = remote_message_count - message_count 

if(message_count == remote_message_count):
    print("No new messages!")
    print("System exiting")
    sys.exit(0)

messages_json=get_messages(skip,limit)
items=messages_json.get("items")
db.message.insert_many(items)

