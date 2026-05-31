# Sambop Skills

Sambop's learning loop is:

```text
Problem → Repo → Contributions → Reviewed Solution → Skill → Reuse
```

A skill is a portable Markdown procedure that AI tools can install or consume.

## Skill goals

- Preserve solved problem knowledge
- Make repeatable solutions reusable
- Work across many AI tools
- Stay reviewable through GitHub PRs

## Suggested skill structure

```text
skills/<skill-name>/
  SKILL.md
  references/
  templates/
  scripts/
```

## Universal skill idea

Even when tools differ, skills should remain mostly Markdown so they can be adapted to:

- Hermes Agent skills
- Claude/Cursor/Codex instruction files
- VS Code Copilot instructions
- MCP resources
- local agent prompt packs
