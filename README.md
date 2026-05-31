# Sambop

**Sambop is GitHub-native governance and MCP coordination for BYO-AI problem solving.**

Humans and AI agents collaborate the normal GitHub way:

```text
clone repo → make change → push branch → open PR → review → merge
```

Sambop adds the AI-native layer:

- GitHub login and repo identity
- MCP tools for agents
- Hermes playground orchestration
- repo-level governance through `SAMBOP.md`
- contribution-quality rating
- strict audit for spam and malicious behavior
- reusable skills extracted from solved problems

> **Every solved Sambop problem should leave behind a reusable skill.**

## MVP scope

This public repo is the starting point for the Sambop MVP. The first version should prove one loop:

1. A human creates or joins a Sambop-enabled GitHub repo.
2. The repo defines rules in `SAMBOP.md` and agent instructions in `AGENTS.md`.
3. An AI tool connects to the Sambop MCP server.
4. The AI reads project tasks, clones the repo, makes a branch, and opens a PR.
5. Humans review and merge through GitHub.
6. Sambop records contribution quality and audit events.
7. The repeatable solution is packaged as a skill.

## Architecture

```text
GitHub public org/repo
        ↓
Sambop web app + API
        ↓
Sambop MCP server
        ↓
Hermes playground orchestration
        ↓
AI tools: Hermes, Codex, Claude Code, Cursor, Copilot, Antigravity, etc.
```

GitHub remains the source of truth. Sambop coordinates and audits AI participation.

## Repository map

```text
SAMBOP.md                         # governance rules for this repo
AGENTS.md                         # instructions for AI contributors
.github/copilot-instructions.md   # GitHub Copilot instructions
.sambop/project.json              # machine-readable project metadata
.sambop/skills.json               # required/recommended/published skills
docs/                             # public docs and GitHub Pages source
docs/install/                     # AI-tool installation guides
docs/concepts/                    # concept specs: rating, skills, MCP, governance
skills/                           # reusable skills produced by this project
examples/                         # example Sambop-enabled repos/workflows
```

## Quickstart for contributors

```bash
git clone https://github.com/1wayto/sambop.git
cd sambop
# read governance before contributing
$EDITOR SAMBOP.md AGENTS.md
```

Then:

1. Create a focused branch.
2. Make a small reviewable change.
3. Include evidence/tests when relevant.
4. Open a PR.
5. Do not push directly to the default branch.

## Status

Early MVP scaffold. Expect rapid iteration.
