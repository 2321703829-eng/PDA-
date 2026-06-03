# 2026-05-07 topic package root entries synced

## What changed

Synced the upstream topic-design entry docs so they now include the phase-6 backend performance package.

Updated:

- `docs/README.md`
- `docs/topic_design/README.md`

## Why

The topic packages were already expanded to include `六期后端性能优化设计`, but the upstream `docs` entry chain still only exposed the earlier set of packages.

Without this sync, the package would exist in the topic root but still be under-exposed from the main docs entry path.

## Outcome

The `docs` side topic-design entry chain now stays aligned with the actual package inventory under `专题设计/`.
