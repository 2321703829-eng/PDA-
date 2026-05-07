# 2026-05-07 design document governance baseline landed

## What changed

Established a first formal baseline for design document governance across `ai-code/docs/` and `ai-code/专题设计/`.

Added new formal entry layers:

- `docs/spec/README.md`
- `docs/spec/design_document_governance_spec.md`
- `docs/topic_design/README.md`
- `docs/archive/README.md`

Updated core entry and governance documents:

- `docs/README.md`
- `docs/review/checklists/document_directory_governance.md`
- `docs/review/checklists/doc_sync.md`

## Why

The repository already had partial directory governance, but the rules were still spread across review and dev notes.

This round formalized the governance baseline around five required aspects:

1. directory governance
2. document classification
3. effective-document rules
4. naming rules
5. change-loop synchronization

It also filled the missing formal layers for:

- `spec`
- `topic_design`
- `archive`

## Outcome

The design document system now has an explicit 7-layer governance view:

- `context`
- `architecture`
- `spec`
- `topic_design`
- `review`
- `change_notes`
- `archive`

And the repo now has a single formal governance entry for design-document standardization:

- `docs/spec/design_document_governance_spec.md`

## Sync completed

This round synced:

- main docs entry
- governance checklist
- doc sync checklist
- topic design entry
- archive entry

No large-scale historical file renaming or physical archive migration was performed in this round.
