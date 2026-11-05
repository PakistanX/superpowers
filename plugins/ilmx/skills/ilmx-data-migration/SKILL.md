---
name: ilmx-data-migration
description: "The data-risk gate for ilmX work: what a Data section must contain before any model, migration, rename, Mongo or storage change is implemented. Use when a plan touches data."
---

# Data migration and the data-risk gate

The riskiest work in the port is data: table and app-label renames (`pakx` to `ilmx`), the block type and entry-point rename
and its alias window, Mongo 3.6 to 7.0, ORA2 2.7.6 to 7.1.0, S3 key and host rewrites, forum Mongo to MySQL, and the
one-window pipeline against the downtime budget. Line coverage says nothing about any of it.

## When the gate applies
A plan touches models, migrations, renames, Mongo, or storage keys and hosts. The planner then fills `## Data`; the
orchestrator holds the gate; the owner signs off before implementation starts.

## `## Data` must say
- **What changes**: tables, collections, keys, columns, with the app label before and after.
- **Reversible**: the exact way back, or why it cannot be reversed and what protects against that.
- **Idempotent**: running it twice leaves the same result.
- **Counts**: before and after row, document or object counts per table, collection or prefix, and the check that compares them.
- **Rehearsal**: which step of the rehearsed pipeline it belongs to, its measured timing, and the window it must fit in.
- **Rollback**: the procedure and the point after which rollback is not possible.
- **Existing data**: initial migrations of renamed tables are applied with `--fake-initial`, so models and migrations of an app land together, in final form.
- **Privacy**: any dump used is sanitized and anonymized first; reports hold counts only.

## Review checks
The reviewer rejects a data change whose `## Data` is missing or incomplete, and any migration that is not reversible without
saying so.
