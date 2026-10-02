# Sensitive and private data review

Apply this review immediately before staging/commit and again against the exact staged or release candidate. The goal is prevention: once a secret or private record is published, deleting a line from a later commit does not erase the exposure.

## Required coverage

Inspect all tracked files, staged content, non-ignored untracked files intended for publication, generated release assets, relevant Git history, commit identity metadata, and annotated Tag metadata. Include text and configuration, environment files, archives/manifests, notebooks, fixtures, screenshots, databases/dumps, and binary metadata when applicable.

Review both sides of logging risk:

1. **Captured artifacts:** `.log`, rotated logs, traces, HAR exports, crash reports, debug bundles, dumps, structured JSON/JSONL logs, terminal transcripts, and CI artifacts.
2. **Logging code:** calls that emit request/response objects, headers, cookies, authorization values, environment variables, configuration objects, user/customer records, payment payloads, exception context, or database connection strings.

The bundled scanner covers common text patterns and high-confidence identifiers. Supplement it with the repository's configured secret scanner, security tooling, and manual domain review. If `gitleaks`, `trufflehog`, GitHub secret scanning, or another project-approved scanner is already configured, run it; do not install or reconfigure tools without authorization.

## Blocking categories

- API keys, OAuth/client secrets, access/refresh tokens, webhook secrets, JWT/session values, cookies, authorization headers, and signed URLs.
- Passwords, password hashes where disclosure is unsafe, database/service connection strings with embedded credentials, private keys, keystores, certificates containing private material, recovery codes, and seed phrases.
- Personal identifiers and records: government ID numbers, personal email/phone/address data in logs, account identifiers, health/education/employment records, precise location, biometrics, or private customer/user payloads.
- Payment and financial data: payment-card numbers, CVV/CVC/security codes, bank-account/IBAN data, live payment-provider keys, wallet credentials, transaction authorization material, and unredacted payment payloads.
- Logging statements that can emit any of the above, even when no captured log is currently present.
- A commit Author or Committer, or annotated Tag tagger, whose email falls outside the explicitly selected identity policy.
- Any relevant file that could not be enumerated, opened, decoded sufficiently for the required review, or scanned to completion.

Examples and test vectors are not automatically safe. Confirm that they are provider-documented test values or unmistakable placeholders and cannot authenticate, identify a real person, or authorize payment. Record that disposition without reproducing the value.

## Required execution and result handling

Run from the skill directory while passing the repository path:

```text
python scripts/preflight.py <repository>
```

The preflight enumerates all blobs reachable from local refs and scans historical text content that differs from the current tracked blob at the same path. A removed secret therefore remains blocking. An unreadable or oversized historical text blob produces an incomplete-scan blocker. Binary, encrypted, archived, image, and proprietary formats still require the supplemental review described above.

Before creating a commit, ask for the identity choice when it is not already established. Recommend the authenticated account's ID-based noreply address and derive it rather than trusting a typed numeric ID:

```sh
ACCOUNT_ID="$(gh api user --jq .id)"
ACCOUNT_LOGIN="$(gh api user --jq .login)"
NOREPLY_EMAIL="${ACCOUNT_ID}+${ACCOUNT_LOGIN}@users.noreply.github.com"
git config --local user.name "$ACCOUNT_LOGIN"
git config --local user.email "$NOREPLY_EMAIL"
```

When an explicit Author is required, include angle brackets and still configure the Committer separately:

```sh
git commit --author="NAME <ID+USERNAME@users.noreply.github.com>" -m "..."
```

If the user explicitly chooses a personal address after the public-metadata warning, configure that exact address at repository scope and run:

```sh
python scripts/preflight.py <repository> --identity-policy configured
```

This mode accepts ID-based noreply identities plus the exact repository-local `user.email`; it does not allow unrelated historical addresses. It emits a warning without printing the selected address. Record the warning as accepted by the user's identity choice.

Immediately before push, Tag, Release, and public conversion, inspect all reachable commits:

```sh
git log --all --format='%H | %an <%ae> | %cn <%ce>'
git for-each-ref --format='%(refname) | %(objecttype) | %(taggeremail)' refs/tags
```

The automated preflight resolves the expected address from `gh api user` without printing email values and rejects syntactically valid noreply addresses owned by another account. If `gh` is not on `PATH`, pass `--gh PATH`. In non-networked CI, pass both `--expected-github-id ID` and `--expected-github-login LOGIN` only from trusted repository configuration; never derive them from the commits being checked.

Interpret exit codes:

- `0`: the bundled scan completed without blockers; continue with repository-specific checks.
- `1`: one or more blockers were found; do not stage, commit, push, tag, publish a Release, or change visibility to public.
- `2`: the scan could not complete; treat this exactly like a blocker.

Machine-readable output is available with `--format json`. It contains finding categories and locations, never the matched values.

For every finding, report only:

```text
[BLOCKER] <category> <relative/path>:<line> — <remediation>
```

Do not print or quote the value, matching line, neighboring lines, diff hunk, request payload, or log entry. If a location has no meaningful line number, report the path and the nearest safe structural location such as a commit SHA, archive member, asset name, or configuration key name without its value.

## Remediation

1. Stop the publication workflow before creating new Git objects or remote mutations.
2. Remove the data from the source and prevent recurrence through redaction, allowlisted safe fields, secret storage, structured logging filters, and effective ignore rules.
3. If a real credential was ever committed or shared, revoke/rotate it first. Then assess history removal with the repository owner; do not improvise force-pushes or tag replacement.
4. If a real email entered unpublished history, rewrite it only with explicit authorization. If it was published, first restrict the repository, then coordinate history, Tag, Release, clone, fork, cached-view, and server-garbage-collection consequences; changing Git config alone does not remove old metadata.
5. Re-run the entire sensitive-data review and all affected tests. A partial rescan is insufficient after identity, logging, configuration, packaging, or artifact changes.
6. Resume only when the scan exits 0 and every manual finding has an explicit safe disposition.

The absence of pattern matches is not proof that a repository contains no sensitive data. Domain-specific identifiers, encoded/encrypted archives, images, proprietary formats, and secrets split across variables require contextual review.
