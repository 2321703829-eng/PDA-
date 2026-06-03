# 2026-04-27 version tag and doc directory governance baseline added

## What Changed

Added a project-level governance baseline for version/tag control and document-directory control:

- added `docs/versioning/version_tag_governance.md`
- added `docs/review/document_directory_governance.md`
- added `docs/dev/structural_governance_one_page_plan.md`

Updated existing entry docs so the new governance rules are part of the current reading chain:

- updated `docs/dev/upgrade_and_verify.md`
- updated `docs/review/doc_sync.md`
- updated `docs/architecture/ARCHITECTURE.md`
- updated `docs/architecture/custom_addons_blueprint.md`
- updated `docs/context/odoo_logistics_context.md`

## Why

The repo had already moved into the `dispatch / trace_core / evidence / exception` mainline, but some core entry docs still described `custom_addons` as if only the older placeholder directories existed. At the same time, the project still lacked an explicit Git tag governance rule and a single document-directory governance rule for naming, folder roles, and status classification.

This round closes that gap by:

1. defining when and how to create `baseline / milestone / release` tags
2. defining how to classify current-effective, bridge, archive, and draft docs
3. reconnecting those rules back into the existing upgrade and doc-sync workflow
4. correcting core architecture/context docs so they reflect the current repo reality

## Outcome

- team members now have a stable entry for version/tag governance
- team members now have a stable entry for document/directory governance
- architecture/context docs no longer imply that `trace_core / evidence / trace_exception / logistics_web` are absent from the repo
- future structural cleanup can proceed from a smaller, clearer baseline instead of from scattered one-off guidance

## Notes

This round only establishes governance documents and syncs entry docs.

It does not yet:

- rename folders
- create actual Git tags
- delete historical docs
- force a new branching strategy
