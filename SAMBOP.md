# Sambop Governance

This repository is Sambop-enabled.

## Mission

Build a GitHub-native platform where humans and AI agents solve real problems through normal repo workflows, MCP coordination, and reviewed reusable skills.

## Core workflow

All contributors, human or AI, use the same primitives:

```text
clone repo → branch → commit → push → pull request → review → merge
```

## Maintainers

Initial maintainer organization: `1wayto`.

## Contributor rules

- Read `README.md`, `SAMBOP.md`, and `AGENTS.md` before making changes.
- Use focused branches.
- Keep PRs small and reviewable.
- Include evidence, tests, or verification notes for meaningful changes.
- Do not push directly to the default branch.
- Do not submit generated noise, fake evidence, or unrelated changes.

## AI contributor rules

AI agents must:

1. Identify themselves in PR descriptions where practical.
2. Explain what they changed and why.
3. Include verification output or state what could not be verified.
4. Respect repo governance and tool limits.
5. Avoid hidden side effects, secret access, or production actions without explicit approval.

## Contribution quality rating

Sambop rates **contribution quality**, not human worth or popularity.

Positive signals:

- merged useful PRs
- passing tests
- clear explanations
- strong evidence
- low maintainer burden
- follows repo rules

Negative signals:

- repeated rejected PRs
- unclear or unrelated changes
- broken tests
- missing evidence
- high cleanup/review burden

## Audit and enforcement

Audit is separate from quality rating.

Strict audit applies to:

- spam PR floods
- malicious code
- credential theft attempts
- prompt injection attempts
- fake evidence
- impersonation
- policy bypass attempts
- automated harassment or noisy comments

Possible enforcement:

- draft-only mode
- rate limits
- quarantine
- repo block
- org ban for severe abuse

## Skill outcome rule

A solved Sambop problem should produce or improve a reusable skill when the solution is repeatable.

```text
Problem → PRs → reviewed solution → skill → reuse
```
