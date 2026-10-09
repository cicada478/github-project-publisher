# Professional commit convention

This profile refines the supplied `commit规范.md` into a self-contained Conventional Commits policy. A repository's documented policy and configured lint rules take precedence when they deliberately differ.

## Canonical form

```text
<type>[optional scope][optional !]: <subject>

[optional body]

[optional footer(s)]
```

There is no space before the colon and exactly one space after it. The body begins after one blank line; footers begin after another blank line.

Examples:

```text
docs(readme): clarify Windows installation
```

```text
fix(api): prevent duplicate requests during retry

Track the latest request identifier and discard stale responses. This removes
the timeout workaround without changing the public response schema.

Refs: #123
```

```text
feat(config)!: replace legacy environment variable names

BREAKING CHANGE: use APP_HOST and APP_PORT instead of HOST and PORT.
```

## Allowed types

- `feat`: introduce user-visible functionality.
- `fix`: correct faulty behavior.
- `docs`: change documentation only.
- `style`: change formatting without altering behavior; do not use for visual UI styling that changes the product.
- `refactor`: restructure code without adding a feature or fixing observable behavior.
- `perf`: improve measurable performance.
- `test`: add or correct tests without changing production behavior.
- `build`: change build systems, packaging, or external build dependencies.
- `ci`: change continuous-integration configuration or scripts.
- `chore`: perform necessary maintenance not represented more precisely above.
- `revert`: revert one or more earlier commits and identify them in the body/footer.

Choose the type from the primary intent of the staged diff, not the filenames. `feat` and `fix` carry release semantics under Conventional Commits; other types do not imply a version bump unless they declare a breaking change. Avoid inventing new types unless the repository documents them.

## Scope

The optional scope is a short, stable noun naming the affected subsystem, package, or domain, for example `api`, `cli`, `parser`, or `readme`. Use lowercase unless project policy says otherwise. Omit scope when it would be vague, list several unrelated areas, or merely repeat the repository name.

## Subject

- Describe the actual change concisely, preferably as an imperative action.
- Keep the subject at 50 characters or fewer under this profile. Also keep the complete header within any configured limit; `@commitlint/config-conventional` defaults to 100 characters.
- Use the repository's established human language consistently.
- Do not end with a full stop, repeat the type, mention implementation trivia, or use vague text such as “update files” or “fix bugs.”
- Do not claim an issue is fixed unless the staged change and verification support that claim.

## Body

Add a body when the rationale, approach, trade-off, compatibility effect, or verification is not obvious from the diff. Explain why the change was necessary and what observable behavior changes; do not narrate every edited line. Wrap lines according to project tooling, using 72 characters as a readable default when no rule exists.

## Footers and breaking changes

Use Git trailer-style footers for machine-readable metadata, for example:

```text
Refs: #123
Closes: #456
Reviewed-by: Name <address@example.com>
```

Include identifiers only when they resolve in the destination repository. Preserve required authorship and sign-off trailers exactly.

A breaking change MUST be marked by `!` immediately before the colon, a `BREAKING CHANGE: <description>` footer, or both. Prefer both when the footer is needed to explain impact and migration. Use uppercase `BREAKING CHANGE`. Do not label an internal refactor as breaking; describe the affected public API, configuration, data format, CLI, or documented contract.

Semantic Versioning mapping applies only when the project has adopted SemVer and declared a public API:

- `fix` corresponds to a patch change;
- `feat` corresponds to a minor change;
- any type with a breaking change corresponds to a major change.

## Commit construction procedure

1. Inspect `git status`, the unstaged diff, and untracked files.
2. Partition changes by coherent intent. Do not mix unrelated cleanup with a feature, fix, or documentation change.
3. Stage explicit paths or hunks and inspect `git diff --cached`.
4. Choose the type from behavior and intent; choose a stable scope only when useful.
5. Draft the subject from the staged result. Add rationale, migration, issue references, or breaking-change metadata only when evidenced.
6. Run the repository's commit-message validation if configured. Otherwise check this profile manually.
7. Run `python scripts/preflight.py <repository> --staged-only --identity-policy <selected-policy>` after staging. Block on sensitive findings or incomplete scans. Record the `index_fingerprint`, inspect the staged diff without exposing sensitive values, and complete relevant project checks; worktree checks alone do not validate different staged content. Confirm the index fingerprint is unchanged immediately before committing; rerun affected checks if it changes.
8. After committing, inspect `git show --stat --oneline --decorate HEAD` and verify that the commit contains the intended files and message.

Do not use `git add -A`, amend, interactive rebase, or history rewriting to enforce this convention when unrelated user work or published history may be affected. Ask before installing Commitizen, commitlint, hooks, or other persistent tooling.

## Sources

- User-provided `commit规范.md`, incorporated and normalized on 2026-09-15.
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [commitlint conventional configuration](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional)
- [Semantic Versioning 2.0.0](https://semver.org/)
