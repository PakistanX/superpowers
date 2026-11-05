---
name: ilmx-port-feature
description: "The workflow for moving one feature from Juniper into a Verawood repo as if starting from scratch. The orchestrator runs it; the other agents do its steps. Use for any feature port."
---

# Port one feature

PR anatomy, source-commit lines and the gates are in `ilmx:ilmx-rules`; this skill is the sequence. The target repo is built
as if from scratch: code lands in final form, with no rename, move or refactor commits.

## Sequence (orchestrator)
1. **Pick** the next feature from the ledger. Its dependencies must already be merged.
2. **Inventory** (`ilmx-parity-auditor`): the Juniper behaviour of the feature, written to `inventories/<feature>.md`: URLs, settings, templates, permissions, emails and tasks, data touched, and the source commits (`ilmx:ilmx-juniper-source`). Each item is marked `port`, `native` or `drop`. The owner reviews it.
3. **Plan** (`ilmx-planner`): `plans/<feature>.md` with the extension point and why each earlier option fails (`ilmx:ilmx-verawood-target`), the files and commits, the tests, and `## Decision needed` and `## Data` when they apply. The owner approves; every Decision needed is answered; the data-risk gate runs when it applies.
4. **Implement** (`ilmx-implementer`): unit tests first, then the code, in the commits the plan lists; 100% line coverage.
5. **Parity tests** (`ilmx-parity-tester`): tests derived from the inventory, not from the new code, one per `port` item.
6. **Review** (`ilmx-reviewer`): `findings.json`; no blocker or major open.
7. **Write** (`ilmx-writer`): commit messages, PR text and README row from the plan and inventory, with the Juniper commit list.
8. **Go**: the owner approves the drafts; the orchestrator commits, pushes, opens the PR, and updates Taiga and the ledger.

## File formats
- Plan: `# <feature>`, `## Source commits`, `## Extension point`, `## Commits`, `## Tests`, `## Decision needed` (options, empty when none), `## Data` (see `ilmx:ilmx-data-migration`), `## Status` (`draft` or `approved`).
- Inventory: one table per area; columns `item`, `source`, `decision` (`port`/`native`/`drop`), `test`.
- Ledger row: see the planning repository's README.
