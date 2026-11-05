---
name: ilmx-context
description: Use before any work in the ilmX Verawood workspace (plugins, XBlocks, Tutor plugin, MFEs, mobile, shop, migration). Gives the repo map, stack, extension model and where the facts live.
---

# ilmX platform context

Durable map of the ilmX Open edX **Verawood** platform. When this file and the code disagree, the code wins:
verify before you assert, and fix this file if it is stale.

## Two codebases: Juniper and Verawood

Check the release before anything else: `openedx/core/release.py` `RELEASE_LINE` in the edx-platform checkout (or the
repo's own README and branch names when there is none). Read versions of Python, Django and packages from the code,
never from memory.

- **Juniper** (the old ilmX fork of edx-platform and its repos): reference by default. Read and audit it; take
  features and their commit ids from it (the project's Juniper commit audit). Change it only in a repo the owner names
  as Juniper maintenance. Never touch Juniper production data, config or databases. Its repos use plain `main` and `develop`.
- **Verawood** (this workspace): the code being written. Everything below describes it.

When both are involved, name the release in every finding, commit and PR ("Juniper:", "Verawood:").

## Stack (Verawood)

- Open edX **Verawood** with **Tutor**. Read the Python, Django, Tutor and package versions from the code in front of you.
- Features are Django app plugins, XBlocks, Tutor plugins, MFE slots and themes; the platform itself is not forked.
- Dev: the Tutor dev stack. Plugin tests run inside the Verawood image, not on the host.

The repository map (names, paths, which repos are pushed) and the traps that are specific to ilmX are kept in the
workspace's local notes, not in this skill. If they are not in your context, ask for them.

## Extension model: why there is no edx-platform fork

Behaviour is added from outside edx-platform. Pick the first option that works:

1. openedx-filters (pipeline steps) or openedx-events (receivers).
2. Plugin settings, plugin URLs, `openedx.course_tab` entry points, `PROFILE_EXTENSION_FORM`.
3. Tutor patches and plugin config.
4. A guarded start-up patch, last resort. Each applies once, disables itself if its target disappears, and has a test. A new patch needs a reason why 1 to 3 cannot work, and an upstream PR plan.

Never import a private upstream name without a test that fails when upstream moves it. A zero-diff fork branch exists only for emergency backports.

## Things that bite

- Open edX loads an app from the `lms.djangoapp` / `cms.djangoapp` entry point only if its AppConfig declares `plugin_app`.
- When tables are renamed from an earlier release, the initial migrations are applied with `--fake-initial`, so models and migrations of an app land together, in final form.
- Never write private files to public storage.
- Juniper code and data are never changed; the legacy repo is read-only reference too: port from it, do not edit it.
