# Cursor Configuration

## Setup

1. Get your API Key from the [Chivox API Portal](https://api-portal.cloud.chivox.com) (format: `sk-xxx`)

2. Open Cursor Settings > MCP

3. Add a new remote MCP server:
   - **Name:** `chivox-eval`
   - **URL:** `https://mcp-global.cloud.chivox.com/`
   - **Headers:** `Authorization: Bearer sk-your-api-key`

Alternatively, create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "chivox-eval": {
      "url": "https://mcp-global.cloud.chivox.com",
      "headers": {
        "Authorization": "Bearer sk-your-api-key"
      }
    }
  }
}
```

4. Restart Cursor

## Usage

In Cursor's AI chat, you can ask:

- "Use en_sentence_eval to evaluate my pronunciation of 'The quick brown fox' from this audio URL: ..."
- "List all available Chivox evaluation tools"
- "Create a streaming evaluation session for real-time pronunciation assessment"
