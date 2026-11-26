# Shard B 契约改造记录（contract_reform_B.md）

> 本文件记录 shard B（spice_sim / characterization）判分契约改造进度。
> 优先级：P1 > P4(只读分析) ≈ P2 > P3。

## 总览

- **P1（pilot 12 case）**：N/A — pilot 12 case 全在 shard A/C/D，B 无 P1 工作。
- **P2（扩展 L2.live）**：见下方 P4 分析结论。B 600 case 全为 self-contained mock/static 判分，
  无 case 判分本质依赖 .75 真跑 EDA → **P2 候选 = 0**（r1258 初判 + r1264 P4 本质问复核一致）。
- **P3（mock case 声明 judge_layers）**：✅ 600/600 完成（r1258，全 B case metadata 加
  `judge_layers=["L0","L1"]`，纯 metadata 增量，未碰 test/prompt/assets；框架旧式 check() 回退兼容）。

---

## P4 实跑适合性分析 (r1264 · 2026-11-26)

本 shard Lite-500 case 数: 130（B Lite 集，eval/cases_lite.txt ∩ cases/B/）

### 判定方法

逐 case 读 case JSON 的 `prompt` + `test`（check.py 快照），用 P4 核心一问判定：

> 「如果 candidate 的输出能让 check.py 的文本断言全过，但 EDA 工具实际跑不起来/结果全错，
>   这个 pass 算不算数？」

并辅以自动化信号扫描（subprocess / hspice / finesim / pyAether / mock-body / 真二进制调用 /
`/rundata` 依赖），对 19 条「引用 hspice/finesim 但无 `_ensure_*` mock 标记」的疑似 case 逐条深查
`subprocess.run([...])` 调用对象（是真调 simulator binary 还是只跑 candidate `.py`）。

### 结论分布

| 档位 | 数量 | 说明 |
|------|------|------|
| T1 适合实跑 | 0 | 无 case 判分本质依赖真实 EDA 执行产物（详见下方论证） |
| T2 可选增强 | 1 | LisMeasExtract-001（已有 real-hspice 路径+fallback，可在 .75 启用真跑） |
| T3 不适合 | 129 | 保持 mock/static 判分，不改 L2.live |

### T1=0 的论证

B shard 130 条 Lite case 全部遵循同一设计范式 —— **「自包含可复现子技能」harness**：

1. **prompt 明示 foundry PDK / 真模拟器在 eval 环境不可用**，要求 candidate 把真实 trace 中的
   「可复现子技能」抽成 self-contained harness（deck 生成器 / 解析器 / 诊断器 / 表征流脚本）。
2. **check.py 的判分对象是 candidate 产物的结构正确性**，不是「在真实 PDK 上跑出某条波形」：
   - 63 条 `script_only`：subprocess 跑 candidate `.py`，断言其输出（CSV/JSON/deck 文本）结构。
   - 47 条 `sim_mock`：check 内嵌 deck-driven mock（`_ensure_hspice`/`_ensure_finesim` 安装 stub
     到 PATH），mock 按 candidate deck 内容返回 .75 上真跑捕获的 GT `.mt0` 值。mock 对 deck 结构
     的校验（pin order / `.measure` / `.param` / `.tran`/`.dc` spec）比 bare syntax check 更严。
   - 19 条疑似「real_eda」：18 条经深查确认 `subprocess.run` 只跑 candidate `.py`，hspice/finesim
     字样仅出现在任务描述 / 注释 / 被解析的 deck 文本里，**无一条真调 simulator binary**。
3. **核心一问回答**：对 sim_mock 类，若 candidate deck 能过 mock 的结构断言但真 hspice 会因语法
   报错 —— 该 pass 仍算数，因为任务意图是「harness 正确实现了表征/解析流」（arc 枚举 / conditioning /
   measure 语法 / pin order），mock 已忠实校验这些；真 hspice 跑不起来是环境问题（GLIBCXX / PDK 缺失），
   非 harness 正确性问题。对 script_only 类，candidate 产物是脚本/文本，根本不涉真跑 → 文本判分够用。
4. **mock 忠实性**：47 条 sim_mock 的 GT 值全部来自 .75 真跑捕获（check.py 注释明示
   `Embedded ground truth (from .75 HSPICE ref runs)`），mock 是真模拟器的功能等价物 ——
   即使改 L2.live 真跑，结果与 mock 一致，判分结论不变 ⇒ 无判分增益。

⇒ **B shard 无 T1 case，P2 候选 = 0**。与 r1258 初判一致；P4 本质问复核覆盖全量 130 条（非仅关键字池），
未发现漏判。

### T1 清单（优先改造顺序）

无。

### T2 清单

| case_id | domain | 可加什么 L2.live 辅助断言 | 工作量 |
|---------|--------|--------------------------|--------|
| EDA-Eval-DesignFlow-LisMeasExtract-001 | spice_sim | check.py 已有 `_run_hspice_b()` 真跑路径（`subprocess.run([hsp,"-i",stimB.sp,...])` + `ran_real` 标志 + pre-captured `.lis` fallback）。eval host 无 hspice → 走 fallback。改 L2.live 可在 .75（hspice 在 PATH）启用真跑路径，产 fresh `stimB.lis` 替代 fallback。**但**：判分对象是 candidate 对 `.lis` 的解析正确性，`.lis` 内容真跑/fallback 等价 → 判分结论不变，仅增强「输入数据真实性」。低判分增益。 | S(<1h) |

**T2 自决结论**：LisMeasExtract-001 改 L2.live 判分增益极低（输入数据等价，非判分依赖），
本轮 **不改**，保持 mock/static 判分。若后续需示范 B shard L2.live 通路可单独立项。

### T3 不适合（129 条 · 不逐条列出）

构成：63 script_only + 47 sim_mock + 1 text_only + 18 疑似 real_eda（经深查确认只跑 candidate `.py`）。
共同特征：判分对象 = candidate 产物结构（脚本输出 / deck 文本 / 诊断报告），mock/embedded-GT 忠实
复现真模拟器结果，真跑无判分增益。保持现有 `judge_layers=["L0","L1"]`（P3 已声明）。

---

## 下一轮计划

- P4 分析已完成（T1=0 / T2=1 自决不改 / T3=129）→ B shard 契约改造全闭合（P1 N/A · P2=0 · P3 ✅ · P4 ✅）。
- 无 P1/P2/P3/P4 待办。回归 Lite 轮转抽检 re-verify（holding 模式），待 zhulong 重建 trace_ledger
  next 通路或扩 mc≥5 池注入新料后再造新题。

---

## Live-eval 审视（2026-11-26 用户令 · R1 只读）

> 令文：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`。本节为 R1 只读三分类结果。
> 🔴 冻结窗口：zhulong r3' 进行中（ETA ~11-27 00:08），R1 只填 `live_eval_review_B.tsv` verdict 列 + 本节，
> 🚫 不落盘改 `reference/*/check.py` / `cases/*.json`。解冻凭据 = `run/MEMORY_ZHULONG.md` 首行 r3' 收口。

### 口径

- 名册：`live_eval_review_B.tsv`（126 行 = 124 green_verified + 2 cross_shard）。
- id 归一化：剥 `EDA-Eval-DesignFlow-` 前缀后匹配。
- 2 条 cross_shard（OtaAcReport-001 / PUvddSweep-001）走原 cross_shard 流程，不进本轮三分类（§1.3）。
- 500 恒定：本轮不增题不删题。

### 桩体检方法（§2.1 Q1/Q2）

逐条对 B shard 的 sim_mock 家族（check.py 调 `_ensure_hspice`/`_ensure_finesim` 安装 deck-driven 桩）做 Q1/Q2 体检。
深读代表样本：BistOscRccReorder-001（finesim-mock）、PorCapSweep-001（hspice-mock，14 条件含 RC 理论交叉验证）、
DffSetupHoldChar-001（hspice-mock char）、FineSimModelScopeFix-001（finesim-mock fix 任务）。

**r1289 全量逐条复核（升级 r1288 的代表样本法）**：r1288 的 verdict reason 为统一模板（47 REQ / 77 NA 各 1 条相同文案），
不满足 §2.1「逐条」要求。本轮对 126 条逐条 grep `check.py` 实证：
- REQ 47/47：均含 self-written mock（hspice-mock 或 finesim-mock）+ subprocess + .75-captured GT 信号 ⇒ 分类稳固，reason 改为按各 case 实际 mock 家族/measure 有无/GT 来源填写的逐条文案（6 distinct）。
- NA 77 → 76：27 条带 sim 信号（hspice/finesim/measure 字样），逐条核 subprocess 上下文 ⇒ 仅 **LisMeasExtract-001** 误判（直调真 hspice 二进制）→ 升 LIVE-OPT；余 76 的 subprocess 仅跑候选脚本，hspice/finesim 仅出现在 deck 文本/字段名 ⇒ NA 稳固。

- **Q1 语义保真 = PASS**：47 条 sim_mock 的 GT 值全部来自 .75 真跑捕获（check.py 注释明示
  `Ground truth captured on .75 with real FineSim/HSPICE V-...`，数值带版本号 + 真实量级），非编造。
  桩按 deck 签名（`.inc` basename / `.param` vdd_val·r_por·vref·load_cap / vvcc pvcc / .temp）查表回放，
  且忠实复现真工具的「cannot open include → abort rc=1」等错误语义。
- **Q2 能否被骗 = 会判过**：桩是 deck-driven，**只按 deck 签名查表回放 GT**，**不执行也不校验**
  候选写的网表拓扑 / `.measure` 语句语义 / 器件尺寸。候选只要把 `.param` 签名造对（vdd/r_por/vref/load_cap
  取值匹配 GT 表键），哪怕网表 R/C 完全错、`.measure` 量错节点，桩仍回放正确 GT → 候选报告 GT →
  通过 mock+GT 比对断言。PorCapSweep 虽有 (h) RC 理论交叉验证，但 GT 本身匹配理论 ⇒ 错网表照样过 (h)。
  真实 hspice/finesim 会因网表/measure 语义错而报错或出错误值 ⇒ 实跑能抓到桩抓不到的假阳性。

### 三分类结果

| verdict | 数量 | 说明 |
|:--|--:|:--|
| **LIVE-REQ** | 47 | sim_mock 家族（hspice-mock/finesim-mock）：Q2 可被骗，判分实质依赖真工具产物（真实仿真波形/.mt0/.lis）。须 R2 拆 check_static/check_live + judge_layers 加 L2.live + live-neg。逐条 grep 验证：47/47 check.py 均含 self-written mock + subprocess + .75-captured GT 信号。 |
| **LIVE-OPT** | 1 | LisMeasExtract-001：check.py 已 subprocess 直调真 hspice 二进制（`_run_hspice_b`，含 pre-captured `.lis` fallback）。B 隐藏 + lis=真捕获产物 ⇒ Q2 不会被骗 ⇒ 非 REQ；静态充分、真跑增益低 ⇒ OPT（r1289 修正 r1288 的 NA 误判）。 |
| **LIVE-NA** | 76 | pure-py/script_only/text：deliverable=脚本/deck 文本/log 分析/问答，判分校验产物结构，无 mock 无真工具调用，无实质真工具产物依赖。逐条 grep 验证：76/76 的 subprocess 仅跑候选脚本（`sys.executable cand_py`），hspice/finesim 仅出现在 deck 文本/字段名。保持 [L0,L1]。 |
| cross_shard（不计入三分类） | 2 | OtaAcReport-001 / PUvddSweep-001 走原 cross_shard 流程。 |

### LIVE-REQ 清单（47 · R2 改造优先序）

家族优先（§8）：hspice-mock / finesim-mock 全家族。按「GT 签名维度少 + 网表候选可控」优先（最易被骗）：

AOI21ArcChar, AlterDeckSplit, BistOscRccReorder, CdlBulkSanitize, CmlPvtAcReport, CTLEAC, CtleAcChar,
CTLESpec, DelayChainEdgeMeas, DelaySigma, DffSetupHoldChar, FineSimModelScopeFix, FineSimNoRefCktFix,
FineSimWorkflowRunner, GmidLut, GrDecPwrVerifTb, InvPVTchar, InvTripDelay, MinpulseRewriteRun,
NetlistLintHsp, OpampACSpec, OpampChar, PFDdeadZone, PlatMosThinIdsatIoffSweep, PorCapSweep,
PostsimPortAudit, PostsimToggleDiag, PVTalterChar, PwlStimTransform, RcurrDirClassify, SimExpl,
SlicerFbTimeOpt, SpGen, SpiceSim, SpiceTbGen, SramSNM, StdLibCharTmpl, StimPWL, StrongarmFomSweep,
TaperBufOpt, Tr0TrTfMeas, TxRonSize, Vcc2scActDeckGen, Vcc2scTranGen, VcoKvcoChar, VlshftParamOpt,
VwlpRefDeckSet（均 -001）。

### 与旧 P4 的差异（§2.1 规则 3）

| 项 | 旧 P4 (r1264) | 本轮 R1 | 依据 |
|:--|:--|:--|:--|
| sim_mock 家族（47） | T3(NA)：harness 结构 + mock 忠实 GT ⇒ 真跑无判分增益 | **LIVE-REQ**：Q2 桩可被骗（签名回放，不校验网表/measure 语义） | §2.1 Q2 严格判据「Q2=会判过 ⇒ REQ，哪怕 ref PASS+neg 全 FAIL」凌驾 P4「无判分增益」论证 |
| LisMeasExtract-001 | T2(OPT 自决不改) | **LIVE-OPT**（已含真 hspice 路径+fallback；Q2 fallback 不会被骗——B 隐藏+lis=真捕获产物，候选须真解析） | §2.1 #2：subprocess 直调真二进制 ⇒ 非 NA；但 Q2 不会被骗 ⇒ 非 REQ ⇒ OPT。r1289 修正 r1288 的 NA 误判（原 NA reason「no real-tool invocation」事实错误）。 |
| script_only/pure-py（77） | T3(NA) | LIVE-NA（一致） | deliverable=脚本/文本，无工具产物依赖 |
| T1(REQ) 合计 | 0 | 47 | 口径变更：P4 按「判分增益」，本轮按「桩可被骗性」 |
| T2(OPT) 合计 | 1（自决不改） | 1（LisMeasExtract，r1289 由 NA 修正） | NA→OPT：r1288 误判为 NA（reason 事实错误），r1289 逐条复核发现直调真 hspice 二进制 |

> 差异根源：P4 用「真跑是否改变判分结论（判分增益）」为判据；本轮 LIVE_EVAL_ORDER §2.1 用「桩会不会被骗」为判据。
> 47 条 sim_mock 在「判分增益」口径下确为 0（mock GT==真跑 GT，ref 不变），但在「桩可被骗」口径下确为 REQ
> （桩不校验网表/measure 语义，shape-right-physics-wrong 提交会假阳）。本轮口径为准。

### R2 计划（解冻后）

1. 等 `run/MEMORY_ZHULONG.md` 首行 r3' 收口 + 3-run 数字冻结。
2. 按 §3 非侵入包装逐条改造（≤3 条/轮）：原 `check`→`_check_static_impl` 一字不动 + `check_static` 包 try/except
   + 新增 `check_live(sess)` 经 eda_flow 在 .75 真跑 + `judge_layers` 加 `L2.live` + JSON `test`/磁盘 `check.py` sha 同步。
3. 每条加 ≥1 live-neg（静态全过、实跑产物错），§5 七项全勾。
4. 收口后报 A 汇总 → 报 zhulong（口径变更候选：47 条升 L2.live）。

---

## R1 桩体检实证 + 再复核（2026-11-26 r1290 · 仍只读）

> 🔴 冻结窗口仍未解冻（r3' 47.8% @ wake#2065，ETA ~11-27 00:12）。本轮在 r1289 全量 grep 三分类基础上，
> 把 r1289 的 **Q2=会判过** 从「grep 推断的统一模板断言」升级为「逐条实证」：对代表 case **真造一个
> shape-right-physics-wrong 提交跑 check.py**，看桩会不会判过。只读：仅改 `live_eval_review_B.tsv`
> 的 live_evidence 列 + 本节 + 1 条 verdict 修正，🚫 未碰 `reference/*/check.py` / `cases/*.json`。

### 实证 1：AOI21ArcChar-001（hspice-mock · candidate-authored deck）→ REQ **实证确认**

- **类型 A（候选自建 deck）**：check.py `run_candidate(script, b_spec_p, b_cell, td, "B")` 传 spec+cell，
  候选 harness **自己生成** `.alter` deck（`.inc` cell + `.param` 签名 + stimulus + `.measure`）。
- **作弊手法**：造 `cheat_harness.py`，deck 里只写正确的 `.param vddv/cload/kp_n/.../vto_n/...` 签名行 +
  `v<pin> pwl/dc` stimulus 行（桩 `_parse_section` 只解析这些），**网表换成垃圾**：无 `.inc`、无 `xaio` 实例、
  仅 `rdummy zn 0 1k`。真 HSPICE 下 `t_out` measure 必 `failed`（zn 永不翻转）→ tpd=null；但桩按签名查表回放真 GT。
- **实证结果**：`AOI21_DEBUG=1 python3 check.py submit.zip workdir` → **13/13 conds全 PASS，verdict=PASS**。
  cond f `cand_baseline=0.3292213 gt_baseline=0.3292213`（候选报值==GT，因两者都走同一桩+同一签名）。
- **结论**：Q2=会判过 **实证成立**（非推断）。桩不校验网表拓扑/measure 语义，garbage-netlist 提交假阳。
  REQ 稳固。此手法可推广到全部「候选自建 deck」的 sim_mock case（Type A）。

### 实证 2：CTLESpec-001（finesim-mock · candidate-runs-provided-deck）→ REQ **过度分类，修正为 OPT**

- **类型 B（候选跑给定 deck）**：check.py `_run_candidate(script, TB_B, SPEC_B, tmp)` 传 **提供的** tb_b.sp，
  候选 `ctle_spec_check.py` `shutil.copy(tb_path,tmpdir); run_sim(tb_path,...)` —— 候选**不造网表**，
  只跑 finesim + 解 .log + 查 spec。
- **桩 `_detect`**：按 `.param rs=50`(B)/`rs=200`(A) 或 `.subckt ctle_b`/`ctle_a` **名字** 选 GT_B/GT_A 回放，
  不校验网表内容。看似同 Type A 可骗——但：
  - **候选无法 hardcode GT**：SUT 沙箱不含 check.py / 桩源码，GT_B 值对候选不可见；唯一拿 GT 的途径是跑 finesim(桩) 解 .log。
  - **候选无法注入 garbage physics**：tb_b.sp 是 hidden 输入，候选只读不写；候选即便自建带 `.subckt ctle_b` 名字的垃圾 deck 跑桩，拿到的仍是同一 GT_B（与跑真 tb_b.sp 同结果），**无判分优势**。
  - **judge 有牙**：cond l cross-input guard 在 (tb_a, spec_b) 上跑候选，要求 dc_a≈GT_A 且 ≠GT_B —— 强制候选真跑 sim+解 .log（hardcode GT_B 必挂 l）；cond e/h/i/j 验候选 spec-checking 逻辑本身。
- **结论**：§2.1 Q2「shape-right-physics-wrong 提交会判过」**不成立**——候选既不产物理也无法 hardcode，
  桩是忠实占位（mock GT==.75 真 finesim 对该 tb 的 GT）。r1289「deck-driven 桩→REQ」的统一推断对此类**过粗**。
  **verdict REQ→LIVE-OPT**（保守：仍 subprocess 调 sim 工具；真 finesim 对该固定 tb 增益边际，但非零——可验候选是否篡改 hidden tb 路径，故不降到 NA）。

### 关键区分：Type A vs Type B（r1289 统一推断的盲区）

r1289 把 47 条 sim_mock 一律按「deck-driven 桩→Q2 可骗→REQ」处理。实证发现 Q2 是否成立取决于**候选是否自建被仿真的 deck**：

| 类型 | 候选角色 | Q2 garbage-physics 骗法 | 案例 |
|:--|:--|:--|:--|
| **A 候选自建 deck** | harness 读 spec+cell → 生成 deck → 跑 sim | **成立**：造对 `.param` 签名、网表全错，桩回放 GT → 假阳 | AOI21ArcChar ✅实证 |
| **B 候选跑给定 deck** | checker 读提供的 tb → 跑 sim → 解 log → 查 spec | **不成立**：候选不造网表、不能 hardcode GT（SUT 瞎）、桩==真工具对该 tb | CTLESpec ✅分析 → OPT |

> 判据信号（在 check.py，不在 prompt）：`run_candidate` 传 **spec+cell**（Type A）vs 传 **tb/deck 文件路径**（Type B）。

### r1290 verdict 变更（仅 1 条）

| case | r1289 | r1290 | 依据 |
|:--|:--|:--|:--|
| CTLESpec-001 | LIVE-REQ | **LIVE-OPT** | Type B：候选跑给定 tb，Q2 N/A，桩忠实，judge 有牙（cond l cross-input） |

### 待办（下一只读轮 / R2 前置）

- 逐条核 47 条的 `run_candidate` 传参，分 Type A / Type B。Type A 维持 REQ（待 R2 改造）；
  Type B 复核是否亦过粗（疑似 B 候选：CTLESpec 已改；待核 NetlistLintHsp/PostsimPortAudit/PostsimToggleDiag/
  CdlBulkSanitize/MinpulseRewriteRun 等「checker/lint/audit」语义 case）。
- 心跳：`LIVE: B review=126/126 · REQ=46(done 0) · OPT=2(done 0) · NA=76 · L2.live 0→0`（REQ 47→46，OPT 1→2）。
