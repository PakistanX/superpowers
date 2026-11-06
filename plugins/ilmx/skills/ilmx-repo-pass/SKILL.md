---
name: ilmx-repo-pass
description: "How to rework a whole ilmX repository feature by feature before it is pushed. Use when a repo is being prepared or rebuilt; the order of repos comes from the ledger."
---

# Repo-by-repo pass

The order of repositories and the skip list are in the ledger (`$ILMX_PLANNING_DIR/ledger/ledger.yaml`), not here. For the
repository in front of you:
1. **Baseline.** List its features (one per app, block, slot or setting group), run its tests, record coverage.
2. **Fixes first.** Apply the fixes already decided for this repo.
3. **Audit each feature** one at a time: right extension point, tested to 100%, settings documented, source commits named.
4. **Branches.** Follow the branch flow in `ilmx:ilmx-rules`.
5. **Rebuild the history from scratch, feature by feature** with `ilmx:ilmx-port-feature`. Pull requests that already exist are not touched; direct commits are re-made on a topic branch and go through a PR.
6. **README**: feature audit, port status and handoff details. The model is the features app's README (a ported-features table with the source commits).
7. **CI** last: the repo's workflow pattern, run locally first, coverage gate 100%.
8. **Show** the commit list and messages to the owner; the orchestrator pushes after the go.
