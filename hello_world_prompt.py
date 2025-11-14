import requests

req_json={"model":"qwen2.5:7b-instruct","prompt":"Thank you for your service!","stream":False}
resp = requests.post("http://localhost:11434/api/generate",json=req_json)
print(resp.json()["response"])
