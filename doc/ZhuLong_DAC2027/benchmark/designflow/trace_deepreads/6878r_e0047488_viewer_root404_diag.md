# deepread: 6878r — e0047488 @ hfeg0plg54 — DRC QA viewer root 404 diagnosis

- **session**: 1794791688016_6878r.messages.json (1.04 MB, 405 msgs)
- **user/host**: e0047488 @ hfeg0plg54 (10.129.35.73), also seen on hfeg0plg85 (10.129.8.136)
- **mc=149**, keywords drc:498;pex:32;synopsys:12;aether:4 — domain **physical_verify** (DRC QA tooling)
- **tools used**: run_commands×198, read_files×12, editor×8, kill×1, grep×1 (cline agent w/ skills+RAG+Sandbox MCP)
- **cwd**: /home/e0047488/qa_pattern_v0.1_1029/ (DRC QA test-pattern editor project)

## 真实任务（2 条 user_input）

- U#1: `test` (greeting)
- U#2: `viewer视图界面没有正常加载，提示{"detail":"Not Found"}` — 报告 DRC QA viewer 的 web UI 根路径返回 404

## agent 诊断链路（核心事实）

1. 项目 `/home/e0047488/qa_pattern_v0.1_1029/` 是 DRC QA 测试图形编辑器（FastAPI viewer + spec_engine + drcqa_kb）。
2. 端口 **45646** 上的 viewer server 是**另一个用户 `e0023936`** 从 `/home/e0023936/devops/eda_data_bridge/qa_pattern_v0.1_1029/` 启动的（PID 3704753）。
3. `curl http://localhost:45646/` → **404 `{"detail":"Not Found"}`**（根路径静态文件挂载失效）。
4. `curl http://localhost:45646/api/rules` → **正常返回 240 条规则**（API 端点工作）。
5. `readlink /proc/3704753/cwd` → `/home/e0023936/devops/eda_data_bridge/qa_pattern_v0.1_1029/`。
6. `/home/e0023936/` 是 NFS 挂载卷，**100% 满（20G/20G）** → e0023936 路径下 `viewer/web/` 目录**丢失** → FastAPI `StaticFiles` 挂载找不到文件 → 根路径 404。
7. 我们的项目 `/home/e0047488/qa_pattern_v0.1_1029/viewer/web/` 完整存在。
8. **次要问题**：默认 `python3` 是 3.7.4，server.py 用了 `str | None` 类型语法（需 Python 3.10+）→ 启动新 server 时 `SyntaxError`。可用 `/apps/local/python/python-3.10.5/bin/python3` 或 `/home/e0023936/miniforge3/envs/py310_env/bin/python3`。
9. `list_rules()` 首次加载 240 条 YAML 约需 20s（之前 timeout 太短误判为 hang）。
10. `DRCQA_CORE` 环境变量须指向 `/home/e0047488/qa_pattern_v0.1_1029/kb/drcqa-kb`。

## 根因分类（两类，都来自同一 trace）

- **A 类（主线）**: `wrong_cwd_missing_static` — server 从错误 cwd 启动 + 静态目录丢失 → 根路径 404，API 正常。
- **B 类（支线）**: `python_version_mismatch` — 默认 python3=3.7 遇 `str|None` SyntaxError → server 启动即崩，API 拒绝连接。

## case 设计（EDA-Eval-DesignFlow-ViewerRoot404Diag-001）

- **交付**: `viewer_diag.py` — 读证据目录（curl_root/curl_api/ps_server/proc_cwd/ls_viewer_web/df_home/python_version/server_log 等 evidence 文件），输出结构化 JSON 诊断：`root_cause / server_port / api_ok / culprit_user / culprit_cwd / missing_path / python_version / error_signature / recommended_fix / evidence_cited`。
- **config_a（public，主线）**: 来自真实 trace 的证据（45646/e0023936/错 cwd/web 丢/NFS 满/python 3.10 OK）→ root_cause=`wrong_cwd_missing_static`。
- **config_b（hidden，支线）**: 同一 trace 家族的另一根因（45647/正确 cwd/web 存在/df OK/python 3.7 SyntaxError）→ root_cause=`python_version_mismatch`。B 与 A 在根因类别、端口、用户、cwd、python 版本、API 可用性上全不同。
- **check()**: 真跑 `python3 viewer_diag.py <evidence_dir>` on B，断言 JSON 结构 + B 的具体值 + cross-input guard（在 A 上须得 A 的值，反硬编）。k=14。
- **negatives**: empty / print_only / hardcode_a / delete_core 全 FAIL（distinct 层）。
