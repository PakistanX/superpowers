# ilmx plugin

Agents and skills for the ilmX upgrade from Open edX Juniper to Open edX Verawood. It is its own plugin (name `ilmx`)
that sits next to Superpowers: its skills call the Superpowers skills (`superpowers:brainstorming`,
`superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`),
so install both. Nothing outside `plugins/ilmx` is changed except one entry in the marketplace file and the workflow
`.github/workflows/ilmx.yml`.

## Install

```bash
claude plugin marketplace add PakistanX/superpowers
claude plugin install superpowers@superpowers-dev
claude plugin install ilmx@superpowers-dev
export ILMX_PLANNING_DIR=~/path/to/ilmx-planning   # the private planning repository
```

Start the orchestrator as the main thread: `claude --agent ilmx:ilmx-orchestrator`.

## Private data

The ledger (one row per feature: inventory, plan, status, PR), the inventories, the plans and the Taiga defaults are not in
this repository. They live in a private planning repository that the skills and the orchestrator find through
`ILMX_PLANNING_DIR`; only the orchestrator writes there. Nothing in the plugin depends on what is in it.

## Both codebases

| | Juniper codebase (source) | Verawood codebase (target) |
|---|---|---|
| Role | Reference: read it, audit it, take features and their commit ids from it | The code being written and maintained |
| Changes | Only in a repo the owner names; never to its production data, configuration or databases | The normal flow in `ilmx-rules` |
| Branches | Plain `main` and `develop` | `ilmx/verawood-main` and `ilmx/verawood-develop` (forks add `upstream/verawood`) |
| Release check | `openedx/core/release.py` `RELEASE_LINE` is `juniper` | `RELEASE_LINE` is `verawood` |

Detect the release first, read versions from the code, never mix the two, and name the release in findings, commits and PRs.

## Agents

| Agent | Model, effort, turns | Role |
|---|---|---|
| `ilmx-orchestrator` | opus, high, 200 | routes work, holds the gates, keeps the ledger and Taiga, does every commit, push, PR and comment after the owner's go |
| `ilmx-parity-auditor` | opus, high, 50 | per-feature Juniper behaviour inventory; each item port, native or drop |
| `ilmx-planner` | opus, high, 40 | plan file with the extension-point rationale, `## Decision needed`, `## Data` |
| `ilmx-implementer` | sonnet, high, 80 | executes an approved plan, tests first, 100% lines |
| `ilmx-parity-tester` | sonnet, high, 60 | parity tests from the inventory, not from the new code |
| `ilmx-debugger` | opus, high, 60 | root cause, read-only by construction |
| `ilmx-reviewer` | opus, high, 30 | four-pass review, writes `findings.json`, never posts |
| `ilmx-writer` | sonnet, medium, 25 | commit and PR text, README rows, Taiga text |
| `ilmx-fetcher` | haiku, low, 15 | reads GitHub, OEPs, release notes and Taiga, short summaries |

## Gates

Inventory reviewed → plan approved with every `## Decision needed` answered → data-risk gate when models, migrations,
renames, Mongo or storage keys are touched → parity tests cover each inventory item → no blocker or major in the review →
the owner's go before anything is pushed or posted.

## The guard hook

`hooks/guard` is a plugin-level PreToolUse hook (plugin subagents ignore hooks in their own frontmatter), keyed on
`agent_type`. Every `ilmx-*` agent except the orchestrator may not push, run `gh` writes (including `gh pr create`),
call GitHub or Taiga write tools, or spawn agents; the planner, auditor and reviewer may write only their own output.

## Skills

`ilmx-rules` (the rules and the one copy of the PR anatomy), `ilmx-juniper-source`, `ilmx-verawood-target` (repository
map with links, visibility and origin, pins, branches, extension order, MFE slots, the remaining start-up patch), `ilmx-data-migration` (the data-risk gate), `ilmx-port-feature` (the
workflow), `ilmx-repo-pass`, `ilmx-taiga`.

## Checks

```bash
python plugins/ilmx/scripts/validate.py          # manifests, agent frontmatter, references, hook
python -m pytest plugins/ilmx/tests              # validator and guard hook
claude plugin validate plugins/ilmx
```

A GitHub workflow runs all three on pull requests.

## Before the first real use

Run one real feature end to end and record turns and cost per agent here.
