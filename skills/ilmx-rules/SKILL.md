---
name: ilmx-rules
description: Use at the start of any ilmX task and before any commit, push, PR, delete or data access. The non-negotiable rules for this workspace.
---

# ilmX working rules

These override convenience. If a task seems to need breaking one, stop and ask.

## Git and PRs
- **No `Co-Authored-By` or other attribution line** in commits or PR bodies unless the owner asks for it explicitly.
- **Show the draft first.** When asked for a commit message, PR text or any draft, show it and wait for an explicit go-ahead. "Show the message" is not permission to commit or push.
- Commit messages and PR text never mention pending or in-progress work, and carry no dates.
- **Branch flow for every repo:** `main` is the upstream head of the last release (forks) or the released state (own repos). All changes go to `develop`, as separate commits. The commit messages and PR text are drafted and a human reviews them first. Then a PR is raised and merged from `develop` into `main`. Never commit to `main` directly.
- **Branch names follow the release.** Repos made for Verawood use `ilmx/verawood-main` and `ilmx/verawood-develop` for the two roles, with `upstream/verawood` as the untouched upstream base (forks). The older Juniper repos use plain `main` and `develop` for now, with no release name appended. Other repos (tooling, agents) use plain `main` and `develop`. Forks are real GitHub forks, made before anything is pushed.
- **Feature to feature PRs.** Each feature is its own PR (its commits split by functionality) from a topic branch, merged into `develop`, then `develop` into `main`. PRs that already exist are left exactly as they are (not edited, not closed, not rewritten); new feature PRs are raised beside them. Work that was committed directly to a branch is re-made on `develop`, feature by feature, and goes through a `develop` to `main` PR too.
- **Source commits are always named.** When a feature comes from Juniper, the commit body and the PR text list the Juniper commits it replaces (`Ported from Juniper: <sha> <subject>`, author), or say there are none.
- **A PR is a deliverable.** The feature works when the package is installed, including its app config and entry point (the plugin app loads with the feature). PRs build on the earlier merged PRs; nothing half-working is merged.
- **PR anatomy.** A feature PR splits by functionality: one commit per piece of the feature, then its tests and its README row in their own commits (the number of feature commits follows the breakdown, not a fixed count). The first PR also has a package skeleton commit first and the CI commit last. No rename, move or refactor commits: code lands in final form. One PR at a time; the next is prepared after the previous is approved.
- One commit per piece of work, with its own files and hunks. README and CI each get their own commit. Each feature commit names the source commit ids it replaces (from the Juniper commit audit).

## Tests
- Unit tests reach **100% line coverage** in every repo. Write the tests before the code that needs them. Run CI locally and have it pass before any push.
- Plugin tests run inside the Tutor/Verawood image (`make test` in the repo), not on the host.

## Safety
- **Juniper is read-only**: no code, config or database change, ever. Reference only.
- **Production dumps must be sanitized and anonymized before any use and before any distribution to the internal team, strictly.** No other distribution, and a raw dump is not kept on a machine. Reports from a dump hold **counts only**, no personal data.
- Internal configuration repositories: read only when needed, skip any file whose name points to credentials, and never copy or print a secret value.
- Never print or store credentials, tokens or keys in chat, commits, docs or test output. Secrets go through Secrets Manager.
- Do not delete files, scratch files, containers, images or volumes without asking and getting a yes for that specific deletion. Docker prune needs confirmation.
- If a request seems to reverse an earlier decision, say so and confirm before acting.

## Docs
- Write the docs as the plan for the target state. No migration-history wording, no "pending" wording in replies or commits.
