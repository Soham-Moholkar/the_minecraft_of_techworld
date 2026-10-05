# ATLAS phase branches

`main` contains the complete current integrated application. The branches below
isolate each phase's current source and transitive shared dependencies. There were
no local historical phase commits to recover; these branches are current source
extractions, not historical releases or proof of phase completion.

| Phase | Branch | Scope/status |
| --- | --- | --- |
| 0 | `soham-moholkar/phase-00-repository-foundation` | Repository foundation; historical local baseline |
| 1 | `soham-moholkar/phase-01-core-ui` | ATLAS Core UI; historical local baseline |
| 2 | `soham-moholkar/phase-02-python-mastery` | Python mastery; historical local baseline |
| 3 | `soham-moholkar/phase-03-full-stack-engineering` | Full-stack engineering; historical local baseline |
| 4 | `soham-moholkar/phase-04-dbms-laboratory` | DBMS laboratory; historical local baseline |
| 5 | `soham-moholkar/phase-05-data-science` | Data science; historical local baseline |
| 6 | `soham-moholkar/phase-06-machine-learning` | Machine learning; historical local baseline |
| 7 | `soham-moholkar/phase-07-deep-learning-applied-ai` | Deep learning and applied AI; historical local baseline |
| 8 | `soham-moholkar/phase-08-llm-ai-engineering` | LLM/AI engineering; historical local baseline |
| 9 | `soham-moholkar/phase-09-agentic-systems` | Agentic systems; in progress |
| 10 | `soham-moholkar/phase-10-data-engineering-apache` | Data engineering/Apache; in progress |
| 11 | `soham-moholkar/phase-11-devops-cloud` | DevOps/cloud; in progress |
| 12 | `soham-moholkar/phase-12-security-devsecops` | Roadmap reference only; not started |
| 13 | `soham-moholkar/phase-13-observability-sre` | Roadmap reference only; not started |
| 14 | `soham-moholkar/phase-14-distributed-systems-design` | Roadmap reference only; not started |
| 15 | `soham-moholkar/phase-15-capstone-integrations` | Roadmap reference only; not started |

Each phase branch has a `PHASE_SCOPE.json` listing its feature files, shared
dependencies, source commit and adapted API composition root. Current shared
contracts/models can contain fields used by adjacent phases. Phase source and
local imports remain at their original paths. Optional API routers are mounted
only for the selected phase; Phase 9 retains the AI router it extends. These
extractions include syntax/import validation, not full independent acceptance.
Integration quality snapshots are reset to unrun on extracted branches.

Use these branches to study or develop a phase. Bring changes back to `main` file
by file; merging a subset tree wholesale would remove unrelated integrated code.
Phases 12–15 contain only the authoritative roadmap/instructions and scope notes.
Security and observability baselines in earlier phases remain part of those earlier
phases; they do not represent completion of the later dedicated phases.

Generation is explicit and local:

```powershell
.venv/Scripts/python.exe scripts/prepare_phase_branches.py --source main
.venv/Scripts/python.exe scripts/prepare_phase_branches.py --source main --create
```

The first command validates/reports selections. The second creates local branch
commits using temporary Git indexes without checking out branches or editing the
main working tree. It rejects existing branch names and never pushes or force
updates refs. GitHub publication is a separate, user-authorized action.

Published 2026-10-05 to `Soham-Moholkar/the_minecraft_of_techworld`: main and all
16 branches were pushed atomically with the initial remote history preserved.
All 17 remote commit hashes matched local refs. Six extraction regressions and
all dependency/syntax checks passed; each of the 12 code trees additionally passed
actual API import and OpenAPI registration in an isolated temporary directory.
