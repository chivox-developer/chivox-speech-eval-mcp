/**
 * Quick test: Chivox MCP speech evaluation
 * Usage: node test_eval.js
 *
 * No external dependencies required (uses built-in fetch).
 */

const API_KEY = "sk-your-api-key";
const BASE_URL = "https://mcp.cloud.chivox.com";

let sessionId = null;

async function mcpRequest(method, params, reqId = 1) {
  const headers = {
    Authorization: `Bearer ${API_KEY}`,
    "Content-Type": "application/json",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;

  const resp = await fetch(`${BASE_URL}/`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: reqId,
      method,
      params,
    }),
  });

  if (!sessionId && resp.headers.get("Mcp-Session-Id")) {
    sessionId = resp.headers.get("Mcp-Session-Id");
  }

  return resp.json();
}

async function main() {
  // 1. Initialize
  console.log("=== Initialize ===");
  let result = await mcpRequest("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "quick-test-js", version: "1.0.0" },
  });
  console.log(JSON.stringify(result, null, 2));

  // 2. List tools
  console.log("\n=== Tools List ===");
  result = await mcpRequest("tools/list", {}, 2);
  const tools = result?.result?.tools || [];
  tools.forEach((t) =>
    console.log(`  - ${t.name}: ${(t.description || "").slice(0, 60)}`)
  );

  // 3. Evaluate 'hello'
  console.log("\n=== Evaluate 'hello' ===");
  result = await mcpRequest(
    "tools/call",
    {
      name: "en_word_eval",
      arguments: {
        ref_text: "hello",
        audio_url: "https://dict.youdao.com/dictvoice?audio=hello&type=1",
      },
    },
    3
  );

  const content = result?.result?.content || [];
  if (content.length > 0 && content[0].type === "text") {
    console.log(JSON.stringify(JSON.parse(content[0].text), null, 2));
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

main().catch(console.error);
