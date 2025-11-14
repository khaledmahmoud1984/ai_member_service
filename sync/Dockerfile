# populator/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY synch.py .
RUN pip install --no-cache-dir ollama pymongo requests
CMD ["python", "synch.py"]

