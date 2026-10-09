# Publication acceptance criteria

Use **MUST** for blockers, **SHOULD** for expectations that need a recorded reason to omit, and **MAY** for contextual improvements. Apply these criteria proportionally to the requested mode and project risk.

## Candidate and authority

- MUST identify the repository root, exact candidate refs and resolved object IDs, worktree/staged scope when applicable, destination, and intended visibility.
- MUST preserve unrelated user changes and MUST NOT publish material with unresolved privacy, authorship, license, or redistribution rights.
- MUST ask only when an unresolved choice changes authority, rights, disclosure, destructive impact, delivery path, release meaning, or public visibility. Deterministic checks and already authorized ordinary steps do not need repeated confirmation.

## Security and privacy

- MUST scan current candidate content and every historical text Blob reachable from the exact refs to be published. Unrelated local refs are outside the gate unless the planned push includes them.
- MUST block candidate credentials, private keys, authentication/session material, private personal or payment data, unsafe sensitive-field logging, and incomplete required scans.
- MUST NOT display a sensitive value or matching source line; report category and safe location only.
- MUST treat a real exposed credential as compromised and recommend revocation or rotation before history repair.
- MUST apply [identity-policy.md](identity-policy.md) to commits or annotated Tags created by the workflow. Existing collaborative identities are provenance unless strict history review was explicitly requested.
- MUST scan the actual index snapshot after staging and before Commit; worktree content cannot substitute for indexed Blobs. Bind commit evidence to `index_fingerprint` and rerun when the index changes. Bind the separate final Push gate to every planned ref and its resolved object ID after Commit.
- SHOULD run an already configured repository secret scanner in addition to the bundled baseline when it provides complementary coverage.

## Repository quality

- MUST keep the intended publication free of accidental caches, build output, editor state, logs, temporary files, local databases, and oversized objects unless they are documented project artifacts.
- MUST run required project validation for the changed surface and MUST NOT report an unexecuted or failing check as passing.
- MUST keep documentation commands, paths, links, versions, and compatibility claims consistent with the candidate revision.
- MUST state license status without choosing a license for the rights holder.
- SHOULD provide an effective `.gitignore`; add community files only when the project context warrants them.

## Publication and release

- MUST verify the remote branch or Tag resolves to the intended commit after push.
- MUST verify a fresh clone before converting a newly created private destination to public. Other pushes need a fresh clone only when checkout, packaging, or reproducibility is at risk.
- MUST align version declarations, Tag, package metadata, documentation, and Release title.
- MUST NOT move or reuse a published version; issue a corrective version.
- MUST compare local SHA-256 with GitHub's remote digest for every user-supplied Release asset. Report the gate as not applicable when there are no uploaded assets.

## Evidence reuse

Evidence remains valid only while its inputs are unchanged. Re-run the affected check when candidate content or resolved ref OIDs, identity policy, relevant configuration, Release assets, destination, or remote state changes. Reuse successful evidence when those inputs are unchanged; never reuse a failed, incomplete, or interrupted result.

Prefer evidence in this order: observable verification output, code/configuration, maintained project documentation, commit or issue history, explicit user statement, then clearly labeled inference.
