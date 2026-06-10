"""
客户服务端示例 — API Key 安全中转

架构：
  用户浏览器 → (用户自有认证) → 本服务 → (Bearer sk-xxx) → MCP 服务
  API Key 仅存在于本服务，不暴露给终端用户

依赖安装：
  pip install flask requests websocket-client

启动：
  python server.py

环境变量：
  MCP_BASE_URL   - MCP 服务地址 (默认 https://mcp-global.cloud.chivox.com)
  MCP_API_KEY    - 你的 API Key (sk-xxx)
  SERVER_SECRET  - 用户 Token 签名密钥
"""

import os
import json
import time
import hashlib
import hmac
import base64
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
import requests as http_requests

# ============================================================
# 配置
# ============================================================

MCP_BASE_URL = os.environ.get("MCP_BASE_URL", "https://mcp-global.cloud.chivox.com")
MCP_API_KEY = os.environ.get("MCP_API_KEY", "sk-your-api-key-here")
SERVER_SECRET = os.environ.get("SERVER_SECRET", "change-me-in-production")
PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__, static_folder="static", static_url_path="/static")

# ============================================================
# 简易用户认证（示例用，生产环境请替换为正式认证系统）
# ============================================================

# 模拟用户数据库
USERS = {
    "user1": {"password": "pass123", "name": "测试用户1"},
    "user2": {"password": "pass456", "name": "测试用户2"},
}

# 活跃 Token 存储（生产环境应使用 Redis 等）
active_tokens = {}


def generate_token(user_id):
    """生成简易用户 Token"""
    payload = f"{user_id}:{time.time()}"
    sig = hmac.new(SERVER_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()
    active_tokens[token] = {"user_id": user_id, "created_at": time.time()}
    return token


def verify_token(token):
    """验证用户 Token，返回 user_id 或 None"""
    info = active_tokens.get(token)
    if not info:
        return None
    # Token 有效期 24 小时
    if time.time() - info["created_at"] > 86400:
        del active_tokens[token]
        return None
    return info["user_id"]


def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing Authorization header"}), 401
        token = auth[7:]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "invalid or expired token"}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


# ============================================================
# 用户认证接口
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():
    """用户登录，返回 Token"""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "invalid username or password"}), 401

    token = generate_token(username)
    return jsonify({
        "token": token,
        "user": {"id": username, "name": user["name"]},
    })


# ============================================================
# MCP 会话管理
# ============================================================

# 用户 → MCP Session ID 映射
user_sessions = {}


def get_mcp_session(user_id):
    """获取或创建用户的 MCP 会话"""
    session_info = user_sessions.get(user_id)

    # 已有会话且未过期（30 分钟）
    if session_info and time.time() - session_info["created_at"] < 1800:
        return session_info["session_id"]

    # 初始化新 MCP 会话
    resp = http_requests.post(
        MCP_BASE_URL + "/",
        headers={
            "Authorization": f"Bearer {MCP_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": f"customer-proxy-{user_id}", "version": "1.0"},
            },
        },
        timeout=10,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"MCP 初始化失败: {resp.status_code} {resp.text}")

    session_id = resp.headers.get("Mcp-Session-Id", "")
    if not session_id:
        raise RuntimeError("MCP 服务未返回 Session ID")

    user_sessions[user_id] = {
        "session_id": session_id,
        "created_at": time.time(),
    }
    return session_id


def mcp_request(user_id, method, params, timeout=10):
    """发送 MCP 请求，自动处理会话过期重试"""
    for attempt in range(2):
        session_id = get_mcp_session(user_id)
        resp = http_requests.post(
            MCP_BASE_URL + "/",
            headers={
                "Authorization": f"Bearer {MCP_API_KEY}",
                "Content-Type": "application/json",
                "Mcp-Session-Id": session_id,
            },
            json={
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": method,
                "params": params,
            },
            timeout=timeout,
        )

        # 会话过期，清除后重试
        if resp.status_code in (404, 400) and attempt == 0:
            user_sessions.pop(user_id, None)
            continue

        if resp.status_code != 200:
            raise RuntimeError(f"MCP 请求失败: {resp.status_code} {resp.text}")

        result = resp.json()
        if "error" in result:
            raise RuntimeError(f"MCP 错误: {result['error']}")
        return result

    raise RuntimeError("MCP 请求失败: 重试已耗尽")


# ============================================================
# MCP 代理接口
# ============================================================

@app.route("/api/mcp/tools", methods=["GET"])
@require_auth
def list_tools():
    """获取可用工具列表"""
    try:
        result = mcp_request(request.user_id, "tools/list", {})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502

    tools = result.get("result", {}).get("tools", [])
    return jsonify({"tools": tools})


@app.route("/api/mcp/call", methods=["POST"])
@require_auth
def call_tool():
    """调用 MCP 工具

    请求体：
    {
        "tool": "en_word_eval",
        "arguments": {
            "ref_text": "hello",
            "audio_url": "https://..."
        }
    }
    """
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool", "")
    arguments = data.get("arguments", {})

    if not tool_name:
        return jsonify({"error": "missing tool name"}), 400

    try:
        result = mcp_request(
            request.user_id,
            "tools/call",
            {"name": tool_name, "arguments": arguments},
            timeout=60,
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502

    # 提取评测结果
    content = result.get("result", {}).get("content", [])
    if content and content[0].get("type") == "text":
        try:
            eval_result = json.loads(content[0]["text"])
            return jsonify({"success": True, "result": eval_result})
        except json.JSONDecodeError:
            return jsonify({"success": True, "result": content[0]["text"]})

    return jsonify({"success": False, "error": "unexpected response"}), 500


# ============================================================
# 流式评测接口
# ============================================================

@app.route("/api/mcp/stream/create", methods=["POST"])
@require_auth
def create_stream():
    """创建流式评测会话

    请求体：
    {
        "core_type": "en.sent.score",
        "ref_text": "hello world",
        "audio_type": "mp3"
    }

    返回：
    {
        "session_id": "stream-xxx",
        "ws_url": "ws://mcp-global.cloud.chivox.com/ws/audio/stream-xxx"
    }
    """
    data = request.get_json(silent=True) or {}
    core_type = data.get("core_type", "")
    ref_text = data.get("ref_text", "")

    if not core_type or not ref_text:
        return jsonify({"error": "core_type and ref_text required"}), 400

    arguments = {
        "core_type": core_type,
        "ref_text": ref_text,
        "audio_type": data.get("audio_type", "mp3"),
        "sample_rate": data.get("sample_rate", 16000),
    }

    try:
        result = mcp_request(
            request.user_id,
            "tools/call",
            {"name": "create_stream_session", "arguments": arguments},
            timeout=15,
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502

    content = result.get("result", {}).get("content", [])
    if content and content[0].get("type") == "text":
        stream_info = json.loads(content[0]["text"])
        return jsonify({
            "session_id": stream_info["session_id"],
            "ws_url": stream_info.get("ws_url", ""),
        })

    return jsonify({"error": "failed to create stream session"}), 500


# ============================================================
# 前端页面 & 健康检查
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mcp_base_url": MCP_BASE_URL})


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════╗
║         客户服务端 (API Key 安全中转)              ║
╠══════════════════════════════════════════════════╣
║  监听端口:    {PORT:<35}║
║  MCP 服务:    {MCP_BASE_URL:<35}║
║  API Key:     {MCP_API_KEY[:12] + '...':<35}║
╠══════════════════════════════════════════════════╣
║  接口列表:                                        ║
║  POST /api/login          用户登录                ║
║  GET  /api/mcp/tools      获取工具列表            ║
║  POST /api/mcp/call       调用评测工具            ║
║  POST /api/mcp/stream/create  创建流式会话        ║
║  GET  /health             健康检查                ║
╚══════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=PORT, debug=True)
