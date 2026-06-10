# 驰声语音评测 MCP 服务接入文档

> 服务地址：`https://mcp-global.cloud.chivox.com`

---

## 目录

- [服务概述](#1-服务概述)
- [认证方式](#2-认证方式)
- [MCP 协议交互](#3-mcp-协议交互)
- [评测工具](#4-评测工具)
- [流式评测](#5-流式评测)
- [AI 客户端配置](#6-ai-客户端配置)
- [错误处理](#7-错误处理)
- [附录](#附录)

---

## 1. 服务概述

驰声语音评测 MCP 服务基于 [Model Context Protocol](https://modelcontextprotocol.io/) 标准，将语音评测能力封装为 MCP 工具，供 AI 客户端（Claude Desktop、Cursor、自定义 Agent 等）直接调用。

**支持的评测能力：**

| 类别 | 工具数 | 说明 |
|------|--------|------|
| 英文评测 | 10 | 单词、句子、段落、自然拼读、实时朗读、口语选择题等 |
| 中文评测 | 6 | 拼音、汉字、词句、段落、有限分支识别、AI Talk |
| 流式评测 | 1 | 通过 WebSocket 实时传输音频并获取评测结果 |

**服务端点：**

| 端点 | 说明 |
|------|------|
| `POST https://mcp-global.cloud.chivox.com/` | MCP JSON-RPC 主端点 |
| `WSS wss://mcp-global.cloud.chivox.com/ws/audio/{session_id}` | 流式评测 WebSocket 端点 |

---

## 2. 认证方式

所有请求需在 HTTP 头中携带 Bearer Token：

```http
Authorization: Bearer <token>
```

服务支持两种认证类型，根据 Token 格式自动识别：

### 2.1 B2C 认证（API Key）

适用于个人用户。Token 为平台分配的 API Key（`sk-` 前缀）。

```http
Authorization: Bearer sk-a1b2c3d4e5f6...
```

API Key 通过平台控制台创建和管理，关联有总量配额和周期配额。

### 2.2 B2B 认证（JWT 签名）

适用于企业租户。Token 为客户端使用凭证签发的 JWT。

**凭证说明：**

企业租户通过平台获取一对凭证：

| 凭证 | 格式 | 用途 |
|------|------|------|
| Access Key | `cvx_ak_<40位十六进制>` | 标识调用方，放入 JWT Claims |
| Secret Key | `cvx_sk_<64位十六进制>` | 签名密钥，仅客户端持有 |

> Secret Key 仅在创建时返回一次，请妥善保管。

**JWT Token 生成规范：**

| 项目 | 说明 |
|------|------|
| 签名算法 | HS256 (HMAC-SHA256) |
| 签名密钥 | Secret Key 原文 |
| 建议有效期 | 5 分钟 |

**JWT Claims：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_key` | string | 是 | 客户端的 Access Key |
| `iat` | int64 | 是 | 签发时间（Unix 时间戳，秒） |
| `exp` | int64 | 是 | 过期时间（Unix 时间戳，秒） |

**生成示例：**

<details>
<summary>Python</summary>

```python
import jwt
import time

access_key = "cvx_ak_xxxxxxxxxxxxxxxxxxxx"
secret_key = "cvx_sk_xxxxxxxxxxxxxxxxxxxx"

now = int(time.time())
payload = {
    "access_key": access_key,
    "iat": now,
    "exp": now + 300,  # 5 分钟有效期
}

token = jwt.encode(payload, secret_key, algorithm="HS256")

# 使用方式
headers = {"Authorization": f"Bearer {token}"}
```

</details>

<details>
<summary>Node.js</summary>

```javascript
const jwt = require("jsonwebtoken");

const accessKey = "cvx_ak_xxxxxxxxxxxxxxxxxxxx";
const secretKey = "cvx_sk_xxxxxxxxxxxxxxxxxxxx";

const now = Math.floor(Date.now() / 1000);
const token = jwt.sign(
  { access_key: accessKey, iat: now, exp: now + 300 },
  secretKey,
  { algorithm: "HS256" }
);

// 使用方式
const headers = { Authorization: `Bearer ${token}` };
```

</details>

<details>
<summary>Go</summary>

```go
import (
    "time"
    "github.com/golang-jwt/jwt/v5"
)

accessKey := "cvx_ak_xxxxxxxxxxxxxxxxxxxx"
secretKey := "cvx_sk_xxxxxxxxxxxxxxxxxxxx"

now := time.Now()
claims := jwt.MapClaims{
    "access_key": accessKey,
    "iat":        now.Unix(),
    "exp":        now.Add(5 * time.Minute).Unix(),
}

token, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(secretKey))

// 使用方式: Authorization: Bearer <token>
```

</details>

<details>
<summary>Java</summary>

```java
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import java.util.Date;

String accessKey = "cvx_ak_xxxxxxxxxxxxxxxxxxxx";
String secretKey = "cvx_sk_xxxxxxxxxxxxxxxxxxxx";

long now = System.currentTimeMillis();
String token = Jwts.builder()
    .claim("access_key", accessKey)
    .setIssuedAt(new Date(now))
    .setExpiration(new Date(now + 300_000))  // 5 分钟
    .signWith(SignatureAlgorithm.HS256, secretKey.getBytes())
    .compact();

// 使用方式: Authorization: Bearer <token>
```

</details>

---

## 3. MCP 协议交互

服务使用 MCP JSON-RPC 2.0 协议，所有请求发送至 `POST https://mcp-global.cloud.chivox.com/`。

### 3.1 初始化连接

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

### 3.2 获取工具列表

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### 3.3 调用评测工具

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "en_word_eval",
    "arguments": {
      "ref_text": "hello",
      "audio_base64": "<base64编码的音频数据>",
      "accent": 2,
      "rank": 100
    }
  }
}
```

---

## 4. 评测工具

### 4.1 音频输入

所有评测工具支持两种音频输入方式（二选一）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `audio_base64` | string | Base64 编码的音频数据 |
| `audio_url` | string | 可访问的音频 HTTP(S) URL |

- 音频文件最大 **50MB**
- 支持格式：MP3、WAV 等

### 4.2 英文评测工具

**通用可选参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `accent` | number | 3 | 发音类型：1=英式, 2=美式, 3=不区分 |
| `rank` | number | 100 | 评分制：4 或 100 |
| `attachAudioUrl` | number | 0 | 是否返回音频 URL：0=否, 1=是 |

| 工具名 | 说明 | 额外参数 |
|--------|------|----------|
| `en_word_eval` | 单词评测 — 总分及每个音标得分 | `voiced`: 0=宽松, 1=严格(默认) |
| `en_word_correction` | 单词纠音 — 发音纠正建议 | — |
| `en_phonics_eval` | 自然拼读评测 | — |
| `en_sentence_eval` | 句子评测 — 流利度、准确度、完整度、每词得分 | `voiced`: 0=宽松, 1=严格(默认) |
| `en_sentence_correction` | 句子纠音 — 发音纠正建议 | — |
| `en_vocab_eval` | 多词评测 | — |
| `en_paragraph_eval` | 段落评测 — 每句、每词得分 | `precision`: 1(默认) 或 0.5 |
| `en_realtime_eval` | 实时朗读评测 | — |
| `en_choice_eval` | 口语选择题评测 | — |
| `en_semi_open_eval` | 半开放题（场景对话）评测 | — |

### 4.3 中文评测工具

**通用可选参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rank` | number | 100 | 评分制：4 或 100 |
| `age_group` | string | `adult` | 适用人群：`child`=儿童, `adult`=成人 |
| `attachAudioUrl` | number | 0 | 是否返回音频 URL |

| 工具名 | 说明 |
|--------|------|
| `cn_word_pinyin_eval` | 拼音评测 — 总分、声母、韵母、声调得分 |
| `cn_word_raw_eval` | 汉字评测 |
| `cn_sentence_eval` | 词句评测 — 总分、声调、准确度、流利度、完整度、每字得分 |
| `cn_paragraph_eval` | 段落评测 |
| `cn_rec_eval` | 有限分支识别 — 从预设选项中识别语音内容 |
| `cn_aitalk_eval` | AI Talk — 识别并评测中文语音内容 |

### 4.4 调用示例

**英文句子评测：**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "en_sentence_eval",
    "arguments": {
      "ref_text": "The quick brown fox jumps over the lazy dog",
      "audio_url": "https://example.com/audio/sentence.mp3",
      "accent": 2,
      "rank": 100
    }
  }
}
```

**中文词句评测：**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "cn_sentence_eval",
    "arguments": {
      "ref_text": "今天天气真好",
      "audio_base64": "//NExAAAAANIAA...",
      "age_group": "adult"
    }
  }
}
```

---

## 5. 流式评测

流式评测适用于实时音频传输场景，通过 WebSocket 逐帧发送音频并实时获取评测结果。

### 5.1 创建流式会话

通过 MCP 调用 `create_stream_session` 工具：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_stream_session",
    "arguments": {
      "core_type": "en.sent.score",
      "ref_text": "hello world",
      "audio_type": "mp3",
      "sample_rate": 16000
    }
  }
}
```

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `core_type` | string | 是 | — | 评测类型（见[附录 A](#a-评测类型速查表)） |
| `ref_text` | string | 是 | — | 参考文本 |
| `audio_type` | string | 否 | `mp3` | 音频格式：mp3, wav |
| `sample_rate` | number | 否 | 16000 | 采样率 (Hz) |
| `channel` | number | 否 | 1 | 声道数：1=单声道, 2=立体声 |
| `sample_bytes` | number | 否 | 2 | 采样位深：2=16bit |
| `accent` | number | 否 | 3 | 英文发音类型 |
| `rank` | number | 否 | 100 | 评分制 |
| `attachAudioUrl` | number | 否 | 0 | 是否返回音频 URL |
| `age_group` | string | 否 | `adult` | 中文适用人群 |

**返回：**

```json
{
  "session_id": "stream-1720000000000-a3b2c1",
  "status": "created",
  "ws_url": "wss://mcp-global.cloud.chivox.com/ws/audio/stream-1720000000000-a3b2c1",
  "message": "会话已创建。通过 WebSocket 连接 ws_url 发送音频流"
}
```

### 5.2 WebSocket 音频传输

使用返回的 `ws_url` 建立 WebSocket 连接，然后：

**客户端 → 服务端：**

| 帧类型 | 内容 | 说明 |
|--------|------|------|
| Binary | 原始音频数据 | 逐帧发送音频，建议每帧 8KB |
| Text | `{"cmd": "stop"}` | 通知服务端音频发送完毕 |

**服务端 → 客户端：**

```json
// 中间结果（实时推送）
{"type": "intermediate", "data": { ... }}

// 最终结果（评测完成）
{"type": "result", "data": { ... }}

// 错误
{"type": "error", "data": {"message": "错误描述"}}
```

### 5.3 Python 完整示例

```python
import asyncio
import json
import httpx
import websockets

API_KEY = "sk-your-api-key"
BASE_URL = "https://mcp-global.cloud.chivox.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def mcp_request(method, params, req_id=1):
    body = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params,
    }
    resp = httpx.post(f"{BASE_URL}/", json=body, headers=HEADERS)
    return resp.json()


async def stream_eval(audio_path, core_type, ref_text):
    # 1. Initialize MCP connection
    mcp_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "demo", "version": "1.0.0"},
    })

    # 2. Create streaming session
    result = mcp_request("tools/call", {
        "name": "create_stream_session",
        "arguments": {
            "core_type": core_type,
            "ref_text": ref_text,
            "audio_type": "mp3",
            "sample_rate": 16000,
        },
    }, req_id=2)

    session_data = json.loads(result["result"]["content"][0]["text"])
    ws_url = session_data["ws_url"]
    print(f"WebSocket URL: {ws_url}")

    # 3. Connect WebSocket and send audio
    async with websockets.connect(ws_url) as ws:
        with open(audio_path, "rb") as f:
            while chunk := f.read(8192):
                await ws.send(chunk)

        await ws.send(json.dumps({"cmd": "stop"}))

        async for message in ws:
            data = json.loads(message)
            if data["type"] == "result":
                print("Result:", json.dumps(data["data"], indent=2, ensure_ascii=False))
                break
            elif data["type"] == "error":
                print("Error:", data["data"])
                break


asyncio.run(stream_eval("audio.mp3", "en.sent.score", "hello world"))
```

---

## 6. AI 客户端配置

### 6.1 Claude Desktop

编辑配置文件 `~/.claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "chivox-eval": {
      "url": "https://mcp-global.cloud.chivox.com/",
      "headers": {
        "Authorization": "Bearer <your_token>"
      }
    }
  }
}
```

### 6.2 Cursor

在 Cursor 的 MCP 设置中添加远程服务器：

- **URL：** `https://mcp-global.cloud.chivox.com/`
- **Headers：** `Authorization: Bearer <your_token>`

### 6.3 自定义客户端

使用任何支持 MCP 协议的客户端库接入，核心流程：

1. 向 `POST https://mcp-global.cloud.chivox.com/` 发送 `initialize` 请求
2. 发送 `tools/list` 获取可用工具
3. 发送 `tools/call` 调用具体评测工具
4. 所有请求携带 `Authorization: Bearer <token>` 头

> `<token>` 为 API Key（B2C）或 JWT Token（B2B）。

---

## 7. 错误处理

### HTTP 层错误

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 401 | Token 缺失、格式错误或 JWT 验签失败/过期 | 检查 Authorization 头，B2B 注意 JWT 有效期 |
| 403 | API Key 无效、已禁用或配额耗尽 | 检查 Key 状态和剩余配额 |
| 403 (B2B) | 凭证被暂停/冻结、租户被禁用或配额耗尽 | 联系管理员检查凭证和租户状态 |

### MCP 层错误

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "评测失败: 具体错误信息"
  }
}
```

### 常见业务错误

| 错误 | 说明 |
|------|------|
| 音频参数缺失 | 未提供 `audio_base64` 或 `audio_url` |
| 音频超限 | 文件超过 50MB |
| 评测超时 | 后端处理超时，检查音频质量后重试 |

---

## 附录

### A. 评测类型速查表

| 工具名 | core_type | 说明 |
|--------|-----------|------|
| `en_word_eval` | `en.word.score` | 英文单词评测 |
| `en_word_correction` | `en.word.pron` | 英文单词纠音 |
| `en_phonics_eval` | `en.nsp.score` | 英文自然拼读 |
| `en_sentence_eval` | `en.sent.score` | 英文句子评测 |
| `en_sentence_correction` | `en.sent.pron` | 英文句子纠音 |
| `en_vocab_eval` | `en.vocabs.pron` | 英文多词评测 |
| `en_paragraph_eval` | `en.pred.score` | 英文段落评测 |
| `en_realtime_eval` | `en.rltm.score` | 英文实时朗读 |
| `en_choice_eval` | `en.choc.score` | 英文口语选择题 |
| `en_semi_open_eval` | `en.scne.exam` | 英文半开放题 |
| `cn_word_pinyin_eval` | `cn.word.score` | 中文拼音评测 |
| `cn_word_raw_eval` | `cn.word.raw` | 中文汉字评测 |
| `cn_sentence_eval` | `cn.sent.raw` | 中文词句评测 |
| `cn_paragraph_eval` | `cn.pred.raw` | 中文段落评测 |
| `cn_rec_eval` | `cn.rec.raw` | 中文有限分支识别 |
| `cn_aitalk_eval` | `cn.recscore.raw` | 中文 AI Talk |

### B. 音频建议

- 采样率：16kHz
- 声道：单声道
- 格式：MP3 或 WAV
- 单次请求不超过 50MB
