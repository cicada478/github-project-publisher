# Skill interaction-policy evals

`cases.jsonl` describes skill applicability and interaction-routing scenarios: direct and implicit requests, negative applicability, incomplete input, each interaction route, `request_user_input` availability, and blocker behavior. Local audit/preparation without a destination and publication with conflicting destinations form a contrast: missing target information matters only when the requested work depends on it.

The default command validates corpus structure and coverage only. With `--execute`, the runner explicitly asks the model to read the skill and report its policy decision as JSON. This tests policy understanding, not automatic skill discovery, actual tool calls, continued independent work, or generated artifact quality. The current result schema cannot verify which local checks continue while a destination choice is pending. It does not replace the deterministic temporary-repository tests in `github-project-publisher/tests/`, which validate publication-ref scoping, identity handling, historical scanning, and Release asset integrity.

Validate the corpus without model access:

```powershell
python .\evals\run_skill_evals.py
```

Run the behavioral cases through an authenticated Codex CLI:

```powershell
python .\evals\run_skill_evals.py --execute
```

Live execution is read-only and writes JSON results to `evals/artifacts/`. Ordinary push and pull-request CI validates the corpus but does not spend model usage. The workflow's optional `workflow_dispatch` live-eval job requires the repository secret `OPENAI_API_KEY`.
