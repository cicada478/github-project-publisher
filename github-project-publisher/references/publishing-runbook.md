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

Confirm the authenticated account, owner/repository name, visibility, destination existence, default branch, and whether the remote has history. Authentication output must not reveal tokens. Prefer GitHub CLI/browser authentication or a credential helper; never embed a token in a remote URL.

If the destination exists, inspect it before changing the local remote:

```sh
gh repo view OWNER/REPO
git ls-remote https://github.com/OWNER/REPO.git
```

Stop if identity, ownership, visibility, or history differs from the user's intent.

## 2. Final local gate

Review `git diff`, `git diff --cached`, `git status --short`, candidate file sizes, and preflight output. Require the preflight process to exit with code 0. Any sensitive-data finding or incomplete/failed scan stops commit and publication. Run project checks. Stage named files only and inspect the staged diff again. A clean, already-committed tree needs no synthetic commit.

Use the profile in [commit-conventions.md](commit-conventions.md) unless the repository defines its own convention. Validate the message against the staged diff before committing. Do not amend, squash, or rewrite user commits unless explicitly requested.

## 3. Create or connect the repository

When a repository must be created, specify visibility explicitly. Prefer separating remote creation from the first push so the target can be re-verified:

```sh
gh repo create OWNER/REPO --private --description "..."
git remote add origin https://github.com/OWNER/REPO.git
git remote get-url origin
git ls-remote origin
```

Substitute `--public` only when public disclosure is explicitly intended. If `origin` exists, do not replace it silently. Use another remote name or obtain explicit authorization to change it.

Push the current branch without force and set upstream only when appropriate:

```sh
git push --set-upstream origin BRANCH
```

Do not push all branches or tags by default.

## 4. Prepare a release

Identify the previous release and candidate range. Confirm version policy and ensure all version-bearing files agree. Decide whether the release is draft, pre-release, or stable based on evidence and the user's stated intent.

Prefer notes in a reviewed local Markdown file so quoting and line breaks are preserved. When immutable releases are enabled or assets must be attached, create a draft first and publish only after assets and metadata are complete.

Typical flow, adapted to repository policy:

```sh
gh release create TAG --target COMMIT --title "TITLE" --notes-file RELEASE_NOTES.md --draft
gh release view TAG
```

Do not create a release from an ambiguous branch tip. Do not mark a release “latest” or stable merely because it has the highest version string. Verify artifact provenance; never attach local binaries whose build process and candidate revision are unknown.

## 5. Verify and report

After pushing, fetch/view remote state and compare the remote branch SHA with the intended commit. After creating a release, view it and verify tag target, title, state, notes, and assets.

Report repository/release URLs and exact SHA. If a wrong but non-sensitive document was published, prefer a normal corrective commit or new patch release. If sensitive data was published, revoke/rotate affected credentials first, restrict exposure if possible, then follow GitHub's sensitive-data removal guidance. Do not improvise destructive history rewriting.
