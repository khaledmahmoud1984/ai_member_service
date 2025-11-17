#!/bin/bash
set -e
bash /app/health/chat_health.sh
bash /app/health/embedding_health.sh
