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
5. **口径变更必须登记**：实跑改造会改 `judge_layers`（`[L0,L1]` → `[L0,L1,L2.live]`）⇒ 属**口径变更**，改的时候按 §1.2 往 `live_eval_changes.tsv` 写一行即可，**不需要等任何人的许可**。

### 1.1 主辅关系：**designflow 是主线，zhulong 评测是辅线 —— 不设等待**

> **2026-11-26 20:5x 用户裁定**：「designflow 等待 zhulong 评测是不对的……我的本意就是以 **designflow 为主，zhulong 评测为辅**，目标是随着 designflow 对于 lite-500 的修复逐渐收敛，评测结果会稳定下来。**从来没说过要等**。」

- **🚫 没有冻结窗口。** 任何 shard 任何时刻都可以改 `reference/*/check.py` / `cases/*.json` / `negative/`。「等 zhulong 跑完再改」= **错误行为**，本条覆盖本文件历史上的任何冻结表述。
- 要治的不是「改动」，而是「**一堆 run 数字说不清口径**」。解法是**登记 + 跟随**，不是停手：

| 角色 | 责任（就这一件事） |
|:--|:--|
| **designflow（主）** | 改判分时往 `designflow/live_eval_changes.tsv` **追加一行**：`ts / shard / case_id / judge_layers 变更 / repo_commit / 一句话原因`。其余照常：改造 → 自验 → commit。 |
| **zhulong（辅）** | 本线已转 **designflow 体温计**（2026-11-26 21:0x 用户令：连续循环 lite-500 × doubao-pro，只有用户令才停，见 `run/ZHULONG_TASK.md`）。每轮 run **起跑时记 `repo_commit`**（EDA-Flow-Bench HEAD）。若该轮期间 `live_eval_changes.tsv` 有新行落入 ⇒ 该 run 标 **`MIXED`**，**不进 3-run 统计**，下一轮自然重跑。 |
| **A（汇总人）** | 每完成一批改造，把累计变更的 commit 范围**报** zhulong。🚫 不替 zhulong 决定重跑与否。 |

- **为什么这样够**：判分器是**逐 case 在判分时刻加载**的 ⇒ 改动不会让 run 崩，只是让**那一轮**变成混合口径。用 `repo_commit` + `MIXED` 就能事后识别并剔除，比让主线程停 4 小时便宜得多。
- **收敛目标照旧**：lite-500 修复越收敛 ⇒ 判分口径变动越少 ⇒ zhulong 的 run 越稳定。**这是目标，不是对 designflow 的约束。**

> 📌 **两个资源别混**（这一点保持不变）：`.75`（hfhds201）+ `eda_flow` MCP = **实跑**，与 zhulong 无关，随时可用；`36.15` 的 `/nasdata/.../EDA-Flow-Bench/` = 同一棵工作树（designflow 的 cwd 也是 zhulong 的判分源）⇒ **改动照做，只需登记**。

- 🧹 **清账（本轮必做一次）**：若你的 MEMORY 顶部仍写着「冻结窗口 / BLOCKED on 解冻 / freeze active / WAITING:1（因冻结）」⇒ **立即删除该表述**，把 `WAITING` 回到真实值（没有别的实际阻塞就写 `0`），并在心跳补一句 `freeze-removed: <date>`。已按旧令只读等待的轮次不追责，但**从本轮起不得再以「等 zhulong」为由停手**。

---

### 1.2 改动登记（唯一额外动作，约 10 秒）

- 文件：`designflow/live_eval_changes.tsv`（表头已建好）。
- 列：`ts / shard / case_id / change / jl_before / jl_after / repo_commit / reason`。
- **何时写**：**commit 之前**写，并与该 commit 一起提交（保证 `ts` 与 `repo_commit` 同源、可对账）。
- **回退要留证**：若某条改造**回退**了已发布口径（例：`L2.live` → `L0,L1`），`reason` 必须写清证据（哪条断言不成立 / 哪个工具不可达），并在 MEMORY 心跳单列 `ROLLBACK=<n>`。🚫 静默回退。
- 这个文件是 zhulong 判 `MIXED` 的**唯一依据** ⇒ **宁多写不少写**。

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
- **预算**：审视轮（纯静态读）**20–30 条/轮**；实跑改造 **A/C/D ≤3 条/轮**（每条 5–15 min），**B ≤ 6–8 条/轮**（2026-11-26 用户批准：B 的 40 条 Type A 高度同族，可批处理）。
  - B 放宽的**前提**（缺一即回落 ≤3）：① 批内**逐条独立自验**——每条都要单独跑 ref PASS + ≥3 neg FAIL distinct + live-neg，🚫 不许「一条验过、六条顺带放行」；② 单轮 wall **≤ 90 min**（超了就停，剩下的留到下一轮，🚫 硬顶）；③ `.75` **严格串行**（open→跑→关，🚫 并发多 session）；④ 某条首次 `check_live` 不通过 ⇒ 该条当轮降级记 `BLOCKED`，🚫 拖累整批。
- 🚫 并发轰炸 `.75`、🚫 起大批量 `run_batch`。
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
6. **报 zhulong（辅线跟随，不是请示）**：A 每批改造收口后通报「变更 commit 范围 + `live_eval_changes.tsv` 新增行数」；zhulong 自行决定下一轮何时起跑，并把跨改动的 run 标 `MIXED` 剔除。🚫 shard 自行宣布「新基线」；🚫 **也不需要等 zhulong 才能改判分**（§1.1）。
   另：zhulong 体温计每轮产出 `run/reports/thermo_feedback_r<N>.md`（Pass@1 / 新增 ERROR·FAIL 的 `case_id` / 13 域通过率）⇒ **A 读取并按 `owner_shard` 分派**，各 shard **优先修体温计暴露的回退**（新增 FAIL 高于新增 OPT）。

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
| **R2…Rn** | 按 REQ 优先级逐条改造（**A/C/D ≤3 条/轮**；**B ≤6–8 条/轮**，见 §4 前提）；先做「桩体检判为 REQ」的家族（B: hspice/finesim-mock；C: virtuoso/calibre；D: pyAether/hspice_mock；A: vcs/vlogan） | 每条：check_live + live-neg + §5 七项全勾 |
| **收口** | REQ 全绿 + OPT 有结论 + NA 有依据 | 报 A → A 汇总 → 报 zhulong（口径变更候选） |

> **优先级口径**：`LIVE-REQ` > `LIVE-OPT` > 新造题。`LIVE-NA` 条目不占轮次（R1 写完理由即结束）。
