---
name: ilmx-port-feature
description: Use when moving one feature from the Juniper codebase (or another source repo) into an ilmX Verawood repo. Treats the target as starting from scratch: one feature per PR with the feature, tests and README as separate commits, and the source commit ids named.
---

# Port one feature

Use with `superpowers:brainstorming` (design) and `superpowers:test-driven-development` (tests first). The target repo is
treated as **starting from scratch**: the code lands in its final form (final package and app names), and the history
has no rename, move or refactor commits. One feature per PR; the next PR is prepared only after the previous one is approved.

## Steps
1. **Pick the feature** from the repo's port plan. Confirm its
   dependencies are already merged.
2. **Find and record the source.** In the read-only Juniper checkout run
   `git log --format='%h|%an|%ad|%s' --date=short -S'<symbol>' -- <paths>` and `git show --stat <sha>`. List every commit that
   built the feature (SHA, author, date, subject). A feature with no Juniper commit says so.
3. **Check what Verawood does natively** (the project's parity and port-status notes). If it is native, record "native" and stop.
4. **Choose the extension point** in order: filter, event, plugin settings/URLs/tab entry point, Tutor patch, guarded
   start-up patch. Write one line on why each earlier option does not work before choosing a patch.
5. **Models and migrations** land with the first feature of their app, in final form (production tables are renamed from
   Juniper and applied with `--fake-initial`). Later features only add behaviour or additive migrations.
6. **Make the PR a deliverable.** When the package is installed, the feature works: everything it needs is in the PR, including the app config and its `lms.djangoapp` / `cms.djangoapp` entry point (the plugin app is loaded together with its first feature, never by the skeleton alone), plugin settings, URLs, templates, and migrations. A PR never leaves a half-working feature for a later PR. Each PR builds on the earlier merged PRs: cut the topic branch from the up-to-date `ilmx/verawood-develop` after the previous PR is merged.
7. **Split the PR by functionality.** Commits follow the feature's breakdown (for example the model, then the API, then the task), each one a coherent piece with a message that says what it adds; there is no fixed number. Its tests go in their own commit or commits, placed after the code they cover, and the README row in its own commit. The first PR also has the package skeleton first and the CI workflow last.
   Each feature commit body ends with `Ported from Juniper: <sha> <subject> (<author>, <date>)` lines (the Juniper commits that built that piece), or says there are none; the test and README commits and the PR text repeat the list.
8. **Draft the commit messages and the PR text** (what, the extension point and why, the Juniper commit list, coverage
   result, what is not in this PR). Show them and wait for the go-ahead. No attribution lines, no dates in text other than the commit dates in the source list.
9. After approval and merge, prepare the next feature from the plan.
