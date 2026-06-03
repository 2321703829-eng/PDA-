# 2026-05-07 topic package master doc lists added

## What changed

Added package-level master document lists and status markers for the current topic-design packages.

Updated:

- `专题设计/README.md`
- `专题设计/前端设计/README.md`
- `专题设计/仓管设计/README.md`
- `专题设计/企业隔离设计/README.md`
- `专题设计/高并发优化设计/README.md`
- `专题设计/六期后端性能优化设计/README.md`

Added:

- `专题设计/前端设计/主文档清单.md`
- `专题设计/仓管设计/主文档清单.md`
- `专题设计/企业隔离设计/主文档清单.md`
- `专题设计/高并发优化设计/主文档清单.md`
- `专题设计/六期后端性能优化设计/主文档清单.md`

Also rewrote:

- `专题设计/六期后端性能优化设计/03_模板与样例/README.md`

## Why

The repo already had topic-package roots, but the packages were still uneven in usability:

- some had package README only
- some had current recommended docs but no single master list
- some had no clear `active / draft / archive` interpretation
- the phase-6 backend package was not yet fully integrated into the root topic entry

## Outcome

Now each current topic package has:

1. a package-level master document list
2. package README guidance for `active / draft / archive`
3. a clearer “read this first” path

The topic-design root entry now also includes the phase-6 backend package.
