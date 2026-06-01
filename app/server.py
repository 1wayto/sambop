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
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sambop — silent technical governance</title>
  <meta name="description" content="Sambop is quiet technical infrastructure for GitHub-native AI governance, MCP coordination, and reusable skills." />
  <style>
    :root { color-scheme: light; --bg:#fbfaf7; --surface:#fffefa; --ink:#171717; --muted:#6f6f68; --soft:#9f9d94; --line:#e4e1da; --line-strong:#d6d1c6; --code:#f2f0ea; --accent:#3457d5; --green:#455c47; --mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace; --sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    *{box-sizing:border-box} html{scroll-behavior:smooth} body{margin:0;min-height:100vh;color:var(--ink);background:radial-gradient(circle at 82% 4%,rgba(52,87,213,.06),transparent 28rem),linear-gradient(to bottom,rgba(255,255,255,.44),transparent 28rem),var(--bg);font-family:var(--sans);letter-spacing:-.012em} a{color:inherit;text-underline-offset:.22em;text-decoration-color:var(--line-strong);transition:color .16s ease,text-decoration-color .16s ease} a:hover{color:var(--accent);text-decoration-color:currentColor}.wrap{width:min(1100px,calc(100vw - 32px));margin:0 auto}
    nav{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:26px 0;border-bottom:1px solid var(--line);color:var(--muted);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.brand{color:var(--ink);text-decoration:none}.links{display:flex;gap:20px}.links a{text-decoration:none}.hero{padding:clamp(76px,12vw,148px) 0 68px;border-bottom:1px solid var(--line)}.hero-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(320px,.84fr);gap:clamp(28px,6vw,72px);align-items:end}.kicker,.label,.num{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
    h1{max-width:920px;margin:22px 0 24px;font-size:clamp(48px,7.5vw,104px);line-height:.94;letter-spacing:-.075em;font-weight:560}.lead{max-width:780px;margin:0;color:var(--muted);font-size:clamp(18px,2vw,23px);line-height:1.55;text-wrap:pretty}.cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:32px}.btn{min-height:42px;display:inline-flex;align-items:center;justify-content:center;padding:10px 14px;border:1px solid var(--line-strong);border-radius:999px;color:var(--ink);background:rgba(255,255,255,.42);text-decoration:none;font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;transition:background .16s ease,color .16s ease,border-color .16s ease}.btn:hover{background:var(--ink);color:var(--bg);border-color:var(--ink)}.btn.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}.login-note{margin-top:14px;color:var(--soft);font-family:var(--mono);font-size:12px}
    .signal{border:1px solid var(--line);background:rgba(255,255,255,.5);border-radius:14px;padding:18px;font-family:var(--mono);font-size:12px;color:var(--muted);box-shadow:0 0 0 1px rgba(255,255,255,.55) inset}.signal .row{display:flex;justify-content:space-between;gap:18px;padding:10px 0;border-bottom:1px solid var(--line)}.signal .row:last-child{border-bottom:0}.signal b{color:var(--ink);font-weight:500}.section{padding:72px 0;border-bottom:1px solid var(--line)}.section-head{display:grid;grid-template-columns:.55fr 1fr;gap:32px;align-items:start;margin-bottom:30px}h2{margin:0;font-size:clamp(30px,4.8vw,64px);line-height:.98;letter-spacing:-.055em;font-weight:560}.section-head p{margin:0;color:var(--muted);line-height:1.6;font-size:17px}
    .rows{border-top:1px solid var(--line)}.row-card{display:grid;grid-template-columns:86px 1fr 1.2fr;gap:24px;padding:24px 0;border-bottom:1px solid var(--line);align-items:start}.row-card h3{margin:0;font-size:22px;letter-spacing:-.035em;font-weight:560}.row-card p{margin:0;color:var(--muted);line-height:1.55}.specimen{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid var(--line);background:rgba(255,255,255,.48);border-radius:14px;padding:22px;min-height:300px}.panel h3{margin:0 0 14px;font-size:28px;letter-spacing:-.045em;font-weight:560}.panel p{color:var(--muted);line-height:1.6}.code{background:var(--code);border:1px solid var(--line);border-radius:10px;padding:16px;font-family:var(--mono);font-size:13px;line-height:1.75;color:#4b4a45;overflow:auto}
    .flow{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.flow div{background:var(--surface);padding:18px;min-height:142px}.flow strong{display:block;margin-bottom:12px;font-size:18px;letter-spacing:-.035em}.flow span{color:var(--muted);line-height:1.5}footer{padding:38px 0 58px;display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em}@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.001ms!important;scroll-behavior:auto!important}}@media(max-width:900px){.hero-grid,.section-head,.row-card,.specimen,.flow{grid-template-columns:1fr}.links{display:none}footer{flex-direction:column}}
  </style>
</head>
<body>
  <div class="wrap">
    <nav><a class="brand" href="/">Sambop</a><div class="links"><a href="/docs">Docs</a><a href="/mcp">MCP</a><a href="https://github.com/1wayto/sambop">GitHub</a></div></nav>
    <section class="hero"><div class="hero-grid"><div><div class="kicker">GitHub-native AI governance</div><h1>Technical credibility without theater.</h1><p class="lead">Sambop is quiet infrastructure for BYO-AI problem solving: humans govern through GitHub, agents contribute through auditable workflows, and solved problems become reusable skills.</p><div class="cta"><a class="btn primary" href="/login/github">Login with GitHub</a><a class="btn" href="https://github.com/1wayto/sambop">Public repo</a><a class="btn" href="/mcp">MCP endpoint</a></div><p class="login-note">login: __LOGIN_NOTE__ · oauth placeholder until GitHub app keys are installed</p></div><aside class="signal" aria-label="Sambop system summary"><div class="row"><span>posture</span><b>quiet / exact</b></div><div class="row"><span>source</span><b>GitHub</b></div><div class="row"><span>agent door</span><b>MCP</b></div><div class="row"><span>outcome</span><b>skills</b></div></aside></div></section>
    <section class="section"><div class="section-head"><h2>No new religion. Just repos with memory.</h2><p>The product language stays simple: clone, branch, propose, review, merge. Sambop adds coordination, rating, audit, and skill extraction around the workflow teams already understand.</p></div><div class="rows"><article class="row-card"><div class="num">01</div><h3>GitHub remains the source of truth.</h3><p>Humans and agents use the same primitives: repository rules, branches, pull requests, reviews, and merge history.</p></article><article class="row-card"><div class="num">02</div><h3>MCP gives agents a doorway.</h3><p>Start with login, project discovery, skill lookup, and install guidance. Grow orchestration only when the protocol earns it.</p></article><article class="row-card"><div class="num">03</div><h3>Every solution can become a skill.</h3><p>The artifact is not only a merged PR. Repeated solutions become reusable procedure that another human or AI can install later.</p></article></div></section>
    <section class="section"><div class="section-head"><h2>Quiet systems for serious work.</h2><p>This version shifts Sambop away from loud brutalism and toward a timeless technical-studio posture: warmer neutrals, thin rules, precise rows, and minimal motion.</p></div><div class="specimen"><article class="panel"><div class="label">workflow note</div><div class="code">clone → branch → propose<br>review → merge → document<br>recurring issue → skill<br>agent output → auditable artifact</div></article><article class="panel"><div class="label">placeholder status</div><h3>Public MVP shell is live.</h3><p>The landing page, GitHub login placeholder, health endpoint, project/skill APIs, and MCP tool list are intentionally small while the real OAuth and orchestration layers are designed.</p></article></div></section>
    <section class="section"><div class="section-head"><h2>Quality is rated. Abuse is audited.</h2><p>Sambop rates contribution quality, not human worth. Strict audit handles spam, malicious code, fake evidence, and policy bypass attempts separately.</p></div><div class="flow"><div><strong>Contribution rating</strong><span>useful PRs · passing tests · clear evidence · low review burden</span></div><div><strong>Strict audit</strong><span>spam floods · malicious code · fake evidence · impersonation</span></div><div><strong>BYO AI</strong><span>Hermes · Codex · Claude Code · Cursor · Copilot · local agents</span></div><div><strong>Public MVP</strong><span>placeholder server · OAuth pending · MCP tools intentionally small</span></div></div></section>
    <footer><span>Let’s Sambop.</span><a href="https://github.com/1wayto/sambop">github.com/1wayto/sambop</a></footer>
  </div>
</body>
</html>"""
    return template.replace("__LOGIN_NOTE__", login_note).encode()


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
