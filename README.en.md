# GitHub Project Publisher

English | [简体中文](README.md)

A Codex skill for disciplined GitHub project publication. It applies an auditable, evidence-based workflow to pre-publication review, sensitive-data gating, README and release-note authorship, Conventional Commits, and explicitly authorized GitHub publication.

## Project status

This repository contains the GitHub Project Publisher skill source. The current version is [`v0.1.0`](https://github.com/cicada478/github-project-publisher/releases/tag/v0.1.0); see [RELEASE_NOTES.md](RELEASE_NOTES.md) for details.

## Capabilities

- Separates audit-only, local preparation, repository publication, and Release publication modes.
- Reviews Git state, repository hygiene, file sizes, documentation completeness, license status, and remote targets.
- Blocks publication on potential API keys, tokens, passwords, private keys, sessions/cookies, personal data, and payment credentials.
- Reviews publishable logs, HAR files, traces, dumps, crash reports, and source code that logs sensitive fields.
- Drafts README and Release Notes from code, configuration, test, and history evidence without inventing features, compatibility, or performance claims.
- Organizes atomic commits with Conventional Commits, including scopes, bodies, footers, and breaking-change metadata.
- Preserves explicit authorization boundaries before commit, push, tag, or Release operations.

## Workflow

```text
Inventory the project
  → review sensitive and private data
  → run project-specific lint/test/build checks
  → prepare README and Release text
  → review the exact publication set
  → confirm destination and authorization
  → commit / push / tag / Release
  → verify remote state
```

The workflow must stop when sensitive data is detected or a required check cannot complete. Reports include only the category and `path:line`; matched values are never printed.

## Standards and sources

This project does not treat a single blog post or personal preference as a universal standard. Each rule is grounded primarily in a formal specification or platform documentation and is translated into an executable check or workflow gate.

| Area | Project policy | Primary sources |
| --- | --- | --- |
| Skill structure and progressive disclosure | `SKILL.md` defines identity, activation, and workflow; detailed policy lives in `references/`, while deterministic checks live in `scripts/` | [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills), [Agent Skills Specification](https://agentskills.io/specification) |
| GitHub repository governance | Require a README, effective ignore rules, applicable verification, and explicit license status; classify blockers, warnings, and advisories | [GitHub: Best practices for repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [project publication standards](github-project-publisher/references/standards.md) |
| README authorship | Explain purpose, value, installation, minimal use, support, maintenance status, and limitations; ground claims in repository evidence | [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [project writing guide](github-project-publisher/references/writing-guide.md) |
| Sensitive-data and privacy gate | Inspect credentials, personal information, payment data, captured logs, and sensitive logging calls; block on a finding or incomplete check | [GitHub: Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection), [project sensitive-data review](github-project-publisher/references/sensitive-data-review.md) |
| Commit convention | Use `type(scope)!: subject`, optional body/footer, and `BREAKING CHANGE`; keep each commit focused on one intent | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), [commitlint config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional), [project commit convention](github-project-publisher/references/commit-conventions.md) |
| Versioning | Map `fix`, `feat`, and breaking changes to PATCH, MINOR, and MAJOR only when the project declares a public API and adopts SemVer | [Semantic Versioning 2.0.0](https://semver.org/) |
| Release notes and publication | Bind each Release to an explicit tag and target commit; organize user-facing changes with categories such as Added, Changed, Fixed, Deprecated, Removed, and Security | [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), [safe publishing runbook](github-project-publisher/references/publishing-runbook.md) |
| License identification | Never choose a license for the rights holder; after a choice is made, prefer the standard license text and SPDX identifiers | [SPDX License List](https://spdx.org/licenses/) |

## Repository layout

```text
github-project-publisher/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── commit-conventions.md
│   ├── publishing-runbook.md
│   ├── sensitive-data-review.md
│   ├── standards.md
│   └── writing-guide.md
└── scripts/
    └── preflight.py
```

The earlier `commit规范.md` source material has been incorporated and corrected in `references/commit-conventions.md`; the publication set no longer depends on the original root-level file.

## Requirements

- A Codex surface that supports local skills;
- Git;
- Python 3.10 or later;
- GitHub CLI only when creating a repository, pushing, or publishing a Release.

The preflight script uses only the Python standard library.

## Installation

### User scope

Run from this repository root in PowerShell:

```powershell
$skillsRoot = Join-Path $HOME ".codex\skills"
New-Item -ItemType Directory -Force -Path $skillsRoot
Copy-Item -LiteralPath ".\github-project-publisher" -Destination $skillsRoot -Recurse
```

The resulting entry point must be:

```text
C:\Users\username\.codex\skills\github-project-publisher\SKILL.md
```

`username` represents the Windows account name; on the current machine the actual root is `C:\Users\Cicada\.codex\skills`. Do not create an extra nested directory with the same name: `SKILL.md` must be directly inside `github-project-publisher`.

Codex normally detects the skill automatically. If it does not appear, start a new task or restart Codex. Use `/skills` in the CLI or IDE extension to inspect discovered skills. To distribute the skill to a team, publish the complete `github-project-publisher` directory and have each user copy it into their own `.codex\skills` directory.

## Usage

Explicit invocation is the most deterministic:

```text
$github-project-publisher Audit the current project for GitHub publication. Report findings only and do not modify files.
```

```text
$github-project-publisher Audit the current project, fix safe issues, and draft the README and Release text. Do not commit or upload anything.
```

```text
$github-project-publisher Publish this project to OWNER/REPOSITORY as a private repository on main. Ask me to confirm the version and target commit before creating a Release.
```

Implicit invocation is enabled in `agents/openai.yaml`, so a matching request may activate the skill without an explicit mention.

## Run the preflight directly

From this repository root:

```powershell
python .\github-project-publisher\scripts\preflight.py .
```

For JSON output:

```powershell
python .\github-project-publisher\scripts\preflight.py . --format json
```

Exit codes:

- `0`: the bundled scan completed without blockers; project-specific checks are still required.
- `1`: blockers were found; do not commit or publish.
- `2`: the scan could not complete; treat it as a blocker.

## Security model

The scanner never prints matched sensitive values. If a real credential has entered Git history, revoke or rotate it first and let the repository owner assess history removal; do not improvise a force-push. See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Limitations

- Pattern matching cannot prove that a repository contains no sensitive data.
- Images, archives, encrypted content, proprietary binary formats, and secrets assembled across variables require manual or domain-specific inspection.
- This skill does not grant GitHub account access; publication still depends on local Git, GitHub CLI, or configured connector capabilities.
- Repository-specific testing, build, licensing, and release policies take precedence over general guidance.

## License

This project is licensed under the [MIT License](LICENSE).
