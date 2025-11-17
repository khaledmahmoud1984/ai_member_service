#model_name=os.getenv("MODEL_NAME","qwen2.5:7b-instruct")
#!/bin/bash
set -e
curl -sf http://localhost:11434/api/chat \
  -d '{"model":"qwen2.5:7b-instruct", "messages":[{"role":"user","content":"hi"}]}' \
| grep -q total_duration
