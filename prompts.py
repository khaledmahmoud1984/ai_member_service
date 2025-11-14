import requests
from pymongo import MongoClient
import os
import ollama
import re
from fastapi import FastAPI
import uvicorn
app = FastAPI()

mongo_uri = os.getenv("MONGO_URL","mongodb://apiuser:apiuser@localhost:27017/messagesdb?authSource=messagesdb")
members_url=os.getenv("MEMBERS_URL","https://november7-730026606190.europe-west1.run.app/messages/")

instruction="Find the person name where are asking about in [%s]"

api_chat_url=os.getenv("CHAT_URL","http://localhost:11434/api/chat")
api_embeddings_url=os.getenv("EMBEDDINGS_URL","http://localhost:11434/api/embeddings")
api_embedding_name=os.getenv("EMBEDDINGS_NAME","mxbai-embed-large")
client = MongoClient(mongo_uri)
db = client.get_default_database()

answer_instruction="Find the answer to the following question from the provided messages. Question:%s, Messages:%s"

from math import sqrt

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

def find_name(question):
    req_json={
            "model":"qwen2.5:7b-instruct",
            "stream":False,
            "messages": [
                {"role":"system","content":"Extract the person name(s) mentioned in the question. Return only the names, comma-separated. Remove possessive apostrophes"},
                
                {"role":"user", "content": instruction % "When is Layla planning her trip to Longon?"},
                {"role":"assistant", "content":"Layla"},


                {"role":"user", "content": instruction % "How many cars does Vikram Desai have?"},
                {"role":"assistant", "content":"Vikram Desai"},


                {"role":"user", "content": instruction % "What are Amira’s favorite restaurants?"},
                {"role":"assistant", "content":"Amira"},


                {"role":"user", "content": instruction % (question)},

                ]
            }

    resp = requests.post(api_chat_url,json=req_json)
    content=resp.json()["message"]["content"]
    return content.split(",")


def answer(question,messages):
    req_json={
            "model":"qwen2.5:7b-instruct",
            "stream":False,
            "messages": [
                {"role":"system","content":"Only answer the question based on the given messages. If the answer is not present, say answer is not in the messages!. Message format is [user_name:message:timestamp]. Use timestamp to infer questions that include date"},
                
                {"role":"user", "content": answer_instruction % ("Where is Khaled right now?","I am planning to visit Yoguslavia in the next 3 hours")},
                {"role":"assistant", "content":"Yoguslavia"},





                {"role":"user", "content": answer_instruction % (question,messages)},

                ]
            }

    resp = requests.post(api_chat_url,json=req_json)
    content=resp.json()["message"]["content"]
    return content

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

def fetch_messages(names):
    or_conditions = [{"user_name": {"$regex": rf"\b{re.escape(w)}\b", "$options": "i"}} for w in names ]
    cursor = db.message.find({"$or": or_conditions})
    docs = list(cursor)
    return docs

def filter_cosine(embedding, docs):
    scored_docs = []
    for doc in docs:
        emb = doc["embedding"]
        score = cosine_similarity(embedding, emb)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return scored_docs

def fetch_context(question):
    names=find_name(question)
    docs=fetch_messages(names)
    question_embedding=get_embedding(question)
    scored_embeddings=filter_cosine(question_embedding,docs)

    context = " ".join(
        f"[{doc['user_name']}:{doc['message']}:{doc['timestamp']}]"
        #f"[{doc['user_name']}]"
        for score, doc in scored_embeddings[:30]
    )
    return context


def get_answer(question):
    context=fetch_context(question)
    #print(context)
    ans=answer(question,context)
    return ans

@app.get("/ask")
async def ask(question: str):
    answer = get_answer(question)
    return {"answer": answer}


if __name__ == "__main__":
    print("Thank you for your service")
    uvicorn.run("prompts:app", host="0.0.0.0", port=7777, reload=True)

#a = get_answer("Where did Vikram want to fly to on Wednesday")

