"""
Quick test: Chivox MCP speech evaluation
Usage: python test_eval.py

Prerequisites: pip install httpx
"""

import json
import httpx

API_KEY = "sk-your-api-key"
BASE_URL = "https://mcp.cloud.chivox.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

session_id = None


def mcp_request(method, params, req_id=1):
    global session_id
    hdrs = {**HEADERS}
    if session_id:
        hdrs["Mcp-Session-Id"] = session_id

    resp = httpx.post(
        f"{BASE_URL}/",
        json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": params},
        headers=hdrs,
        timeout=60,
    )

    if not session_id and "Mcp-Session-Id" in resp.headers:
        session_id = resp.headers["Mcp-Session-Id"]

    return resp.json()


# 1. Initialize
print("=== Initialize ===")
result = mcp_request("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "quick-test", "version": "1.0.0"},
})
print(json.dumps(result, indent=2, ensure_ascii=False))

# 2. List tools
print("\n=== Tools List ===")
result = mcp_request("tools/list", {}, req_id=2)
for tool in result.get("result", {}).get("tools", []):
    print(f"  - {tool['name']}: {tool.get('description', '')[:60]}")

# 3. Call en_word_eval
print("\n=== Evaluate 'hello' ===")
result = mcp_request("tools/call", {
    "name": "en_word_eval",
    "arguments": {
        "ref_text": "hello",
        "audio_url": "https://dict.youdao.com/dictvoice?audio=hello&type=1",
    },
}, req_id=3)

content = result.get("result", {}).get("content", [])
if content and content[0].get("type") == "text":
    eval_result = json.loads(content[0]["text"])
    print(json.dumps(eval_result, indent=2, ensure_ascii=False))
else:
    print(json.dumps(result, indent=2, ensure_ascii=False))
