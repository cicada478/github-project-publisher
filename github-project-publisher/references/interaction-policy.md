# Interaction and decision policy

Ask only when an answer changes authority, rights, destructive impact, or the public contract. Prefer a structured choice/card when supported; otherwise ask one concise question with mutually exclusive options. Never use a question to offload a deterministic safety check.

## Ask with a choice/card

- Final conversion from private to public, after presenting the completed gate evidence.
- An owner/repository name that cannot be inferred uniquely.
- License selection or any unresolved authorship or redistribution right.
- Release version and draft, pre-release, or stable state when project evidence does not determine them.
- Use of a non-empty destination, remote replacement, force-push, history rewrite, repository deletion, or Tag/Release deletion or replacement.
- Explicit disposition of a suspected sensitive-data false positive.
- Inclusion of an artifact whose provenance, build revision, or redistribution permission is unresolved.

Offer two or three concrete choices, recommend the safest reversible option first, and explain the consequence of each in one sentence. Pause when the choice is required for safe progress.

## Execute without asking, then report

- Read-only repository, identity, remote, and GitHub authentication inspection.
- Preflight, secret/privacy scanning, project lint/test/build checks, link checks, file-size checks, and exact-SHA comparison.
- Repository-scoped configuration of the authenticated account's ID-based GitHub noreply address for new commits.
- Author, Committer, and annotated Tag tagger verification across all reachable publication refs.
- Creation of a new destination as private, private upload, and a fresh-clone verification.
- SHA-256 calculation for every user-supplied Release asset and comparison with GitHub's remote digest.
- Reporting that Release asset hashing is not applicable when the Release has no user-supplied assets.
- Enabling applicable secret scanning and push protection after public conversion when the account and repository support them.

If a mandatory action fails, do not ask whether to bypass it. Stop, classify the failure as a blocker, and provide the safe remediation. A user decision may select among remediations but may not redefine a failed mandatory gate as passing.
