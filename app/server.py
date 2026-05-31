#!/usr/bin/env python3
"""Tiny Sambop placeholder web + MCP server.

This is intentionally dependency-free so the Hermes playground can serve it now.
It provides a landing page, GitHub-login placeholder, and a small JSON-RPC-ish
MCP surface while the real OAuth/MCP implementation is still being designed.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HOST = os.getenv("SAMBOP_HOST", "127.0.0.1")
PORT = int(os.getenv("SAMBOP_PORT", "8788"))
PUBLIC_BASE_URL = os.getenv("SAMBOP_PUBLIC_BASE_URL", "https://sambop.com")
GITHUB_CLIENT_ID = os.getenv("SAMBOP_GITHUB_CLIENT_ID", "")
GITHUB_OAUTH_SCOPE = os.getenv("SAMBOP_GITHUB_SCOPE", "read:user user:email read:org")

PROJECTS = [
    {
        "name": "sambop",
        "owner": "1wayto",
        "repo": "https://github.com/1wayto/sambop",
        "description": "GitHub-native governance and MCP coordination for BYO-AI problem solving.",
        "skills": ["sambop-git-pr-workflow"],
        "status": "placeholder-mvp",
    }
]

SKILLS = [
    {
        "name": "sambop-git-pr-workflow",
        "version": "0.1.0",
        "repo": "https://github.com/1wayto/sambop/tree/main/skills/sambop-git-pr-workflow",
        "description": "Contribute to a Sambop repo through clone, branch, PR, review, and merge.",
        "install_hint": "Use Sambop MCP install_skill, or copy the SKILL.md into your agent's skill/instructions folder.",
    }
]

TOOLS = [
    {
        "name": "list_projects",
        "description": "List public Sambop projects available for AI/human collaboration.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_skills",
        "description": "List Sambop skills published by solved projects.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "install_skill",
        "description": "Return installation guidance for a Sambop skill on the user's platform.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "platform": {"type": "string", "default": "generic"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_login_url",
        "description": "Return the GitHub login URL for Sambop.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def html_page() -> bytes:
    login_note = "GitHub OAuth client not configured yet" if not GITHUB_CLIENT_ID else "Ready"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sambop — BYO AI. Solve together.</title>
  <meta name="description" content="Sambop is GitHub-native governance and MCP coordination for BYO-AI problem solving." />
  <style>
    :root {{ color-scheme: dark; --bg:#070716; --panel:#11112a; --ink:#f6f2ff; --muted:#b9b1d9; --hot:#ff4fd8; --gold:#ffd166; --cyan:#39e6ff; --green:#8cffc1; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background: radial-gradient(circle at 18% 12%, #442066 0, transparent 34%), radial-gradient(circle at 88% 16%, #09385a 0, transparent 30%), linear-gradient(135deg, #070716, #09091c 70%); color:var(--ink); }}
    a {{ color: inherit; }}
    .wrap {{ width:min(1120px, 92vw); margin:0 auto; }}
    nav {{ display:flex; justify-content:space-between; align-items:center; padding:28px 0; }}
    .brand {{ display:flex; align-items:center; gap:12px; font-weight:900; letter-spacing:-.04em; font-size:26px; }}
    .mark {{ width:38px; height:38px; border-radius:12px; background: conic-gradient(from 210deg, var(--hot), var(--gold), var(--cyan), var(--hot)); box-shadow:0 0 40px rgba(255,79,216,.35); }}
    .links {{ display:flex; gap:18px; color:var(--muted); font-size:14px; }}
    .hero {{ padding:70px 0 54px; display:grid; grid-template-columns: 1.1fr .9fr; gap:42px; align-items:center; }}
    h1 {{ font-size: clamp(48px, 7vw, 92px); line-height:.92; margin:0 0 24px; letter-spacing:-.07em; }}
    .grad {{ background:linear-gradient(90deg, var(--hot), var(--gold), var(--cyan)); -webkit-background-clip:text; color:transparent; }}
    .lead {{ color:var(--muted); font-size:20px; line-height:1.6; max-width:720px; }}
    .cta {{ display:flex; gap:14px; flex-wrap:wrap; margin-top:30px; }}
    .btn {{ border:1px solid rgba(255,255,255,.18); padding:14px 18px; border-radius:999px; text-decoration:none; background:rgba(255,255,255,.07); font-weight:800; }}
    .btn.primary {{ background:linear-gradient(90deg, var(--hot), #8a5cff); border:0; box-shadow:0 12px 50px rgba(255,79,216,.28); }}
    .card {{ background:linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.04)); border:1px solid rgba(255,255,255,.14); border-radius:28px; padding:24px; box-shadow:0 20px 90px rgba(0,0,0,.28); }}
    .terminal {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color:#d9fff2; font-size:14px; line-height:1.8; }}
    .pill {{ display:inline-flex; gap:8px; align-items:center; padding:8px 12px; border-radius:999px; background:rgba(57,230,255,.10); color:#bff7ff; border:1px solid rgba(57,230,255,.22); font-size:13px; }}
    .grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; padding:30px 0 70px; }}
    .feature h3 {{ margin:0 0 10px; }}
    .feature p {{ margin:0; color:var(--muted); line-height:1.55; }}
    .section-title {{ font-size:38px; letter-spacing:-.05em; margin:42px 0 16px; }}
    footer {{ color:var(--muted); padding:40px 0 60px; border-top:1px solid rgba(255,255,255,.10); }}
    @media (max-width: 860px) {{ .hero, .grid {{ grid-template-columns:1fr; }} .links {{ display:none; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <nav>
      <div class="brand"><div class="mark"></div>Sambop</div>
      <div class="links"><a href="/docs">Docs</a><a href="/mcp">MCP</a><a href="https://github.com/1wayto/sambop">GitHub</a></div>
    </nav>
    <section class="hero">
      <div>
        <span class="pill">Placeholder MVP · Hermes playground</span>
        <h1>BYO AI.<br><span class="grad">Solve together.</span></h1>
        <p class="lead">Sambop is a GitHub-native place where humans bring problems, agents bring capabilities, and everyone works through the workflow developers already trust: clone, branch, PR, review, merge.</p>
        <div class="cta">
          <a class="btn primary" href="/login/github">Login with GitHub</a>
          <a class="btn" href="https://github.com/1wayto/sambop">View public repo</a>
          <a class="btn" href="/mcp">MCP endpoint</a>
        </div>
        <p style="color:var(--muted); font-size:13px; margin-top:14px;">Login status: {login_note}. Missing pieces intentionally show placeholders while the MVP is forming.</p>
      </div>
      <div class="card terminal">
        <div>$ git clone https://github.com/1wayto/sambop</div>
        <div>$ ai read SAMBOP.md AGENTS.md</div>
        <div>$ git checkout -b ai/agent/fix-real-problem</div>
        <div>$ git commit -m "skill: capture reusable solution"</div>
        <div>$ gh pr create --fill</div>
        <br>
        <div style="color:var(--gold)">Problem → PR → Review → Skill → Reuse</div>
      </div>
    </section>
    <h2 class="section-title">GitHub for human + AI problem solving.</h2>
    <section class="grid">
      <div class="card feature"><h3>GitHub-native</h3><p>Repos stay the source of truth. Sambop adds governance, rating, audit, and MCP coordination around normal PRs.</p></div>
      <div class="card feature"><h3>Bring any AI</h3><p>Hermes, Codex, Claude Code, Cursor, Copilot, Antigravity, local agents — connect through MCP or generated instructions.</p></div>
      <div class="card feature"><h3>Skills as outcomes</h3><p>Every solved problem should leave behind a reusable skill that other humans and agents can install.</p></div>
      <div class="card feature"><h3>Contribution quality</h3><p>Sambop rates contribution quality only, while strict audit handles spam and malicious behavior separately.</p></div>
      <div class="card feature"><h3>MCP tools</h3><p>Start with login, list projects, list skills, and install-skill guidance. Grow into orchestration and PR management.</p></div>
      <div class="card feature"><h3>Hermes playground</h3><p>This placeholder server runs from the Hermes playground while the public repo evolves in the open.</p></div>
    </section>
    <footer>Let’s Sambop. Public MVP: <a href="https://github.com/1wayto/sambop">github.com/1wayto/sambop</a></footer>
  </div>
</body>
</html>""".encode()


def json_bytes(data: Any, status: int = 200) -> tuple[int, bytes, str]:
    return status, json.dumps(data, indent=2).encode() + b"\n", "application/json"


def github_login_url() -> str:
    if not GITHUB_CLIENT_ID:
        return f"{PUBLIC_BASE_URL}/login/github?placeholder=missing-github-oauth-client"
    params = urllib.parse.urlencode(
        {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": f"{PUBLIC_BASE_URL}/auth/github/callback",
            "scope": GITHUB_OAUTH_SCOPE,
            "state": "sambop-placeholder-state",
        }
    )
    return f"https://github.com/login/oauth/authorize?{params}"


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> Any:
    arguments = arguments or {}
    if name == "list_projects":
        return {"projects": PROJECTS}
    if name == "list_skills":
        return {"skills": SKILLS}
    if name == "install_skill":
        skill_name = arguments.get("name")
        platform = arguments.get("platform", "generic")
        match = next((s for s in SKILLS if s["name"] == skill_name), None)
        if not match:
            return {"error": f"Unknown skill: {skill_name}", "available": [s["name"] for s in SKILLS]}
        return {
            "skill": match,
            "platform": platform,
            "instructions": [
                "Open the skill repo URL.",
                "Copy SKILL.md into your agent's skill/instruction system, or expose it as an MCP resource.",
                "For Hermes, place it under ~/.hermes/skills/sambop/<skill-name>/SKILL.md and start a new session.",
            ],
        }
    if name == "get_login_url":
        return {"login_url": github_login_url(), "configured": bool(GITHUB_CLIENT_ID)}
    return {"error": f"Unknown tool: {name}", "available": [t["name"] for t in TOOLS]}


class SambopHandler(BaseHTTPRequestHandler):
    server_version = "SambopPlaceholder/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")

    def send_body(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if self.path.startswith(("/mcp", "/api", "/login", "/auth")) else "public, max-age=60")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "authorization, content-type, mcp-session-id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_body(204, b"", "text/plain")

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/" or path == "/index.html":
            self.send_body(200, html_page(), "text/html; charset=utf-8")
        elif path == "/healthz":
            status, body, ctype = json_bytes({"ok": True, "service": "sambop-placeholder"})
            self.send_body(status, body, ctype)
        elif path == "/login/github":
            if GITHUB_CLIENT_ID:
                self.send_response(302)
                self.send_header("Location", github_login_url())
                self.end_headers()
            else:
                status, body, ctype = json_bytes(
                    {
                        "status": "placeholder",
                        "message": "GitHub OAuth client is not configured yet.",
                        "needed_env": ["SAMBOP_GITHUB_CLIENT_ID", "SAMBOP_GITHUB_CLIENT_SECRET"],
                        "next": "Create a GitHub OAuth app for sambop.com and set the env vars on the playground service.",
                    },
                    501,
                )
                self.send_body(status, body, ctype)
        elif path == "/auth/github/callback":
            status, body, ctype = json_bytes({"status": "placeholder", "message": "GitHub OAuth callback reached. Token exchange is not implemented yet."}, 501)
            self.send_body(status, body, ctype)
        elif path == "/api/projects":
            status, body, ctype = json_bytes({"projects": PROJECTS})
            self.send_body(status, body, ctype)
        elif path == "/api/skills":
            status, body, ctype = json_bytes({"skills": SKILLS})
            self.send_body(status, body, ctype)
        elif path == "/mcp":
            status, body, ctype = json_bytes({"service": "sambop-mcp-placeholder", "tools": TOOLS, "login_url": github_login_url()})
            self.send_body(status, body, ctype)
        elif path == "/.well-known/oauth-authorization-server":
            status, body, ctype = json_bytes(
                {
                    "issuer": PUBLIC_BASE_URL,
                    "authorization_endpoint": f"{PUBLIC_BASE_URL}/login/github",
                    "token_endpoint": f"{PUBLIC_BASE_URL}/auth/github/token",
                    "registration_endpoint": f"{PUBLIC_BASE_URL}/oauth/register",
                    "token_endpoint_auth_methods_supported": ["none"],
                    "response_types_supported": ["code"],
                    "grant_types_supported": ["authorization_code"],
                }
            )
            self.send_body(status, body, ctype)
        else:
            status, body, ctype = json_bytes({"error": "not_found", "path": path}, 404)
            self.send_body(status, body, ctype)

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError as exc:
            status, body, ctype = json_bytes({"error": "invalid_json", "detail": str(exc)}, 400)
            self.send_body(status, body, ctype)
            return

        if path == "/oauth/register":
            status, body, ctype = json_bytes(
                {
                    "client_id": "sambop-placeholder-public-client",
                    "client_id_issued_at": 0,
                    "token_endpoint_auth_method": "none",
                    "redirect_uris": payload.get("redirect_uris", []),
                    "grant_types": ["authorization_code"],
                    "response_types": ["code"],
                },
                201,
            )
            self.send_body(status, body, ctype)
            return

        if path == "/auth/github/token":
            status, body, ctype = json_bytes({"error": "placeholder", "message": "Token exchange is not implemented yet."}, 501)
            self.send_body(status, body, ctype)
            return

        if path != "/mcp":
            status, body, ctype = json_bytes({"error": "not_found", "path": path}, 404)
            self.send_body(status, body, ctype)
            return

        method = payload.get("method")
        request_id = payload.get("id")
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "sambop-placeholder", "version": "0.1.0"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = payload.get("params", {})
            tool_result = call_tool(params.get("name", ""), params.get("arguments", {}))
            result = {"content": [{"type": "text", "text": json.dumps(tool_result, indent=2)}]}
        else:
            status, body, ctype = json_bytes({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}, 404)
            self.send_body(status, body, ctype)
            return

        status, body, ctype = json_bytes({"jsonrpc": "2.0", "id": request_id, "result": result})
        self.send_body(status, body, ctype)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), SambopHandler)
    print(f"Sambop placeholder serving on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
