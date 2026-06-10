# Chivox Speech Evaluation MCP Server

**驰声语音评测 MCP 服务**

> Integrate AI-powered speech & pronunciation evaluation into Claude, Cursor, and any MCP-compatible client.

[English](#english) | [中文](#中文)

---

## English

### What is this?

Chivox Speech Evaluation MCP Server exposes professional speech assessment capabilities as [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) tools. Connect your AI assistant to our cloud service and let it evaluate pronunciation quality for English and Chinese.

**Service endpoint:** `https://mcp.cloud.chivox.com`

### Features

- **16 evaluation tools** — word, sentence, paragraph, phonics, real-time reading, and more
- **English + Chinese** — 10 English tools, 6 Chinese tools
- **Real-time streaming** — WebSocket-based live audio evaluation
- **Multiple audio inputs** — URL, Base64, or file upload
- **Works everywhere** — Claude Desktop, Cursor, and any MCP-compatible client
- **Dual authentication** — B2C (API Key) and B2B (JWT)

### Quick Start

#### 1. Get Your API Key

Contact [Chivox](https://www.chivox.com) to obtain your API Key (`sk-xxx` format).

#### 2. Configure Your AI Client

**Claude Desktop** — Edit `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chivox-eval": {
      "url": "https://mcp.cloud.chivox.com",
      "headers": {
        "Authorization": "Bearer sk-your-api-key"
      }
    }
  }
}
```

**Cursor** — Add remote MCP server in Settings > MCP:

- URL: `https://mcp.cloud.chivox.com/`
- Headers: `Authorization: Bearer sk-your-api-key`

#### 3. Try It

Ask your AI assistant:

> "Use the en_word_eval tool to evaluate my pronunciation of the word 'hello'. Here is the audio: https://dict.youdao.com/dictvoice?audio=hello&type=1"

### Available Tools

#### English Evaluation

| Tool | Description | core_type |
|------|-------------|-----------|
| `en_word_eval` | Word pronunciation scoring | `en.word.score` |
| `en_word_correction` | Word pronunciation correction | `en.word.pron` |
| `en_phonics_eval` | Phonics evaluation | `en.nsp.score` |
| `en_sentence_eval` | Sentence reading assessment | `en.sent.score` |
| `en_sentence_correction` | Sentence pronunciation correction | `en.sent.pron` |
| `en_vocab_eval` | Multi-word evaluation | `en.vocabs.pron` |
| `en_paragraph_eval` | Paragraph reading assessment | `en.pred.score` |
| `en_realtime_eval` | Real-time reading evaluation | `en.rltm.score` |
| `en_choice_eval` | Oral choice evaluation | `en.choc.score` |
| `en_semi_open_eval` | Semi-open question evaluation | `en.scne.exam` |

#### Chinese Evaluation

| Tool | Description | core_type |
|------|-------------|-----------|
| `cn_word_pinyin_eval` | Pinyin pronunciation scoring | `cn.word.score` |
| `cn_word_raw_eval` | Character pronunciation scoring | `cn.word.raw` |
| `cn_sentence_eval` | Sentence reading assessment | `cn.sent.raw` |
| `cn_paragraph_eval` | Paragraph reading assessment | `cn.pred.raw` |
| `cn_rec_eval` | Limited-branch recognition | `cn.rec.raw` |
| `cn_aitalk_eval` | AI Talk — oral expression evaluation | `cn.recscore.raw` |

#### Streaming Evaluation

| Tool | Description |
|------|-------------|
| `create_stream_session` | Create a streaming session, returns `session_id` and WebSocket URL |

### Streaming Workflow

```
1. Create session    →  tools/call: create_stream_session
                         ↓ returns ws_url
2. Connect WebSocket →  wss://mcp.cloud.chivox.com/ws/audio/{session_id}
                         ↓
3. Send audio frames →  Binary frames (8KB chunks recommended)
                         ↓
4. Stop & get result →  Send {"cmd": "stop"}, receive final scores
```

### Examples

| Example | Description |
|---------|-------------|
| [Customer Proxy Server](examples/customer-server/) | Python Flask server that securely proxies MCP calls (keeps API Key server-side) |
| [Claude Desktop Config](examples/claude-desktop/) | Configuration guide for Claude Desktop |
| [Cursor Config](examples/cursor/) | Configuration guide for Cursor |
| [Quick Test Scripts](examples/quick-test/) | Minimal test scripts in Python, Node.js, and curl |

### Documentation

- [API Reference](docs/api-reference.md) — Full protocol documentation, authentication, tool parameters, and streaming details

### Support

- Website: [chivox.com](https://www.chivox.com)
- Issues: [GitHub Issues](https://github.com/chivox-developer/chivox-speech-eval-mcp/issues)

---

## 中文

### 简介

驰声语音评测 MCP 服务基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 标准，将专业语音评测能力封装为 MCP 工具，供 AI 客户端（Claude Desktop、Cursor 等）直接调用。

**服务地址：** `https://mcp.cloud.chivox.com`

### 功能特性

- **16 种评测工具** — 单词、句子、段落、自然拼读、实时朗读等
- **中英文双语** — 10 种英文评测 + 6 种中文评测
- **实时流式评测** — 通过 WebSocket 实时推送音频，获取评测结果
- **多种音频输入** — 支持 URL、Base64 编码、文件上传
- **广泛兼容** — 支持 Claude Desktop、Cursor 及任何 MCP 兼容客户端
- **双认证模式** — B2C（API Key）和 B2B（JWT 签名）

### 快速开始

#### 1. 获取 API Key

联系[驰声](https://www.chivox.com)获取 API Key（`sk-xxx` 格式）。

#### 2. 配置 AI 客户端

**Claude Desktop** — 编辑 `~/.claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "chivox-eval": {
      "url": "https://mcp.cloud.chivox.com",
      "headers": {
        "Authorization": "Bearer sk-your-api-key"
      }
    }
  }
}
```

**Cursor** — 在 Settings > MCP 中添加远程服务器：

- URL：`https://mcp.cloud.chivox.com/`
- Headers：`Authorization: Bearer sk-your-api-key`

#### 3. 开始使用

向 AI 助手提问：

> "使用 cn_sentence_eval 工具评测我朗读'今天天气真好'的发音，音频地址是 https://example.com/audio.mp3"

### 评测工具列表

#### 英文评测

| 工具名 | 说明 | core_type |
|--------|------|-----------|
| `en_word_eval` | 单词评测 — 总分及每个音标得分 | `en.word.score` |
| `en_word_correction` | 单词纠音 — 发音纠正建议 | `en.word.pron` |
| `en_phonics_eval` | 自然拼读评测 | `en.nsp.score` |
| `en_sentence_eval` | 句子评测 — 流利度、准确度、完整度 | `en.sent.score` |
| `en_sentence_correction` | 句子纠音 | `en.sent.pron` |
| `en_vocab_eval` | 词语评测 | `en.vocabs.pron` |
| `en_paragraph_eval` | 段落评测 — 每句、每词得分 | `en.pred.score` |
| `en_realtime_eval` | 实时朗读评测 | `en.rltm.score` |
| `en_choice_eval` | 口语选择题评测 | `en.choc.score` |
| `en_semi_open_eval` | 半开放题评测 | `en.scne.exam` |

#### 中文评测

| 工具名 | 说明 | core_type |
|--------|------|-----------|
| `cn_word_pinyin_eval` | 拼音评测 — 总分、声母、韵母、声调 | `cn.word.score` |
| `cn_word_raw_eval` | 汉字评测 | `cn.word.raw` |
| `cn_sentence_eval` | 词句评测 — 总分、声调、准确度、流利度 | `cn.sent.raw` |
| `cn_paragraph_eval` | 段落评测 | `cn.pred.raw` |
| `cn_rec_eval` | 有限分支识别 | `cn.rec.raw` |
| `cn_aitalk_eval` | AI Talk — 识别并评测口语表达 | `cn.recscore.raw` |

#### 流式评测

| 工具名 | 说明 |
|--------|------|
| `create_stream_session` | 创建流式评测会话，返回 session_id 和 WebSocket 地址 |

### 流式评测流程

```
1. 创建会话      →  tools/call: create_stream_session
                      ↓ 返回 ws_url
2. 连接 WebSocket →  wss://mcp.cloud.chivox.com/ws/audio/{session_id}
                      ↓
3. 推送音频帧     →  二进制帧（建议每帧 8KB）
                      ↓
4. 停止并获取结果 →  发送 {"cmd": "stop"}，接收最终评分
```

### 示例

| 示例 | 说明 |
|------|------|
| [客户代理服务器](examples/customer-server/) | Python Flask 代理服务，API Key 安全中转 |
| [Claude Desktop 配置](examples/claude-desktop/) | Claude Desktop 接入指南 |
| [Cursor 配置](examples/cursor/) | Cursor 接入指南 |
| [快速测试脚本](examples/quick-test/) | Python、Node.js、curl 最小化调用示例 |

### 文档

- [API 接入文档](docs/api-reference.md) — 完整协议文档、认证方式、工具参数、流式评测说明

### 支持

- 官网：[chivox.com](https://www.chivox.com)
- 问题反馈：[GitHub Issues](https://github.com/chivox-developer/chivox-speech-eval-mcp/issues)

---

## License

The example code and documentation in this repository are licensed under the [MIT License](LICENSE).

The Chivox Speech Evaluation MCP Service itself is a commercial product. Please contact [Chivox](https://www.chivox.com) for service access and pricing.
