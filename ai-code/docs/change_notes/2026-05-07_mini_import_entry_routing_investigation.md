# 2026-05-07 mini import entry routing investigation

## Summary

During deployment verification we confirmed that the previously used local URL and the newly checked public URL are not the same delivery path.

## Findings

- The user's historical validation URL was `http://127.0.0.1:19070/odoo/action-527`.
- Local port `19070` is listened on by `ssh.exe` on the user's machine.
- The exact tunnel command is:
  - `ssh -L 19070:127.0.0.1:19069 tianshukeji@192.168.0.17`
- This means the local validation path is:
  - `127.0.0.1:19070` -> SSH tunnel -> `192.168.0.17:127.0.0.1:19069`
- The public server entry `http://8.166.131.218:7084` is a different chain.
- On `8.166.131.218`, port `7084` is owned by `frps`, not by the deployed Odoo container or local nginx.
- FRP dashboard inspection shows `7084` belongs to proxy `odoo19-dev`.
- The `8.166.131.218` host is running `frps` only; it is not running the matching `frpc` client for `odoo19-dev`.
- Therefore public `7084` currently forwards to another machine, not to the Odoo instance we just updated on `8.166.131.218`.

## Impact

- Container-local verification on `8.166.131.218` succeeded, but that does not make the public `7084` route usable for this feature.
- To match the user's actual validation path, the same code must also be deployed to the Odoo environment behind `192.168.0.17:19069`.

## Next Step

- Deploy the mini-program raw sheet import changes to the Odoo instance on `192.168.0.17`.
- Re-run `mini/admin template` smoke checks through the existing local tunnel entry at `127.0.0.1:19070`.
