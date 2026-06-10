#!/bin/bash
# Quick test: Chivox MCP speech evaluation
# Usage: API_KEY=sk-xxx bash test_eval.sh

API_KEY="${API_KEY:-sk-your-api-key}"
BASE_URL="${BASE_URL:-https://mcp.cloud.chivox.com}"

echo "=== 1. Initialize ==="
INIT_RESP=$(curl -s -X POST "$BASE_URL/" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl-test", "version": "1.0.0"}
    }
  }' -D /tmp/mcp_headers.txt)
echo "$INIT_RESP" | python3 -m json.tool 2>/dev/null || echo "$INIT_RESP"

# Extract session ID from response headers
SESSION_ID=$(grep -i 'Mcp-Session-Id' /tmp/mcp_headers.txt | tr -d '\r' | awk '{print $2}')
echo "Session ID: $SESSION_ID"
echo ""

echo "=== 2. List Tools ==="
curl -s -X POST "$BASE_URL/" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for t in data.get('result', {}).get('tools', []):
    print(f\"  - {t['name']}: {t.get('description', '')[:60]}\")
"
echo ""

echo "=== 3. Evaluate 'hello' ==="
curl -s -X POST "$BASE_URL/" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "en_word_eval",
      "arguments": {
        "ref_text": "hello",
        "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1"
      }
    }
  }' | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
content = data.get('result', {}).get('content', [])
if content and content[0].get('type') == 'text':
    result = json.loads(content[0]['text'])
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print(json.dumps(data, indent=2, ensure_ascii=False))
"
echo ""
echo "=== Done ==="
