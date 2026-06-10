# Customer Proxy Server (Python Flask)

A secure proxy server that keeps your API Key on the server side, exposing a simple REST API and web UI to end users.

## Architecture

```
Browser / Client
      │
      ▼  (user's own auth)
┌──────────────────┐
│  This Flask App  │  ← API Key stored here
└──────┬───────────┘
       │  (Bearer sk-xxx)
       ▼
┌──────────────────┐
│  Chivox MCP      │
│  Service          │
└──────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MCP_API_KEY="sk-your-api-key"
export MCP_BASE_URL="https://mcp.cloud.chivox.com"  # optional, this is the default
export SERVER_SECRET="your-session-secret"

# Run
python server.py
```

Open `http://localhost:5000` in your browser.

## Test Users (Demo)

| Username | Password |
|----------|----------|
| `user1` | `pass123` |
| `user2` | `pass456` |

> Replace with your own authentication system in production.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/login` | User login, returns token |
| GET | `/api/mcp/tools` | List available evaluation tools |
| POST | `/api/mcp/call` | Call an evaluation tool |
| POST | `/api/mcp/stream/create` | Create a streaming evaluation session |
| GET | `/health` | Health check |

## Test with curl

```bash
bash test_client.sh http://localhost:5000
```

## Web UI Features

- Login with demo credentials
- Dynamic tool loading from MCP service
- Non-streaming evaluation (audio URL or file upload)
- Streaming evaluation (microphone recording via WebSocket)
- Score visualization with detail breakdown
