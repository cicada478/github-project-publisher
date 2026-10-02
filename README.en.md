# GitHub Project Publisher

English | [简体中文](README.md)

A Codex skill for disciplined GitHub project publication. It applies an auditable, evidence-based workflow to pre-publication review, sensitive-data gating, README and release-note authorship, Conventional Commits, and explicitly authorized GitHub publication.

## Project status

This repository contains the GitHub Project Publisher skill source. The current version is [`v0.3.0`](https://github.com/cicada478/github-project-publisher/releases/tag/v0.3.0); see [RELEASE_NOTES.md](RELEASE_NOTES.md) for details.

## Capabilities

- Separates audit-only, local preparation, repository publication, and Release publication modes.
- Reviews Git state, repository hygiene, file sizes, documentation completeness, license status, and remote targets.
- Blocks publication on potential API keys, tokens, passwords, private keys, sessions/cookies, personal data, and payment credentials in the current publication set and every reachable historical text blob.
- Reviews publishable logs, HAR files, traces, dumps, crash reports, and source code that logs sensitive fields.
- Creates every new repository as private, completes review there, and keeps public conversion as a separate final decision.
- Selects Git identity through a conversational choice before commit: GitHub ID-based noreply is recommended, while a personal address is optional with a public-metadata warning. A noreply address must match the account ID and login returned by `gh api user`, not merely the expected syntax.
- Computes SHA-256 for every user-uploaded Release asset and compares it with GitHub's remote digest.
- Uses a decision matrix to distinguish no-question paths, binary confirmation, option cards, free-form questions, and host permissions; required decisions stop before mutation, no material option is dropped for UI capacity, and every option explains its outcome, rationale, tradeoff, and recommendation level.
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
  → select and verify Git commit identity
  → create and upload to a private repository
  → compare Release asset SHA-256 values with remote digests
  → verify a fresh clone and remote state
  → ask whether to convert to public
  → recheck anonymous access and security features
```

The workflow must stop when sensitive data is detected or a required check cannot complete. Reports include only the category and `path:line`; matched values are never printed.

## Standards and sources

This project does not treat a single blog post or personal preference as a universal standard. Each rule is grounded primarily in a formal specification or platform documentation and is translated into an executable check or workflow gate.

| Area | Project policy | Primary sources |
| --- | --- | --- |
| Skill structure and progressive disclosure | `SKILL.md` defines identity, activation, and workflow; detailed policy lives in `references/`, while deterministic checks live in `scripts/` | [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills), [Agent Skills Specification](https://agentskills.io/specification) |
| GitHub repository governance | Require a README, effective ignore rules, applicable verification, and explicit license status; classify blockers, warnings, and advisories | [GitHub: Best practices for repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [project publication standards](github-project-publisher/references/standards.md) |
| README authorship | Explain purpose, value, installation, minimal use, support, maintenance status, and limitations; ground claims in repository evidence | [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [project writing guide](github-project-publisher/references/writing-guide.md) |
| Sensitive-data and privacy gate | Inspect current files, reachable historical blobs, credentials, personal information, payment data, captured logs, and sensitive logging calls; block on a finding or incomplete check | [GitHub: Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection), [project sensitive-data review](github-project-publisher/references/sensitive-data-review.md) |
| Private-first visibility | Upload and review every new repository privately, including a fresh clone; treat public conversion as a separate final decision | [GitHub: Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility), [GitHub CLI: `gh repo create`](https://cli.github.com/manual/gh_repo_create), [safe publishing runbook](github-project-publisher/references/publishing-runbook.md) |
| Git identity privacy | Prefer the current account's `ID+USERNAME@users.noreply.github.com`; use a personal address only after an explicit choice and public-exposure warning, while still blocking unapproved identities | [GitHub: Email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference), [project sensitive-data review](github-project-publisher/references/sensitive-data-review.md) |
| Human decision boundary | Use binary confirmation for a true proceed/cancel checkpoint and structured selection for how/which decisions; when `request_user_input` is available and the semantic test passes, call it directly; the Skill cannot enable Plan mode or host controls; trace deterministic defaults without asking | [OpenAI: Plan mode](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), [interaction and decision policy](github-project-publisher/references/interaction-policy.md) |
| Skill behavior verification | Maintain cases for direct, implicit, negative, incomplete-input, structured-card, host-permission, and blocker behavior; ordinary CI validates the corpus and optional manual CI runs live Codex evals | [OpenAI: Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills), [behavior eval guide](evals/README.md) |
| Commit convention | Use `type(scope)!: subject`, optional body/footer, and `BREAKING CHANGE`; keep each commit focused on one intent | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), [commitlint config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional), [project commit convention](github-project-publisher/references/commit-conventions.md) |
| Versioning | Map `fix`, `feat`, and breaking changes to PATCH, MINOR, and MAJOR only when the project declares a public API and adopts SemVer | [Semantic Versioning 2.0.0](https://semver.org/) |
| Release notes and publication | Bind each Release to an explicit Tag and target commit; require local SHA-256 and remote digest agreement for every user-uploaded asset | [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), [GitHub: Release assets API](https://docs.github.com/en/rest/releases/assets), [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), [safe publishing runbook](github-project-publisher/references/publishing-runbook.md) |
| License identification | Never choose a license for the rights holder; after a choice is made, prefer the standard license text and SPDX identifiers | [SPDX License List](https://spdx.org/licenses/) |

## Repository layout

```text
.github/
└── workflows/
    └── ci.yml
evals/
├── cases.jsonl
├── README.md
├── result.schema.json
└── run_skill_evals.py
github-project-publisher/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── commit-conventions.md
│   ├── interaction-policy.md
│   ├── publishing-runbook.md
│   ├── sensitive-data-review.md
│   ├── standards.md
│   └── writing-guide.md
├── scripts/
│   ├── preflight.py
│   └── release_integrity.py
└── tests/
    ├── test_documentation.py
    └── test_preflight.py
```

## Requirements

- A Codex surface that supports local skills;
- Git;
- Python 3.10 or later;
- GitHub CLI for identity resolution, repository operations, Releases, and remote verification; browser use is only a fallback for authentication or a missing CLI capability.

The preflight and Release integrity scripts use only the Python standard library; remote Release verification also requires GitHub CLI.

## Installation

After downloading, place the complete `github-project-publisher` folder in either location:

- Project scope: `<project-root>\.codex\skills\github-project-publisher`
- User scope (global): `C:\Users\username\.codex\skills\github-project-publisher`

Ensure that `SKILL.md` is directly inside that folder, then start a new task or restart Codex.

## Usage

Explicit invocation is the most deterministic:

```text
$github-project-publisher Audit the current project for GitHub publication. Report findings only and do not modify files.
```

```text
$github-project-publisher Audit the current project, fix safe issues, and draft the README and Release text. Do not commit or upload anything.
```

```text
$github-project-publisher Publish this project safely to OWNER/REPOSITORY: upload and verify it privately, then ask me with a structured choice before converting it to public.
```

Implicit invocation is enabled in `agents/openai.yaml`, so a matching request may activate the skill without an explicit mention.

### Option cards and runtime mode

Option cards are rendered by the Codex host; they are not UI created by the Skill. For publication tasks that are likely to require decisions, enter Plan mode first. This gives the host an opportunity to expose structured input, but it does not turn every question into a card.

A card is used only when an unresolved material choice has at least two real mutually exclusive alternatives, changes authority, privacy, disclosure, compatibility, reversibility, or release meaning, and must be resolved before the next mutation. When `request_user_input` is available in the current turn, the Skill must call it directly and must not imitate a card with Markdown. When the tool is unavailable, the Skill cannot switch modes itself; it uses the narrowest interaction supported by the host and stops before the affected mutation.

## Run the preflight directly

From this repository root:

```powershell
python .\github-project-publisher\scripts\preflight.py .
```

Preflight uses `gh api user` to verify that noreply addresses belong to the authenticated account. If `gh` is not on `PATH`, pass its path:

```powershell
python .\github-project-publisher\scripts\preflight.py . --gh "C:\path\to\gh.exe"
```

Trusted CI may provide independently verified account metadata:

```powershell
python .\github-project-publisher\scripts\preflight.py . --expected-github-id 12345678 --expected-github-login USERNAME
```

For JSON output:

```powershell
python .\github-project-publisher\scripts\preflight.py . --format json
```

Exit codes:

- `0`: the bundled scan completed without blockers; project-specific checks are still required.
- `1`: blockers were found; do not commit or publish.
- `2`: the scan could not complete; treat it as a blocker.

Preflight requires an ID-based noreply address owned by the verified GitHub account and scans every reachable historical text blob. After an explicit personal-email choice, add `--identity-policy configured`: only the repository-local email and an ID-based noreply identity owned by the verified account are accepted, while other historical identities still block. Reports never print an address or matched sensitive value.

## Development and validation

```powershell
python -m unittest discover -s .\github-project-publisher\tests -v
python .\evals\run_skill_evals.py
```

The second command validates corpus structure and coverage without model usage. With an authenticated Codex CLI, run the live read-only behavior evals:

```powershell
python .\evals\run_skill_evals.py --execute
```

GitHub Actions runs deterministic checks on pushes, pull requests, and manual dispatches. Live Codex evals run only when a manual dispatch selects `run_live_evals` and the repository has an `OPENAI_API_KEY` secret.

After uploading Release assets, run:

```powershell
python .\github-project-publisher\scripts\release_integrity.py OWNER/REPO TAG .\dist\asset.zip
```

List every user-uploaded asset. With no uploaded assets, omit file arguments and the script reports `not-applicable`.

## Security model

The scanner never prints matched sensitive values. If a real credential has entered Git history, revoke or rotate it first and let the repository owner assess history removal; do not improvise a force-push. See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Limitations

- Pattern matching cannot prove that a repository contains no sensitive data.
- Historical scanning covers reachable text blobs; binaries, images, archives, encrypted content, and proprietary formats still require manual or domain-specific inspection.
- Images, archives, encrypted content, proprietary binary formats, and secrets assembled across variables require manual or domain-specific inspection.
- This skill does not grant GitHub account access; publication still depends on local Git, GitHub CLI, or configured connector capabilities.
- The default noreply policy blocks other historical identities; personal-email mode permits only the explicitly selected repository-local address. Rewriting published history is destructive and always requires separate authorization.
- Repository-specific testing, build, licensing, and release policies take precedence over general guidance.

## License

This project is licensed under the [MIT License](LICENSE).
