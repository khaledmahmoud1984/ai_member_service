# populator/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY prompts.py .
RUN pip install --no-cache-dir ollama pymongo requests fastapi uvicorn
CMD ["python", "prompts.py"]

