# BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md — Lite-500 逐条「实跑评估」审视令 · 4 shard 共享规格

> **下发**：2026-11-26 18:5x · 用户令「安排 designflow 4 agent 对 lite-500 中自己的 Case 进行审视，按需进行『实跑评估』改造」
> **适用范围**：designflow shard **A / B / C / D**（各自 `BAIZE_DESIGNFLOW_BENCH_TASK_<shard>.md` 顶部有指针）
> **优先级**：高于造题 / 扩池 / 治理 / intent_audit / stop-loss；**低于**「已绿条目的 P0 止损」与 §1.1 冻结窗口。
> **不改变**任何铁律：不改题面、不降难度、不改判分严格度、不删题凑数、不改论文宏。
> **体量**：本文件 ≤ 12KB；各 shard 任务书顶部只留 6 行指针。

---

## 0. 一句话

**把 Lite-500 里属于自己 shard 的那一份（A116 / B126 / C137 / D121）逐条重判「该不该实跑」：该实跑的（判分实质依赖真实 EDA 工具产物）一条不剩改成 `L2.live`；不该实跑的写明「本质问」依据、保持 mock 但**不许改判分**；改造只做**增量加层**，断言条数与严格度只增不减。**

> 与旧 P4 的关系：本令**不是**旧 P4 的重复。旧 P4 是「按关键词 + 局部复核」做过一轮（A T1=2/T2=2/T3=117、C T1=6/T2=16/T3=115、D lite-128 T1=4、B 未产出 T1），但
> **① 口径不统一**（有按 585/609 全量算，有按 lite 子集算）；**② 关键词扫法已被证伪**（A r1272 三例误判）；**③ 自写 mock 桩的语义保真度从未系统体检**。
> 本轮要求**逐条重判 + 桩体检**；旧结论只当线索、不得直接抄。

---

## 1. 口径（先冻结，写进各 shard MEMORY 顶部一行）

1. **名册唯一来源** = `designflow/lite_health_all.tsv`（501 行 = 表头 + 500 条；列 `case_id / owner_shard / status / L0..L5 / src_shard / fix_note`）。
   本轮已按 `owner_shard` 切成逐条清单：**`designflow/live_eval_review_<shard>.tsv`**（A116 / B126 / C137 / D121）。**只勾自己那份，🚫 不改别人的清单**。
2. **id 归一化**：清单里短名（`DesignListGen-001`）与全名（`EDA-Eval-DesignFlow-OtaAcReport-001`）混排 ⇒ 匹配前统一剥 `EDA-Eval-DesignFlow-` 前缀，规则写进 MEMORY 一行。
3. **B 的 2 条 `cross_shard`**（`OtaAcReport-001` / `PUvddSweep-001`）走 cross_shard 流程，**不进**本轮三分类；`OpampChar-001` 跨 shard P0 遗留照旧挂账。
4. **500 恒定**：本轮**不增题、不删题**。审视出「题本身坏了」⇒ 记 `TODO(BLOCKED)` + 报 A，🚫 不许借实跑改造之名退题。
5. **口径变更必须报**：实跑改造会改 `judge_layers`（`[L0,L1]` → `[L0,L1,L2.live]`）⇒ 属**口径变更**，收口后必须通报 zhulong（§6）。

### 1.1 🔴 冻结窗口（先看这条再动手）

**zhulong 正在跑 doubao-pro rerun#2 r3'（PID 1498010，w=4，ETA ≈ 2026-11-27 00:08；见 `run/MEMORY_ZHULONG.md` 首行）**，它读的就是同一个 EDA-Flow-Bench 工作树的 `reference/<id>/check.py`。

| 阶段 | 允许 | 🚫 禁止 |
|:--|:--|:--|
| **现在 → zhulong r3' 收口 + 3-run 数字冻结** | **只读审视**：读 check.py / negative / trace，填 `live_eval_review_<shard>.tsv` 的 verdict 列，产出 REQ 清单 | 🚫 落盘改 `reference/*/check.py`、🚫 改 `cases/*.json`、🚫 提交判分文件 |
| **zhulong 报「r3' 收口 + 3-run=x.xx±y.yy%」之后** | 按 §3 改造 + 自验 + commit | 🚫 仍不许在 zhulong 起新 run 的窗口内改判分 |

> 理由：判分器**逐 case 在判分时刻加载**。跑到 41% 时换 check.py = 半程换尺 ⇒ 整轮 Pass@1 不可用（白跑约 6 小时且污染 3-run 统计）。
> 「解冻」的唯一凭据 = `run/MEMORY_ZHULONG.md` 首行已写 r3' 收口，**不靠猜时间**。

---

### 1.2 ✅ 隔离工作树通道（解冻前即可「改造 + 自验」，只是不许「合入」）

**冻结的是主工作树，不是实跑能力。** 两个资源必须分清：

| 资源 | 是谁的 | 与 zhulong 关系 |
|:--|:--|:--|
| `.75`（`hfhds201`）+ `eda_flow` MCP（hspice/finesim/vcs/vlogan/calibre） | **designflow 自己的 EDA 沙盒** | **无关**，随时可用（A r1314 / C r1229 / D r1478 已在用） |
| `36.15`（`hfeg0tedaap02`）的 `/nasdata/app.e0031982/code/EDA-Flow-Bench/` | designflow agent 的 **cwd**，也是 zhulong `eval/run_batch.sh` 的 **cwd** | **同一棵工作树** ⇒ 改 `check.py`/`cases` = 半程换尺 |

| 允许（现在就能做） | 🚫 禁止（等 r3' 收口） |
|:--|:--|
| ① `/tmp` 下 `git worktree add --detach` 一份**隔离树**，在隔离树里改 `reference/<id>/check.py` / `cases/*.json` / `negative/` | ① 改**主树**任何 `benchmarks/` `reference/` `cases/` 文件 |
| ② 在隔离树内跑 `SKIP_RUN=1 eval/run_one.sh ...` 静态自验 + `.75` L2.live ref 自验 | ② 在主树 `git pull` / `checkout` / `rebase`（会掀掉 zhulong 正在读的文件） |
| ③ 改动 commit 到**隔离树的本地分支**（不 push） | ③ `git push origin master`（master = zhulong 工作树分支） |
| ④ 收口后：`git fetch` → cherry-pick 到主树/origin → 再 push | ④ 收口前 merge 进 master |

**fail-closed 前置（每 shard 第一次走通道必须先过）**：在隔离树跑一次 `run_one.sh`，前后各取一次**主树指纹**——
`git -C /nasdata/app.e0031982/code/EDA-Flow-Bench status --porcelain`（前后必须逐字节一致）+
`ls -l --time-style=full-iso eval/status*.jsonl`（mtime 不得变）。
**任何一项变了 ⇒ 该 shard 立即退回严格等待**（说明 `run_one.sh` 会写主树共享路径，会污染 zhulong 的 status 台账），并在 MEMORY 记 `隔离通道不可用: <证据>`。

**命名/清理**：隔离树固定 `/tmp/live_eval_<shard>`，收口后 `git worktree remove`，🚫 常驻、🚫 在里面放 assets 大文件。

---

## 2. 三分类判据（逐条填 `live_verdict`，必须带理由）

**本质问（每条都问一遍）**：
> 「候选把文本断言全骗过、但真实 EDA 工具跑不起来 / 产物全错 —— 这题 pass 算不算数？」

| verdict | 判据 | 动作 |
|:--|:--|:--|
| **`LIVE-REQ`** | 答「**不算数**」：判分实质依赖**真实工具产物**（编译产物 / 仿真波形 / 网表提取 / DRC 结果 / 几何 dump / 时序报告） | **必须改造**：拆 `check_static`/`check_live`，`judge_layers` 加 `L2.live`，`.75` 真跑验 ref PASS |
| **`LIVE-OPT`** | 静态判分**已足够**（不会造成假阳/假阴），但 `.75` 真跑能再加一条更硬断言 | 排期做；做不了写清**缺什么**（工具/许可/资产/权限），具体到可核查 |
| **`LIVE-NA`** | deliverable **本身就是**文本/脚本/日志分析/改文件/问答（写 Makefile、解析既有 log、改 tcl、答 API 用法） | 保持 `[L0,L1]`，**只写理由**，🚫 不许改判分 |

### 2.1 三条硬规则（覆盖旧 P4 做法）

1. **mock 桩体检（本轮重点）**：凡 `check.py` 调**自写假工具**（`hspice_mock` / `finesim_mock` / 伪 tcl 桩 / 内嵌 GT 常量），必须答两问：
   - **Q1 语义保真**：桩是不是把真实工具输出语义**抄了一遍**？（数值来自真实工具抓的 GT，还是编的？）
   - **Q2 能否被骗**：「按模板把文件形状造对、但物理数值/时序/几何全错」的提交，桩会不会判过？
   - **Q2 = 会判过 ⇒ 记 `LIVE-REQ`**（哪怕当前 ref PASS + neg 全 FAIL）。本轮最可能挖出真问题的地方：**B 的 `hspice-mock`/`finesim-mock` 家族、D 的 `hspice_mock` 家族**优先体检。
2. **「工具名出现 ≠ 真跑」**：`vcs`/`verdi`/`calibre`/`innovus`/`hspice` 出现在 `make -n` 展开串、内嵌日志、`evidence` 文本里——**不算**实跑（A r1272 三例已证伪）。判据只看 `subprocess` 是否**直调真二进制**且该条件 **required**。
3. **旧 P4 结论不作数**：线索可复用但**必须复验**；冲突时以本轮 + 落盘证据为准，并在 tsv 记「与旧 P4 不一致：……」一行。


---

## 3. 改造手法（照 `CONTRACT_REFORM_GUIDE.md` §3 非侵入包装，🚫 不重造 check.py）

1. 原 `check` → 改名 `_check_static_impl`，**一字不动**（断言条数/阈值/严格度原封保留）。
2. `check_static(...)` 包 `try/except`，收口三元组（与指南 §3 模板一致）。
3. **新增** `check_live(sess)`：经 `eda_flow` MCP 在 `.75` 真跑，**读真实产物**再断同样的物理量（🚫 不读 `reference/`、🚫 不读隐藏 GT 文件）。
4. `check()` 保留兼容包装；case JSON `metadata.judge_layers` 追加 `"L2.live"`；JSON `test` 字段与磁盘 `check.py` **sha 同步**（字节一致）。
5. `negative/` 至少加 **1 条「静态全过、实跑产物错」的 live-neg**（新层必须有牙），`negative_selftest.py` 同步登记。
6. 判不了 `LIVE-REQ`（工具不可达/许可缺失/资产缺失）⇒ 降级 `LIVE-OPT`，tsv 写 `BLOCKED: 缺 <具体项>`，🚫 不许伪装成 `LIVE-NA`。

---

## 4. `.75` 实跑纪律

- 通路：`eda_flow` MCP `open_session` → `run_commands`；记录 **hostname / RC / wall_s**；session 用完即关。
- 现成真工具（`/apps/synopsys/SRB/`）：`hspice` / `finesim` / `vcs` / `vlogan` / `hspice64`；`calibre` / `icv` 视可达性；`virtuoso` / `pyAether` 走 `ae.*` 代理（注意 A r1292 先例：`dbCreateLabel`/`dbGetInstByName`/`dbGetPinShapes` 在 .75 pyAether 沙盒**不存在**）。
- **缺工具/许可/超时 ⇒ 记 `infra`**（铁律 2），写进 tsv `live_evidence`；🚫 不得写成「能力不足」、🚫 不得据此下模型结论。
- **预算**：审视轮（纯静态读）**20–30 条/轮**；实跑改造 **≤3 条/轮**（每条 5–15 min）；🚫 并发轰炸 `.75`、🚫 起大批量 `run_batch`。
- **确定性**：同一 case 连跑 3 次产物 md5 一致，才允许把该产物写进 `check_live` 断言；不一致先修确定性再改判分。

---

## 5. 验收判据（每条 `LIVE-REQ` 全勾才算收口）

- [ ] **①** `.75` 真跑 ref（L2.live）**PASS**，证据＝`hostname / RC / wall_s / 产物 md5`。
- [ ] **②** ≥3 neg 全 FAIL、**first-fail 断言 distinct**，且**含至少 1 条 live-neg**（静态过、实跑错）。
- [ ] **③** 3-seed 确定性（产物 md5 一致）。
- [ ] **④** `SKIP_RUN=1 eval/run_one.sh <task_id> --shard <S>` 静态判分**仍 PASS**（实跑挂掉不得拖垮静态层）。
- [ ] **⑤** `judge_layers` / JSON `test` 字段 / 磁盘 `check.py` **sha 三方同步**。
- [ ] **⑥** 断言**条数只增不减**、阈值**不放宽**、条件**不删**（改造前后逐条 diff 记进 `contract_reform_<shard>.md`）。
- [ ] **⑦** L5 不退化：hidden-B 不外泄、`check_live` 不读 `reference/`、沙箱不含 `.jsonl`/`test` 字段。

---

## 6. 交付物（每 shard）

1. `designflow/live_eval_review_<shard>.tsv` —— **全量填满**（`live_verdict` / `live_reason` / `check_live` / `live_evidence` / `round`）。
2. `designflow/contract_reform_<shard>.md` 增一节「**Live-eval 审视（2026-11-26 用户令）**」：REQ/OPT/NA 三张清单 + 与旧 P4 的差异。
3. MEMORY 顶部**心跳一行**（固定格式，便于汇总）：
   `LIVE: <shard> review=<n>/<n> · REQ=<a>(done <b>) · OPT=<c>(done <d>) · NA=<e> · L2.live <f>→<g>`
4. 日报：`daily_<shard>_<date>.md` 照旧。
5. **A 汇总**：全 shard review 填满后，A 出 `designflow/live_eval_summary.md`（三分类合计 + REQ 改造进度 + 缺口台账）。B/C/D 把汇总数字**报** A，🚫 不写 A 的文件。
6. **报 zhulong**：落盘改造完成后由 A 统一通报「Lite-500 判分层变更（X 条升 L2.live）」；**是否重跑由 zhulong 定**。🚫 任何 shard 自行宣布「新基线」。

---

## 7. 禁止（踩线即回退）

1. 🚫 降断言条数 / 放宽阈值 / 删条件 / 把「看图」改「读数值」/ 拆子步骤给提示（=降难度，凌驾于「好跑」之上）。
2. 🚫 改 prompt 语义、改 assets 难度、改用户原话。
3. 🚫 为实跑省事把 required 条件降成 optional，或把真跑断言包进 `try: ... except: pass`。
4. 🚫 动别 shard 的 case / reference / manifest；🚫 动 Full 集；🚫 动论文宏（`\LiteSet` / `\Neval` / `\MzeroPass` / `\ScriptPass`）。
5. 🚫 `git add -A` / `git clean` / `reset --hard` / 在 zhulong 起跑窗口内改判分（§1.1）。
6. 🚫 把 infra 失败（工具缺失/许可/超时/隧道断）写成能力结论。

---

## 8. 排期（每 shard 照此推进，别跳步）

| 轮 | 内容 | 产出 |
|:--|:--|:--|
| **R1** | 读 `live_eval_review_<shard>.tsv` 全量，逐条静态重判三分类（**只读、不落盘判分**） | tsv verdict 填满 + REQ 清单 + 缺口台账 + 心跳行 |
| **R2…Rn** | 按 REQ 优先级逐条改造（**≤3 条/轮**）；先做「桩体检判为 REQ」的家族（B: hspice/finesim-mock；C: virtuoso/calibre；D: pyAether/hspice_mock；A: vcs/vlogan） | 每条：check_live + live-neg + §5 七项全勾 |
| **收口** | REQ 全绿 + OPT 有结论 + NA 有依据 | 报 A → A 汇总 → 报 zhulong（口径变更候选） |

> **优先级口径**：`LIVE-REQ` > `LIVE-OPT` > 新造题。`LIVE-NA` 条目不占轮次（R1 写完理由即结束）。
