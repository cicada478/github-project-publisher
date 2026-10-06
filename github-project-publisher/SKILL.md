---
name: github-project-publisher
description: Audit, prepare, and publish local software projects to GitHub, from a routine first upload through versioned Releases. Use when Codex is asked to check a project for GitHub, improve repository-facing documentation, create or connect a repository, push a branch, or publish a Release. Do not use for an isolated Git command or routine code edit with no publication intent.
---

# GitHub Project Publisher

Help ordinary project authors publish safely without requiring Git or security expertise. Match the workflow to the request and risk; preserve privacy gates without treating normal collaboration or unrelated local refs as publication failures.

## Choose the narrowest mode

- **Audit:** inspect and report; make no project or remote changes.
- **Prepare:** audit, improve repository-facing files, and verify locally; do not commit or publish unless requested.
- **Publish repository:** prepare as needed, then push the exact authorized branch or refs to a verified destination.
- **Publish release:** verify a version, Tag, notes, and assets, then create or publish the requested GitHub Release.

A request to publish authorizes ordinary in-scope preparation and a non-force push, not destructive history changes, destination overwrite, or an unrequested visibility change. Create a new destination privately first only when its requested end state is public; verify it before asking for the final public conversion. Preserve an existing repository's visibility and workflow.

Read [references/interaction-policy.md](references/interaction-policy.md) only when a consequential choice is unresolved.

## Establish and verify the candidate

1. Read repository instructions and identify the root, worktree state, exact branch/Tag/commit, staged paths, Release assets, destination, and refspec relevant to the request.
2. During preparation, run `python scripts/preflight.py <repository>` to inspect the worktree, non-ignored untracked files, and `HEAD`. Before pushing committed refs, run `python scripts/preflight.py <repository> --committed-only --ref <candidate-ref>` for every ref in the planned push.
3. Run the project's relevant lint, test, type-check, build, package, and documentation checks. Do not install dependencies or alter toolchains unless authorized.
4. Report **blocker**, **warning**, and **advisory** findings with evidence and remedies. Read [references/standards.md](references/standards.md) for acceptance criteria.

Treat successful checks as evidence tied to their inputs. Re-run only checks invalidated by a change to worktree/staged content, resolved ref OIDs, identity policy, relevant configuration, assets, destination, or remote state. Never reuse incomplete or failed evidence. A final committed-ref preflight is still required after creating a commit because the candidate ref changed.

## Protect sensitive data

Read [references/sensitive-data-review.md](references/sensitive-data-review.md) when auditing privacy or before commit, push, Tag, Release, or public conversion. Block candidate credentials, private keys, sessions/cookies, credential-bearing URLs, private personal records, payment data, unsafe sensitive logging, and incomplete required scans. Never print a detected value or matching line. If a real credential may have entered candidate history, recommend revocation or rotation before history repair.

Scan only refs included by the planned push unless the user requests a whole-repository audit. Treat existing contributor identities as provenance; apply [references/identity-policy.md](references/identity-policy.md) only before creating a commit or annotated Tag, or for an explicitly requested identity audit.

## Prepare repository-facing material

Preserve correct content and established language. Ground claims in code, configuration, tests, or user-provided facts. Do not invent compatibility, performance, citations, contributors, support levels, or roadmap commitments. Do not select a license for the rights holder.

- Before substantially rewriting a README, or drafting or revising release notes, read [references/writing-guide.md](references/writing-guide.md). Release notes use Chinese and English unless the user explicitly requests otherwise; follow the guide's bilingual template.
- Before creating a commit, read [references/commit-conventions.md](references/commit-conventions.md), stage explicit paths, and inspect the staged diff.

## Publish and verify

Read [references/publishing-runbook.md](references/publishing-runbook.md) only for external repository, push, Tag, visibility, or Release operations. Prefer non-interactive `gh` and `git` after verifying authentication and destination. Never expose tokens, force-push, rewrite published history, replace a Tag or Release, change visibility, or overwrite a non-empty destination unless that exact action is separately requested and understood.

After pushing, fetch or view the remote ref and compare it with the intended commit. A fresh clone is additionally required only for a newly created private destination before public conversion or when checkout/reproducibility is itself at risk. For user-supplied Release assets, run `scripts/release_integrity.py OWNER/REPO TAG [FILES...]`; missing assets or digests, mismatches, and incomplete verification block publication.

Return a proportional record: mode and outcome, unresolved risks, files changed, checks run or reused, evidence inputs, consequential decisions, published refs and commit SHA, URLs, and correction guidance. Do not claim success until the remote result is verified.
