# Deepread: ogspt — junxu virtuoso-cli python 环境跨机修复

- **session**: 1789435102785_ogspt.messages.json
- **user/host**: junxu @ hfeg0plg79 (10.129.8.122)
- **mc**: 517 (keywords: virtuoso:2113; schematic:166; cadence:93; binary:39; cellview:16; rtl:7; dbcreaterect:6; dbopencellviewbytype:2; analog:2)
- **trace 体积**: 329 msgs / 969 KB
- **选料轮**: r1068 (shard D, mc≥5 池, fresh)
- **domain 判定**: schematic_netlist（关键词主导 virtuoso/schematic；实际任务形态=env-config/debug-Q&A，属 §0 合法真实意图）
- **trace_source**: real, junxu@hfeg0plg79, session_file=1789435102785_ogspt.messages.json, match_count=517

## 用户真实意图（按时间线）

1. **U#0 (m[0])**：参考 `/home/junxu/.cline/skills/brainstorming` 和 `writing-for-agents`，检查当前 skill 有无可优化处；关于 grilling 部分，不要假设用户装了这个 skill，直接内化到当前 skill。
2. **U#39 (m[39])**：在另一台服务器 setup 时遇到 `[virtuoso-cli:stderr] python3: GLIBC_2.15/2.14/2.17 not found`（daemon exited status=1）——问 skill 能否正确处理 python 环境问题。
3. **U#117 (m[117])**：用户已完全理解源码，列出三个核心缺陷 + 优化方案：
   - **缺陷 1**：`skill_bridge.il` 的 `RBStart()` (L108) 硬编码 `python3`，忽略 `RB_PYTHON_PATH` 配置 → 修复：改 `%s` 传 `RBPython`。
   - **缺陷 2**：`setup_cmd.py` 在 CLI 主机选 Python，但 daemon 在 Virtuoso 主机跑（不同机，共享 NFS 家目录不共享系统目录）→ 修复：在 NFS 家目录部署 `find_python.sh` wrapper，任意主机自动找可用 Python。
   - **缺陷 3**：（用户消息被截断，第三缺陷未完整显示，从后续可知涉及 pip 安装方式）
4. **U#164 (m[164])**：① 脚本修复后 skill.md 不需要提及；② 能否将 virtuoso-cli 从 pip 安装（这样不需要 wrapper）。
5. **U#271 (m[271])**：你能在当前机器上用 pip 安装吗？我试一下。
6. **U#285 (m[285])**：这个仓库的 change 已经很久没有 commit 了，你处理一下。

## Agent 工具链（核心）

- `run_commands` ×80, `editor` ×47, `read_files` ×39, `search_codebase` ×4
- 编辑的关键文件：
  - `block-design/SKILL.md` (m[7]) — 内化 grilling
  - `virtuoso-cli/scripts/virtuoso_cli/skill_bridge.il` (m[50]) — RBStart() 改用 RBPython
  - `virtuoso-cli/scripts/virtuoso_cli/cli.py` (m[50])
  - `virtuoso-cli/scripts/virtuoso_cli/setup_cmd.py` (m[50]) — 部署 find_python.sh wrapper
  - `virtuoso-cli/SKILL.md` (m[63])
  - `virtuoso-cli/scripts/tests/test_cli.py` (m[91])
  - `virtuoso-cli/scripts/pyproject.toml` (m[171]) — 后删除（pip install 方案）
  - `virtuoso-cli/scripts/virtuoso-cli.sh` (m[171])
  - `virtuoso-cli/scripts/setup.py` (m[236]) — 改为 pip 可装
- 关键测试命令：
  - `cd scripts && python3 -m pytest tests/ -x`
  - `env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3.6 -c '...'`（模拟 GLIBC 坏境）
  - `pip install --target /tmp/vcli-test-py36 ...`（验证 pip 装包）
  - `bash tests/run_tests.sh`

## 任务最终交付

- **virtuoso-cli 仓库** 2 个 commit：
  - `e305d3d` — `schematic API: add_pin stub orientation, connect_by_name label improvements, wire midpoint tapping`（之前的 schematic API 增量）
  - `d2b800a` — `fix: Python environment handling — cross-host wrapper, pip install`（本轮核心修复）
- **block-design**：无独立 git 仓库，未提交。

## 可合成 case 的方向（供下一轮合成参考）

任务形态=env-config/debug-Q&A。可重构成「修一个有 bug 的 virtuoso-cli skill 跨机 python 启动」：

**A (visible, SUT 可见)**：含 bug 的 `setup_cmd.py`（机器特定路径）+ `skill_bridge.il`（硬编码 python3）+ 一组 mock python 环境（A 机：/usr/bin/python3 GLIBC 坏 + /usr/bin/python3.12 好）。

**B (hidden, SUT 不可见)**：另一组 mock python 环境（B 机：python3.10 好 + python3 坏 + python3.11 在 /usr/local/bin）+ 期望 wrapper 选 python3.10、RBStart 用配置变量。

**A' (hidden, anti-hardcode)**：第三组 mock 环境（A' 机：所有 python3.* 都 GLIBC 坏，只有 /opt/python3.11 可用）+ 期望 wrapper fallback 到 /opt/python3.11。

**Deliverable**: zip 含 `setup_cmd.py`、`skill_bridge.il`、`find_python.sh`、`run_tests.log`。

**check.py 牙齿（≥14 断言）**：
- a 候选 setup_cmd.py 在 B mock 环境跑 exit 0
- b 部署 find_python.sh 到 NFS 家目录路径（含 $HOME/.cline/...）非 /usr/bin
- c find_python.sh 内容含 `unset PYTHONHOME PYTHONPATH`
- d find_python.sh 内容含 version 检查（sys.version_info >= (3,8)）
- e find_python.sh 跳过 GLIBC 坏的 python 选 python3.10
- f skill_bridge.il RBStart() format 串含 `%s` 占位（非字面 "python3"）
- g RBStart() 传入 RBPython 变量
- h 候选在 B 跑产 run_tests.log 含 PASS
- i-j A' 交叉：候选在 A' 跑 exit 0（A' python 全坏只有 /opt 可用）
- k A' wrapper 选 /opt/python3.11
- l A' 输出含正确 A'-gold token（判分器独立重算）
- m A' 输出不含 B 拓扑（python3.10）
- n 3-seed 确定性
- o 候选不污染 SUT workdir（不留 __chk）

**风险**：需在沙盒构造 mock python 二进制（或用脚本模拟 GLIBC 坏境），fixture 较重；合成工作量≈1.5 轮。

## 处置

- **本轮 (r1068) 不合成**：trace 体积大（329 msgs/969KB）、任务涉及多文件跨机 mock 环境构造，合成需 ≥1 轮专门深读+合成，40 min 预算内强行合成会产 weak case（违反 §4「有牙」+ 顶部令「宁可报 GAP 也不要漏报」精神应用于造题=宁可慢造不造 weak）。
- **台账处置**：`mark --status parked --note "complex multi-file cross-host py-env debug, needs dedicated synthesis round, deepread done"`（不重复捡；下一轮造题时若选此料先恢复 claim 状态）。
- **DEBT**: 1 deepread 未合成（ogspt），下一轮或下下轮合成。
