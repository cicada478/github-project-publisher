# Sensitive and private data review

Prevent disclosure from the exact publication candidate. Deleting a value from the worktree does not remove it from candidate history, while an unrelated local ref is outside the gate unless the planned push includes it.

## Coverage

Inspect candidate tracked and staged content, intended non-ignored untracked files, generated Release assets, history reachable from publication refs, and relevant binary metadata. Review both:

- captured logs, traces, HAR files, crash reports, dumps, terminal transcripts, databases, notebooks, screenshots, archives, and CI artifacts;
- code that may log headers, cookies, authorization values, environment/configuration objects, user records, payment payloads, exceptions, or connection strings.

The bundled scanner covers common text patterns and repository publication state. Also run an already configured project scanner such as gitleaks or trufflehog when it adds complementary provider-specific or repository-specific coverage. Do not install extra scanners merely to duplicate equivalent coverage.

## Machine-specific paths

The baseline warns about Windows drive paths, personal home directories, and common local runtime locations in publishable text. Review hardcoded Python/R executables, working directories, data paths, and logs for portability and personal-directory exposure. Use the current interpreter, PATH discovery, project-relative paths, or explicit configuration as appropriate; do not blindly replace paths.

These heuristic findings are not automatic blockers. Explicit documentation placeholders and conventional system/container paths can be valid. Historical path findings are advisory and do not justify history rewriting by themselves. Reports omit the matched value. UNC paths, assembled paths, and other installation layouts may need contextual review.

## Blockers

- API keys, OAuth/client secrets, access or refresh tokens, webhooks, JWT/session values, cookies, authorization headers, and signed URLs.
- Passwords, unsafe password hashes, credential-bearing connection strings, private keys, keystores, recovery codes, and seed phrases.
- Private personal, customer, health, education, employment, location, biometric, or account records.
- Payment-card, CVV/CVC, bank/IBAN, live payment-provider, wallet, or transaction authorization data.
- Logging statements capable of emitting the above without an effective redaction boundary.
- A required candidate file or Blob that cannot be enumerated, read, classified, or scanned sufficiently.

Examples and test vectors are not automatically safe. Confirm that they are documented non-live values or unmistakable placeholders. Never reproduce a possible secret merely to ask for that determination.

## Run the baseline

During preparation, include worktree and non-ignored untracked content:

```text
python scripts/preflight.py <repository>
```

For the final committed candidate, exclude unrelated local work and name every ref in the planned push:

```text
python scripts/preflight.py <repository> --committed-only --ref <branch-or-tag>
```

Repeat `--ref` for multiple refs. Large text that exceeds the scan limit is an incomplete-scan blocker. Large binary content receives a warning and needs format-appropriate review when it will be published. Symbolic links are inspected as links rather than followed outside the repository.

Apply [identity-policy.md](identity-policy.md) separately when the workflow creates a commit or annotated Tag. Do not turn normal collaborative history into a sensitive-data blocker.

## Reporting and remediation

Report only category, safe path or commit/Tag identifier, and remediation. Never print the value, matching line, surrounding context, diff hunk, request payload, or log entry.

If a real credential was committed or shared, revoke or rotate it first. Then remove the source, prevent recurrence, and let the repository owner decide whether history repair is necessary. Do not improvise force-pushes or Tag replacement. Re-run only checks invalidated by content, identity, configuration, packaging, asset, or destination changes; never reuse incomplete evidence.

Pattern matching cannot prove absence of sensitive data. Encoded or encrypted content, images, proprietary formats, archives, domain-specific identifiers, and secrets assembled across variables require contextual or format-specific review.
