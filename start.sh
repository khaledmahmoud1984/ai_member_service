#!/usr/bin/env bash
set -e
ollama serve &


while ! ollama list >/dev/null 2>&1; do
  echo "waiting for ollama..."
  sleep 1
done




ollama pull qwen2.5:7b-instruct
ollama pull mxbai-embed-large
wait -n

