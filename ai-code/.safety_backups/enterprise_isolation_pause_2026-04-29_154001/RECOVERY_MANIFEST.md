# Enterprise Isolation Recovery Manifest

## Purpose

This backup package is the single recovery anchor for the paused enterprise-isolation work.

It was created before the workspace was reset back to `origin/feat-text`, so it preserves:

- code snapshot
- design-doc snapshot
- runtime config snapshot
- database dumps
- git state records

## Included Parts

### 1. `snapshot/`

File-level snapshot of the enterprise-isolation related working tree at pause time.

It includes:

- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_web`
- enterprise-isolation topic docs
- change notes
- `.runtime`
- `odoo_local.conf`

Use this directory when restoring code and document state.

### 2. `db_dumps/`

Database dumps saved at pause time:

- `odoo_logistics_dev.dump`
- `tenant_kebi.dump`

Use these when restoring runtime database state.

### 3. Git state files

- `branch.txt`
- `head.txt`
- `origin_feat_text_head.txt`
- `git_status_short.txt`
- `git_status_full.txt`
- `tracked_changes.patch`

Use these for:

- confirming pause-time branch and commit
- comparing restored state with pause-time status
- reapplying tracked diffs if needed

## Recommended Recovery Order

1. Create a dedicated restart branch.
2. Restore code and docs from `snapshot/`.
3. Restore databases from `db_dumps/` if runtime state is needed.
4. Rebuild local runtime entry points.
5. Continue work from the enterprise-isolation topic docs.

## Important Warning

Do not treat isolated files from this package as independent truth sources.

Use the whole package together:

- snapshot
- db dumps
- git state records

That is the safest way to restart the enterprise-isolation work.
