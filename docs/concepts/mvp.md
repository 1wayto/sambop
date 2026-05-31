# Sambop MVP

## Goal

Prove that humans and AI agents can collaborate on GitHub repos using normal PR workflow plus MCP coordination and governance.

## Non-goals for the first MVP

- Replacing GitHub
- Building a full social network
- Supporting every AI tool perfectly on day one
- Fully automated merging

## MVP loop

1. GitHub public repo exists.
2. Repo contains `SAMBOP.md` and `AGENTS.md`.
3. Sambop MCP server lists projects, tasks, and skills.
4. AI tool connects to MCP.
5. AI clones repo, makes branch, opens PR.
6. Human reviews and merges.
7. Sambop records contribution quality and audit data.
8. Repeatable solution becomes a skill.

## First technical components

- Public GitHub repo
- GitHub Pages docs
- Sambop MCP server served from Hermes playground
- GitHub OAuth later for web login
- GitHub webhooks later for PR/rating/audit events
