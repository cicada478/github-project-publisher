# Safe GitHub publishing runbook

Use this runbook only for the externally mutating portion of the skill.

## 1. Verify identity and destination

Run read-only checks first:

```sh
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git branch --show-current
git rev-parse HEAD
gh auth status
```

Confirm the authenticated account, owner/repository name, visibility, destination existence, default branch, and whether the remote has history. Authentication output must not reveal tokens. Prefer non-interactive GitHub CLI and Git operations; do not automate a browser when the CLI supports the operation. A browser is a fallback for interactive authentication or a missing CLI capability. Never embed a token in a remote URL.

If the destination exists, inspect it before changing the local remote:

```sh
gh repo view OWNER/REPO
git ls-remote https://github.com/OWNER/REPO.git
```

Stop if identity, ownership, visibility, or history differs from the user's intent.

Before the first publication commit, reuse an established repository policy or ask once with a structured identity choice:

- **GitHub ID-based noreply (Recommended):** protects the account's personal address.
- **Configured personal email:** permitted only after warning that Git Author, Committer, and Tagger metadata is public, durable, cloned, and mirrored.

For noreply, derive the address from the authenticated account and configure it locally. Do not use a user-supplied numeric ID without checking `gh api user`:

```sh
ACCOUNT_ID="$(gh api user --jq .id)"
ACCOUNT_LOGIN="$(gh api user --jq .login)"
NOREPLY_EMAIL="${ACCOUNT_ID}+${ACCOUNT_LOGIN}@users.noreply.github.com"
git config --local user.name "$ACCOUNT_LOGIN"
git config --local user.email "$NOREPLY_EMAIL"
```

For an explicitly approved personal address, configure the exact selected address at repository scope and use `preflight.py --identity-policy configured`. Never discover, display, or substitute an address from unrelated history.

## 2. Final local gate

Review `git diff`, `git diff --cached`, `git status --short`, candidate file sizes, and preflight output under the selected identity policy. Require the current-file scan, reachable-history blob scan, and authenticated-account identity match to complete with exit code 0. Any sensitive-data, unapproved Author, Committer, tagger, or incomplete-scan finding stops commit and publication. Run project checks. Stage named files only and inspect the staged diff again. A clean, already-committed tree needs no synthetic commit.

Use the profile in [commit-conventions.md](commit-conventions.md) unless the repository defines its own convention. Validate the message against the staged diff before committing. Do not amend, squash, or rewrite user commits unless explicitly requested.

## 3. Create or connect the repository

When a repository must be created, create it as private even when public visibility is the requested end state. Separate creation from the first push so the empty destination can be re-verified:

```sh
gh repo create OWNER/REPO --private --description "..."
git remote add origin https://github.com/OWNER/REPO.git
git remote get-url origin
git ls-remote origin
```

Do not substitute `--public` during creation. If `origin` exists, do not replace it silently. Use another remote name or obtain explicit authorization to change it.

Push the current branch without force and set upstream only when appropriate:

```sh
git push --set-upstream origin BRANCH
```

Do not push all branches or tags by default.

After the private push, repeat preflight and project checks against the exact remote candidate. Clone the private repository into an isolated temporary directory and verify expected refs, noreply identities, absence of obsolete/unreachable objects, and a clean preflight result. Delete the temporary clone after verification.

## 4. Prepare a release

Identify the previous release and candidate range. Confirm version policy and ensure all version-bearing files agree. Decide whether the release is draft, pre-release, or stable based on evidence and the user's stated intent.

Prefer notes in a reviewed local Markdown file so quoting and line breaks are preserved. When immutable releases are enabled or assets must be attached, create a draft first and publish only after assets and metadata are complete.

Typical flow, adapted to repository policy:

```sh
gh release create TAG --target COMMIT --title "TITLE" --notes-file RELEASE_NOTES.md --draft
gh release view TAG
```

Do not create a release from an ambiguous branch tip. Do not mark a release “latest” or stable merely because it has the highest version string. Verify artifact provenance; never attach local binaries whose build process and candidate revision are unknown.

For every user-supplied asset, compute SHA-256 locally and compare it with GitHub's `sha256:...` asset digest after upload. The repository includes a deterministic verifier:

```sh
python scripts/release_integrity.py OWNER/REPO TAG path/to/asset-one path/to/asset-two
```

The command must cover every uploaded asset exactly once and exit 0 before a draft is published. Missing or additional assets, missing remote digests, hash mismatches, API failure, or unreadable files block publication. When the Release has no uploaded assets, run the command without file arguments and report its not-applicable result. GitHub-generated source ZIP/TAR links are not uploaded assets.

## 5. Public-visibility gate

Keep the repository private until branch, Tag, Release, identity, asset-integrity, security/privacy, and fresh-clone checks all pass. Present the evidence and request a separate final decision using a structured choice/card when supported. A request made before upload may express the desired end state, but it does not bypass this post-verification hold point.

After explicit approval, use the CLI and acknowledge visibility-change consequences:

```sh
gh repo edit OWNER/REPO --visibility public --accept-visibility-change-consequences
gh repo view OWNER/REPO --json nameWithOwner,visibility,url,defaultBranchRef
```

After conversion, verify anonymous Git access and re-check commit identities and obsolete SHA isolation. Enable applicable secret scanning and push protection when supported, then verify their state.

## 6. Verify and report

After pushing, fetch/view remote state and compare the remote branch SHA with the intended commit. After creating a release, view it and verify tag target, title, state, notes, assets, and SHA-256 results. After public conversion, independently verify public visibility and anonymous reachability.

Report repository/release URLs and exact SHA. If a wrong but non-sensitive document was published, prefer a normal corrective commit or new patch release. If sensitive data was published, revoke/rotate affected credentials first, restrict exposure if possible, then follow GitHub's sensitive-data removal guidance. Do not improvise destructive history rewriting.
