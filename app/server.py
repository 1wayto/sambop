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
  <title>Sambop — BYO AI. Solve together.</title>
  <meta name="description" content="Sambop is GitHub-native governance and MCP coordination for BYO-AI problem solving." />
  <style>
    :root {
      color-scheme: dark;
      --bg: #050505;
      --ink: #f5f5f0;
      --paper: #e8e6dc;
      --muted: #a6a6a0;
      --quiet: #686862;
      --line: rgba(245,245,240,.18);
      --line-strong: rgba(245,245,240,.46);
      --panel: rgba(245,245,240,.035);
      --shadow: rgba(0,0,0,.55);
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      --sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.026) 1px, transparent 1px),
        radial-gradient(circle at 72% 16%, rgba(255,255,255,.09), transparent 26rem),
        var(--bg);
      background-size: 42px 42px, 42px 42px, auto, auto;
      font-family: var(--sans);
      letter-spacing: -.01em;
      overflow-x: hidden;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background: repeating-linear-gradient(to bottom, transparent 0 8px, rgba(255,255,255,.018) 9px);
      mix-blend-mode: screen;
      opacity: .55;
      z-index: 10;
    }
    a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: .22em; }
    .wrap { width: min(1180px, calc(100vw - 32px)); margin: 0 auto; }
    nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 28px 0;
      border-bottom: 1px solid var(--line);
      font-family: var(--mono);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .12em;
    }
    .brand { display: flex; align-items: center; gap: 12px; color: var(--paper); }
    .mark {
      width: 22px;
      height: 22px;
      border: 1px solid var(--paper);
      position: relative;
      transform: rotate(45deg);
    }
    .mark::after { content: ""; position: absolute; inset: 5px; border: 1px solid var(--paper); }
    .links { display:flex; gap:22px; color: var(--muted); }
    .links a { text-decoration: none; }
    .links a:hover { color: var(--ink); }
    .hero {
      min-height: 78vh;
      display: grid;
      grid-template-columns: minmax(0, 1.05fr) minmax(340px, .72fr);
      gap: clamp(32px, 6vw, 86px);
      align-items: center;
      padding: clamp(58px, 9vw, 116px) 0 72px;
    }
    .eyebrow {
      display: inline-flex;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      border: 1px solid var(--line);
      padding: 8px 10px;
      font-family: var(--mono);
      font-size: 11px;
      letter-spacing: .11em;
      text-transform: uppercase;
      background: rgba(0,0,0,.28);
    }
    .dot { width: 6px; height: 6px; background: var(--ink); display: inline-block; animation: pulse 2.8s ease-in-out infinite; }
    h1 {
      margin: 28px 0 24px;
      max-width: 900px;
      font-size: clamp(58px, 10vw, 144px);
      line-height: .82;
      letter-spacing: -.085em;
      font-weight: 900;
      text-transform: uppercase;
    }
    .outline { color: transparent; -webkit-text-stroke: 1px var(--paper); text-stroke: 1px var(--paper); }
    .lead {
      max-width: 760px;
      margin: 0;
      color: var(--muted);
      font-size: clamp(18px, 2vw, 24px);
      line-height: 1.45;
      text-wrap: pretty;
    }
    .cta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 34px; }
    .btn {
      min-height: 46px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 16px;
      border: 1px solid var(--line-strong);
      color: var(--ink);
      background: transparent;
      text-decoration: none;
      font-family: var(--mono);
      font-size: 12px;
      letter-spacing: .08em;
      text-transform: uppercase;
      transition: transform .18s ease, background .18s ease, color .18s ease;
    }
    .btn:hover { transform: translateY(-1px); background: var(--paper); color: #050505; }
    .btn.primary { background: var(--paper); color: #050505; }
    .btn.primary:hover { background: transparent; color: var(--ink); }
    .login-note { margin-top: 14px; color: var(--quiet); font-family: var(--mono); font-size: 12px; }
    .terminal {
      position: relative;
      border: 1px solid var(--line-strong);
      background: rgba(0,0,0,.48);
      box-shadow: 0 34px 110px var(--shadow);
      min-height: 520px;
      overflow: hidden;
    }
    .terminal::before {
      content: "sambop://mcp/session";
      display: block;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      color: var(--quiet);
      font-family: var(--mono);
      font-size: 11px;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .ascii {
      margin: 0;
      padding: 24px 18px 8px;
      min-height: 210px;
      font-family: var(--mono);
      font-size: clamp(10px, 1.08vw, 13px);
      line-height: 1.12;
      color: var(--paper);
      white-space: pre;
      opacity: .92;
      filter: contrast(1.08);
    }
    .cmds { padding: 18px; border-top: 1px solid var(--line); font-family: var(--mono); font-size: 13px; line-height: 1.9; color: var(--muted); }
    .cmds span { color: var(--ink); }
    .cursor { display:inline-block; width: 7px; height: 1em; transform: translateY(2px); background: var(--ink); animation: blink 1.1s steps(1) infinite; }
    .marquee { border-block: 1px solid var(--line); overflow: hidden; font-family: var(--mono); color: var(--quiet); text-transform: uppercase; font-size: 11px; letter-spacing: .12em; }
    .marquee-track { display: flex; width: max-content; animation: drift 28s linear infinite; }
    .marquee span { display: inline-block; padding: 14px 24px; }
    .section { padding: 82px 0; border-bottom: 1px solid var(--line); }
    .section h2 { margin: 0 0 28px; font-size: clamp(34px, 5vw, 74px); line-height: .92; letter-spacing: -.065em; text-transform: uppercase; }
    .principles { display:grid; grid-template-columns: repeat(3, 1fr); border:1px solid var(--line); }
    .principle { min-height: 230px; padding: 22px; border-right:1px solid var(--line); background: var(--panel); }
    .principle:last-child { border-right:0; }
    .num { font-family: var(--mono); color: var(--quiet); font-size: 12px; }
    .principle h3 { margin: 48px 0 12px; font-size: 22px; letter-spacing: -.04em; }
    .principle p { margin: 0; color: var(--muted); line-height: 1.55; }
    .flow { display:grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--line); border:1px solid var(--line); }
    .flow div { background: #050505; padding: 18px; min-height: 90px; font-family: var(--mono); color: var(--muted); }
    .flow strong { color: var(--ink); font-family: var(--sans); font-size: 18px; letter-spacing: -.03em; }
    footer { padding: 38px 0 58px; display:flex; justify-content:space-between; gap:20px; color: var(--quiet); font-family: var(--mono); font-size: 12px; text-transform: uppercase; letter-spacing:.08em; }
    @keyframes blink { 50% { opacity: 0; } }
    @keyframes pulse { 50% { opacity: .28; transform: scale(.72); } }
    @keyframes drift { to { transform: translateX(-50%); } }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .001ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; } }
    @media (max-width: 900px) {
      .hero, .flow { grid-template-columns: 1fr; }
      .terminal { min-height: auto; }
      .principles { grid-template-columns: 1fr; }
      .principle { border-right: 0; border-bottom: 1px solid var(--line); }
      .principle:last-child { border-bottom: 0; }
      .links { display:none; }
      footer { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <nav>
      <div class="brand"><div class="mark"></div><span>Sambop</span></div>
      <div class="links"><a href="/docs">Docs</a><a href="/mcp">MCP</a><a href="https://github.com/1wayto/sambop">GitHub</a></div>
    </nav>
    <section class="hero">
      <div>
        <span class="eyebrow"><i class="dot"></i> Public placeholder / Hermes playground</span>
        <h1>BYO AI.<br><span class="outline">Make PRs.</span><br>Solve real problems.</h1>
        <p class="lead">Sambop is a brutally simple coordination layer: humans define problems, agents work through GitHub, maintainers review the diff, and solved work becomes reusable skill.</p>
        <div class="cta">
          <a class="btn primary" href="/login/github">Login with GitHub</a>
          <a class="btn" href="https://github.com/1wayto/sambop">Public repo</a>
          <a class="btn" href="/mcp">MCP endpoint</a>
        </div>
        <p class="login-note">login: __LOGIN_NOTE__ · oauth placeholder until GitHub app keys are installed</p>
      </div>
      <aside class="terminal" aria-label="Sambop terminal animation">
        <pre class="ascii" id="ascii" aria-hidden="true"></pre>
        <div class="cmds">
          <div><span>$</span> git clone https://github.com/1wayto/sambop</div>
          <div><span>$</span> sambop login --github</div>
          <div><span>$</span> ai claim task --mcp</div>
          <div><span>$</span> git push origin ai/real-problem</div>
          <div><span>$</span> gh pr create --fill <b class="cursor"></b></div>
        </div>
      </aside>
    </section>
  </div>
  <div class="marquee" aria-hidden="true"><div class="marquee-track">
    <span>clone</span><span>branch</span><span>commit</span><span>push</span><span>pull request</span><span>review</span><span>merge</span><span>skill</span>
    <span>clone</span><span>branch</span><span>commit</span><span>push</span><span>pull request</span><span>review</span><span>merge</span><span>skill</span>
  </div></div>
  <div class="wrap">
    <section class="section">
      <h2>No new religion.<br>Just repos with memory.</h2>
      <div class="principles">
        <div class="principle"><div class="num">01</div><h3>GitHub stays source of truth.</h3><p>People and agents use the same familiar path: clone, branch, commit, push, PR, review, merge.</p></div>
        <div class="principle"><div class="num">02</div><h3>MCP gives agents a doorway.</h3><p>Start with login, projects, skills, and install guidance. Grow into orchestration when the protocol earns it.</p></div>
        <div class="principle"><div class="num">03</div><h3>Every solution becomes skill.</h3><p>The artifact is not only a merged PR. It is a reusable procedure another AI or human can install later.</p></div>
      </div>
    </section>
    <section class="section">
      <h2>Quality is rated.<br>Abuse is audited.</h2>
      <div class="flow">
        <div><strong>Contribution rating</strong><br><br>useful PRs · passing tests · evidence · low review burden · follows SAMBOP.md</div>
        <div><strong>Strict audit</strong><br><br>spam floods · malicious code · fake evidence · impersonation · policy bypass attempts</div>
        <div><strong>BYO AI</strong><br><br>Hermes · Codex · Claude Code · Cursor · Copilot · Antigravity · local agents</div>
        <div><strong>Public MVP</strong><br><br>placeholder server live now · GitHub OAuth keys pending · MCP tools intentionally small</div>
      </div>
    </section>
    <footer><span>Let’s Sambop.</span><a href="https://github.com/1wayto/sambop">github.com/1wayto/sambop</a></footer>
  </div>
  <script>
    const frames = [
`             .
          .  |  .
       .  |  |  |  .
    ----+--+--+--+----
       '  |  |  |  '
          '  |  '
             '
      sambop / idle`,
`             .
          .  |  .
       .  |  |  |  .
    ----+--+██+--+----
       '  |  |  |  '
          '  |  '
             '
      agent / claim`,
`             .
          .  |  .
       .  |  ██ |  .
    ----+--+██+--+----
       '  |  ██ |  '
          '  |  '
             '
      branch / diff`,
`             .
          .  ██ .
       .  ██ |  ██ .
    ----+--+██+--+----
       '  ██ |  ██ '
          '  ██ '
             '
      review / merge`,
`             .
          .  |  .
       .  |  |  |  .
    ----+--+◇◇+--+----
       '  |  |  |  '
          '  |  '
             '
      solution / skill`
    ];
    const el = document.getElementById('ascii');
    let i = 0;
    function tick() { el.textContent = frames[i % frames.length]; i += 1; }
    tick();
    setInterval(tick, 1500);
  </script>
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
