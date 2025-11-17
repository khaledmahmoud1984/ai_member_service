#!/bin/bash
set -e
curl -sf http://localhost:11434/api/embeddings \
-d '{"model":"mxbai-embed-large","prompt":"hi"}' \
| grep -q embedding
