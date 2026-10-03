# Publication decisions

Ask only when an unresolved answer changes authority, rights, disclosure, destructive impact, delivery path, release meaning, or the public contract. Stop before the affected mutation. Do not use questions to offload deterministic safety work.

Use the interaction capability available in the current turn. When structured input is available for a bounded choice, call it rather than imitating a card in prose. Host permission prompts grant technical execution permission; they do not answer business decisions.

## Choose the interaction

- **No question:** evidence is sufficient and the next step is safe, in scope, and already authorized.
- **Binary confirmation:** one fully specified consequential action remains and the only meaningful outcomes are proceed or cancel.
- **Structured choice:** two or more concrete, mutually exclusive outcomes materially change the result.
- **Free-form question:** the user must supply an unconstrained name, value, or explanation and no evidence-backed candidates exist.
- **Host permission:** the sandbox, network, credential broker, or filesystem requires execution approval after the business decision is settled.

Do not invent alternatives to force a choice card, repeat authorization for ordinary in-scope steps, or silently select a consequential option because one is recommended.

## Publication choices that may require the user

- Git identity before the first workflow-created commit, unless repository policy or the current request already fixes it; apply [identity-policy.md](identity-policy.md).
- Owner/repository target when candidates conflict, or a free-form target when none can be inferred.
- License or unresolved redistribution rights.
- Release version and draft, pre-release, or stable state when project evidence does not determine them.
- Inclusion of assets with unresolved provenance, build revision, or redistribution permission.
- Direct push versus branch-and-PR when both are valid and materially different.
- Use of a non-empty destination, remote replacement, force-push, history rewrite, deletion, or replacement of a Tag or Release.
- Disposition of a suspected sensitive-data false positive when it cannot be resolved deterministically.
- Final conversion of a newly created verified private destination to public.

For a bounded choice, state each option's outcome and material tradeoff. Mark a recommendation only when evidence supports it. Never offer bypassing a mandatory safety gate as an option.

## Continue without asking

After the user has requested publication and the target choices are settled, continue through read-only inspection, preflight, relevant project checks, exact-path staging, an approved commit, non-force push, remote verification, temporary fresh-clone verification when required, and Release digest comparison. A repository policy may still require a final commit checkpoint.

Record consequential decisions and automatically applied defaults with their basis and scope. Notification of a completed check is not a new approval request.
