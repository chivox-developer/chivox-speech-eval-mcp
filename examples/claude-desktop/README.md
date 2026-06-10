# Claude Desktop Configuration

## Setup

1. Get your API Key from [Chivox](https://www.chivox.com) (format: `sk-xxx`)

2. Edit `~/.claude/claude_desktop_config.json`:

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

3. Restart Claude Desktop

4. You should see Chivox evaluation tools in the tools list

## Usage

Ask Claude to evaluate pronunciation:

- "Use en_word_eval to evaluate the pronunciation of 'hello' from this audio: https://dict.youdao.com/dictvoice?audio=hello&type=1"
- "Use cn_sentence_eval to evaluate the Chinese pronunciation of '今天天气真好' from this audio URL: ..."
- "What English evaluation tools are available? List them with descriptions."

## B2B (JWT) Configuration

For enterprise users with Access Key / Secret Key, generate a JWT token first (see [API Reference](../../docs/api-reference.md#22-b2b-认证jwt-签名)), then use it in the config:

```json
{
  "mcpServers": {
    "chivox-eval": {
      "url": "https://mcp-global.cloud.chivox.com",
      "headers": {
        "Authorization": "Bearer <your-jwt-token>"
      }
    }
  }
}
```

> Note: JWT tokens expire (recommended: 5 minutes). You will need to regenerate and update the config periodically, or use a B2C API Key for convenience.
