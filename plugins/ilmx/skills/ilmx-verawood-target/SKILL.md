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
`existing` means it already existed in the Juniper era; `new` means it was created for Verawood. `proposed` marks a row that depends on a Master Plan thread that is still open; it is not a settled decision.
| Repository | Visibility | Origin | Purpose |
|---|---|---|---|
| [`ilmx-features-app`](https://github.com/PakistanX/ilmx-features-app) | private | new | ilmX features for Open edX as Django app plugins (edx-platform carries no ilmX code). Features are moved in from the Juniper codebase one at a time, each as a working deliverable. |
| [`openedx-org-membership`](https://github.com/PakistanX/openedx-org-membership) | private | new, proposed (reusable-plugin split) | Reusable plugin: organization membership and roles, and access scoped by organization. Certificates belong with it, including a small independent view-only service so issued certificates keep working if ilmX is retired. No dependency on ilmX code. |
| [`ilmx-adminpanel`](https://github.com/PakistanX/ilmx-adminpanel) | private | new, proposed (reusable-plugin split) | The admin panel backend API (users, roles, bulk registration and enrolment, analytics, reports, course management) used by the admin MFE. Depends on `openedx-org-membership`. |
| [`frontend-app-ilmx-admin`](https://github.com/PakistanX/frontend-app-ilmx-admin) | private | new | The admin panel MFE that talks to `ilmx-adminpanel`. |
| [`frontend-ilmx-widgets`](https://github.com/PakistanX/frontend-ilmx-widgets) | private | new | The ilmX React widgets rendered into MFE plugin slots, published as a pinned package (`@ilmx/widgets`) that `tutor-contrib-ilmx` installs. |
| [`ilmx-xblocks`](https://github.com/PakistanX/ilmx-xblocks) | private | new | The XBlocks that exist only for ilmX, in one package. |
| [`edx-ora2`](https://github.com/PakistanX/edx-ora2) | public | existing fork | Fork of upstream with ilmX changes, kept as small as possible and tracking the upstream release. |
| [`edx_xblock_scorm`](https://github.com/PakistanX/edx_xblock_scorm) | public | existing fork | Same rule as `edx-ora2`. |
| [`xblock-drag-and-drop-v2`](https://github.com/PakistanX/xblock-drag-and-drop-v2) | public | existing fork, proposed to shrink or go after the diff | Same rule as `edx-ora2`. |
| [`xblock-image-explorer`](https://github.com/PakistanX/xblock-image-explorer) | public | existing fork, proposed to shrink or go after the diff | Same rule as `edx-ora2`. |
| [`pxc`](https://github.com/PakistanX/pxc) | private | existing | Private copy of the upstream `pxc` XBlock. |
| [`tutor-contrib-ilmx`](https://github.com/PakistanX/tutor-contrib-ilmx) | private | new | The Tutor plugin: configuration, mounts and installs, MFE slot components, theme installation. It also configures the reusable plugins for ilmX, which stay separate repositories so others can reuse them. No business logic. |
| [`ilmx-brand`](https://github.com/PakistanX/ilmx-brand) | private | new | Brand layer for the LMS and the MFEs: Paragon design tokens and the stylesheet. |
| [`frontend-app-authn`](https://github.com/PakistanX/frontend-app-authn) | public | new fork | Fork of the upstream MFE that adds the plugin slots ilmX needs. |
| [`frontend-app-authoring`](https://github.com/PakistanX/frontend-app-authoring) | public | new fork | Same rule as `frontend-app-authn`. |
| [`frontend-app-discussions`](https://github.com/PakistanX/frontend-app-discussions) | public | new fork | Same rule as `frontend-app-authn`. |
| [`ilmx-payments-woocommerce`](https://github.com/PakistanX/ilmx-payments-woocommerce) | private | new | The WordPress/WooCommerce shop for course checkout, connected to the LMS; replaces the retired ecommerce service. |
| [`edx-platform`](https://github.com/PakistanX/edx-platform) | public | existing fork | Zero-diff fork of upstream, kept only for emergency backports; no ilmX code lives in it. |
| [`ilmx-data-migrations`](https://github.com/PakistanX/ilmx-data-migrations) | private | new | The tools that move the Juniper data to Verawood: inventory, key rename, Mongo copy, forum prep, shop import. |

Branch names and flow: `ilmx:ilmx-rules`.

MFE slots in use (each is filled by a widget from `frontend-ilmx-widgets` through `tutor-contrib-ilmx`): `account.additional_profile_fields`, `authn.{banner_content,footer,form_header}`, `authoring.certificates_content`, `catalog.course_about_page.{course_media,intro,overview,sidebar}`, `discussions.author_name`, `layout.{footer,studio_footer,studio_header_actions}`, `learner_dashboard.{course_card_banner,course_list,widget_sidebar}`, `learning.{course_outline_sidebar,course_recommendations,progress_certificate_status}`; all `org.openedx.frontend.<name>.v1` except the catalog ones.

## Extension order
Pick the first option that works and write one line on why each earlier one does not:
1. openedx-filters (pipeline steps) or openedx-events (receivers).
2. Plugin settings, plugin URLs, `openedx.course_tab` entry points, `PROFILE_EXTENSION_FORM`, Django middleware through plugin settings, `ModelAdmin` unregister and re-register (public API).
3. Tutor patches and plugin config.
4. A guarded start-up patch, last resort.
Frontend: slots first, then widgets (`frontend-ilmx-widgets`), then MFE edits. Never import a private upstream name without a test that fails when upstream moves it. A zero-diff fork branch of edx-platform exists only for emergency backports.

## Start-up patches
A patch wraps one private upstream function, applies once, disables itself and logs if its target disappears, and has a test.
| Patch | Target | Why no hook | Upstream PR | Status |
|---|---|---|---|---|
| Numerical input grading (non-numbers graded incorrect; setting `ILMX_JUNIPER_NUMERICAL_INPUT`) | `NumericalResponse.get_score` | the problem block has no grading hook | none filed | stays |
| `user_role` in the `edx-user-info` cookie | `cookies._get_user_info_cookie_data` | no filter for the cookie data | none filed | proposed: replace with a middleware |
| HTML placeholders `%%FIRSTNAME%%`, `%%USERNAME%%` | `HtmlBlockMixin.get_html` | upstream substitutes only the user id, email and course id | none filed | proposed: replace with the `VerticalBlockRenderCompleted` filter |
| Search within followed posts | `forum.api.search._get_thread_ids_from_indexes` | the discussion API rejects `following` with `text_search` | none filed | proposed: replace with an endpoint over the public forum API |

The three `proposed` rows are proven in a test spike but not ported yet, and the Master Plan decision is still pending. Until
the feature PR for a row lands in `ilmx-features-app`, treat the Juniper patch as the behaviour (a difference from upstream there
is not a bug). The cookie replacement works like this: a middleware (registered through plugin settings) sets a separate
`ilmx-user-role` cookie, and the WordPress header reads that cookie instead of `user_role` in `edx-user-info`; the header
change is made outside this repository. Admin actions are not patches: unregister the model and re-register a `ModelAdmin` subclass.
Before adding a patch, follow the extension order above and write why each earlier option does not work.

## Storage
Two buckets: private (signed URLs, import/export, ORA, SCORM, reports) and media (behind a CDN). Never write private files to
media. Object keys stay unchanged by the move; only the bucket host in stored URLs is rewritten.

## Planning data
The ledger, inventories, plans and Taiga defaults live in the private planning repository, found through the environment
variable `ILMX_PLANNING_DIR`. The planner and the auditor write their plan and inventory files there; only the orchestrator commits there.
