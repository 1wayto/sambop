# Agent Instructions for Sambop

You are contributing to a Sambop-enabled GitHub repository.

## Before changing files

1. Read `README.md`.
2. Read `SAMBOP.md`.
3. Check `.sambop/project.json` and `.sambop/skills.json` if present.
4. Search existing docs before creating new concepts.
5. Prefer small, reviewable PRs.

## Required workflow

```bash
git checkout -b ai/<agent-name>/<short-task-name>
# make focused changes
git status
git diff
git commit -m "docs: describe concise change"
git push -u origin HEAD
# open a PR
```

Do not push directly to `main` or `master`.

## PR description checklist

Include:

- Summary of changes
- Why the change is useful
- Verification performed
- Any risks or incomplete parts
- Whether a skill was added or should be extracted

## Style

- Prefer clear Markdown specs over heavy implementation until the MVP shape is stable.
- Keep examples concrete.
- Use plain language.
- Do not invent unsupported implementation details; mark assumptions explicitly.

## Security

Never expose secrets, tokens, private keys, or credential files. Do not attempt production actions unless explicitly requested by a maintainer.
