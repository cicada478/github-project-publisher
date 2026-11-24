# GitHub publishing runbook

Use this runbook only for external repository, push, Tag, visibility, or Release operations.

## GitHub CLI guidance

Use structured output (`--json` and, when useful, `--jq`) for decisions based on remote state. Target the verified repository explicitly with a repository argument or `--repo OWNER/REPO`, as supported by the command. When complete lists are needed, account for result limits and API pagination.

If command syntax, output, or pagination needs clarification, consult the available official [gh skill](https://github.com/cli/cli/blob/trunk/skills/gh/SKILL.md) or the installed command's `--help`. Apply only relevant guidance and check newer flags against the installed CLI. This optional reference does not change publication scope, authorization, or verification requirements; do not install or update skills implicitly.

## Verify destination and candidate

Resolve the authenticated account, owner/repository, destination existence and visibility, default branch, current remote URL, candidate refs, and whether the destination contains history. Never expose a token or embed one in a remote URL.

```sh
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git rev-parse HEAD
gh auth status
```

For an existing destination:

```sh
gh repo view OWNER/REPO --json nameWithOwner,visibility,url,defaultBranchRef
git ls-remote https://github.com/OWNER/REPO.git
```

Stop if identity, ownership, visibility, or history conflicts with the user's intent. Apply [identity-policy.md](identity-policy.md) only if the workflow will create a commit or annotated Tag.

After any commit has been created, run the final push gate against the exact committed refs once its inputs are stable:

```sh
python scripts/preflight.py <repository> --committed-only --ref BRANCH
```

Repeat `--ref` for every ref in the planned push. The default identity report preserves collaborative provenance. Apply the selected identity policy at the commit gate when creating a new commit; pushing existing commits alone does not require a new identity choice. Reuse this result while the reported ref OIDs, identity policy, relevant configuration, and candidate assets remain unchanged. A clean already committed tree needs no synthetic commit.

## Create or connect the repository

When creating a destination whose requested end state is public, create it privately and verify the empty target before the first push:

```sh
gh repo create OWNER/REPO --private --description "..."
git remote add origin https://github.com/OWNER/REPO.git
git remote get-url origin
git ls-remote origin
```

For a destination intended to remain private, use the requested private visibility without adding a public-conversion gate. Preserve an existing repository's visibility. If `origin` already exists, do not replace it silently; use another remote name or obtain explicit authorization.

Push only the intended branch or refs, without force:

```sh
git push --set-upstream origin BRANCH
```

Do not push all branches or Tags by default. After push, fetch or view the remote ref and compare its object ID with the preflight candidate. Do not repeat unchanged local scans merely because the push completed.

For a newly created private destination that may become public, clone it into an isolated temporary directory and verify the expected refs, checkout, and publication content. This remote verification replaces another identical local scan. Remove the temporary clone afterward.

## Verify an update in private staging

Use this path when the user asks to keep the candidate private until remote validation is complete and the formal destination is already public. Keep the formal repository public and the staging repository private. Use the user-authorized staging destination or an established staging repository authorized for this project. If neither is available, propose a specific staging destination and wait for authorization before creating or uploading to it. Continue independent local checks while waiting.

1. Resolve the version, candidate commit SHA, intended public refs, and any assets. Verify the staging owner, repository, and private visibility before upload. Push only the candidate refs without force to an explicitly named staging destination. Use a separate remote name if needed and preserve the formal remote and upstream.
2. Compare the staged remote refs with the preflight candidate. Clone the private staging repository into an isolated temporary directory, check out the exact candidate, and run applicable checks against that checkout. If uploading candidate Release assets for verification, compare every staged asset digest with its local file using the Release procedure below. Remove the temporary local clone after verification.
3. Present the staging result, exact candidate SHA, any asset digests, and what will become public. Wait for explicit approval before exposing the candidate through any ref, pull request, release draft, or asset upload in the public repository. Keep the candidate private if checks fail or publication is deferred.
4. After approval, recheck the formal destination and publish through its established workflow. Check the actual public refs, Release target, and assets against the approved candidate. If the workflow needs a different candidate commit or asset before publication, rerun the checks affected by the change and request approval for the revised candidate before exposing it. Verify the public result after the operation.
5. Retain the private staging repository by default so it can be reused. Delete a remote staging repository or its refs only when the user explicitly authorizes that exact cleanup and the formal update has been verified.

## Publish a Release

Identify the previous release and candidate range. Confirm version policy, exact target commit, notes, and draft/pre-release/stable state. Prefer reviewed notes from a local Markdown file. When assets are attached, create a draft first:

```sh
gh release create TAG --repo OWNER/REPO --target COMMIT --title "TITLE" --notes-file RELEASE_NOTES.md --draft
gh release view TAG --repo OWNER/REPO --json tagName,isDraft,isPrerelease,url
```

Do not release an ambiguous branch tip, reuse a published version, or attach an artifact whose build revision or provenance is unknown.

For every user-supplied asset, compare the local SHA-256 with GitHub's remote digest:

```sh
python scripts/release_integrity.py OWNER/REPO TAG path/to/asset-one path/to/asset-two
```

List every uploaded asset exactly once. Missing or additional assets, missing digests, mismatches, API failure, or unreadable files block publication. With no uploaded assets, run without file arguments and report `not-applicable`; GitHub-generated source archives are outside this gate.

## Convert a new destination to public

After the private upload, remote-ref comparison, required fresh clone, and any Release asset checks pass, present the evidence and request the final visibility decision. An earlier preference for public does not bypass this post-verification checkpoint.

```sh
gh repo edit OWNER/REPO --visibility public --accept-visibility-change-consequences
gh repo view OWNER/REPO --json nameWithOwner,visibility,url,defaultBranchRef
```

Verify anonymous access after conversion. Enable applicable secret scanning, push protection, dependency alerts, code scanning, and branch rules when supported and appropriate.

## Report

Report repository and Release URLs, exact published refs and commit SHA, remote verification, asset-integrity result, residual risk, and correction guidance. Prefer a normal corrective commit or new patch release for non-sensitive mistakes. If sensitive data was published, revoke or rotate credentials first and follow GitHub's removal guidance; do not improvise destructive history rewriting.
