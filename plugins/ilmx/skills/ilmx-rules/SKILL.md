---
name: ilmx-rules
description: "The rules every ilmX agent follows, and the single home of the PR anatomy. Use at the start of any ilmX task and before any commit, push, PR, comment, delete or data access."
---

# ilmX rules

These override convenience. If a task seems to need breaking one, stop and ask the owner.

## Git and PRs
- **No attribution lines** (`Co-Authored-By` and the like) in commits or PR bodies unless the owner asks.
- **Draft first.** Commit messages, PR text, Taiga comments and any other outward text are drafted and shown; nothing is committed, pushed, posted or created until the owner says go. Only the orchestrator does outward writes.
- **Branch flow.** `main` is the upstream head of the last release (forks) or the released state (own repos). Work goes on a topic branch cut from the up-to-date `develop`, is reviewed in a PR into `develop`, then `develop` goes into `main` by PR. Never commit to `main`. Branch names follow the release: Verawood repos use `ilmx/verawood-main` and `ilmx/verawood-develop` (forks add `upstream/verawood`); repos of the older Juniper release keep plain `main` and `develop`. Forks are real GitHub forks, made before anything is pushed.
- **PR anatomy (the only copy; other skills refer here).** One feature per PR, split by functionality: one commit per piece of the feature (for example model, API, task), each message saying what it adds; then its tests in their own commit or commits, after the code they cover; then its README row in its own commit. There is no fixed number of commits. The first PR of a repo also has the package skeleton first and the CI workflow last. No rename, move or refactor commits: code lands in final form.
- **Source commits.** When a feature comes from Juniper, every feature commit body ends with `Ported from Juniper: <sha> <subject> (<author>, <date>)` for the Juniper commits that built that piece, or says there are none. The test and README commits and the PR text repeat the list.
- **A PR is a deliverable.** The feature works when the package is installed: the app config, its `lms.djangoapp` or `cms.djangoapp` entry point, settings, URLs, templates and migrations it needs are in the PR. The plugin app loads with its first feature, never with the skeleton alone. Each PR builds on the earlier merged PRs; nothing half-working is merged. One PR at a time; the next is prepared after the previous is approved.
- **Existing PRs** are left exactly as they are. New work gets new PRs.

## Tests
- Unit tests reach 100% line coverage in every repo. Tests come before the code that needs them. Run CI locally and have it pass before any push.
- Plugin tests run inside the Tutor/Verawood image, not on the host.
- Line coverage proves the code runs, not that it behaves like Juniper. Behaviour parity is proven by tests derived from the inventory (see `ilmx:ilmx-port-feature`).

## Safety
- Juniper code and data are read-only reference: never changed.
- **Production dumps must be sanitized and anonymized before any use and before any distribution to the internal team, strictly.** No other distribution, and a raw dump is not kept on a machine. Reports from a dump hold counts only, no personal data.
- Internal configuration repositories: read only when needed, skip any file whose name points to credentials, and never copy or print a secret value.
- Never print or store credentials, tokens or keys in chat, commits, docs or test output.
- Do not delete files, containers, images or volumes without asking and getting a yes for that specific deletion.
- If a request seems to reverse an earlier decision, say so and confirm before acting.

## Gates (held by the orchestrator)
Inventory reviewed (port, native, drop) → plan approved, every `## Decision needed` answered → data-risk gate when models, migrations, renames, Mongo or storage keys are touched (`ilmx:ilmx-data-migration`) → parity tests cover each inventory item → no blocker or major in the review → the owner's go before anything is pushed or posted.
