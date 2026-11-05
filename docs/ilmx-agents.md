# ilmX agents (this fork)

This is the ilmX fork of [Superpowers](https://github.com/obra/superpowers) (MIT). Upstream keeps supplying the process
skills (brainstorming, plans, TDD, debugging, verification, review); the `ilmx-*` skills and agents added here carry the
ilmX knowledge, rules and workflows. Upstream files stay untouched so upstream changes merge cleanly.

## What it is for

The ilmX skills and agents were written for the **ilmX upgrade from Open edX Juniper to Open edX Verawood**. They work on
**both** codebases, and the wording below is explicit about what holds for each:

| | Juniper codebase (the old ilmX fork of edx-platform and its plugins) | Verawood codebase (the new plugins, forks and Tutor setup) |
|---|---|---|
| Role | Reference by default: read it, audit it, take features and their commit ids from it | The code being written and maintained |
| Changes | Only in a repo the owner names as Juniper maintenance. Never to Juniper production data, config or databases | The normal flow of `ilmx-rules` |
| Extension model | Fork edits are how Juniper was changed; the agents describe them, they do not copy the style | Filters, events, plugin settings and URLs first, a guarded patch last |
| Branches | Plain `main` and `develop` (no release name for now) | `ilmx/verawood-main` and `ilmx/verawood-develop` (forks add `upstream/verawood`) |
| Release check | `openedx/core/release.py` `RELEASE_LINE` is `juniper` | `RELEASE_LINE` is `verawood` |

Compatibility rules for both ends:

1. **Detect the release first.** Read `openedx/core/release.py` in the checkout (or the repo's own README and branch
   names when there is no edx-platform) and load the matching section of `ilmx-context`. Never assume a Python, Django,
   package or API version: read it from `requirements/` or `pyproject.toml` of the code in front of you.
2. **Do not mix the two.** A Verawood plugin never imports a Juniper-only module, and nothing is copied from the Juniper
   fork without checking that Verawood does not already do it natively (`ilmx-port-feature` step 2).
3. **The shared rules do not change with the release:** the branch flow, tests to 100% line coverage, commit and PR
   drafting, safety rules, and source-commit references (below).
4. **Say which release a statement is about.** Findings, commit messages and PR text name the release ("Juniper:",
   "Verawood:") whenever both are involved.

## Moving a feature from Juniper to Verawood

Every ported feature keeps its history visible:

- **Source commits.** The feature's Juniper commit ids (full or 8-character SHA, author, subject) are listed in the
  new commit body under `Ported from Juniper:` and in the PR description. They come from
  the project's Juniper commit audit and `git log` in the Juniper checkout. A feature with no Juniper commit says so.
- **A PR is a deliverable.** The feature works when the package is installed: its app config, entry point, settings, URLs
  and migrations are in the PR (the plugin app is loaded together with its first feature), and each PR builds on the
  earlier merged ones.
- **One feature, one PR, commits by functionality.** The feature's code is split by functionality, with its tests and its
  README row in their own commits (the first PR also has the package skeleton first and CI last). The repo is treated as
  starting from scratch: no rename or refactor commits. The PR text is drafted and reviewed by a person first, and the
  next PR is prepared only after the previous one is approved.
- **Existing PRs stay as they are.** The first PRs already open (for example the one that brought in the whole
  features app) are not edited, closed or rewritten. New feature PRs are raised beside them.
- **Direct commits are redone through a PR.** Work that was committed straight to a branch is re-made on `develop`,
  feature by feature, and merged through a `develop` to `main` PR like everything else.

## Contents

| Kind | Name | What it does |
|---|---|---|
| Skill | `ilmx-context` | Repo map, stack, extension model, where the facts live, known traps |
| Skill | `ilmx-rules` | Git, test, safety and docs rules that always apply |
| Skill | `ilmx-port-feature` | Moving or adding a feature: source commits, native check, extension point, tests, README row, commit plan |
| Skill | `ilmx-repo-pass` | Repo-by-repo, feature-by-feature rework: branches, commit split, README, CI, coverage |
| Agent | `ilmx-coder` | Plans, then implements test-first to 100% coverage; drafts commits for approval |
| Agent | `ilmx-debugger` | Root cause with evidence, configuration before code; diagnosis only |
| Agent | `ilmx-reviewer` | Four-pass review: placement, approach, security and data, code and tests; review only |

## Install

Add this fork as the marketplace and install `superpowers` from it (it replaces the upstream plugin; do not install both).

## Design notes

- **Fork with additions.** `PakistanX/superpowers` is a public fork of `obra/superpowers`. ilmX work lives in `skills/ilmx-*`,
  `agents/ilmx-*.md`, `scripts/validate-ilmx.py` and `tests/ilmx/`. Branch flow: `develop` into `main`; `upstream` is `obra/superpowers`.
- **Context is checked, not trusted.** `ilmx-context` says the code wins; the first agent that finds it stale fixes it.

## Next

- A migration agent for the rehearsal and cut-over steps.
- A release agent for the pinned release manifest.
- Evaluate on real tasks (a small plugin change, an XBlock fix, a migration step) and tune the skills from what fails.

## Checks

`python3 scripts/validate-ilmx.py` checks the manifests and that every skill and agent has a matching name and a
description. `pytest tests/ilmx` covers the script (100%).
