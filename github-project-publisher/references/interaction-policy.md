# Interaction and decision policy

Ask only when an answer changes authority, rights, destructive impact, privacy exposure, delivery path, release meaning, or the public contract. When such a decision is unresolved, asking is mandatory and work MUST stop before the affected mutation until the user answers. When a structured-input tool such as `request_user_input` is available, call it rather than imitating a card in prose. If the current surface cannot render a card, preserve every material alternative in the narrowest supported interaction and do not proceed silently. Never use a question to offload a deterministic safety check.

## Runtime capability gate

Before composing any user question, inspect the tools and interaction mode available in the current turn.

- If `request_user_input` or an equivalent structured-input tool is available and the card decision test below passes, its use is mandatory. Call the tool; do not write a prose imitation of a card.
- If structured input is unavailable, the skill cannot enable it, switch the task into Plan mode, or override host policy. Use the narrowest interaction the host permits, state the limitation when useful, and stop before the affected mutation.
- Plan mode commonly exposes follow-up and structured-input capabilities in Codex surfaces, but availability and rendering remain host-, version-, and account-dependent. Enabling Plan mode makes a card possible; it does not make every question a card.
- A native sandbox or network approval prompt is never a substitute for a business decision, and a business decision is never a substitute for host permission.

The card rule is complete only when both gates pass: the **semantic gate** (an unresolved consequential choice exists) and the **runtime gate** (a structured-input tool is actually available). The semantic gate determines whether the workflow must ask; the runtime gate determines how the question can be rendered.

Use this compact rule before choosing an interaction:

> **Whether to do one settled action → binary confirmation.**
>
> **How to do it or which valid alternative to use → option card.**
>
> **The host needs technical execution permission → native approval UI.**

## Interaction decision matrix

| Situation | Interaction |
| --- | --- |
| Evidence is sufficient and the next step is safe and already authorized | Continue without asking |
| The user authorized a publication workflow and the next step is an ordinary in-scope check or mutation | Do not repeat confirmation |
| There is one settled action and the only meaningful answers are proceed or cancel | Use a simple binary confirmation when a separate checkpoint is required |
| Two or more materially different valid methods or outcomes exist | Use a structured option card |
| One option is clearly safer or more reversible while alternatives remain reasonable | Use an option card and mark the supported recommendation |
| A high-risk action requires the user to select the method, target, or remediation | Use an option card with explicit consequences |
| The sandbox, network, filesystem, credential broker, or host requires permission | Allow the native host approval UI |
| The user must supply an unconstrained name, value, explanation, or other free text | Ask one concise free-form question |
| Information is missing but a low-risk reversible default is well supported | Continue with the default and state the assumption |

Before treating an action as automatic, verify that it is already authorized, deterministic or low-risk and reversible, and does not silently choose among materially different outcomes. Otherwise it is a required decision, not a default.

## Binary confirmation

Use a simple confirmation only when there is exactly one fully specified action and no meaningful alternative beyond proceed or cancel. State the action, exact scope, and immediate external effect in one sentence. Do not fabricate options such as “now,” “later,” and “cancel” merely to force a card.

For example, after staged paths, commit message, and Git identity are already fixed, a repository policy or explicit user request may require one final “Create this commit / Cancel” checkpoint. If the user already authorized that exact commit as part of the publication request and no separate checkpoint is required, do not ask again.

## Card decision test

Use an option card only when all of these are true:

1. The answer is not already fixed by the current request, an accepted earlier choice, or an authoritative repository policy.
2. Two or more concrete, mutually exclusive choices can be stated without inventing facts.
3. The choice materially changes external state, disclosure, rights, compatibility, reversibility, or release meaning.
4. Work cannot safely pass the next mutation boundary until the user chooses.

When all four conditions are true, the card is mandatory. Do not continue with a recommended option merely because one choice appears safer, more common, or easier to automate.

Immediately before asking, perform a fifth runtime check: confirm that `request_user_input` or an equivalent structured-input tool is listed for the current turn. If it is listed, MUST call it. If it is not listed, do not claim that a native card was shown or can be forced by this skill.

A card chooses **how**, **which**, or **what outcome**. It is not a decorated proceed/cancel prompt.

Do not use a card for an open-ended value when there are no evidence-backed candidates. Ask one short free-form question instead. For example, an unknown repository name is free-form; two conflicting repository names discovered in configuration are suitable card options.

## Ask with a choice/card

- Final conversion from private to public, after presenting the completed gate evidence.
- Commit identity before the first publication commit, unless the repository policy or the current request already records the choice. Offer **GitHub ID-based noreply (Recommended)** because it hides the account's personal address, and **Personal email (Caution)** with an explicit warning that Author, Committer, and Tagger metadata becomes permanently public in clones and mirrors. Recommendation is not consent: an unrecorded identity choice MUST still produce the card.
- An owner/repository target when two or more evidence-backed candidates exist; use free text when no bounded candidates exist.
- License selection or any unresolved authorship or redistribution right.
- Release version and draft, pre-release, or stable state when project evidence does not determine them.
- Use of a non-empty destination, remote replacement, force-push, history rewrite, repository deletion, or Tag/Release deletion or replacement.
- Explicit disposition of a suspected sensitive-data false positive.
- Inclusion of an artifact whose provenance, build revision, or redistribution permission is unresolved.
- Selection of a branch, ref, publication set, direct-push path, or branch-and-PR path when multiple valid delivery outcomes remain.
- Disposition of a warning or failed gate when more than one safe remediation exists; never include bypassing a mandatory gate as an option.

## Publication choice-card matrix

| Decision | Use the card when | Required option content |
| --- | --- | --- |
| Git identity | No identity choice is already recorded before the first publication commit | **GitHub noreply (Recommended)** and **Personal email (Caution)**; state that recommendation is not automatic selection, explain privacy exposure and metadata permanence, and apply the chosen identity to both Author and Committer |
| Repository visibility | A verified repository may remain private, become public, or an existing public repository may be restricted | Describe discoverability, access loss or expansion, fork and collaborator impact, and whether exposure already occurred |
| Release state | Evidence does not uniquely establish draft, pre-release, or stable | Include only applicable states; describe audience visibility, stability signal, and whether another review gate remains |
| Version | More than one valid version follows from the project's declared policy | Show exact candidate versions and the compatibility meaning of each; never guess a versioning policy |
| License or rights | The rights holder must select among known candidates or defer licensing | Put **Do not license yet (Recommended)** first when rights are unresolved; explain redistribution consequences without giving legal advice |
| Destination conflict | A non-empty repository, conflicting remote, or two evidence-backed owner/name targets exist | Prefer **Stop/keep current (Recommended)** or a new destination; identify overwrite, merge, and ownership consequences |
| Destructive repair | Force-push, history rewrite, repository deletion, or Tag/Release deletion or replacement is proposed | Include **Keep current state (Recommended)** and a non-destructive corrective path when one exists; name affected refs and irreversibility |
| Sensitive-data disposition | A suspected false positive cannot be resolved deterministically | Include **Stop and remediate (Recommended)** plus only evidence-backed exclusion or documented-test-fixture choices; never offer “ignore and publish” |
| Release artifact | Provenance, candidate revision, redistribution right, or inclusion is unresolved | Include **Exclude asset (Recommended)**, verified inclusion when achievable, or stop; explain what users would download |
| Branch and delivery path | Protected branches, divergent refs, or repository policy leave direct push, new branch plus PR, or stop as valid outcomes | Identify the target ref, review path, protection impact, and whether the default branch changes |
| Publication scope | More than one evidence-backed file, commit, branch, or Tag set could be published | Name the exact included and excluded scope and its effect on users and reviewability |
| Warning disposition | A warning cannot be resolved deterministically and multiple safe dispositions remain | Offer remediation, documented acceptance, or deferral only when each is permitted; state residual risk and required follow-up |
| Commit plan | Multiple coherent commit partitions materially change review, release semantics, or rollback | Describe each partitioning strategy, its review/rollback effect, and the evidence supporting any recommendation |

## Card construction standard

- Ask one decision per card. Combine at most three questions only when they are independent, share the same checkpoint, and none depends on another answer.
- Use a short header of at most 12 characters or roughly five English words.
- Write the question as one sentence naming the decision and its timing.
- Include every evidence-backed material option; there is no policy-level minimum or maximum beyond having at least two alternatives. Do not add filler, merge distinct outcomes, or discard a valid option to fit a UI limit.
- If one card cannot display all material options, decompose the decision along real dimensions into sequential cards or use another supported structured selector. Every original option MUST remain reachable, and a later card MUST not contradict an earlier choice. Do not add an `Other` option when the client supplies one automatically.
- Use short, unambiguous labels. Order options by recommendation and reversibility when evidence supports that ordering, not alphabetically or for convenience.
- Give every option a concise explanation covering: what happens, why someone might choose it, its material tradeoff, and its recommendation level with an evidence-based reason. Add privacy, public visibility, compatibility, data-loss, or reversibility impact when applicable.
- Do not place commands, tokens, secret values, raw personal email addresses, or implementation details that do not affect the decision in an option. Use labels such as `Personal email`; collect a value separately only after that policy is selected.
- Assign each option one recommendation level: **Recommended**, **Conditionally recommended**, **Neutral / owner decision**, **Caution**, or **Not recommended**. Use **Recommended** for at most one option when evidence establishes a best default; use **Neutral / owner decision** for legal, subjective, or equally supported choices. An unsafe bypass is not a valid option even when marked **Not recommended**.
- After selection, record the decision and its scope, apply it consistently, and do not ask again unless the scope or evidence changes.
- If the surface cannot render cards, state that limitation, preserve the same labels, explanations, recommendation levels, and consequences in the supported interaction, and wait for an explicit answer. Do not collapse the decision into an unexplained yes/no confirmation or silently take the recommended option.

## Reference card patterns

Git identity:

- **GitHub noreply (Recommended):** **Recommended** because it configures the authenticated account's ID-based noreply address for Author and Committer without publishing the personal address.
- **Personal email:** **Caution** because it uses the explicitly provided repository-local address for Author and Committer and remains public in commits, tags, clones, mirrors, and archives; choose it only when public attribution is intentional.

Final visibility:

- **Keep Private (Recommended):** **Recommended** when public distribution is not yet required because access remains restricted and no new public disclosure occurs.
- **Make Public:** **Conditionally recommended** only when distribution is intended and every gate has passed because the repository and reachable Git metadata become anonymously accessible immediately.

Destructive correction:

- **Keep current (Recommended):** **Recommended** when correction is optional because it preserves published history and stops before the destructive mutation.
- **Correct forward:** **Conditionally recommended** when an auditable correction is required because it adds a new commit, Tag, or patch Release without rewriting published objects.
- **Replace history:** **Not recommended** except for an explicitly authorized exceptional remediation because it disrupts clones, forks, caches, and references and cannot guarantee removal from prior copies.

These patterns define the required information density, not mandatory wording. Adapt labels to the actual evidence and omit inapplicable choices.

Do not represent a binary host permission prompt as this decision card. Select the Git identity first; only then request any technical permission needed to configure or commit with it.

## Execute without asking, but leave an audit trace

- Read-only repository, identity, remote, and GitHub authentication inspection.
- Preflight, secret/privacy scanning, project lint/test/build checks, link checks, file-size checks, and exact-SHA comparison.
- Repository-scoped configuration of the selected Git identity after the user has chosen it.
- Author, Committer, and annotated Tag tagger verification against the selected identity policy across all reachable publication refs.
- Creation of a new destination as private, private upload, and a fresh-clone verification.
- SHA-256 calculation for every user-supplied Release asset and comparison with GitHub's remote digest.
- Reporting that Release asset hashing is not applicable when the Release has no user-supplied assets.
- Enabling applicable secret scanning and push protection after public conversion when the account and repository support them.

An explicit request to upload or publish authorizes the ordinary in-scope sequence: read-only inspection, exact-path staging, an already-approved commit, non-force push, remote verification, and temporary fresh-clone verification. Do not add separate conversational confirmations for those steps. A repository policy or explicit request may still require one binary commit checkpoint after its exact scope is settled. Commit identity remains a multi-option choice when it has not already been selected; destructive methods and final public conversion retain their own cards.

For every automatic or defaulted consequential step, keep a compact trace containing:

- the action or default that was applied;
- the authorization, policy, or evidence that made a question unnecessary;
- the exact scope and affected repository/ref/files;
- the observed result and verification evidence;
- any residual warning or follow-up.

Surface material automatic decisions in progress commentary when useful and include them in the final publication record. Do not create or commit a repository log file solely for this trace unless the user or repository policy requests one. Routine read-only commands may be grouped into one trace entry; do not flood the user with command-by-command narration.

## Host permission prompts

The Codex sandbox or host may independently require approve/deny prompts for network access, protected `.git` writes, or paths outside the workspace. These are technical execution permissions, not workflow decisions, and a skill cannot replace their UI with a choice card. When such prompts are unavoidable:

- consolidate compatible, already-authorized operations into the fewest narrowly scoped requests;
- label the request as a host permission rather than a new publication decision;
- request a reusable narrow approval when the host supports it;
- never weaken the sandbox, broaden the target, or suppress a consequential decision merely to reduce prompts.

If a mandatory action fails, do not ask whether to bypass it. Stop, classify the failure as a blocker, and provide the safe remediation. A user decision may select among remediations but may not redefine a failed mandatory gate as passing.
