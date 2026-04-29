# 2026-04-27 tag docs moved to versioning folder

## What Changed

Created a dedicated tag/versioning document folder:

- added `docs/versioning/README.md`

Moved the current tag-related formal docs into that folder:

- moved `docs/dev/version_tag_governance.md` -> `docs/versioning/version_tag_governance.md`
- moved `docs/dev/baseline_2026-04-27_v0.1.0_tianshu_tag_note.md` -> `docs/versioning/baseline_2026-04-27_v0.1.0_tianshu_tag_note.md`

Updated existing entry docs and references:

- updated `docs/dev/upgrade_and_verify.md`
- updated `docs/review/doc_sync.md`
- updated `docs/review/document_directory_governance.md`
- updated related `change_notes`

## Why

The project now already has both tag governance and a formal first baseline tag note. Keeping those files under `docs/dev/` made them easy to lose among general execution docs.

Creating `docs/versioning/` gives the team a single place to find:

1. the actual tag specification
2. the current baseline explanation
3. future milestone and release notes

## Outcome

- tag-related docs now have a dedicated home
- future tag explanations and tag rules can continue accumulating in one folder
- project entry docs no longer point tag governance to a general-purpose dev folder
