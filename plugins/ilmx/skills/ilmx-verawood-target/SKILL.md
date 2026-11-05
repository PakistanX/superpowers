---
name: ilmx-verawood-target
description: "The Verawood (target) side of the ilmX port: repository map, version pins, extension order, the start-up patches, storage rules and where the planning ledger lives. Use before writing or reviewing target code."
---

# Verawood target

Detect the release first: `openedx/core/release.py` `RELEASE_LINE` must be `verawood`. Read versions from the code; the pins
below are the plan, so drift is detectable.

## Pins
Open edX Verawood (`release/verawood.1`), Tutor 22.0.3, Python 3.12, Django 5.2, MySQL 8.4, MongoDB 7.0. Plugin tests run in
Tutor's `openedx` image with a MongoDB service.

## Repository map
| Repository | Purpose |
|---|---|
| `ilmx-features-app` | ilmX features for Open edX as Django app plugins (edx-platform is not forked). Features are moved in from the Juniper codebase one at a time, each as a working deliverable. |
| `openedx-org-membership` | Reusable plugin: organization membership and roles, and access scoped by organization. Certificates belong with it, including a small independent view-only service so issued certificates keep working if ilmX is retired. No dependency on ilmX code. |
| `ilmx-adminpanel` | The admin panel backend API (users, roles, bulk registration and enrolment, analytics, reports, course management) used by the admin MFE. Depends on `openedx-org-membership`. |
| `frontend-app-ilmx-admin` | The admin panel MFE that talks to `ilmx-adminpanel`. |
| `ilmx-widgets` | The ilmX React widgets rendered into MFE plugin slots, published as a pinned package that `tutor-contrib-ilmx` installs. |
| `ilmx-xblocks` | The XBlocks that exist only for ilmX, in one package. |
| XBlock forks (upstream names: `edx-ora2`, `edx_xblock_scorm`, `xblock-drag-and-drop-v2`, `xblock-image-explorer`, `pxc`) | Forks of upstream XBlocks that carry ilmX changes, kept as small as possible and tracking the upstream release. |
| `tutor-contrib-ilmx` | The Tutor plugin: configuration, mounts and installs, MFE slot components, theme installation. It also configures the reusable plugins for ilmX, which stay separate repositories so others can reuse them. No business logic. |
| `ilmx-brand` | Brand layer for the LMS and the MFEs: Paragon design tokens and the stylesheet. |
| MFE forks (upstream names: `frontend-app-authn`, `frontend-app-authoring`, `frontend-app-discussions`) | Forks of the upstream MFEs that add the plugin slots ilmX needs. |
| `ilmx-payments-woocommerce` | The WordPress/WooCommerce shop for course checkout, connected to the LMS; replaces the retired ecommerce service. |
| `ilmx-data-migrations` | The tools that move the Juniper data to Verawood: inventory, key rename, Mongo copy, forum prep, shop import. |

## Extension order
Pick the first option that works and write one line on why each earlier one does not:
1. openedx-filters (pipeline steps) or openedx-events (receivers).
2. Plugin settings, plugin URLs, `openedx.course_tab` entry points, `PROFILE_EXTENSION_FORM`, Django middleware through plugin settings, `ModelAdmin` unregister and re-register (public API).
3. Tutor patches and plugin config.
4. A guarded start-up patch, last resort.
Frontend: slots first, then widgets (`ilmx-widgets`), then MFE edits. Never import a private upstream name without a test that fails when upstream moves it. A zero-diff fork branch of edx-platform exists only for emergency backports.

## Start-up patches
A patch wraps one private upstream function, applies once, disables itself and logs if its target disappears, and has a test.
| Patch | Target | Why no hook | Status |
|---|---|---|---|
| Numerical input grading (non-numbers graded incorrect; setting `ILMX_JUNIPER_NUMERICAL_INPUT`) | `NumericalResponse.get_score` | the problem block has no grading hook | stays |
These three are replaced by public extension points (each is its own feature PR in the ledger, with a test proving the replacement):
| Was | Replaced by |
|---|---|
| `user_role` in the `edx-user-info` cookie (patch of `cookies._get_user_info_cookie_data`) | a Django middleware (plugin settings) that sets its own role cookie; the WordPress header reads it |
| Search within followed posts (patch of `forum.api.search._get_thread_ids_from_indexes`) | an ilmX endpoint using the public `forum.api.search.search_threads` and the subscriptions API |
| HTML placeholders `%%FIRSTNAME%%`, `%%USERNAME%%` (patch of `HtmlBlockMixin.get_html`) | the `VerticalBlockRenderCompleted` filter rewriting the rendered fragment |
Admin actions are not patches: unregister the model and re-register a `ModelAdmin` subclass.

## Storage
Two buckets: private (signed URLs, import/export, ORA, SCORM, reports) and media (behind a CDN). Never write private files to
media. Object keys stay unchanged by the move; only the bucket host in stored URLs is rewritten.

## Planning data
The ledger, inventories, plans and Taiga defaults live in the private planning repository, found through the environment
variable `ILMX_PLANNING_DIR`. Only the orchestrator writes there.
