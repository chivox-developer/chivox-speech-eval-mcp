#!/bin/bash
# 客户服务端测试脚本
# 用法: bash test_client.sh [server_url]

BASE_URL="${1:-http://localhost:5000}"

echo "=== 1. 登录 ==="
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}')
echo "$LOGIN_RESP" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESP"

TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['token'])" 2>/dev/null)
if [ -z "$TOKEN" ]; then
  echo "登录失败，退出"
  exit 1
fi
echo ""

echo "=== 2. 获取工具列表 ==="
curl -s -X GET "$BASE_URL/api/mcp/tools" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null
echo ""

echo "=== 3. 调用英文单词评测 ==="
curl -s -X POST "$BASE_URL/api/mcp/call" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1"
    }
  }' | python3 -c "
import sys, json
r = json.loads(sys.stdin.read(), strict=False)
if r.get('success'):
    result = r['result'].get('result', {})
    print(f'overall: {result.get(\"overall\")}')
    print(f'accuracy: {result.get(\"accuracy\")}')
    print(f'pron: {result.get(\"pron\")}')
else:
    print(f'error: {r.get(\"error\")}')
"
echo ""

echo "=== 4. 创建流式评测会话 ==="
curl -s -X POST "$BASE_URL/api/mcp/stream/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "core_type": "en.sent.score",
    "ref_text": "hello world",
    "audio_type": "mp3"
  }' | python3 -m json.tool 2>/dev/null
echo ""

echo "=== 测试完成 ==="
