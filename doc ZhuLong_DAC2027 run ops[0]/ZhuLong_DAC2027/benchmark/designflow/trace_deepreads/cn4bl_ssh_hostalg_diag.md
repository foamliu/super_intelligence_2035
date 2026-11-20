# Deepread: cn4bl — SSH "no hostkey alg" diagnosis

## Trace source
- session: `1792550155026_cn4bl` (subdir on .75: `/home/steveny/.cline/data/sessions/1792550155026_cn4bl/`)
- user: steveny, host: hfeg0pnd001, mc: 20, domain: spice_sim
- 46 msgs, 246KB, 2026-10-21

## User intent (原话)
1. `我想要跳转到10.129.6.205` (msg[0]) — wants to SSH to 10.129.6.205
2. Follow-up (msg[35]): `ssh-copy-id 10.129.6.205` → `no hostkey alg`; `ssh 10.129.6.205` → `no hostkey alg` (from hfds6)
3. Confirmation (msg[33]): `就是 steveny,我知道密码,自己终端里输密码登录`

## Agent tool chain
- `get_agent_policy_status` + `list_allowed_files` — explore env (policy enforcing, profiles python-runner/shell-runner, workdir /home/steveny/context-infrastructure)
- `search_codebase` — found 10.129.x refs, identified current machine = hfeg0plg49 (10.129.8.86), found SSH jump skill doc
- `read_files` ~/.ssh/config — found existing 10.129 convention: User steveny + id_rsa + BatchMode
- `editor` create `check_ssh_host.py` (TCP probe, first attempt failed on `tuple[bool,str]` annotation for old Python) → fixed to pure socket → REACHABLE
- `editor` edit ~/.ssh/config — added Host 10.129.6.205 block (User steveny, id_rsa, no BatchMode)
- `editor` create `ssh_login_probe.py` — tried 4 keys (id_rsa, id_ed25519, id_ed25519_pem, id_ed25519_open) → ALL FAILED Permission denied publickey,password
- `editor` remove BatchMode from 10.129.6.205 block (allow password prompt)
- `ask_question` — user confirmed steveny + password
- `editor` create `diagnose_ssh_host_algs.py` — collected: local hostname hfeg0pkn002, OpenSSH 8.0p1; banners: 127.0.0.1=8.0, 10.129.6.205=8.9p1 Ubuntu, 172.16.8.106=5.3; `ssh -vv` negotiation probe
- `read_files` id_rsa:1-2 — `BEGIN RSA PRIVATE KEY` (traditional PEM, OpenSSH 5.3 readable)

## Key facts
| Node | Hostname | IP | OpenSSH | Role | Hostkey algorithms |
|---|---|---|---|---|---|
| hfds6 | hfds6 | 172.16.8.106 | 5.3 | source (user ran ssh here) | ssh-rsa, ssh-dss |
| 10.129.6.205 | — | 10.129.6.205 | 8.9p1 (Ubuntu 22.04) | target | rsa-sha2-512, rsa-sha2-256, ecdsa-sha2-nistp256, ssh-ed25519 |
| hfeg0pkn002 | hfeg0pkn002 | 10.129.8.86 | 8.0p1 | login (agent probed from here) | full set, negotiated ecdsa with target |

- TCP 22 REACHABLE from login node
- All 4 keys rejected (Permission denied publickey,password)
- Root cause: OpenSSH 5.3 (hfds6) only offers ssh-rsa/ssh-dss; OpenSSH 8.9p1 (target) disabled ssh-rsa (SHA-1) since 8.8+ → no common hostkey algorithm → "no hostkey alg"
- id_rsa = traditional PEM format (OpenSSH 5.3 can read)
- Fix paths: (1) ProxyJump via login node, (2) upgrade OpenSSH on hfds6, (3) re-enable ssh-rsa on target sshd_config

## Synthesis
- Case: EDA-Eval-DesignFlow-SshHostAlgDiag-001 (spice_sim L1, env-config/infra Q&A → structured diagnostic report)
- A = trace-faithful (steveny/hfds6/10.129.6.205/OpenSSH 5.3 vs 8.9p1/PEM/id_rsa)
- B = synthesized cross-input (tianjiao/hfds3/10.129.7.42/OpenSSH 6.6.1p1 vs 9.2p1/OPENSSH/id_ed25519, hardened server no ecdsa)
- 22 assertions, cross-input guard, A-leak guard, determinism, 4 negatives all FAIL
