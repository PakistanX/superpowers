---
name: ilmx-repo-pass
description: Use when auditing or reworking a whole ilmX repo before it is pushed, one repo at a time and one feature at a time. Covers branches, commit split, README, CI and coverage.
---

# Repo-by-repo, feature-by-feature pass

Order: features app, xblocks, Tutor plugin, brand, admin MFE, XBlock forks, MFE forks, mobile forks. Do one repo fully before the next. Skip `infra`, `migration`, `e2e` (not pushed).

For each repo:

1. **Baseline.** Read the repo, list its features (one per app, block, slot or setting group), run its tests and record coverage.
2. **Fixes first.** Apply the fixes already decided for this repo in the project's open-work list and review notes.
3. **Audit each feature**, one at a time: does it use the right extension point, is it tested to 100%, are the settings documented, which source commits does it replace.
4. **Branches.** `main` and `develop` (see `ilmx-rules`): changes land on `develop`, a reviewed PR merges `develop` into `main`. Branch names follow the release: Verawood repos use `ilmx/verawood-main` and `ilmx/verawood-develop` (forks add `upstream/verawood`); the older Juniper repos keep plain `main` and `develop`. Forks are real GitHub forks first.
5. **Rebuild the history from scratch, feature by feature** (see `ilmx-port-feature`: feature commits split by functionality, then tests and a README row in their own commits; no rename or refactor commits; one PR at a time, the next only after approval).
   Details: **Rebuild the history.** Do not touch PRs that already exist. Re-make direct commits on `develop`: one commit per feature (files and hunks of that feature), `Ported from Juniper:` source commit ids in each body, and a new `develop` to `main` PR per feature.
6. **README** in its own commit: feature audit, port status and handoff details. The model is the features app's README (a ported-features table with the source commits).
7. **CI** in its own commit, last: workflow copied from the repo's pattern, run locally first , coverage gate 100%.
8. **Show** the commit list and messages to the owner. Push only after the go-ahead.
