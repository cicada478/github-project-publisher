---
name: github-project-publisher
description: Audit and prepare a local software project for a disciplined GitHub publication, including repository hygiene, Conventional Commit messages, README authorship, release notes, versioning, and authorized repository, push, tag, or GitHub Release operations. Use when Codex is asked to check a project before upload or publish it to GitHub; do not use for an isolated Git command or a routine code edit with no publication intent.
---

# GitHub Project Publisher

Produce a repository that is safe to disclose, reproducible to use, accurately documented, and traceable to a verified revision. Treat publication as a sequence of evidence-backed gates rather than a file upload.

## Select the requested mode

- **Audit:** inspect and report; make no project or remote changes.
- **Prepare:** audit, edit repository-facing documents and configuration, and verify locally; do not publish.
- **Publish repository:** prepare, then create or connect the intended GitHub repository and push only after the target is verified and the action is authorized.
- **Publish release:** prepare a versioned release and notes, then tag/publish only after the exact version, target commit, and release state are verified and authorized.

Infer the narrowest mode that fulfills the request. An explicit request to publish authorizes preparation and private upload, but never a direct public repository creation. Create every new GitHub repository as private, finish upload and verification there, and treat conversion to public as a separate final gate.

Read [references/interaction-policy.md](references/interaction-policy.md) before asking the user anything during preparation or publication. Use a structured choice/card when the surface supports it. Ask only for a material choice or destructive action that cannot be inferred safely; perform mandatory deterministic checks without asking and report their results.

## Establish evidence

1. Read repository instructions and inspect the project tree, Git status, branches, remotes, tags, recent commits, build metadata, CI, ignore rules, and existing community files.
2. Run `python scripts/preflight.py <repository>` from this skill. A pre-publication run MUST exit with code 0; exit code 1 means blockers were found and exit code 2 means the inspection could not complete. Treat it as a conservative baseline, not a substitute for repository-specific checks.
3. Discover the project's own lint, test, type-check, build, package, and documentation commands. Run the checks appropriate to the changed surface. Do not install dependencies or alter toolchains unless the request authorizes that work.
4. Review tracked history as well as the working tree for secrets when disclosure risk exists. Inspect logging statements and publishable log, trace, dump, HAR, crash, and diagnostic artifacts for credentials, personal data, and payment data. Never print a detected value. If a real credential may have entered Git history, stop publication and recommend revocation/rotation before history repair.
5. Inspect effective Git identity, every reachable commit's Author and Committer, and annotated Tag taggers. Require the authenticated account's ID-based GitHub noreply address before creating a commit or making a repository public.
6. Report findings as **blocker**, **warning**, or **advisory**, with file/command evidence and a concrete remedy. Distinguish verified facts from inferences and unverified items.

Read [references/standards.md](references/standards.md) for the normative quality model and acceptance gates. Use project-specific conventions when they are stricter.

## Enforce the sensitive-data gate

Read [references/sensitive-data-review.md](references/sensitive-data-review.md) before any commit, push, tag, Release, or change from private to public visibility.

Treat a potential API key, authentication token, private key, password, session/cookie, credential-bearing URL, personal identifier, personal contact/address data in logs, payment-card/bank identifier, payment security code, live payment-provider key, or code that logs sensitive fields as a blocker. A failed, interrupted, incomplete, or unreadable required scan is also a blocker.

Treat a non-noreply Author, Committer, or annotated Tag tagger in any reachable publication ref as a privacy blocker. Report only the commit SHA or ref name and role; never echo the email address.

Report only the finding category and location as `path:line`, plus a remediation. Redact the value completely; do not quote the matching line, include surrounding context, place it in a diff summary, or copy it into issues, commits, README text, Release notes, terminal output, or chat. A suspected false positive requires human review of the local file and an explicit disposition; never weaken or bypass the gate automatically.

## Prepare repository-facing material

- Preserve correct existing content and the project's established language. For a broad audience, a concise primary language plus a linked translation is preferable to interleaving every paragraph twice.
- Base all claims on code, configuration, tests, or user-provided facts. Do not invent support levels, performance results, compatibility, citations, contributors, or roadmap commitments.
- Write the README for first successful use: identity, purpose, status, prerequisites, installation, a minimal verified example, configuration, validation, support, limitations, contribution, security, and license information as applicable.
- Keep commands copyable from a fresh checkout. Mark shell and platform assumptions. Explain expected output when it helps users verify success.
- Write release notes from the diff, commits, changelog, issues/PRs, and test evidence. Separate user-visible changes from internal maintenance; state breaking changes, migration, known issues, and verification honestly.
- Do not select or change a license without the rights holder's explicit choice. Do not imply that source availability grants reuse rights.

Read [references/writing-guide.md](references/writing-guide.md) before drafting or substantially rewriting a README or release notes.

## Review the exact publication set

Before any commit, push, tag, or release:

1. Re-run relevant checks and the preflight script; require exit code 0. Any sensitive-data finding or required-check failure stops the workflow before staging or committing.
2. Inspect `git status`, unstaged diff, staged diff, and untracked files. Stage explicit paths; do not use broad staging when unrelated user changes exist.
3. Confirm that generated artifacts, local state, datasets, credentials, personal information, and licensed third-party material are intentionally included or excluded.
4. Ensure version declarations, changelog/release notes, tag, package metadata, and documentation agree.
5. Identify the exact branch and commit to publish. Confirm the remote URL, repository owner/name, visibility, and whether the destination already contains commits.
6. For a newly created destination, verify it is private before the first push. Before public conversion, verify the private remote and a fresh clone contain only the intended refs and objects.

Do not proceed while a blocker remains. Warnings require an explicit, recorded disposition; advisories may be deferred.

## Prepare coherent commits

Read [references/commit-conventions.md](references/commit-conventions.md) before proposing or creating a commit. Follow a repository's documented commit convention when it is stricter or intentionally different; otherwise use the provided Conventional Commits profile.

Build each commit from one coherent intent. Select explicit paths, inspect the staged diff, and derive the type, scope, subject, body, and footers from that diff. Do not hide unrelated changes in a documentation or release commit. Validate the message with the repository's configured commitlint/Commitizen workflow when present, and do not install optional commit tooling merely to create one message.

Before committing through GitHub publication mode, derive the authenticated account's ID-based noreply address with `gh api user`, configure it at repository scope, and ensure both Author and Committer use it. `--author` alone is insufficient because it does not set the Committer. The preflight identity scan MUST pass before commit, push, tag, Release, or public conversion.

## Execute external publication safely

Read [references/publishing-runbook.md](references/publishing-runbook.md) whenever creating a remote repository, pushing, tagging, or creating a GitHub Release.

Prefer `gh` and `git` non-interactively after checking authentication and target identity. Do not use browser automation when the CLI can complete the operation; a browser is a fallback for interactive authentication or a capability unavailable through the CLI. Use least privilege. Never expose tokens in commands or output. Never force-push, rewrite published history, delete/replace a tag or release, change visibility, or overwrite a non-empty destination unless that exact action is separately requested and its impact is understood.

Upload a new repository privately even when the requested end state is public. After private upload, run the full gate, verify a fresh clone, summarize evidence, and obtain an explicit final public-conversion decision. Do not collapse repository creation and visibility conversion into one mutation.

Every user-supplied Release asset MUST receive a local SHA-256 digest and a post-upload comparison with GitHub's remote asset digest. Run `scripts/release_integrity.py OWNER/REPO TAG [FILES...]` after upload and before publishing a draft. Exit code 1 or 2 blocks publication. When there are no uploaded assets, run the verifier without files and report that asset hashing is not applicable; GitHub-generated source archives are not user-supplied Release assets.

## Deliver a publication record

Return:

- publication mode and outcome;
- blocker/warning/advisory summary and any accepted residual risk;
- files changed and checks run, including failures or omissions;
- published branch and commit SHA, repository URL, and release/tag URL when applicable;
- concise rollback or correction guidance for any external mutation.

Do not claim success until the remote branch or release is fetched/viewed and shown to reference the intended commit.
