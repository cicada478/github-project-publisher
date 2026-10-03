# Skill interaction-policy evals

`cases.jsonl` checks activation and interaction routing: direct and implicit activation, negative activation, incomplete input, each interaction route, `request_user_input` availability, and blocker behavior. It does not replace the deterministic temporary-repository tests in `github-project-publisher/tests/`, which validate publication-ref scoping, identity handling, historical scanning, and Release asset integrity.

Validate the corpus without model access:

```powershell
python .\evals\run_skill_evals.py
```

Run the behavioral cases through an authenticated Codex CLI:

```powershell
python .\evals\run_skill_evals.py --execute
```

Live execution is read-only and writes JSON results to `evals/artifacts/`. Ordinary push and pull-request CI validates the corpus but does not spend model usage. The workflow's optional `workflow_dispatch` live-eval job requires the repository secret `OPENAI_API_KEY`.
