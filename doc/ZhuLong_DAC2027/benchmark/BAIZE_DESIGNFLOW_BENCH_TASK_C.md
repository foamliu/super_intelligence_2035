# BAIZE_DESIGNFLOW_BENCH_TASK.md — 设计流 Benchmark 任务书（2026-10-30 重构版）

> ## 🚀 2026-11-26 运维令 · 开始判分契约改造（check_static/check_live 拆分） · 最高优先（Lite-500 全绿后接续）
>
> **背景**：Lite-500 已 4 shard 全绿（507/507），zhulong 正在跑 3-run 验收。8670 服务已修复（16 worker 并发秒级），L2.live 实跑通路就绪。现在开始判分契约改造。
>
> **完整指南（每轮先读）**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`
>
> **三个优先级**：
> - **P1（立即）**：修复 pilot 12 case 的 judge_layers 声明 + check_live（部分在 Lite-500 修复中丢失）。清单见指南 §2 表格。
> - **P2（P1 完成后）**：扩展本 shard 真正调 EDA 的 case 到 L2.live（加 check_live + `judge_layers=["L0","L1","L2.live"]`）。
> - **P3（与 P2 并行）**：mock case 声明 `judge_layers=["L0","L1"]`（不需要拆 check_static，框架已兼容旧式 check() 回退）。
>
> **改造手法**：非侵入包装（原 `check` → `_check_static_impl` 一字不动 + `check_static` 包 try/except 收口三元组 + `check_live(sess)` 新增 + `check` 兼容包装）。模板见指南 §3。
>
> **自验**：`SKIP_RUN=1 eval/run_one.sh <task_id> --shard <shard>` → PASS；P1/P2 case 再跑 `eval/run_one.sh <task_id> --shard <shard>` 验 L2.live 实跑 PASS。
>
> **心跳**：MEMORY 顶部一行 `CONTRACT: P1=<done>/<12> · P2=<n> L2.live · P3=<n>/<total> judge_layers`
>
> **优先级**：P1 > P2 > P3。造新题让位给 P1/P2，P3 可与造题并行。体积超限先归档已闭合的旧令（Lite-500 令已完成，可搬 ARCHIVE）。



> ## 🥇 2026-11-24 22:0x 用户令 · 4 shard 优先修 Lite 集（500） · 最高优先（排期覆盖造题/扩池/治理）
>
> **用户原话**：「安排 designflow 4 shard 优先修复 lite 集」。**完整规格（每轮先读）**：`doc/ZhuLong_DAC2027/benchmark/BAIZE_DESIGNFLOW_LITE_FIX_ORDER.md`。
> **执行**：本 shard 只修 `cases/C/` 且属于 Lite 清单的条目，判据 **L0–L5 全 PASS**；**造新题/扩池/治理一律让位**；每轮 `designflow/lite_health_C.tsv` 增量 + MEMORY 顶部一行 `LITE_FIX: C=<green>/<n> · P0 余 <m>`。
> **验收**：4 shard 合计 **500/500 全绿**（`retired_broken=0`，退一补一保持 500），再由 zhulong 用同一清单跑 1 次 3-run（broken=0）才入账。


> ## 🚨 2026-11-23 运维令 · 停止追加 jsonl，改写 cases/ 文件 · 最高优先（覆盖本文件中一切关于 jsonl 的指令）
>
> **用户令**：「执行修复」→ 发现 agent 每次唤醒加载的是 `BAIZE_DESIGNFLOW_BENCH_TASK_<shard>.md`（本文件），不是 `agent_workspace/BAIZE_DESIGNFLOW_BENCH_TASK.md`。本文件中所有「追加 jsonl / 只往 X.jsonl 追加 / DoD 写进 jsonl / 你的 case 只追加到 X.jsonl」指令均已被本令覆盖。
>
> **立即生效**：
> 1. 📝 新增 case 时**只写** `benchmarks/EDA-Eval-DesignFlow/cases/<shard>/<task_id>.json`（一个 JSON 文件），不要碰任何 `*.jsonl`。
> 2. 🚫 **不要 `git add` 任何 `*.jsonl`**（即使 `git add -f` 能绕过 .gitignore，也不要用）。jsonl 文件已物理删除，重建是违规。
> 3. 🚫 **不要用 `_append*.py` / `append_jsonl.py` / `build_jsonl_entry.py` 辅助脚本** append jsonl。新 case 直接用 `editor` / `write_to_file` 写 `cases/<shard>/<task_id>.json`。
> 4. ✅ **"dangling case"（cases/ 有但 jsonl 无）是正常状态**。jsonl 已不存在，不要"补 jsonl 条目"，不要把 cases/ 与 jsonl 对账。
> 5. 🔧 评测前 evaluator 自动调 `scripts/build_jsonl.py` 从 `cases/` 生成临时 jsonl。你不需要手动生成或维护 jsonl。
>
> **优先级**：本令 > 本文件中任何关于 jsonl 的指令 > loop shard 卡 > 任何前令。若本文件下方说「追加 jsonl / 只往 X.jsonl / DoD 写进 jsonl」，**全部忽略，按本令写 cases/ 文件**。

> ## 🔧 2026-11-24 运维令 · 判分契约修复 · 按需执行（与造题并行）
>
> **背景**：框架判分契约已修（commit `6c1a50ee9`），两条判分通路统一为严格契约：**仅 `return True` / `return {'pass':True}` / `return {'ok':True}` 算 PASS，其余一律 FAIL**。当前 ~70% check.py 的返回值形状不符合新契约（tuple/str/None/dict 非法键），在新契约下会被判 FAIL——即使交付件正确。
>
> **你要做什么**：
> 1. 📖 读契约规范：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/JUDGE_CONTRACT.md`（**先读这个文件**，里面有完整的 PASS/FAIL 定义 + 每种违规形状的修法示例）
> 2. 🔧 扫自己的 check.py 返回值，按契约修：tuple→`return True/False`，str→`return True/False`，无 return→补 `return True`，dict 非 pass/ok 键→加 `pass` 键
> 3. ✅ **只改返回值形状，不改断言逻辑、不改断言条数、不改判分严格度**
> 4. 🚫 不改 case 的 prompt / assets / hidden
> 5. 📝 修好的 case 在自己 MEMORY 记一行
>
> **优先级**：tuple 返回（最大类）> str > None/无 return > dict 非法键 > 辅助函数透传
>
> **自验**：`SKIP_RUN=1 eval/run_one.sh <task_id> --shard <你的shard>`，看 status.jsonl verdict=PASS
>
> **不需要改的**：已经 `return True`/`return False`/`return {'pass':True/False}` 的 case（~62%），不用动。
>
> **时间线**：立即开始，不等 ref 自验清单。每日看 zhulong 的 lite 500 × 3-run 体检报告确认进度。完成信号：连续 2 天 Pass@1 标准差收敛 + broken case 清单清零。

> ## 🔴 2026-11-21 17:0x 用户令 · **全部 4 shard：mc 阈值统一降到 5** · 最高优先

> **用户原话**：「4个shard mc都降为5吧，保持一致」

**配置已改好，直接生效**：`designflow/summary_stats.json` → `shard_mc = {"A":5,"B":5,"C":5,"D":5}`（`target_mc` 仍 10，全局分母口径不变）。`trace_ledger.py` L337-340 优先读 `shard_mc[<shard>]`，故 `--shard 
X
` 自动按 mc≥5 选料，**你无需改代码、无需改配置**。

**你要做的**：① 复算 `python3 designflow/trace_ledger.py --shard <你的shard> mc-matrix --src designflow/summary_1121.tsv --thresholds 5,10,15,20,30`，把 **mc5 / mc10 / touched / fresh** 写进 MEMORY；② **用 mc≥5 池选料造题**（§6 流程）；③ 每轮心跳报三数：**mc≥5 pool/touched/fresh · 本轮 peek 的本域 vs 跨域比例 · 本轮产出 case 数**。

**质量闸门一条不放松**（mc 降低 ≠ 标准降低）：k≥8、3 neg 全 FAIL、§4.9 三假 FAIL、hidden B、A 档自包含、真实 trace 溯源（`metadata.trace_source`）。🚫 不为凑数造 weak case；🚫 不改题/图/`check.py`、不动别 shard 文件、不 `git add -A`。

**跨域归属先判**（防串台）：本域 keyword 不主导的候选记一行交对应 shard，🚫 不自己造别域的题。

**止损**：若 mc≥5 连续 3 轮仍 0 case（且每轮真的 peek 过 ≥10 个本域 fresh），在 MEMORY 写「mc≥5 扩池实测无效 + 数据依据」并转做不依赖新候选的产出（§4.9 anti-hardcode 自查 / `test_rationale` 补断言清单 / ledger 治理）。

---

> ## 🎯 任务初衷（最高优先级 · 一切规则与之冲突时以本段为准）
>
> **基于真实 trace 创建评测用例，评价 agent 解决用户真实任务并交付结果的能力。**
>
> 由此推出的三条铁律：
>
> 1. **任务形态 = 用户意图**。真实用户在 trace 里想干什么，就造什么样的任务——查文档就造查文档，跑 DRC 就造跑 DRC，写脚本就造写脚本。**没有任何预设的题型清单、难度配比或层级配额可以否决一个真实用户意图。**
> 2. **交付结果 = 判分对象**。每道 case 的 `check()` 必须能区分「真的交付了用户要的东西」和「没交付」：断言独立可失败、退化提交（空壳/只打印期望/删核心逻辑）必须 FAIL、隐藏输入 B 防背题。
> 3. **真实性 = 唯一来源**。每条 case 必须能溯源到真实 trace（`metadata.trace_source{user, host, session_file, match_count, real_task_summary}`）；没有真实 trace 的 case 没有资格入库。
>
> **难度分布是观察对象，不是生产指标。** L1/L2/L3 只用于事后统计当前题库覆盖了什么，**不得用于限制新建 case**。**通过率同样是观察值**——由用户任务的真实难度与 agent 真实能力共同决定，如实测量即可，不为凑数字而挑题、改题、加难或降难。


> ## 🔍 2026-11-15 用户令 · 用新标准重审「已造的题」与「候选池」· **C 已收口**

> **用户原话**：「安排4线重新审视自己已经造的题和候选池，如果跟任务初衷有违背可以重做」

**✅ C 收口**：`intent_audit_C.tsv` **580/580 全 keep**（off_intent/over_constrained/downgraded 均 0）；`pool_reaudit_C.tsv` 可造 6 → **380**（+374 误杀复活，§二 C 域增益最大）。

**判据仍有效（造题时对照）**：难度配额、「只做 L2/L3」、「analysis-only 判 weak」**全部作废**；`analysis-Q&A`/`doc-search`/`debug-Q&A`/`env-config`/`flow-driving` **都是合法真实意图**；唯一排除标准 = ①无真实 trace ②`check()` 没牙。重做 ≠ 删了重来（新增 `-v2` 并说明改了什么）。

> 📦 原文见 git 历史与 `ARCHIVE_OPERATOR_DESIGNFLOW_C.md`。

## 0. 目标（一句话）

用 `.75` 内网 **698 台机 / 2,850 用户 / 52,698 会话（24,085 条 IC-EDA 命中）** 的真实 cline 轨迹，构建「设计流编排」评测集——**用户真实在做什么，就造什么样的题**，通过率如实测量、不设目标区间（见顶部「任务初衷」）。

## 1. 红线（不可协商）

1. **真实 trace 才有资格**：每条 case 必带 `metadata.trace_source{user, host, session_file, match_count, real_task_summary}`。没有真实 trace 的 case 一律删除，🚫 不许改个名字保留。
2. **不脱敏（全产物）**：`user` / `host` / `session_file` / `/home/<user>` 路径 / `prompt` / `attachments` / 深读笔记 / MEMORY **一律保留原值**；只有 **key / token / 密码** 需掩码。🚫 prompt 里出现"脱敏""不要出现真实用户名"字样视为违规。
3. **per-case 文件**（运维令 2026-11-23 覆盖）：每条 case 写 `benchmarks/EDA-Eval-DesignFlow/cases/<shard>/<task_id>.json`（一个 JSON 文件）。🚫 **不要碰任何 `*.jsonl`**（jsonl 已物理删除，是 build 产物，由 `scripts/build_jsonl.py` 从 cases/ 生成）。
4. **只读纪律**：对 698 机只 `find`/`ls`/`cat`/`head -c`/`awk`/`python3` 只读；🚫 写目标机、🚫 `rm`/`tee`/`>`；🚫 本机自扫；🚫 lineage 自审计 / §X 递归。
5. **git 双仓**：workspace → `super_intelligence_2035` **main**；用例产物 → `EDA-Flow-Bench` **master**；🚫 `git add -A`。
6. **体积**：本 TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限按 §8 归档（原文搬 ARCHIVE，留 1 行指针）。

## 2. 环境速查

| 项 | 值 |
|:--|:--|
| workspace | `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/` |
| 用例仓库 | `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（jsonl / assets / reference） |
| 历史快照 | `EDA-Flow-Bench/agent_workspace/designflow/`（bench_v0.1~v0.50，只读，不迁） |
| 运行时 cwd | `/nasdata/app.e0031982/code/EDA-Flow-Bench/` |
| 沙盒入口 | `eda_flow` MCP `http://127.0.0.1:18891/mcp` → `.75`（`hfhds201` / `10.129.32.75`）`run_commands`·`run_code`·`read_file`·`write_file` |
| 扫描结果 | `.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`（列：`ip host user session_file match_count keywords tools`） |
| 评测框架 | `./RUN_EVAL.sh --design-flow` / `--design-flow-agent`；`scripts/run_design_flow_batch.py`；`config.yaml`；`docs/design_flow_session_backend.md`（§3 接口 / §9 判分两步）；`docs/设计流Benchmark-{测试用例编写指南,框架改进设计文档}.html` |
| pi（被测） | `pi` 1.4.0，provider `cxmt` / `deepseek-v4-pro-cloud`，已配 `eda_flow` MCP。调用：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`（Node 22 需在 PATH：`export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH`） |

**`.75` 可达性判据（最高优先 · 凌驾于本节一切 ssh 提法之上）**

- **`.75` 可达 = `eda_flow` MCP 工具能正常调用并返回**（`open_session` / `run_commands` / `run_code`）。**不是** `ssh 10.129.32.75` / `ping` / DNS。
- `ssh 10.129.32.75` 超时**只代表「本机直连 .75 的 22 端口不通」**，**不得**据此判「`.75` 不可达」，🚫 更不得据此把整轮转成「止损轮」或跳过 sim 真跑。
- **实测（2026-11-25）**：`eda_flow` MCP `open_session` 秒级、`run_commands` 秒级、`run_code pyAether` ~30s 全部正常；`.75`（`hfhds201`）上 `hspice` / `hspice64` / `finesim` 均在 PATH（`/apps/synopsys/...`），sim 类 case 可直接走真模拟器抓真值，无需 self-contained mock。
- **连通性自测命令**（写到 MEMORY 顶部一行作证据）：
  ```python
  import sys; sys.path.insert(0, '/nasdata/app.e0031982/code/EDA-Flow-Bench/scripts')
  from eda_flow_judge import EDASession
  with EDASession(task_id='reach', eval_id='reach', timeout=60) as sess:
      print(sess.run_commands(["hostname; which hspice finesim; echo OK"]))
  ```
- 失败时**逐层区分**：MCP server 未启动 / 隧道断 / 认证失败 / 超时 / 工具缺失，🚫 不得只写「不可达」了事。

**命令模板（扫描 698 台机 cline trace · 经 eda_flow run_commands 在 .75 上跑 · 不是 .75 连通判据）**
```bash
# 以下 ssh 是在 .75 上经 eda_flow run_commands 执行，去扫 698 台内网的 cline session，
# 不是从本机直连 .75。.75 本身的可达性看上面的「.75 可达性判据」。
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "ls /home/*/.cline/data/sessions/*.messages.json | head -20"
```
> `.75` 已对 **697/698** 台免密（`e0031982` 身份）。**分批 5–10 台/次**，别一次扫 698 台（会超时）。

**三个已知坑（别再踩）**
1. **GitHub 假阴性**：`curl https://github.com` 在剥掉 proxy 的环境里返回 `000`，但 `git push` 走 `git config --global http.proxy` 仍可通。**判据用 `git ls-remote origin HEAD`，不要用 curl**。（确需代理：`git config --global http.proxy http://172.19.92.23:13128`）
2. **`write_file(content_base64=...)` 会腐蚀内容**（`$dA` → `$d\x01`）：一律用 plain `content` 字符串，或 `run_commands` 里 `base64 -d` 在本机解码。
3. **`ssh` 经 eda_flow `run_commands` 跑时会 hang**：命令前加 `</dev/null`（`-n` 反而会断 stdin pipe）。**注意：ssh 到某台机超时只代表「那台机 ssh 不通」，不代表 `.75` 不可达——`.75` 可达性只看 eda_flow MCP（见上方「`.75` 可达性判据」）。**

## 3. 用例契约（proper `design_flow`）

```text
mode:        "design_flow"
entry_point: "outputs/submit.zip"
test:        "def check(deliverable, workdir): ..."   # 双参，返回通过 / 抛异常失败
prompt:      自然语言，写真实场景（真实用户名/路径/工具/指标），不是函数签名题
attachments: [assets/<task_id>/...]                    # 真实输入文件
metadata:    { trace_source{...}, domain, test_rationale }
```
🚫 不带 `lang` / `host` / `runtime`；🚫 不写"实现 `xxx(args)->dict`"这类抽象题。

**单轮闭环 + 交付定义（DoD）**

一轮 = 一条 case 从选料到落库，**建议不要拆成两轮**（拆开会拉长交付周期）：

- **深读是硬闸门，但不是独立的一轮**：必须先解析完整对话流（`scp` `messages.json` → user 意图 / assistant 工具链 / 关键产物 → `designflow/trace_deepreads/<sid>_<主题>.md`）才允许合成；已有笔记可直接复用，不重复深读。
- **DoD（交付定义）**：1 条 case 通过自验并写进 `cases/<shard>/<task_id>.json` 才算交付（运维令 2026-11-23 覆盖）；**深读笔记是中间产物，不算交付**。🚫 不要写进任何 jsonl。
- **每轮做多少条由你判断**：只要上下文不失控、每条都过质检，一轮做 1 条或 3 条都可以。**硬要求是质量不是数量**：未过闸门的 case 一律标 `incomplete`，不进 jsonl、不计通过率。
- **单条 trace 过大时**（>2MB 或 >600 msgs）可以本轮只深读，心跳记 `DEBT: 1 deepread 未合成`，下一轮交付 case。连续多轮只深读会让产出滞后——如果确实需要（例如在追一个大线索），说明理由并给出交付 ETA。
- **选 trace 走台账（去重与进度的事实源）**：`python3 designflow/trace_ledger.py next --n 5` → 在 `.75` 上取候选 → 选第一条 → `claim` 落台账。
  - 出完 case：`mark --session <s> --status case --case-id <EDA-Eval-DesignFlow-XXX>`（覆盖率的唯一分子）；
  - 暂缓：`mark --session <s> --status parked --note "<原因>"`（如 aether 超时），**不重复捡**。
  - 台账是**去重与进度的记录**，不是选题的紧箍咒：如果你从别的途径（深读、domain 关键词、其他 shard 线索）发现了一个值得做的 session，**只要先 `claim` 登记**就可以做。跳过 claim 才会让去重失真，所以登记就行。
- 选料偏好：`match_count` 高 + **该 domain 尚无 case**（domain 覆盖优先于纯命中数）——这是偏好，不是硬性规则，遇到更好的题可以覆盖。

## 4. 判分质量（"有牙"，缺一不可）

1. **隐藏输入 B**：A 给 SUT 看，B 放 `assets/<id>/hidden/` + `hidden_manifest.json`，**不进 SUT 沙箱**；`check()` **只跑 B**，B 与 A 在规模/取值/结构上必须不同（不是换文件名）。
2. **真跑候选**：≥1 个条件用 `subprocess` 在 B 上执行候选脚本，断言**输出结构**（解析成字段/拓扑/计数再比较），不是文本相似。
3. **≥8 个独立条件**，每个单独可 FAIL；🚫 "仅成员名 / 仅子串出现"式断言。
4. **负样本入库**：`reference/<id>/negative/` ≥2 个错解（naive / always-XXX stub）+ `negative_selftest.py`，一次跑完必须**全 FAIL**；每轮抽查 1 条重跑。
5. **随机化**：在 B 上随机抽子集（net / signal / 行），3 个随机种子跑 3 次结论一致；🚫 把期望值硬编码成固定串。
6. **`metadata.test_rationale` = 逐条断言清单（不是摘要）**：格式固定 `k 条断言：①<验什么> ②<验什么> …`，**一条对应 `check()` 里一个可独立失败的条件**，写清"对象 + 判定"。
   - ✅ `7 条断言：① zip 内 5 个文件齐全 ② mac4.v 有 module mac4 且端口 clk/rst_n/acc0 齐全 ③ 累加为 32-bit 有符号饱和（边界 0x7fffffff/0x80000000） ④ sim_mac4.log 含 MAC4_SIM_PASS 且无 MAC4_SIM_FAIL ⑤ …`
   - 🚫 废话：`解 zip 校验 3 文件`、`校验交付件完整性`、`断言内容达标`
   - 🚫 实现细节：`raise AssertionError(...)`、`zipfile.ZipFile(...)`、`z.read(...).decode(...)`
   - 自检：`k` 必须等于 §4.3 要求的独立条件数（≥8）；两者对不上 = 未完成。⇒ 按顶部令 21:5x 执行：标 `incomplete`、进 `designflow/rewrite_queue.tsv`、🚫 不许落 jsonl、🚫 不许计入通过率。
7. `check()` 在**独立临时目录**解 zip；🚫 在 SUT workdir 留 `__chk`。
8. **泄漏隔离**：SUT 沙箱不得包含 `benchmarks/EDA-Eval-DesignFlow/`（`reference/`、jsonl、`test` 字段）；结论写 MEMORY 一行。
9. **退化提交回归**：每条 case 必须让 (a) 空壳 (b) 只 print 期望串 (c) 参考解删核心 三种假提交**全部 FAIL**；任一 PASS ⇒ 该 case 判分不合格，限期整改或下线。

## 5. 难度分布（观察指标 · 不是生产配额）

| 层 | 定义 | 当前占比（事后统计） |
|:--|:--|--:|
| L1 | 离线 Python 复刻（读附件写脚本） | 观察值 |
| L2 | 真跑沙盒工具（calibre LVS/DRC、Virtuoso、PrimeTime、VCS，经 eda_flow / .75） | 观察值 |
| L3 | 多工具链路 + 修复 + 回归（DRC 179→0、LVS 干净 CORRECT、ERC 全清） | 观察值 |

- 🎯 **层级不是造题的准入门槛**：trace 里用户实际在做什么，就造什么难度的题（见顶部「任务初衷」第 1 条）。此表只用于**事后统计题库覆盖了哪些难度**，供判断题库是否偏科，**不得用于否决任何真实用户意图**。
- 若观察发现某一层长期为 0（例如 L2 一直没题），说明**选料没覆盖到这类 trace**，应去扩大选料面，而不是禁止其他层造题。
- 总样本 **<30 条前不报通过率**，只写"已跑 n 条中 x PASS"（6 条算百分比没有统计意义）。
- 🎯 **通过率是观察指标，不是造题目标**：真实用户的任务有的容易、有的很难，题库本来就该长这样。**不得为了让数字落进某个区间而挑题、改题、加难或降难。**
- 实际含义：通过率由“用户任务的真实难度分布 + agent 的真实能力”共同决定，我们只负责如实测量，不负责塑造。总样本 **<30 条前不报通过率**，只写“已跑 n 条中 x PASS”。
- 心跳每轮写一行：`🎯 通过率: 最近20条 x/20 = y%（观察值）`。
- 若某条 case 长期 0 PASS，**先查 `check()` 是否误判**（参考解能不能 PASS），再判断是题难还是判分错——**不要为了好看向下调难度**。

## 6. 每轮流程

1. `trace_ledger.py next --n 5` 取候选 → `claim` → 深读（有笔记就复用）→ 合成（`assets/` `reference/` `hidden/` `negative/`）。
2. 自验：`reference/` 参考解跑 `check()` 必 PASS；§4.9 (a)(b)(c) 三假提交必 FAIL；`negative_selftest.py` 全 FAIL。
3. pi 实跑：`designflow/pi_debug_status.jsonl` 追加一行，记 `pi_model / pi_thinking / pi_dur_sec / pi_verdict / ref_check`。
6. 收尾：`WAITING: 0`（下一轮 60s 后立即开下一条 case）；仅真外部阻塞（pi 异步未回 / 推送失败 / 等人工）才写 `WAITING: 1`。

## 7. 当前基线（每轮只更新这一行，不堆历史）

`11 条 proper（10 域）· 已跑 6 条 = 6 PASS · 6 trace_deepreads · test_rationale 断言清单 0/30（硬闸门见顶部令 21:5x）· 目标通过率（B 档）20–30%`
`📊 trace 覆盖率：见 designflow/trace_ledger.py stats（covered / mc≥10 候选池，target_mc=10）`
> 现存 11 条的 `test_rationale` 本轮内全部改写成 `k 条断言：①…`（k = 该 case `check()` 的独立条件数）。

## 8. 收尾（轻量结账，不是每轮做全套）

> 收尾是"结账"：**一轮 = 1 条 case = 1 次结账**。别把结账做成产出，也别攒着不提交。

0. **体积自检**：TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限先把已闭合块**原文**搬 `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针），搬前 `git pull --rebase --autostash`，🚫 不改小节编号/标题。数字抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB`。
1. **心跳（轻）**：`MEMORY_DESIGNFLOW.md` 顶部快照**只改变化的几行** + **追加 1 行流水**（三口径 + `🎯 通过率` + `📊 trace 覆盖率 x/y=z%` + `DEBT`）；🚫 每轮重写整份快照。
   - 顺带刷新候选池（**2026-11-11 令：mc≥10 口径**）：统计 `sessions / mc10 / mc20 / mc30 / mc100`，然后
     `python3 designflow/trace_ledger.py refresh --json '{"sessions":N,"mc10":N10,"mc30":N30,"mc100":N100,"target_mc":10,"shard_mc":{"A":10,"B":10,"C":10,"D":10}}'`
     ⚠️ **禁止**写 `"target_mc":30` 或 `shard_mc` 出现 15/30。本 shard 非共享配置 owner（只读）；A 已换池则跳过本步。
2. **日记忆**：`daily-memories-designflow/<YYYY-MM-DD>.md` **当天首轮创建，之后只追加**。
3. **提交**：**每轮（1 条 case）结束即提交**（loop 另有每 30 分钟兜底）；🚫 把工作留在工作树过夜。双仓命令：
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/designflow \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
           doc/ZhuLong_DAC2027/reports
git commit -m "designflow #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow
git commit -m "designflow #<轮次>: <一句话>" && git push origin master
```
4. **闭环自检**：`git status -sb` 无 ahead/behind；push 失败重试 1 次并记报错原文。

> ⏱ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

## 9. 待确认（未确认前按默认走）

- Benchmark 是否对外（默认：先内部）
- 是否允许主动扫描 698 机（默认：否，只被动只读发现）

---

> ⚠️ 本文件为**只读指令文件**，agent 禁止修改；有异议写进 MEMORY 并存疑执行。



## 🔀 SHARD 配置（本 shard 专用 · 覆盖主 TASK 中的通用描述）

**你是 shard C（physical_layout）**。只负责以下 domain：layout_aether, layout_virtuoso, pg_layout, physical_verify

### 你的文件（不要碰别的 shard 的文件）
- **case 文件**（运维令 2026-11-23 覆盖）：`benchmarks/EDA-Eval-DesignFlow/cases/<shard>/<task_id>.json`（每条 case 一个 JSON 文件，不再用 jsonl）
- **台账**：`designflow/trace_ledger_C.tsv`（通过 `trace_ledger.py --shard C` 自动使用）
- **心跳**：`MEMORY_DESIGNFLOW_C.md`（只写这个文件）
- **日记忆**：`daily-memories-designflow/daily_C_*.md`

### 选 trace 命令（带 shard 过滤）
```bash
python3 designflow/trace_ledger.py --shard C next --n 5
python3 designflow/trace_ledger.py --shard C claim --session <s> --user <u> --host <h> --match <m> --domain <d>
python3 designflow/trace_ledger.py --shard C mark --session <s> --status case --case-id <id>
```

### 合并
- **不要碰任何 `*.jsonl`**（运维令 2026-11-23 覆盖）：shard jsonl 和 main jsonl 均已物理删除，merge 脚本在缺文件时优雅 skip
- 你的 case 只写进 `cases/<shard>/<task_id>.json`（运维令 2026-11-23 覆盖，不再追加 jsonl）

### 收尾提交（只提交自己 shard 的文件）
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_C.md \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_C.tsv \
           doc/ZhuLong_DAC2027/benchmark/designflow/trace_deepreads \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow/daily_C_*
git commit -m "designflow shard C #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl \
           benchmarks/EDA-Eval-DesignFlow/assets benchmarks/EDA-Eval-DesignFlow/reference
git commit -m "designflow shard C #<轮次>: <一句话>" && git push origin master
```
