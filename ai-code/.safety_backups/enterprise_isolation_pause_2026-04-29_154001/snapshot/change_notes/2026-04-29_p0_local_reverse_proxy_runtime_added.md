# 2026-04-29 P0 Local Reverse Proxy Runtime Added

## Background

The local `P0` validation already had dedicated tenant/database runtime entries, but it still lacked an independent reverse-proxy-style entrance for a more formal route validation pass.

## What changed

- added a lightweight local host-based reverse proxy runtime:
  - `.runtime/tenant_reverse_proxy.py`
- added a startup helper script:
  - `.runtime/start_tenant_reverse_proxy.ps1`

Current intended local reverse-proxy mappings:

- `kebi.tianshu.test -> 127.0.0.1:8070`
- `dev.tianshu.test -> 127.0.0.1:8071`

The reverse proxy itself listens on:

- `127.0.0.1:8090`

## Purpose

- simulate a more formal independent entry layer before the Odoo runtime
- support a local `P0` validation pass closer to the later route architecture
- keep `tenant_kebi` and `odoo_logistics_dev` clearly separated at the proxy layer
