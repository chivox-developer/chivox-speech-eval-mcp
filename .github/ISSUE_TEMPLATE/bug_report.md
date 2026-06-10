---
name: Bug Report
about: Report an issue with the Chivox MCP service
title: '[Bug] '
labels: bug
---

## Description

A clear description of the issue.

## Environment

- **Client:** (e.g., Claude Desktop, Cursor, custom client)
- **Auth type:** B2C (API Key) / B2B (JWT)
- **API Key prefix:** (e.g., `sk-a1b2...`, do NOT include the full key)

## Steps to Reproduce

1. ...
2. ...

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Request / Response

```json
// MCP request (remove sensitive data)
{
  "method": "tools/call",
  "params": {
    "name": "...",
    "arguments": { ... }
  }
}
```

```json
// Response or error
{ ... }
```

## Additional Context

Any other relevant information (audio format, file size, etc.)
