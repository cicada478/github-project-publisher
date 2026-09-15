# Sensitive and private data review

Apply this review immediately before staging/commit and again against the exact staged or release candidate. The goal is prevention: once a secret or private record is published, deleting a line from a later commit does not erase the exposure.

## Required coverage

Inspect all tracked files, staged content, non-ignored untracked files intended for publication, generated release assets, and relevant Git history. Include text and configuration, environment files, archives/manifests, notebooks, fixtures, screenshots, databases/dumps, and binary metadata when applicable.

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
- Any relevant file that could not be enumerated, opened, decoded sufficiently for the required review, or scanned to completion.

Examples and test vectors are not automatically safe. Confirm that they are provider-documented test values or unmistakable placeholders and cannot authenticate, identify a real person, or authorize payment. Record that disposition without reproducing the value.

## Required execution and result handling

Run from the skill directory while passing the repository path:

```text
python scripts/preflight.py <repository>
```

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
4. Re-run the entire sensitive-data review and all affected tests. A partial rescan is insufficient after logging, configuration, packaging, or artifact changes.
5. Resume only when the scan exits 0 and every manual finding has an explicit safe disposition.

The absence of pattern matches is not proof that a repository contains no sensitive data. Domain-specific identifiers, encoded/encrypted archives, images, proprietary formats, and secrets split across variables require contextual review.
