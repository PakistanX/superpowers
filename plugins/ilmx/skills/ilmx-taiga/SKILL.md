---
name: ilmx-taiga
description: "How the ilmX agents read and write Taiga stories and tasks through the Taiga MCP. Only the orchestrator writes; workers read through the fetcher. Use when a feature is linked to a Taiga story."
---

# Taiga

Tickets are created and updated through the Taiga MCP, which is signed in as the owner's own account, so every write is made as
the owner. **Only the orchestrator writes, and only after the owner's go.** The guard hook denies every `mcp__taiga__*`
write tool for the other agents.

## Ids
Project, epic, role, status and point ids are cached in the planning repository (`defaults/taiga.yaml`). Do not re-fetch
them unless a call fails with a stale id.

## Behaviour
- **Before the plan**: read the feature's story and tasks (`taiga_userstories_get`, `taiga_tasks_list` through the fetcher) and note anything the story says that the inventory does not.
- **After the plan is approved**: comment the plan summary and the answers to `## Decision needed` on the story (`taiga_userstory_comment_create`). Create tasks for the plan's commits only if the story has none.
- **When the PR opens**: comment the PR link, set the story to In progress, and the task statuses to match.
- **When the PR merges**: set Ready for test or Done as the owner decides; update the points only by the LLM-pace rule (code, tests and docs cost a quarter to a third of the hand-written time; clock-bound work is not reduced).
- Story updates need the current `version`; read the story first.
- The comment text is drafted by `ilmx-writer`, shown to the owner, then posted.
