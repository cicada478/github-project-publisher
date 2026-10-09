# Git identity policy

Apply this policy only when the workflow will create a commit or annotated Tag, or when the user explicitly requests an identity audit. A read-only audit does not require identity selection or GitHub authentication.

## New commits created by the workflow

Reuse an established repository identity policy when one exists. Otherwise ask once before the first commit:

- **GitHub ID-based noreply (Recommended):** avoids publishing the account's personal address.
- **Personal email:** allowed after warning that Author, Committer, and Tagger metadata is public, durable, cloned, and mirrored.

Recommendation is not consent. Configure the chosen identity at repository scope so Author and Committer agree. For noreply, derive the address from the authenticated account rather than trusting a typed numeric ID:

```sh
ACCOUNT_ID="$(gh api user --jq .id)"
ACCOUNT_LOGIN="$(gh api user --jq .login)"
git config --local user.name "$ACCOUNT_LOGIN"
git config --local user.email "${ACCOUNT_ID}+${ACCOUNT_LOGIN}@users.noreply.github.com"
```

Run preflight with the matching policy:

```sh
python scripts/preflight.py <repository> --staged-only --identity-policy noreply
python scripts/preflight.py <repository> --staged-only --identity-policy configured
```

The `noreply` policy verifies ownership against `gh api user`. Trusted offline CI may provide both `--expected-github-id` and `--expected-github-login`. Never derive those values from the commits being checked. The `configured` policy accepts the explicitly selected repository-local address and reports its public exposure without printing it.

## Existing history

Existing Author, Committer, and Tagger identities are provenance. Different contributors, bots, imports, or historical addresses are advisories, not blockers, merely because they differ from the current publisher.

Use `--history-identity-policy strict` only when the user explicitly requests a single-identity or history-anonymization gate. Rewriting history requires separate authorization and must account for signatures, Tags, Releases, forks, clones, and changed commit IDs.

## Result handling

Never print an email address discovered from unrelated history. Report only the commit SHA or Tag ref, role, and privacy category. Record the selected policy once and reuse it while the repository policy and configured identity remain unchanged.
