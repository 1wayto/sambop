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
  <title>Sambop — GitHub-native AI governance</title>
  <meta name="description" content="Sambop is quiet technical infrastructure for GitHub-native AI governance, MCP coordination, contribution quality, audit, and reusable skills." />
  <meta property="og:title" content="Sambop — GitHub-native AI governance" />
  <meta property="og:description" content="Quiet infrastructure for BYO-AI problem solving: GitHub workflows, MCP coordination, auditable contributions, and reusable skills." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://sambop.com" />
  <meta name="theme-color" content="#fbfaf7" />
  <style>
    :root{color-scheme:light;--bg:#fbfaf7;--surface:#fffefa;--ink:#171717;--muted:#6f6f68;--soft:#9f9d94;--line:#e4e1da;--line-strong:#d6d1c6;--code:#f2f0ea;--accent:#3457d5;--accent-soft:rgba(52,87,213,.12);--green:#455c47;--warm:#c4a36d;--mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace;--sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;color:var(--ink);background:radial-gradient(circle at 82% 4%,rgba(52,87,213,.06),transparent 28rem),linear-gradient(to bottom,rgba(255,255,255,.44),transparent 28rem),var(--bg);font-family:var(--sans);letter-spacing:-.012em}a{color:inherit;text-underline-offset:.22em;text-decoration-color:var(--line-strong);transition:color .16s ease,text-decoration-color .16s ease}a:hover{color:var(--accent);text-decoration-color:currentColor}.wrap{width:min(1160px,calc(100vw - 32px));margin:0 auto}
    nav{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:26px 0;border-bottom:1px solid var(--line);color:var(--muted);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.brand{color:var(--ink);text-decoration:none}.links{display:flex;gap:20px}.links a{text-decoration:none}.hero{padding:clamp(58px,9vw,116px) 0 68px;border-bottom:1px solid var(--line)}.hero-grid{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(360px,.98fr);gap:clamp(30px,6vw,76px);align-items:center}.kicker,.label,.num,.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
    h1{max-width:920px;margin:22px 0 24px;font-size:clamp(48px,7vw,96px);line-height:.94;letter-spacing:-.075em;font-weight:560}.lead{max-width:780px;margin:0;color:var(--muted);font-size:clamp(18px,2vw,23px);line-height:1.55;text-wrap:pretty}.cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:32px}.btn{min-height:42px;display:inline-flex;align-items:center;justify-content:center;padding:10px 14px;border:1px solid var(--line-strong);border-radius:999px;color:var(--ink);background:rgba(255,255,255,.42);text-decoration:none;font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;transition:background .16s ease,color .16s ease,border-color .16s ease,transform .16s ease}.btn:hover{background:var(--ink);color:var(--bg);border-color:var(--ink);transform:translateY(-1px)}.btn.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}.login-note{margin-top:14px;color:var(--soft);font-family:var(--mono);font-size:12px;line-height:1.5}
    .hero-visual{position:relative;min-height:520px;border:1px solid var(--line);border-radius:24px;overflow:hidden;background:linear-gradient(145deg,rgba(255,255,255,.72),rgba(242,240,234,.52));box-shadow:0 24px 70px rgba(23,23,23,.08),0 0 0 1px rgba(255,255,255,.7) inset}.hero-visual:before{content:"";position:absolute;inset:18px;border:1px solid rgba(214,209,198,.72);border-radius:18px;pointer-events:none}.hero-visual canvas{position:absolute;inset:0;width:100%;height:100%;display:block}.visual-copy{position:absolute;left:24px;right:24px;bottom:22px;display:grid;grid-template-columns:1fr auto;gap:18px;align-items:end;z-index:2}.visual-card{border:1px solid rgba(214,209,198,.9);background:rgba(255,254,250,.74);backdrop-filter:blur(14px);border-radius:14px;padding:16px;font-family:var(--mono);font-size:12px;color:var(--muted);box-shadow:0 10px 30px rgba(23,23,23,.06)}.visual-card strong{display:block;color:var(--ink);font-size:14px;font-weight:500;margin-bottom:8px}.visual-status{width:132px}.visual-status .dot{display:inline-block;width:8px;height:8px;border-radius:999px;background:var(--green);margin-right:8px;box-shadow:0 0 0 6px rgba(69,92,71,.1)}.three-fallback{position:absolute;inset:0;display:grid;place-items:center;color:var(--soft);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.12em}.section{padding:72px 0;border-bottom:1px solid var(--line)}.section-head{display:grid;grid-template-columns:.55fr 1fr;gap:32px;align-items:start;margin-bottom:30px}h2{margin:0;font-size:clamp(30px,4.8vw,64px);line-height:.98;letter-spacing:-.055em;font-weight:560}.section-head p{margin:0;color:var(--muted);line-height:1.6;font-size:17px}
    .rows{border-top:1px solid var(--line)}.row-card{display:grid;grid-template-columns:86px 1fr 1.2fr;gap:24px;padding:24px 0;border-bottom:1px solid var(--line);align-items:start}.row-card h3{margin:0;font-size:22px;letter-spacing:-.035em;font-weight:560}.row-card p{margin:0;color:var(--muted);line-height:1.55}.specimen{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid var(--line);background:rgba(255,255,255,.48);border-radius:14px;padding:22px;min-height:300px}.panel h3{margin:0 0 14px;font-size:28px;letter-spacing:-.045em;font-weight:560}.panel p{color:var(--muted);line-height:1.6}.code{background:var(--code);border:1px solid var(--line);border-radius:10px;padding:16px;font-family:var(--mono);font-size:13px;line-height:1.75;color:#4b4a45;overflow:auto}.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:18px}.metric-grid div{background:var(--surface);padding:16px}.metric-grid b{display:block;font-size:28px;letter-spacing:-.05em}.metric-grid span{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
    .flow{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.flow div{background:var(--surface);padding:18px;min-height:142px}.flow strong{display:block;margin-bottom:12px;font-size:18px;letter-spacing:-.035em}.flow span{color:var(--muted);line-height:1.5}.docs-callout{display:flex;align-items:center;justify-content:space-between;gap:18px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.48);padding:22px}.docs-callout p{margin:6px 0 0;color:var(--muted);line-height:1.5}footer{padding:38px 0 58px;display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em}@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.001ms!important;scroll-behavior:auto!important}.hero-visual canvas{display:none}.three-fallback{display:grid}}@media(max-width:980px){.hero-grid,.section-head,.row-card,.specimen,.flow,.metric-grid{grid-template-columns:1fr}.hero-visual{min-height:440px}.links{display:none}.visual-copy{grid-template-columns:1fr}.visual-status{width:auto}footer,.docs-callout{flex-direction:column;align-items:flex-start}}@media(max-width:560px){.hero-visual{min-height:380px;border-radius:18px}.visual-copy{left:14px;right:14px;bottom:14px}.hero{padding-top:44px}}
  </style>
</head>
<body>
  <div class="wrap">
    <nav><a class="brand" href="/">Sambop</a><div class="links"><a href="/docs">Docs</a><a href="/mcp">MCP</a><a href="https://github.com/1wayto/sambop">GitHub</a></div></nav>
    <section class="hero"><div class="hero-grid"><div><div class="kicker">GitHub-native AI governance</div><h1>Technical credibility without theater.</h1><p class="lead">Sambop is quiet infrastructure for BYO-AI problem solving: humans govern through GitHub, agents contribute through auditable workflows, and solved problems become reusable skills.</p><div class="cta"><a class="btn primary" href="/login/github">Login with GitHub</a><a class="btn" href="https://github.com/1wayto/sambop">Public repo</a><a class="btn" href="/docs">Read docs</a><a class="btn" href="/mcp">MCP endpoint</a></div><p class="login-note">login: __LOGIN_NOTE__ · oauth placeholder until GitHub app keys are installed</p></div><aside class="hero-visual" aria-label="Three.js governance network animation"><div class="three-fallback">governance graph</div><canvas id="sambop-graph" data-three="hero"></canvas><div class="visual-copy"><div class="visual-card"><strong>Repo memory, not platform theater.</strong><span>Branches, reviews, ratings, audit trails, and skills orbit the same GitHub source of truth.</span></div><div class="visual-card visual-status"><span class="dot"></span>live shell<br>mcp ready</div></div></aside></div></section>
    <section class="section"><div class="section-head"><h2>No new religion. Just repos with memory.</h2><p>The product language stays simple: clone, branch, propose, review, merge. Sambop adds coordination, rating, audit, and skill extraction around the workflow teams already understand.</p></div><div class="rows"><article class="row-card"><div class="num">01</div><h3>GitHub remains the source of truth.</h3><p>Humans and agents use the same primitives: repository rules, branches, pull requests, reviews, and merge history.</p></article><article class="row-card"><div class="num">02</div><h3>MCP gives agents a doorway.</h3><p>Start with login, project discovery, skill lookup, and install guidance. Grow orchestration only when the protocol earns it.</p></article><article class="row-card"><div class="num">03</div><h3>Every solution can become a skill.</h3><p>The artifact is not only a merged PR. Repeated solutions become reusable procedure that another human or AI can install later.</p></article></div></section>
    <section class="section"><div class="section-head"><h2>Quiet systems for serious work.</h2><p>This version gives Sambop a timeless technical-studio posture: warmer neutrals, thin rules, precise rows, restrained motion, and a Three.js governance graph built for the hero rather than decoration.</p></div><div class="specimen"><article class="panel"><div class="label">workflow note</div><div class="code">clone → branch → propose<br>review → merge → document<br>recurring issue → skill<br>agent output → auditable artifact</div><div class="metric-grid"><div><b>4</b><span>MCP tools</span></div><div><b>1</b><span>public loop</span></div><div><b>0</b><span>hidden magic</span></div></div></article><article class="panel"><div class="label">placeholder status</div><h3>Public MVP shell is live.</h3><p>The landing page, GitHub login placeholder, health endpoint, project/skill APIs, docs route, and MCP tool list are intentionally small while the real OAuth and orchestration layers are designed.</p></article></div></section>
    <section class="section"><div class="section-head"><h2>Quality is rated. Abuse is audited.</h2><p>Sambop rates contribution quality, not human worth. Strict audit handles spam, malicious code, fake evidence, and policy bypass attempts separately.</p></div><div class="flow"><div><strong>Contribution rating</strong><span>useful PRs · passing tests · clear evidence · low review burden</span></div><div><strong>Strict audit</strong><span>spam floods · malicious code · fake evidence · impersonation</span></div><div><strong>BYO AI</strong><span>Hermes · Codex · Claude Code · Cursor · Copilot · local agents</span></div><div><strong>Public MVP</strong><span>placeholder server · OAuth pending · MCP tools intentionally small</span></div></div></section>
    <section class="section"><div class="docs-callout"><div><div class="eyebrow">missing piece filled</div><p>The top navigation now has a real docs route instead of a dead link. It summarizes the install guides, MCP surface, rating model, and MVP loop.</p></div><a class="btn" href="/docs">Open docs</a></div></section>
    <footer><span>Let’s Sambop.</span><a href="https://github.com/1wayto/sambop">github.com/1wayto/sambop</a></footer>
  </div>
  <script type="module">
    const canvas = document.querySelector('#sambop-graph');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (canvas && !reduced) {
      import('https://unpkg.com/three@0.160.0/build/three.module.js').then((THREE) => {
        const visual = canvas.closest('.hero-visual');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
        camera.position.set(0, 0.65, 7.5);
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        const group = new THREE.Group();
        scene.add(group);
        const ink = new THREE.Color('#171717');
        const blue = new THREE.Color('#3457d5');
        const green = new THREE.Color('#455c47');
        const warm = new THREE.Color('#c4a36d');
        const nodeMaterial = new THREE.MeshBasicMaterial({ color: ink, transparent: true, opacity: 0.82 });
        const coreMaterial = new THREE.MeshBasicMaterial({ color: blue, transparent: true, opacity: 0.92 });
        const ringMaterial = new THREE.LineBasicMaterial({ color: '#d6d1c6', transparent: true, opacity: 0.78 });
        const orbitMaterial = new THREE.LineBasicMaterial({ color: '#3457d5', transparent: true, opacity: 0.28 });
        const lineMaterial = new THREE.LineBasicMaterial({ color: '#6f6f68', transparent: true, opacity: 0.3 });
        const nodeGeometry = new THREE.SphereGeometry(0.07, 24, 16);
        const core = new THREE.Mesh(new THREE.SphereGeometry(0.18, 32, 20), coreMaterial);
        group.add(core);
        const labels = ['repo','pr','review','mcp','audit','skill','rating','agent'];
        const points = [];
        labels.forEach((label, index) => {
          const angle = (index / labels.length) * Math.PI * 2;
          const radius = index % 2 === 0 ? 2.25 : 3.05;
          const y = Math.sin(angle * 1.7) * 0.62;
          const position = new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * 0.95);
          points.push(position);
          const material = nodeMaterial.clone();
          if (label === 'mcp') material.color = green;
          if (label === 'skill') material.color = warm;
          const node = new THREE.Mesh(nodeGeometry, material);
          node.position.copy(position);
          node.userData = { base: position.clone(), index };
          group.add(node);
          const connector = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), position]);
          group.add(new THREE.Line(connector, lineMaterial));
        });
        [1.65, 2.45, 3.15].forEach((radius, index) => {
          const curve = new THREE.EllipseCurve(0, 0, radius, radius * (0.34 + index * 0.05), 0, Math.PI * 2);
          const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(120).map((p) => new THREE.Vector3(p.x, 0, p.y)));
          const ring = new THREE.LineLoop(geometry, index === 1 ? orbitMaterial : ringMaterial);
          ring.rotation.x = 0.92 + index * 0.16;
          ring.rotation.z = index * 0.58;
          group.add(ring);
        });
        const path = new THREE.CatmullRomCurve3([...points, points[0]], true, 'catmullrom', 0.42);
        const pathGeometry = new THREE.BufferGeometry().setFromPoints(path.getPoints(220));
        group.add(new THREE.Line(pathGeometry, new THREE.LineBasicMaterial({ color: '#3457d5', transparent: true, opacity: 0.22 })));
        function resize(){
          const rect = visual.getBoundingClientRect();
          renderer.setSize(rect.width, rect.height, false);
          camera.aspect = rect.width / rect.height;
          camera.updateProjectionMatrix();
        }
        window.addEventListener('resize', resize, { passive: true });
        resize();
        let frame = 0;
        function animate(){
          frame += 0.006;
          group.rotation.y = frame;
          group.rotation.x = Math.sin(frame * 0.7) * 0.08;
          core.scale.setScalar(1 + Math.sin(frame * 5) * 0.045);
          group.children.forEach((child) => {
            if (child.userData && child.userData.base) {
              const pulse = Math.sin(frame * 4 + child.userData.index) * 0.055;
              child.position.copy(child.userData.base).multiplyScalar(1 + pulse);
            }
          });
          renderer.render(scene, camera);
          requestAnimationFrame(animate);
        }
        animate();
      }).catch(() => {
        canvas.style.display = 'none';
      });
    }
  </script>
</body>
</html>"""
    return template.replace("__LOGIN_NOTE__", login_note).encode()


def docs_page() -> bytes:
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sambop Docs — MVP map</title>
  <meta name="description" content="Sambop MVP docs map for GitHub-native AI governance, MCP, install guides, rating, and reusable skills." />
  <style>
    :root{--bg:#fbfaf7;--surface:#fffefa;--ink:#171717;--muted:#6f6f68;--line:#e4e1da;--line-strong:#d6d1c6;--code:#f2f0ea;--accent:#3457d5;--mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace;--sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);letter-spacing:-.012em}.wrap{width:min(980px,calc(100vw - 32px));margin:0 auto}nav,footer{display:flex;justify-content:space-between;gap:20px;padding:26px 0;border-bottom:1px solid var(--line);font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}footer{border-top:1px solid var(--line);border-bottom:0;margin-top:54px}a{color:inherit;text-underline-offset:.22em;text-decoration-color:var(--line-strong)}a:hover{color:var(--accent)}.hero{padding:72px 0 38px}h1{margin:18px 0 20px;font-size:clamp(44px,7vw,86px);line-height:.94;letter-spacing:-.07em;font-weight:560}.lead{max-width:760px;color:var(--muted);font-size:20px;line-height:1.55}.eyebrow,.num{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:28px 0 54px}.card{border:1px solid var(--line);background:rgba(255,255,255,.48);border-radius:14px;padding:20px;min-height:190px}.card h2{margin:12px 0 10px;font-size:28px;letter-spacing:-.045em}.card p{color:var(--muted);line-height:1.55}.card ul{margin:12px 0 0;padding-left:18px;color:var(--muted);line-height:1.65}.code{background:var(--code);border:1px solid var(--line);border-radius:10px;padding:16px;font-family:var(--mono);font-size:13px;line-height:1.7;color:#4b4a45;overflow:auto}.cta{display:flex;flex-wrap:wrap;gap:10px}.btn{display:inline-flex;align-items:center;min-height:40px;padding:9px 13px;border:1px solid var(--line-strong);border-radius:999px;text-decoration:none;font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.btn.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}@media(max-width:760px){.grid{grid-template-columns:1fr}nav,footer{flex-direction:column}}
  </style>
</head>
<body><div class="wrap"><nav><a href="/">Sambop</a><span>Docs map</span></nav><main><section class="hero"><div class="eyebrow">MVP documentation</div><h1>One loop: repo → agent → PR → skill.</h1><p class="lead">This route is a compact public map for the current Sambop shell. The canonical source remains the GitHub repository docs; this page keeps the live site navigation from ending in a 404.</p><div class="cta"><a class="btn primary" href="/mcp">View MCP endpoint</a><a class="btn" href="https://github.com/1wayto/sambop/tree/main/docs">GitHub docs</a></div></section><section class="grid"><article class="card"><div class="num">01</div><h2>Install guides</h2><p>Tool-specific setup docs live in the repository for Hermes, Claude Code, Codex, Cursor, Copilot, VS Code, and Antigravity.</p><a href="https://github.com/1wayto/sambop/tree/main/docs/install">Open install docs</a></article><article class="card"><div class="num">02</div><h2>MCP surface</h2><p>The placeholder MCP server currently exposes:</p><ul><li>list_projects</li><li>list_skills</li><li>install_skill</li><li>get_login_url</li></ul></article><article class="card"><div class="num">03</div><h2>Rating and audit</h2><p>Rating measures contribution quality only. Audit handles spam, malicious code, fake evidence, impersonation, and policy bypass attempts separately.</p><a href="https://github.com/1wayto/sambop/blob/main/docs/concepts/rating.md">Read rating concept</a></article><article class="card"><div class="num">04</div><h2>Skill outcome</h2><p>Every solved Sambop problem should leave reusable procedure behind.</p><div class="code">Problem → PRs → reviewed solution → skill → reuse</div></article></section></main><footer><span>quiet governance infrastructure</span><a href="https://github.com/1wayto/sambop">github.com/1wayto/sambop</a></footer></div></body></html>"""
    return template.encode()

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
        elif path in ("/docs", "/docs/"):
            self.send_body(200, docs_page(), "text/html; charset=utf-8")
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
