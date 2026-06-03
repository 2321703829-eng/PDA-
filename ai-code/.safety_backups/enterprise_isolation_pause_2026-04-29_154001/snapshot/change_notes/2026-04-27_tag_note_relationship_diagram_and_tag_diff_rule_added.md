# 2026-04-27 tag note relationship diagram and tag diff rule added

## What Changed

Expanded the current baseline tag note with two new parts:

- module relationship diagram explanations
- historical optimization result summary across previous phases

Updated:

- `docs/versioning/baseline_2026-04-27_v0.1.0_tianshu_tag_note.md`

Also updated tag governance so future tags are expected to record the result delta from the previous tag:

- `docs/versioning/version_tag_governance.md`

## Why

The baseline tag note needed to work better for non-technical readers:

1. they need a one-glance structure view of how modules relate to each other
2. they need to understand what the previous optimization phases actually produced
3. future tags should not only describe the current state, but also clearly explain what changed since the last tag

## Outcome

- the baseline note now contains relationship diagrams that are easier to scan
- the baseline note now includes a phase-by-phase optimization summary
- future tag notes now have a clearer expectation to include “this tag vs previous tag” result tracking
