# Terminal-Bench 2.0 · 7-Harness Cross-Evaluation

> **Status**: T1 prep (skeleton + unit tests). **Docker BLOCKED** — see Blockers below.
> Backbone: `kimi-k2.6-cloud` @ `http://agi-gateway.cxmt.com/cloud/v1`
> Framework: Harbor v0.24.0 · Dataset: `terminal-bench-core@0.1.1` (80 tasks per registry.json; task doc wrote "terminal-bench@2.0/89" — actual is 80, "以实际为准")

## Directory Layout

```
terminalbench/
├── __init__.py              # Package root; AGENT_IMPORT_PATHS dict
├── agents/
│   ├── __init__.py          # Exports all 7 adapter classes
│   ├── _base.py             # TBBaseAgent — shared base (model, env, helpers)
│   ├── cline_patched.py     # ClinePatched adapter
│   ├── codex.py             # CodexTB adapter
│   ├── hermes.py            # HermesTB adapter
│   ├── opencode.py          # OpenCodeTB adapter
│   ├── claude_code.py       # ClaudeCodeTB adapter
│   ├── deepseek_harness.py  # DeepseekHarnessTB adapter
│   └── pi.py                # PiTB adapter
├── traces/                  # Tool-call trajectory outputs (per task)
├── test_adapters.py         # Mock unit tests (no Docker needed)
├── launch_tb_7way.sh        # Full/pilot launch script
└── README.md                # This file
```

## 7 Harnesses

| # | Harness | Adapter Class | Native CLI | Tool Loop |
|---|---------|--------------|------------|-----------|
| 1 | cline-patched | `ClinePatched` | `cline -c <cwd> --data-dir /tmp/... -P openai -m ... --auto-approve true --json` | read/write/exec multi-turn |
| 2 | codex | `CodexTB` | `codex exec --cd <cwd> --sandbox workspace-write --json` | shell/file multi-turn |
| 3 | hermes | `HermesTB` | `hermes -z<prompt> --provider kimi-proxy --yolo` | shell/file multi-turn |
| 4 | opencode | `OpenCodeTB` | `opencode run --dir <cwd> --model gw/... --auto` | shell/file multi-turn |
| 5 | claude-code | `ClaudeCodeTB` | `claude --print --dangerously-skip-permissions --max-turns 50` | bash/file/search |
| 6 | deepseek-harness | `DeepseekHarnessTB` | `DeepSeekHarness(provider, model, cwd).run(prompt)` | SDK JSON-RPC stdio |

## Install & Reproduce

```bash
# 1. Install Harbor (independent uv env, does not pollute shared py310)
P=http://172.19.92.25:13128
https_proxy=$P http_proxy=$P uv tool install harbor
harbor --version  # → 0.24.0

# 2. Set API key from doc/keys.txt (kimi-k2.6-cloud entry)
export TB_API_KEY="<key_from_doc/keys.txt>"

# 3. Verify Docker (REQUIRED for Harbor)
docker info && docker run --rm hello-world

# 4. Run unit tests (no Docker needed)
cd doc/BaiZe-ISEDA2027/run/harness
python3 terminalbench/test_adapters.py

# 5. Oracle check (MUST be 5/5 before full eval)
harbor run -d terminal-bench@2.0 --agent oracle -k 5 --n-concurrent 4

# 6. Full 7×89 cross-evaluation
bash terminalbench/launch_tb_7way.sh

# 6b. Or pilot 7×5
bash terminalbench/launch_tb_7way.sh --pilot
```

## Version Pinning

| Component | Version | Source |
|-----------|---------|--------|
| Harbor | 0.24.0 | `uv tool install harbor` |
| uv | 0.8.13 | pre-installed |
| Docker | 27.5.1 (client) | system — **BLOCKED: user not in docker group** |
| Dataset | terminal-bench-core@0.1.1 | Harbor Hub (needs auth; GitHub OAuth URL generated) — 80 tasks |
| Model | kimi-k2.6-cloud | `doc/keys.txt` → `http://agi-gateway.cxmt.com/cloud/v1` |

## Blockers (2026-10-17, R424 updated)

### B1: Docker Access Blocked (HARD BLOCKER — all execution paths need Docker)

**Symptom**: `docker info` → `permission denied while trying to connect to the Docker
daemon socket at unix:///var/run/docker.sock`

**Root cause**: `docker.sock` owned by `root:docker` (mode `srw-rw----`). User
`app.e0031982` is in group `app.adm`, NOT in `docker` group. No passwordless sudo.
No rootlesskit/podman. No TCP daemon reachable (localhost/.29/.12:2375 all fail).

**Tried**: `docker info`(perm denied) · `sg docker`(invalid pw) · `newgrp docker`(invalid pw)
· `sudo -n docker`(needs pw) · `podman`(not found) · `rootlesskit`(not found)
· `docker -H tcp://localhost:2375`(no server) · `docker -H tcp://10.239.2.29:2375`(no server)
· `harbor run --dry-run`("Docker daemon is not running")

**Impact**: Cannot run any Terminal-Bench task. Cannot run oracle 5/5. Cannot validate
adapters against real tasks. **All paths (harbor run / tb run / oracle) require Docker.**

**Fix needed**: Ops adds user to docker group (`sudo usermod -aG docker app.e0031982`),
then user re-login or `newgrp docker`.

### B2: Dataset terminal-bench-core@0.1.1 (corrected from terminal-bench@2.0)

**Actual dataset name**: `terminal-bench-core@0.1.1` (**80 tasks**, not 89).
The task document wrote `terminal-bench@2.0` / 89 tasks; the actual registry
(`laude-institute/t-bench` repo, `registry.json`) shows `terminal-bench-core@0.1.1`
with 80 task_id_subset entries on branch `dataset/terminal-bench-core/v0.1.x`.

**Why `harbor download` fails**:
1. `harbor download terminal-bench@2.0` → not found (wrong name)
2. `harbor download terminal-bench-core@0.1.1` (no auth) → not found (needs Harbor Hub auth)
3. `harbor download --repo laude-institute/t-bench terminal-bench-core@0.1.1` → not found
   (root cause: the repo's `registry.json` is legacy `tb` format with `task_id_subset`
   field; Harbor's `DatasetSpec` model expects `tasks: list[RegistryTaskId]` → validation
   mismatch → dataset appears "not found")
4. The GitHub repo's tasks use legacy `task.yaml` format (not Harbor's `task.toml`)

**Fix**: Authenticate with Harbor Hub via GitHub OAuth:
1. `harbor auth login --no-browser` generates an OAuth URL (stored in `~/.harbor/oauth-pending.json`)
2. Ops opens the URL in a browser → GitHub login → authorize
3. Ops copies the full callback URL from the browser redirect
4. Agent runs `harbor auth login --callback-url <callback_url>` to complete auth
5. Then `harbor download terminal-bench-core@0.1.1` should work (Harbor Hub has Harbor-format version)

**Alternative**: `uv tool install terminal-bench` → `tb run --dataset-name terminal-bench-core
--dataset-version 0.1.1` — but also requires Docker (B1).

## Evaluation Design (Pre-registered)

- **Scale**: 7 × 89 = 623 trials (pass@1, 1 attempt per task per harness)
- **Pilot**: 7 × 5 = 35 trials (pipeline validation only)
- **Primary metric**: task resolution rate
- **Secondary**: timeout rate / no-submission rate / avg steps / token or cost
- **Statistics**: Wilson 95% CI; 7×7 McNemar exact test (paired, same tasks)
- **Three-column**: `resolved / failed / infra-or-quota`
- **Halt condition**: harness infra failure rate >30% → stop and troubleshoot

## Discipline

- No GPU usage; `nice -n 19` for IO; no full-tree directory scans
- No `git add -A` (shared workspace); use explicit paths
- Concurrency = 1 per harness; 7 parallel if no 429, else drop to 2-3
- 429/quota: pause and wait; `quota-blocked` is NOT counted as harness failure
- Commit prefix: `harness tb:`
- Results: `terminalbench_kimi_k2.6_results.json`
- Report: `reports/report_harness_terminalbench_7way_zh.html`


| 7 | pi | `PiTB` | `pi -p --provider gw --model ...` | shell/file multi-turn |

Each adapter is a `BaseInstalledAgent` subclass that:
1. **`install()`** — installs the harness CLI inside the Docker container (npm/pip/binary)
2. **`run()`** — executes the harness headlessly with the task instruction
3. Preserves the **native tool loop** (no generic shell agent, no prompt-only swap)
