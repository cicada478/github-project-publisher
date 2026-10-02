# Publication standards and acceptance gates

Use RFC-style terms deliberately: **MUST** is a release blocker, **SHOULD** requires a documented reason to omit, and **MAY** is contextual. Apply proportionality: a research prototype and a security-sensitive library need different depth, but neither may misrepresent evidence.

## A. Provenance and scope

- MUST identify the repository root, current branch, exact candidate commit, worktree state, remote URL, and intended visibility.
- MUST create a new GitHub destination as private, upload and verify it privately, and keep public conversion as a distinct final decision.
- MUST preserve unrelated user changes and review tracked, untracked, ignored, and generated material according to disclosure risk.
- MUST NOT publish material whose authorship, license, privacy status, or redistribution right is unresolved.
- SHOULD make generated files reproducible from a documented source and toolchain; otherwise label their provenance.

## B. Security and privacy

- MUST find and remove API keys, passwords, credentials, private keys, authentication/session material, personal data, payment credentials, local paths containing sensitive identities, private endpoints, confidential datasets, and diagnostic dumps before publication.
- MUST inspect both sensitive values already present in publishable log/trace/dump/HAR/crash artifacts and source-code logging sinks that may emit credentials, request headers, cookies, personal records, payment payloads, environment variables, or configuration objects at runtime.
- MUST complete an automated scan of every reachable historical text blob, including content no longer present in the working tree. Failure to enumerate, read, or scan a relevant historical blob is a blocker.
- MUST treat an exposed real credential as compromised: revoke or rotate it. Deleting only the working-tree line is insufficient if it exists in a commit.
- MUST NOT display a sensitive value or matching source line while reporting it. Report category and `path:line` only.
- MUST block commit, push, tag, Release, and public-visibility changes when a sensitive-data blocker exists or when the required scan fails, is interrupted, skips a relevant file, or cannot read it.
- MUST select the commit identity before the first publication commit unless repository policy or the current request already determines it. Offer GitHub ID-based noreply as the recommended privacy-preserving option; a personal email is optional only after an explicit warning that Git metadata is public and durable.
- MUST use the selected identity for both Author and Committer on commits created by the workflow.
- MUST inspect Author and Committer email metadata for every reachable publication commit and the tagger email of every annotated publication Tag. Under the personal-email policy, only the exact repository-configured email and ID-based noreply identities are approved; any other address is a privacy blocker. Reports must identify only the SHA/ref and role.
- MUST verify that every accepted ID-based noreply identity belongs to the authenticated GitHub account, using `gh api user` or an explicitly supplied and independently verified account ID/login pair. Syntax alone is insufficient.
- MUST require explicit human disposition for a suspected false positive; automated bypass or allowlisting is not acceptable during the same publication run.
- SHOULD maintain an effective `.gitignore`; public or security-relevant projects SHOULD document vulnerability reporting in `SECURITY.md`.
- SHOULD enable applicable GitHub protections after publication: secret scanning/push protection, dependency alerts, code scanning, and protected branches or rulesets.

## C. Repository hygiene

- MUST exclude dependency caches, build output, editor state, logs, temporary files, environment files, and local databases unless they are intentional project artifacts.
- MUST keep individual Git objects within GitHub's current file limits; use Git LFS only when large binaries genuinely belong under version control.
- MUST avoid broken links, case-only path ambiguity, invalid filenames for supported platforms, and undocumented submodules or LFS requirements.
- SHOULD use coherent, reviewable commits and a stable default branch.
- MUST verify a fresh clone of a new private destination before offering public conversion; the clone must contain only intended reachable objects and refs.

## D. Functional verification

- MUST run the repository's required validation for the changed surface, or explicitly state why it could not be run.
- MUST NOT describe a failing or unexecuted check as passing.
- SHOULD verify a fresh-checkout path when installation, packaging, path assumptions, or generated artifacts changed.
- SHOULD make CI reproduce the important local checks with pinned or constrained tool versions appropriate to the ecosystem.

## E. Documentation and reproducibility

- MUST accurately state purpose, prerequisites, installation, minimal use, support channel, and license status when applicable.
- MUST ensure every documented command exists and matches the current interface.
- MUST distinguish facts, measured results, design rationale, limitations, and future work.
- SHOULD document configuration defaults, supported environments, test commands, data/model provenance, deterministic seeds, and expected outputs when relevant.
- SHOULD add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `CITATION.cff` only when the collaboration, security, or scholarly context warrants them. Empty boilerplate is not compliance.

## F. Version and release integrity

- MUST make the release tag resolve to the intended tested commit.
- MUST align the tag, package metadata, changelog, documentation, and release title.
- MUST NOT move or reuse a published version. Issue a new corrective version.
- MUST calculate SHA-256 for every user-supplied Release asset and compare it with GitHub's post-upload asset digest before publication. A missing asset, missing digest, mismatch, or incomplete comparison is a blocker.
- MUST report the asset-integrity gate as not applicable when no user-supplied Release assets exist; GitHub-generated source archives are outside this gate.
- SHOULD use Semantic Versioning only when the project declares a public API whose compatibility can be assessed. Otherwise document the actual versioning policy.
- SHOULD distinguish stable, pre-release, experimental, archived, and unsupported states visibly.
- SHOULD additionally publish a checksum manifest or provenance attestation when users rely on artifact integrity.

## G. Interaction and tooling

- MUST ask before an unresolved choice changes rights, destructive impact, privacy exposure, delivery path, release state, commit identity, destination identity, publication scope, or final visibility. When structured input is available, the workflow MUST invoke it and stop before the affected mutation until the user answers.
- MUST enumerate all evidence-backed material alternatives before adapting them to the interface. Interface limits may require sequential cards or another structured selector, but MUST NOT cause a valid outcome to be omitted or merged deceptively.
- MUST explain every option's outcome, rationale, material tradeoff, and evidence-based recommendation level. A mandatory safety bypass MUST NOT be offered as an option.
- MUST NOT ask whether to perform deterministic safety work such as scans, selected-identity verification, SHA comparison, exact-ref verification, or fresh-clone validation; run it and report the result.
- MUST record automatically applied defaults and already-authorized consequential steps with their basis, scope, outcome, verification evidence, and residual risk; this trace MUST NOT require committing a new repository file unless requested.
- MUST NOT add redundant workflow confirmations for read-only checks, exact-path staging, non-force push, remote verification, or fresh-clone validation after the user has explicitly requested publication. Unavoidable host/sandbox permission prompts are separate technical controls and SHOULD be consolidated narrowly.
- MUST stop rather than offer a bypass when a mandatory gate fails.
- MUST prefer non-interactive `gh` and `git` operations. Browser automation is a fallback only for interactive authentication or a capability unavailable through the CLI.

## Evidence levels

Use the strongest available source, in this order:

1. observable test/build output from the candidate revision;
2. code and machine-readable configuration;
3. maintained project documentation and changelog;
4. commit/PR/issue history;
5. explicit user statement;
6. inference, clearly labeled.

## Baseline sources

- [GitHub: Best practices for repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)
- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub: Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)
- [GitHub: Email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)
- [GitHub: Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub: REST API endpoints for release assets](https://docs.github.com/en/rest/releases/assets)
- [GitHub CLI: `gh repo create`](https://cli.github.com/manual/gh_repo_create)
- [GitHub CLI: `gh repo edit`](https://cli.github.com/manual/gh_repo_edit)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [SPDX License List](https://spdx.org/licenses/)

These links are authority anchors, not a reason to copy generic boilerplate. Check current GitHub documentation when a platform limit, CLI behavior, or feature availability affects the operation.
