---
name: ilmx-juniper-source
description: "The Juniper (source) side of the ilmX port: what is in scope, how to find the commits that built a feature, pakx naming, and where the feature audit lives. Use when auditing or porting from the Juniper codebase."
---

# Juniper source

Juniper is the release the ilmX platform runs on today. It is reference only: read it, audit it, take features and their
commit ids from it. Never change it, its configuration or its production data.

## Find the source of a feature
In the read-only Juniper checkout:
```bash
git log --format='%h|%an|%ad|%s' --date=short -S'<symbol or string>' -- <paths>
git log --format='%h|%an|%ad|%s' --date=short -- <file>
git show --stat <sha>
```
List every commit that built the feature (SHA, author, date, subject). Commits that only fixed lint, QA findings or merges
fold into their feature. A feature with no Juniper commit says so.

## Naming to expect
- Juniper app and table names use the `pakx` prefix (for example `pakx_*` tables and block types); Verawood uses `ilmx_*`. The data migration renames them, so never assume a Verawood name from a Juniper one.
- ilmX code in the Juniper platform fork sits in ilmX-specific packages (features, admin app, overrides) and in small edits across the platform; both count as source.

## Where the audit lives
The per-feature audit (every Juniper commit and where it went, the feature list with port, native or drop) is kept in the
planning repository (`$ILMX_PLANNING_DIR`, see `ilmx:ilmx-verawood-target`). The parity auditor writes one inventory per
feature there.
