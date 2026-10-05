# ATLAS — Phase 00: Repository foundation

Branch: `soham-moholkar/phase-00-repository-foundation`. Status: **historical local baseline**.

This is a current source extraction from integration commit `8c76cca9692437b232adcf57893348e68f165ac1`. It is not a historical release. The complete integrated application and its checkpoint are on `main`.

`PHASE_SCOPE.json` lists this phase's source and transitive shared dependencies. Shared current models/contracts may contain fields used by adjacent phases. Optional API router wiring is limited to the selected phase and core. These source views are for studying and developing phase code; integrate changes on main file by file rather than merging a subset tree.

Import closure and Python syntax are checked for each extraction. Full runtime, frontend build and phase acceptance are not implied by a branch existing. Read the authoritative roadmap for remaining acceptance.

API environment: `python -m pip install -e './apps/api-python[data,dev]'`. Some phase tests require optional frameworks/streaming/lakehouse extras and native runtimes described in their runbooks. Frontend: `pnpm install --frozen-lockfile`, then run the selected component tests.

See [all phase branches](docs/phase-branches.md).
