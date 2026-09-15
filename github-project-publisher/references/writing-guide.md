# README and release writing guide

## README: design from reader tasks

Start with the shortest path from discovery to a verified result. Select sections because the project needs them, not to satisfy a template.

### Opening block

State the project name and one precise sentence answering: what is it, for whom, and what result does it produce? Follow with maturity/status and the most important constraint. Use badges sparingly; every badge must convey maintained, decision-relevant state.

### Recommended information architecture

1. **Overview** — problem, scope, non-goals, and distinguishing approach.
2. **Quick start** — prerequisites, installation, minimal command/example, and expected observable result.
3. **Usage** — representative workflows ordered by user importance; link exhaustive API material elsewhere.
4. **Configuration** — names, types, defaults, precedence, secret-handling, and safe examples.
5. **Development and validation** — supported toolchain, setup, lint/test/build commands, and contribution route.
6. **Reproducibility or architecture** — include only if users or reviewers need it; identify inputs, versions, seeds, hardware, datasets, and known sources of variance.
7. **Limitations and status** — known failure modes, unsupported environments, stability, and compatibility policy.
8. **Support, security, license, citation, and acknowledgements** — link dedicated files where they exist.

For a library, define the public API and compatibility promise. For a CLI, document command syntax and exit behavior. For a service, document deployment assumptions and health verification. For research software, document method, data provenance, environment capture, reproduction procedure, evaluation definition, and citation.

### Style rules

- Prefer falsifiable, specific claims over promotional adjectives.
- Keep terminology consistent with code and UI.
- Use relative repository links and fenced blocks with the correct language identifier.
- Never put live credentials in examples; use unmistakable placeholders such as `YOUR_API_TOKEN`.
- Avoid screenshots for information that changes frequently or must be accessible/searchable.
- Do not claim cross-platform support unless tested or otherwise evidenced.
- Treat benchmark numbers as incomplete without workload, environment, method, sample count, baseline, and date/revision.

## Release notes: communicate change and consequence

Derive notes from the candidate range, not memory. Determine the previous release/tag and inspect the diff, merged PRs, issues, commit history, package metadata, and verification results.

### Release header

- **Title:** version/tag plus a short factual theme; avoid repeating marketing slogans.
- **Summary:** audience, principal outcome, and stability classification.
- **Date:** use an unambiguous ISO date when included.

### Body

Use only relevant sections:

- **Highlights** — a small set of user-important outcomes.
- **Added / Changed / Fixed / Deprecated / Removed / Security** — Keep a Changelog categories where they improve scanning.
- **Breaking changes and migration** — old behavior, new behavior, affected users, exact migration steps, and rollback considerations.
- **Compatibility** — runtime/platform/API/data-format requirements.
- **Known issues** — impact, conditions, workaround, and tracking link if available.
- **Verification** — checks actually run against the release candidate and their result.
- **Install or upgrade** — exact commands and asset choice, if not obvious.
- **Contributors and full diff** — credit from verified history; link the comparison range.

Do not dump raw commit messages, describe internal refactors as user features, or say “various fixes.” Link issue/PR identifiers only when they resolve correctly in the destination repository. For a security fix, avoid exploit-enabling detail before coordinated disclosure; use the repository's security advisory process.

## Editorial acceptance test

Before saving either artifact, verify:

- a new reader can identify whether the project fits their need;
- the first-use procedure is complete and executable;
- every capability and compatibility claim has evidence;
- limitations are as visible as strengths;
- links, anchors, filenames, commands, and versions agree with the candidate revision;
- prose is concise, neutral, grammatical, and free of unexpanded acronyms where the audience may not know them.
