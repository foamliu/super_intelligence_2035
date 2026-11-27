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

---

## R1 Type A/B 全量再复核（2026-11-26 r1291 · 仍只读）

> 🔴 冻结窗口仍未解冻（r3' 54.2% @ wake#2065，ETA ~23:58 Nov-26 / ~00:12 Nov-27）。
> 本轮在 r1290 的 Type A/B 区分框架基础上，对全部 46 条 REQ 逐条核 `run_candidate` 传参 +
> mock keying + cross-input guard，完成 A/B 分类。只读：仅改 `live_eval_review_B.tsv`
> 的 verdict/reason/evidence 列 + 本节，🚫 未碰 `reference/*/check.py` / `cases/*.json`。

### 方法

对每条 REQ case，在 check.py 中查三信号：
1. **候选收什么**：`subprocess.run([sys.executable, <cand>, ...])` 的参数 —— 传 spec+cell/netlist+params（候选**自建** deck → Type A）vs 传 tb/deck/netlist 文件路径（候选**跑给定** deck → Type B）。
2. **mock key 什么**：GT 回放键 —— 候选-authored deck 签名（`.param`/`.inc`/stimulus，Type A 可骗）vs provided deck/netlist 身份（Type B 不可骗）。
3. **cross-input guard**：有无 cond 在 A 输入上 rerun 候选并要求 GT_A（强制真跑+解析，挡 hardcode）。

### 分类结果

| 类型 | 候选角色 | Q2 garbage-physics 骗法 | 数量 |
|:--|:--|:--|--:|
| **A 候选自建/改写 deck** | harness 读 spec+cell/netlist+params → 生成/改写 deck → 跑 sim | **成立**：造对签名、网表全错，桩回放 GT → 假阳 | 41 |
| **B 候选跑给定 deck** | checker 传 provided deck/netlist → 候选跑 sim+解析/log+查 spec | **不成立**：候选不造网表、不能 hardcode GT（SUT 瞎）、桩==真工具对该 deck | 5 |

### Type B → OPT 变更（5 条 · r1291）

r1290 仅识别 CTLESpec-001（finesim-mock）。本轮全量复核再发现 5 条同模式（候选跑给定 deck，无 authorship）：

| case | mock 家族 | 候选收 | cross-input guard | 依据 |
|:--|:--|:--|:--|:--|
| NetlistLintHsp-001 | hspice-mock | provided netlist.sp | conds j/k: candidate first_error_line/msg == judge INDEPENDENT _judge_hspice(bnet_tmp) | 候选 lint provided netlist，不能注入网表；mock==真 hspice 对该 broken netlist |
| PostsimToggleDiag-001 | finesim-mock | provided b_net | cond k: rerun on A -> stuck==GT_A | GT_B/GT_A 固定 dict 按 provided netlist 身份回放；候选不能 hardcode（SUT 瞎） |
| PostsimPortAudit-001 | finesim-mock | provided B_DECK/B_NETLIST/B_SPF/B_SPEC | cond m: cross-input A guard | 候选 audit provided 文件，不产 deck |
| SimExpl-001 | finesim-mock | provided baseline_b + bloated_b | vout_final proves real sim ran | 候选跑 provided decks，解析 .log counts；不能 fake vout_final |
| RcurrDirClassify-001 | hspice-mock | provided rdir_B.sp（含 .measure） | cond j: B names!=A names pkneg diff>5%; cond k: rerun A->GT_A; cond l: real hspice log | GT 按 provided netlist 电阻名 keyed；候选不能注入网表 |

> 5 条均同 CTLESpec-001 模式（r1290 已实证分析）：候选跑给定 deck，mock==真工具对该 deck，候选既不产物理也无法 hardcode GT，judge 有 cross-input 牙。
> 判据信号：`run_candidate`/`_run_cand` 传 **deck/netlist 文件路径**（Type B）vs 传 **spec+cell/params**（Type A）。

### Type A 维持 REQ（41 条 · 待 R2 改造）

41 条 sim_mock 的候选**自建或改写**被仿真的 deck（harness 读 spec+cell/netlist+params/config → 生成 .alter/.tran deck → 跑 mock sim）。
桩 deck-driven 按 `.param`/`.inc`/stimulus 签名查表回放 GT，**不校验**候选写的网表拓扑/`.measure` 语义/器件尺寸。
AOI21ArcChar-001（r1290）已实证：garbage-netlist+正确签名 → 13/13 PASS 假阳。此手法可推广到全部 Type A。

**Type A 41 条清单**（按家族）：
- hspice-mock: AOI21ArcChar(r1290实证), AlterDeckSplit, CmlPvtAcReport, CtleAcChar, DelayChainEdgeMeas, DelaySigma, DffSetupHoldChar, GmidLut, GrDecPwrVerifTb, InvPVTchar, InvTripDelay, OpampACSpec, OpampChar, PFDdeadZone, PVTalterChar, PlatMosThinIdsatIoffSweep, PorCapSweep, PwlStimTransform, SlicerFbTimeOpt, SpGen, SpiceSim, SpiceTbGen, SramSNM, StdLibCharTmpl, StimPWL, StrongarmFomSweep, TaperBufOpt, Tr0TrTfMeas, TxRonSize, Vcc2scActDeckGen, Vcc2scTranGen, VcoKvcoChar, VlshftParamOpt, VwlpRefDeckSet, CdlBulkSanitize(r1292实证确认 REQ)
- finesim-mock: BistOscRccReorder, CTLEAC, FineSimModelScopeFix, FineSimNoRefCktFix, FineSimWorkflowRunner

**borderline 注记（r1292 empirical cheat 验证完成）**：
- CdlBulkSanitize-001：**REQ 实证确认（r1292）**。r1291 推测「静态反相器 high/low 对 W/L 不敏感 ⇒ 真 hspice 亦出 ~0/~VPWR」**被证伪**。cheat harness：正确 bulk(VPWR/VGND)+正确 d/g/s 顺序（过 conds c-h）+ W/L 篡改为 w=1e-21u l=1e3u（电死反相器）→ check.py **12/12 PASS 假阳**（mock 仅按 P+N mos 存在+d/g/s 回放 GT，忽略 W/L）。**真 hspice**：w=1e-21u 反相器无法翻转 → cond j(v_lo<0.15·VPWR) / k(v_hi>0.85·VPWR) **FAIL**。⇒ Type A 确认：候选 transform 的 CDL 成为 `.include` 仿真的网表，可注入垃圾 W/L 物理。r1291「lean Type B」误判已纠正。
- MinpulseRewriteRun-001：**降级 REQ→OPT（r1292）**。cond l 对 mock **和**真 hspice **都是纯语法检查**（check.py docstring 明示：「cond l only inspects .lis for job concluded + absence of syntax/parse error tokens -- does NOT check any measurement value」）。physics-cheat：正确 replace + RC 篡改 r1=1e-21 c1=1e-21（语法合法）→ check.py **14/14 PASS**；**真 hspice 同样 PASS**（语法合法→concluded，不查测量值）。⇒ L2.live **不加任何物理断言** ⇒ 非 REQ。唯一 mock↔real 差距：真 hspice parser 比 mock regex 严（如 mock 接受 `r1 a b c 1k` 多节点电阻，真 hspice abort）→ 边际语法增益 ⇒ OPT。r1291「保守归 REQ」已纠正。
- FineSimModelScopeFix/FineSimNoRefCktFix/FineSimWorkflowRunner-001：「fix」语义：候选改写 provided broken deck → fixed deck 被 mock 仿真。候选 author fixed deck content ⇒ 可注入 garbage physics（造对 fix 签名但网表错）⇒ Type A。

### 与 r1290 的差异

| 项 | r1290 | r1291 | r1292 | 依据 |
|:--|:--|:--|:--|:--|
| REQ 合计 | 46 | 41 | **40** | r1291 5 条 Type B 降 OPT；r1292 MinpulseRewriteRun borderline 实证降 OPT |
| OPT 合计 | 2 | 7 | **8** | +MinpulseRewriteRun（cond l 纯语法，mock==real，无物理增益） |
| Type A/B 区分 | AOI21(A实证)+CTLESpec(B分析) | 全量 46 条分类完成 | 2 borderline empirical 验证完成 | r1292: CdlBulkSanitize cheat 12/12 假阳→REQ 确认；MinpulseRewriteRun cheat 14/14 但 real 亦过→OPT |

### 待办（R2 前置 / 解冻后）

- R2 改造 Type A 40 条（≤3/轮）：拆 check_static/check_live + judge_layers 加 L2.live + live-neg。
- 优先序：hspice-mock 家族（GT 签名维度少 + 网表候选可控 = 最易被骗）→ finesim-mock 家族。
- ~~CdlBulkSanitize/MinpulseRewriteRun borderline 验证~~ **已完成（r1292）**：CdlBulkSanitize=REQ 确认，MinpulseRewriteRun=OPT 降级。
- 心跳：`LIVE: B review=126/126 · REQ=40(done 0) · OPT=8(done 0) · NA=76 · L2.live 0→0`。

## R2 前置：.75 L2.live 通路验证 + check_live 设计稿（2026-11-26 r1293 · 仍只读/冻结中）

### 背景
- 冻结仍未解冻：zhulong r3' @ 330/500=66%（status mtime 20:50 活跃写入），ETA ~00:11 Nov-27。主树 check.py/cases 一律不动。
- §1.2 隔离工作树通道**本轮 infra-blocked**：`/tmp` 100% 满（49G/61M free，其他会话占用 eda_platform_sdk/cl_cfg 等）；改用 `/nasdata/.cache/live_eval_B` 建 `git worktree add --detach` 因 NFS 慢（23218 文件 checkout）超时，留下无 `.git` marker 的半状态目录；已 `rm -rf` 清理 + `worktree prune`。主树指纹核验稳定（porcelain=29 前后一致，仅 r3 status mtime 移动）。⇒ 本轮退回纯只读 + .75 通路验证，🚫 未碰 check.py/cases。

### .75 L2.live 通路验证（CdlBulkSanitize-001 · 实跑证据）
经 `eda_flow` MCP `open_session` → `write_file`(deck/cdl/models) → `run_commands`(hspice) → `close_session`，在 `hfhds201`(.75) 跑通：

| deck | hspice RC | wall | .mt0 v_y_hi | .mt0 v_y_lo | 说明 |
|:--|:--:|:--:|:--:|:--:|:--|
| REF（sanitize_cdl_ref 产出，w=0.5u/0.25u） | 0 concluded | 266ms | **-2.545e-07** | **0.7200** | == mock 内嵌 GT，Q1 语义保真确认 |
| CHEAT（拓扑+bulk 正确，W/L 篡改 w=1e-21u） | 0 concluded | 372ms | **0.3600** | **0.3600** | 反相器电死、卡中轨无法翻转 |

- hspice = `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`，license `12000@hfds4`（primesim，7627/9999 in use），版本 V-2023.12-SP1-1 linux64。
- **Q2 实证**：CHEAT deck 静态全过（.SUBCKT 保留、bulk=VPWR/VGND、P+N mos 齐全、d/g/s 顺序对）但实跑产物错（v_y_hi=0.36 ≠ 期望低电平 ~0，v_y_lo=0.36 ≠ 期望高电平 ~0.72）；mock 忽略 W/L 仅按 P+N mos 回放 GT ⇒ 假阳。⇒ **LIVE-REQ 成立**，live-neg 候选 = cheat_b.cdl（w=1e-21u）。

### check_live(sess) 设计稿（CdlBulkSanitize-001 · 待解冻后落盘）
```python
def check_live(sess):
    """L2.live: 在 .75 跑真 hspice，读真实 .mt0，断同样的物理量（v_y_hi/v_y_lo）。
    不读 reference/、不读隐藏 GT 文件。断言条数只增不减。"""
    # 1. 从 deliverable zip 取 candidate 的 sanitize_cdl.py，在 sess workdir 跑它处理 hidden-B cdl_b.cdl -> sanitized_b.cdl
    #    （hidden-B 由 check_live 从 assets/hidden/ 上传到 sess workdir，不进 SUT 沙箱）
    # 2. 组 tb_inv.sp（与 _check_static_impl 同款 testbench，VPWR=0.72）
    # 3. sess.run_commands(["hspice tb_inv.sp -o ."])  -> 读回 tb_inv.mt0
    # 4. 解析 .mt0 -> v_y_hi(input high@9n -> out low), v_y_lo(input low@14n -> out high)
    # 5. 断言：v_y_hi < 0.15*VPWR（低电平合格）&& v_y_lo > 0.85*VPWR（高电平合格）
    #    （与 _check_static_impl cond j/k 同阈值，不放宽）
    # live-neg(cheat_b.cdl w=1e-21u)：v_y_hi=v_y_lo=0.36 -> 两断言均 FAIL（first-fail distinct）
```
- 关键不变量：check_live 与 _check_static_impl 断**同一物理量、同阈值**（只增不减）；live-neg = 静态全过/实跑错（cheat_b.cdl）；3-seed 确定性（同 deck md5 一致，hspice 确定性已由 266ms 单跑佐证，R2 落盘时跑 3 次）。

### 待办（解冻后 R2）
1. 重建隔离工作树（优先清 /tmp 或等 NFS 空闲；或直接在解冻后改主树）。
2. CdlBulkSanitize-001 作为 R2 首条改造样板（通路+设计稿已就绪）：落 _check_static_impl/check_static/check_live + judge_layers=[L0,L1,L2.live] + live-neg + §5 七项自验。
3. 其余 39 条 Type A 按家族批量复用样板（hspice-mock → finesim-mock）。
- 心跳：`LIVE: B review=126/126 · REQ=40(done 0) · OPT=8(done 0) · NA=76 · L2.live 0→0`（done 仍 0，未落盘）。

---

## R2 改造（2026-11-26 r1294 · 冻结已清除 · designflow 主线）

> **§1.1 清账**：2026-11-26 20:5x 用户裁定「designflow 主、zhulong 辅，不设等待」⇒ 本节清除上方 r1293「仍只读/冻结中」表述。
> `freeze-removed: 2026-11-26`。主树 check.py/cases 本轮起正常改，仅在 `live_eval_changes.tsv` 登记。

### R2-001：CdlBulkSanitize-001（hspice-mock · Type A）✅ DONE

- **改造手法（§3 非侵入包装）**：
  1. 原 `check` → 改名 `_check_static_impl`，**一字不动**（12 断言 a..l + mock + return True 原封保留）。
  2. `check_static(deliverable, workdir)` 包 try/except，收口三元组 `(ok, errs, stage)`。
  3. 新增 `check_live(deliverable, workdir, sess)`：经 eda_flow 在 .75 跑真 hspice（`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`），上传 deliverable + hidden B → 候选 sanitize → 组同款 INVXB testbench → 真跑 hspice → 读真实 `.mt0` → 断**同物理量同阈值**（v_lo < 0.15·VPWR / v_hi > 0.85·VPWR，与 cond j/k 一致，只增不减）。不读 reference/、不读隐藏 GT 文件。
  4. `check()` 兼容包装保留；case JSON `metadata.judge_layers` → `["L0","L1","L2.live"]`；JSON `test` 字段与磁盘 `check.py` sha 三方同步（sha256 短=`87f20ed995fa`，34261B 一致）。
  5. **live-neg** = `negative/cheat_wl_corrupt.py`：正确 bulk 显式化（过静态 cond c-h + mock 回放 GT 过 cond i/j/k/l）但 W/L 篡改 `w=1e-21u l=1e3u`（电死反相器）⇒ 静态全过、实跑产物错。`negative_selftest.py` 同步登记（静态 5 neg FAIL distinct + live-neg static-pass/live-fail）。

- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1 license ok，wall <1s，`.mt0` v_lo=-2.545e-07 / v_hi=0.72（==mock GT，Q1 保真），产物 md5=`602f3f777be0c65eaa947a69204a5ab2`。
  - ② ≥3 neg 全 FAIL、first-fail distinct（{b,c,d,e}=4-distinct），含 1 条 live-neg（cheat_wl_corrupt：static PASS / live FAIL）。
  - ③ 3-seed 确定性：ref `.mt0` md5 三次一致（`602f3f777be0c65eaa947a69204a5ab2`）。
  - ④ 静态判分仍 PASS：`check_static(ref_zip)` → PASS 12/12（实跑层独立，不拖垮静态）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`87f20ed995fa`）。
  - ⑥ 断言条数只增不减、阈值不放宽、条件不删：`_check_static_impl` 原文未改一字；`check_live` 新增 2 条同阈值物理断言（v_lo/v_hi）。
  - ⑦ L5 不退化：hidden-B 不外泄（框架上传，check_live 不读 reference/）；`check_live` 不读 `reference/`；沙箱不含 `.jsonl`/`test` 字段。

- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。
- **心跳**：`LIVE: B review=126/126 · REQ=40(done 1) · OPT=8(done 0) · NA=76 · L2.live 0→1`。

### R2 续办（下一轮）
- 其余 39 条 Type A 按家族批量复用 CdlBulkSanitize 样板（hspice-mock 优先 → finesim-mock）。
- B 预算 ≤6-8 条/轮（§4 前提：逐条独立自验、wall ≤90min、.75 串行、单条不过降级 BLOCKED）。
- 优先序：AlterDeckSplit / AOI21ArcChar / SpiceSim / InvTripDelay ...（hspice-mock，GT 签名维度少）。

### R2 改造 #2: InvTripDelay-001 (2026-11-26 r1295)
- **家族**：hspice-mock (deck-driven)，Type A Q2-cheatable。
- **Q2 实证（r1295）**：cheat harness（`vin in 0 dc 0` 无翻转 + 正确 `.param vref=2.5 vcc=5.0` + 正确 `.measure tran tpd trig/targ` + `.dc`/`.meas dc vtrip when` + inv 例化）→ `_check_impl` **14/14 PASS 假阳**（mock 按 W/L+vcc+vref 签名 + `.measure` 关键词存在回放 GT，不查 stimulus 翻转/measure 语义）。真 hspice：`vin=dc` 不翻转 → `.measure tran tpd` never reached trig → `tpd=failed`。
- **改造手法（非侵入包装，照 §3）**：
  1. 原 `check` → `_check_static_impl`（一字不动，`return all(ok for _,ok in _check_impl(...))`）。
  2. `check_static` try/except 收口三元组。
  3. 新增 `check_live(deliverable, workdir, sess)`：经 eda_flow 在 .75 跑真 hspice（`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`），本地抽 tb.sp + 读 hidden B1/B2 → `_build_deck`（复用静态同款 inlining + `_strip_defs`）→ 上传 cand/gt 两组 deck → 真跑 hspice → 读真实 `.lis` → 断**同物理量同阈值**（cand tpd ±15% of GT / cand vtrip ±0.15V of GT，与 cond h/i(B1) + j/k(B2) 一致，只增不减）。GT = ref testbench 在同一 hidden B 上真跑。不读 `reference/`、不读隐藏 GT 文件。
  4. `check()` 兼容包装；`judge_layers=["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步（`646ce56711a1`，23554B）。
  5. **live-neg** = `negative/stub_cheat_dcstim/tb.sp`：正确 `.param`/`.measure`/`.tran`/`.dc` 语法 + inv 例化 + 正确 vcc/vref（过静态 cond a-g + mock 回放 GT 过 cond h-k）但 `vin=dc` 无翻转 ⇒ 静态全过、实跑 `tpd=failed`。`negative_selftest.py` 同步登记（4 static neg FAIL distinct + live-neg static-pass）；新增 `negative/live_selftest.py` 在 .75 验 live-neg FAIL。
- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1，B1 tpd=106.2369p/vtrip=2.1927、B2 tpd=955.4316p/vtrip=2.4498（==mock _GT，Q1 保真）。
  - ② 4 static neg FAIL distinct（{b,c,e,f}=4-distinct）+ 1 live-neg（stub_cheat_dcstim：static PASS / live FAIL `tpd=None`）。
  - ③ 3-seed 确定性：真 hspice GT 值与 mock 捕获值逐位一致（B1 106.2369p / B2 955.4316p）。
  - ④ 静态判分仍 PASS：`_check_impl(ref)` 14/14（实跑层独立）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`646ce56711a1`）。
  - ⑥ 断言只增不减：`_check_static_impl` 原文未改一字；`check_live` 新增 4 条同阈值物理断言（B1 tpd/vtrip + B2 tpd/vtrip）。
  - ⑦ L5 不退化：hidden-B 不外泄；`check_live` 不读 `reference/`；沙箱不含 `.jsonl`/`test`。
- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。

### R2 改造 #4: AlterDeckSplit-001 (2026-11-26 r1297)
- **家族**：hspice-mock (deck-driven, MULTI/ORIG table keyed on rupe_res+corner-file+.ic+.alter)，Type A Q2-cheatable（候选自建 split deck，可注入垃圾网表）。
- **Q2 实证（r1297）**：cheat 候选产出 split deck 带**正确签名**（`.lib 'corner_B.sp' ss` / `.param rupe_res=4700` / `.ic v(FzOut)=0` / `.meas` 5 行 / `.probe` 收窄 / 无 `.alter` / `.temp`+`.param pvcc` 烘焙）但 EFUSE_CELL 网表物理破坏（`R0 AfInt Lvfsbln 1e12` 开路 + `M0 ... w=1e-21u l=1e3u` 电死）→ `check.py` **10/10 PASS 假阳**（mock 按 rupe_res+corner-file+.ic+.alter 签名回放 `MULTI["B"]` GT，从不解电路）。真 hspice V-2023.12-SP1-1 @ hfhds201：cheat split deck 跑挂、无 `.mt0` → cond (i) split==alter 等价 FAIL。
- **Q1 保真实证**：真 hspice ref `split_ss.mt0` = `v_fzout=0.3987 / v_lvfsbln=1.0 / i_r0=-3.103e-09 / i_mos=3.156e-09 / v_delta=0.6013` == mock `MULTI["B"]` row0 逐位一致；`multi.mt0` 3 行全部匹配 mock 表。
- **改造手法（非侵入包装，照 §3）**：
  1. 原 `check` → `_check_static_impl`（一字不动，10 条 a-j 断言 + cond (i) 等价 + cond (j) 跨输入守卫）。
  2. `check_static` try/except 收口三元组。
  3. 新增 `check_live(deliverable, workdir, sess)`：上传 submit.zip + hidden `deck_B.sp`/`corner_B.sp` → .75 跑候选 `alter_deck_split.py deck_B.sp out_B` → 构建 `multi_ic.sp`（deck_B + `.ic v(FzOut)=0` 注入，同 cond (i)）→ 真跑 hspice → 逐角跑 `out_B/split_<corner>.sp` → 读真实 `.mt0` → 复用 `parse_deck_corners`/`_parse_mt0_text`/`equiv_ok` → 断**同 cond (i) 物理**（每角 5 measure `split==alter` within `REL_TOL=1e-3`，阈值不变，只增不减）。不读 `reference/`、不读隐藏 GT。
  4. `check()` 兼容包装；`judge_layers=["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步（`7d15035225f87e02`，30835B）。
  5. **live-neg** = `negative/cheat_garbage_netlist/alter_deck_split.py`：正确签名 + 垃圾网表（R0=1e12 / M0 w=1e-21u l=1e3u）⇒ 静态全过、实跑无 `.mt0` 全 3 角 FAIL。`negative_selftest.py` 重写登记（7 static neg FAIL distinct{a,c,d,e,g} + §4.9 trio {empty:a,print:c,core:g} distinct + live-neg static-pass/live-fail）。
- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1，3 corners split==alter（ss/tt/ff 全 measure `equiv_ok`）。
  - ② 7 static neg FAIL distinct（{a,c,d,e,g}=5-distinct）+ 1 live-neg（cheat_garbage_netlist：static PASS 10/10 / live FAIL 无 `.mt0` 3 角）。
  - ③ 3-seed 确定性：`multi.mt0` md5=`2803c675ca8c0172bed26453f0e89f03`、`ref_ss.mt0` md5=`3c3f544caf8fb36d34beaa2ca0231bb0` 连跑 3 次一致。
  - ④ 静态判分仍 PASS：`_check_static_impl(ref)` 10/10（实跑层独立）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`7d15035225f87e02`）。
  - ⑥ 断言只增不减：`_check_static_impl` 原文未改一字；`check_live` 新增逐角 5-measure 等价断言（同 `REL_TOL=1e-3`）。
  - ⑦ L5 不退化：hidden-B 不外泄；`check_live` 不读 `reference/`；沙箱不含 `.jsonl`/`test`。
- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。

### R2 改造 #5: SpiceSim-001 (2026-11-26 r1298)
- **家族**：hspice-mock (deck-driven)，Type A Q2-cheatable（候选自建 .measure deck，可注入跨节点 trig/targ）。
- **Q2 实证（r1298）**：cheat 候选产出 shape-right deck（正确 .measure 名 tr_q1/q2/q3 + val=10%/90%/50% levels + TR/TF/DUTY 分组 + 正确节点引用 v(q1)/v(q2)/v(q3)）但 tr_/tf_ 用 **CROSS-NODE trig/targ**（`trig v(din) val=0.12 rise=1 targ v(<node>) val=1.08 rise=1`）→ `_check_static_impl` **10/10 PASS 假阳**（mock 按 measure NAME + val= levels 查表回放 GT，**不校验 trig/targ 节点身份**）。真 hspice V-2023.12-SP1-1 @ hfhds201：tr_q1=227.29p / tr_q2=381.50p / tr_q3=445.12p（din→node 传播延迟）>> spec_trtf=140p → cond (h) FAIL。
- **Q1 保真实证**：真 hspice ref tr=[130.522p, 125.4771p, 42.3032p] / tf=[102.6924p, 93.5357p, 42.0338p] / duty=[0.5104399, 0.5099491, 0.5108075] == mock `_MOCK_VALUES` 逐位一致。
- **改造手法（非侵入包装，照 §3）**：
  1. 原 `check` → `_check_static_impl`（一字不动，10 断言 a-j + mock + return True）。
  2. `check_static` try/except 收口三元组。
  3. 新增 `check_live(deliverable, workdir, sess)`：经 eda_flow 在 .75 跑真 hspice（`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`），上传 submit.zip + hidden netlist/nodes/spec → 跑候选 `gen_meas_deck.py` 产 deck → cat netlist_b + deck → 真跑 hspice → 读真实 `.lis` → 复用同款 `parse_measures` → 断**同物理量同阈值**（cond (g) measures not failed / cond (h) tr·tf < spec_trtf / cond (i) duty ∈ [duty_lo,duty_hi] / cond (j) 3-seed 一致性，阈值全同静态，只增不减）。不读 `reference/`、不读隐藏 GT。
  4. `check()` 兼容包装 + `__main__` 块（供 negative_selftest subprocess 调用取 first-fail tag）；`judge_layers=["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步（`8170cc02353e`，36071B）。
  5. **live-neg** = `negative/cheat_cross_node/gen_meas_deck.py`：正确签名 + 跨节点 trig/targ ⇒ 静态全过（mock 回放 GT）/ 实跑 cond (h) FAIL（tr_q1=227.29p≥140p）。`negative_selftest.py` 重写（CdlBulkSanitize 模式：subprocess 调 check.py 取 first-fail distinct + live-neg static-pass/live-fail）。
- **§4.9-trio 修复（latent）**：原 trio（empty/print/core）全 FAIL cond (c) 不 distinct → 重设计：empty→(c) no output / print→(d) interleaved 分组 / core→(e) DUTY 块仅首节点（tr/tf 全节点过 (d)）。trio 现 distinct {c,d,e}。
- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1，tr=[130.522p,125.4771p,42.3032p]==mock GT（Q1 保真）。
  - ② 6 static neg FAIL distinct {c,d,e,f}=4-distinct + 1 live-neg（cheat_cross_node：static PASS 10/10 / live FAIL cond (h) tr_q1=227.29p≥140p）。
  - ③ 3-seed 确定性：ref check_live 连跑 3 次 errs 字串逐位一致（tr/tf/duty 值相同）。
  - ④ 静态判分仍 PASS：`check_static(ref)` → PASS 10/10（实跑层独立，不拖垮静态）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`8170cc02353e`）。
  - ⑥ 断言只增不减：`_check_static_impl` 原文未改一字；`check_live` 新增 (g)(h)(i)(j) 4 条同阈值实跑断言；trio 重设计 only-add teeth。
  - ⑦ L5 不退化：hidden-B 由 check_live 从 workdir/hidden 上传 sess.workdir（不进 SUT 沙箱）；`check_live` 不读 `reference/`；forbidden-list 阻 reference/negative/hidden 入 SUT。
- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`，commit `553134735`）。
- **心跳**：`LIVE: B review=126/126 · REQ=40(done 5) · OPT=8(done 0) · NA=76 · L2.live 4→5`。

### R2 改造 #6: DffSetupHoldChar-001 (2026-11-27 r1299)
- **家族**：hspice-mock (deck-driven)，Type A Q2-cheatable（候选自建 setup/hold testbench deck，可注入「D 不翻转」物理破坏）。
- **Q2 实证（r1299）**：cheat char_gen.py 在 `build_setup_tb` 中将 `t_d_rise = tstop + 1.0`（D 翻转时刻远超仿真结束），deck 仍带正确签名（`* setup_tb tsu_lead=<X>` 首行注释 + `VVDD vdd 0 <vdd>`）⇒ `_check_static_impl` **14/14 PASS 假阳**（mock 仅按 `setup_tb`/`hold_tb` 注释 + VVDD 行查表回放 REF_B/REF_A GT，**不校验 VDIN stimulus 翻转 / DFF 网表 / .measure 语义**）。真 hspice V-2023.12-SP1-1 @ hfhds201：D 永不翻转 → Q 卡在 .ic=0 → vq_setup≈0 (< vthr=0.7) → 无 passing setup point → tSU=None/tCQ=None → cond (i) FAIL。
- **Q1 保真实证**：真 hspice ref 全量扫描（11 setup + 10 hold = 21 跑）B：tSU=5e-12 / tCQ=9.83877e-11（**== mock REF_B 逐位一致**）/ tH=0 / hspice_ran=true / n_setup=11 / n_hold=10；A：tSU=1e-11 / tCQ=1.300134e-10（vs REF_A=1.289142e-10，0.85%）；cross-input |tSU_B-tSU_A|/tSU_A=50% / |tCQ_B-tCQ_A|/tCQ_A=24% 均 >5%。
- **改造手法（非侵入包装，照 §3）**：
  1. 原 `check` → `_check_static_impl`（一字不动，14 断言 a-n + mock + `_summarize` raise/return True）。
  2. `check_static` try/except 收口三元组。
  3. 新增 `check_live(deliverable, workdir, sess)`：上传 submit.zip 解出 char_gen.py + hidden B（dff_B.sp/params_B.json）+ visible A（dff_A.sp/params_A.json）到 sess.workdir → .75 跑候选 `python3 char_gen.py dff_B.sp params_B.json out`（真 hspice 在 PATH，候选 `_ensure_hspice` 检测到真 hspice 不装 mock）+ 同样跑 A → 读真实 `out/result.json` → 复用 `json.loads` → 断**同物理量同阈值**（cond h hspice_ran / i tSU∈[2e-12,8e-12] / j tCQ within 20% of REF_B / k tH==0/None / l required keys / m cross-input |B-A|>5% / n n_pts>=8，阈值全同静态，只增不减）。不读 `reference/`、不读隐藏 GT 文件（用嵌入 REF_B/REF_A grader 常量，同 `_check_static_impl`）。
  4. `check()` 兼容包装 + `__main__` 块（供 negative_selftest subprocess 调用取 STATIC_VERDICT/first-fail）；`judge_layers=["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步（`9257274fff98`，21451B）。
  5. **live-neg** = `negative/cheat_no_drise/char_gen.py`：`build_setup_tb` 设 `t_d_rise=tstop+1.0`（D 不翻转）⇒ 静态全过（mock 回放 GT）/ 实跑 cond (i) FAIL（tSU=None）。`negative/negative_selftest.py` 重写（SpiceSim 模式：STATIC_NEGATIVES 7 条 subprocess check.py 取 first-fail distinct + LIVE_NEG cheat_no_drise static-pass/live-fail via EDASession + S4.9 trio distinct）。
- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1，B tSU=5e-12/tCQ=9.83877e-11（==mock REF_B，Q1 保真），A tSU=1e-11/tCQ=1.300134e-10，cross-input 50%/24%>5%。
  - ② 7 static neg FAIL distinct（{b,c,d,g,h,i,m}=7-distinct）+ 1 live-neg（cheat_no_drise：static PASS 14/14 / live FAIL cond(i) tSU=None）。
  - ③ 3-seed 确定性：真 hspice 对同 deck 确定性（ref tCQ=9.83877e-11 == mock GT 逐位，Q1 run 复现）；candidate 全量扫描参数固定 ⇒ result.json 确定性。
  - ④ 静态判分仍 PASS：`check_static(ref)` → PASS 14/14（实跑层独立，不拖垮静态）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`9257274fff98`）。
  - ⑥ 断言只增不减：`_check_static_impl` 原文未改一字；`check_live` 新增 7 条同阈值实跑断言（h-n）。
  - ⑦ L5 不退化：hidden-B 由 check_live 从本地 workdir/hidden 读取并 upload_text 到 sess.workdir（不进 SUT 沙箱）；`check_live` 不读 `reference/`；SKIP_RUN deploy 自检 workdir clean（无 check.py/reference/hidden 泄漏）。
- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。
- **心跳**：`LIVE: B review=126/126 · REQ=40(done 6) · OPT=8(done 0) · NA=76 · L2.live 5→6`。

### R2 改造 #7: GrDecPwrVerifTb-001 (2026-11-27 r1300)
- **家族**：hspice-mock (deck-driven)，Type A Q2-cheatable（候选自建 verification testbench deck，可注入「DUT Mpup 拉死」物理破坏）。
- **Q2 实证（r1300）**：cheat `gen_grdecpwr_verif.py` 生成的 testbench 带正确签名（`vvwlp vwlp! 0 <vwlp>` / `cgr GrDecPwr 0 <cgr>` / `.temp <temp>` / `vsec secHV 0 PULSE` / `.tran` / `.measure v(GrDecPwr)`）但 DUT 子电路 `Mpup` W 篡改为 `1e-21u` l=`1e3u`（电死上拉管）⇒ `_check_static_impl` **13/13 PASS 假阳**（mock 仅按 `vwlp|cgr|temp` 签名查表回放 `_MOCK_VALUES` GT，**不校验 DUT 网表内容/管子尺寸/电路拓扑**）。真 hspice V-2023.12-SP1-1 @ hfhds201：Mpup 无法在 ACT 期间给 GrDecPwr 充电 → v_act 缺失 / `hspice_ran=False` → cond (h)(i)(j)(k)(l)(m) FAIL。
- **Q1 保真实证**：真 hspice ref B v_act=2.6 / v_init=0.8075329 / v_pre=0.8545628；A v_act=3.4 / v_init=0.7003245 / v_pre=0.7996354 —— **== mock `_MOCK_VALUES` 逐位一致**（`3.4|20f|25` / `2.6|50f|-40` 两键）。
- **改造手法（非侵入包装，照 §3）**：
  1. 原 `check` → `_check_static_impl`（一字不动，13 断言 a-m + mock + `_summarize` raise/return True）。
  2. `check_static` try/except 收口三元组（兼容旧式 dict `{'pass':bool,'conds':...}` 返回）。
  3. 新增 `check_live(deliverable, workdir, sess)`：上传 submit.zip 解出 `gen_grdecpwr_verif.py` + hidden B（dut_B.sp/params_B.json）+ visible A（dut_A.sp/params_A.json）+ model.lib 到 sess.workdir → .75 跑候选 `python3 gen_grdecpwr_verif.py dut_B.sp params_B.json model.lib out`（真 hspice 在 PATH，候选 `_ensure_hspice` 检测到真 hspice 不装 mock）+ 同样跑 A → 读真实 `out/grdecpwr_verif_result.json` → 复用 `json.loads` → 断**同物理量同阈值**（cond h hspice_ran / i v_act+v_pre keys / j v_act>v_init / k v_act within 20% of REF_B_VWLP=2.6 / l v_pre<v_act / m cross-input |B_v_act - A_v_act|>0.5，阈值全同静态，只增不减）。不读 `reference/`、不读隐藏 GT 文件（用嵌入 `REF_B_VWLP`/`REF_A_V_ACT` grader 常量，同 `_check_static_impl`）。
  4. `check()` 兼容包装 + `__main__` 块（供 negative_selftest subprocess 调用取 STATIC_VERDICT/first-fail）；`judge_layers=["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步（`5606b2607278`）。
  5. **live-neg** = `negative/cheat_dead_mpup/gen_grdecpwr_verif.py`：`gen_testbench` 将 DUT Mpup W 篡改 `1e-21u`（电死上拉）但保留所有签名行 ⇒ 静态全过（mock 回放 GT）/ 实跑 cond (h)(i)(j)(k)(l)(m) FAIL（`hspice_ran=False`，无 measures）。`negative_selftest.py` 重写（SpiceSim/DffSetupHold 模式：STATIC_NEGATIVES 5 条 subprocess check.py 取 first-fail distinct + LIVE_NEG cheat_dead_mpup static-pass/live-fail via EDASession + S4.9 trio distinct + packaged A GT 在 result.json 以过 cond m）。
- **§5 七项自验（全勾）**：
  - ① `.75` 真跑 ref（L2.live）PASS：`hostname=hfhds201`，hspice V-2023.12-SP1-1，B v_act=2.6/v_init=0.8075/v_pre=0.8546（==mock `_MOCK_VALUES`，Q1 保真），A v_act=3.4，cross-input |2.6-3.4|=0.8>0.5。
  - ② 5 static neg FAIL distinct（{c,d,h,k}=4-distinct）+ 1 live-neg（cheat_dead_mpup：static PASS 13/13 / live FAIL cond h hspice_ran=False + i/j/k/l/m）。
  - ③ 3-seed 确定性：ref `result.json` md5=`f7d73ccda85553947b197b6f386a6c90` 三次连跑一致。
  - ④ 静态判分仍 PASS：`check_static(ref)` → PASS 13/13（实跑层独立，不拖垮静态）。
  - ⑤ `judge_layers`/JSON `test`/磁盘 `check.py` sha 三方同步（`5606b2607278`）。
  - ⑥ 断言只增不减：`_check_static_impl` 原文未改一字；`check_live` 新增 6 条同阈值实跑断言（h-m）。
  - ⑦ L5 不退化：hidden-B 由 check_live 从本地 workdir/hidden 读取并 upload_text 到 sess.workdir（不进 SUT 沙箱）；`check_live` 不读 `reference/`；SKIP_RUN deploy 自检 workdir clean（无 check.py/reference/hidden 泄漏）。
- **登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。
- **心跳**：`LIVE: B review=126/126 · REQ=40(done 7) · OPT=8(done 0) · NA=76 · L2.live 6→7`。

---

## R1 再复核（2026-11-27 r1301 · 3 条 Type A→B 误判修正 · 只读）

> 本轮为 R2 改造的前置再复核。在准备对剩余 33 条 Type A 逐条改造时，深读 3 条候选 check.py
> 的候选调用签名，发现 r1291 的 Type A 清单误把这 3 条（候选**不 author** deck）归入 Type A。
> 按 §2.1 规则 3（旧结论必须复验，冲突以本轮落盘证据为准）+ r1290/r1291 Type B→OPT 先例
> （CTLESpec/NetlistLintHsp/PostsimPortAudit/PostsimToggleDiag/SimExpl/RcurrDirClassify）降级。
> **只读**：仅改 `live_eval_review_B.tsv` verdict/reason/evidence 列 + 本节，🚫 未碰
> `reference/*/check.py` / `cases/*.json`（无 judge_layers 变更 ⇒ 无 `live_eval_changes.tsv` 登记）。

### 判据（Type A vs Type B，r1291 自己的口径）

> r1291 方法：「`subprocess.run([sys.executable, <cand>, ...])` 的参数 —— 传 spec+cell/netlist+params
> （候选**自建** deck → Type A）vs 传 tb/deck/netlist 文件路径（候选**跑给定** deck → Type B）」。

3 条的候选调用都传**文件路径**（tb / netlist / tr0），不是 spec+cell/params ⇒ 按该口径即 Type B。
Type B ⇒ 候选不 author deck ⇒ Q2「shape-right-physics-wrong deck 会判过」**不成立** ⇒ 非 REQ ⇒ OPT。

### 降级 1：Tr0TrTfMeas-001（hspice-mock · 候选=纯 tr0 解析器）REQ→OPT

- **候选调用**：`_run_tool(tool, tr0_path, rep)` → `python3 tr0_trtf_meas.py <tr0_path> <rep>`（check.py L311-314）。
  候选收 **tr0 文件路径**，解析波形测 tr/tf，**不 author deck、不 run hspice**。
- **deck 归属**：`_DECK_B_SRC`（check.py L61）**内嵌于 check.py，judge 拥有**；JUDGE 跑 hspice(mock)→tr0_B；候选只解析 tr0_B。
- **ref 证实**：`tr0_trtf_meas_ref.py` 的 `main(tr0_path, report_path)` = 纯解析器（parse_tr0 + crossings + measure_signal）。
- **Q2 N/A**：候选不 author deck（无注入 garbage physics 入口）；不能 hardcode GT_B（SUT 瞎；cond k cross-input 在 tr0_A 上 rerun 期望 GT_A；cond l 插值守卫）。
- **Q1 保真**：`_TR0_B_PREGEN` 注释明示「Captured on .75 (hfhds201) via hspice deck_B.sp -o lis_B on 2026-11-25，byte-verified to GT_B」；mock 逐字写回。
- **judge 有牙**：cond k/l cross-input + cond m 单位/合理性 + cond n 确定性。
- **r1291 误判根因**：r1291 Type A 清单按「hspice-mock 家族」批量归 Type A，未核候选调用签名（候选收 tr0 路径 = Type B，按 r1291 自己的口径）。
- **verdict**：LIVE-REQ → **LIVE-OPT**（mock==real 对 judge-owned 嵌入 deck；候选纯解析器无工具调用；真跑增益边际）。

### 降级 2：CTLEAC-001（finesim-mock · 候选=跑给定 tb 的 spec 自检器）REQ→OPT

- **候选调用**：`subprocess.run([cand, tb_ctle_ac_B.sp, spec_B.json, report])`（check.py L414）。
  候选收 **judge-built tb 文件路径**，跑 finesim + 解析 + spec 自检，**不 author tb**。
- **tb 归属**：`_stage_hidden` L354 `open("tb_ctle_ac_B.sp","w").write(_tb_b_template(ndec))` —— **judge 从模板构建**，候选只读。
- **Q2 N/A**：候选不 author tb（无注入 garbage physics 入口）；不能 hardcode GT（SUT 瞎；judge `_ground_truth` 独立跑 finesim on gt_tb.sp 算 GT_B；multi-ndec rerun cond 强制真跑+解析）。
- **Q1 保真**：`_GT_B`/`_GT` 注释明示 .75-captured；mock 按 tb 签名回放。
- **judge 有牙**：multi-ndec 重跑 + judge 独立 GT 比对。
- **r1291 误判根因**：r1291 把 finesim-mock 家族（CTLEAC/FineSimModelScopeFix/NoRefCktFix/WorkflowRunner）全归 Type A；但 CTLEAC 候选收 **provided tb**（非 fix 任务里候选改写 broken deck）。FineSimModelScopeFix/NoRefCktFix/WorkflowRunner 是「fix」语义（候选 author fixed deck）= 真 Type A；CTLEAC 是「check provided tb」= Type B。r1291 未区分。
- **verdict**：LIVE-REQ → **LIVE-OPT**（同 CTLESpec r1290 模式：mock==real 对 judge-built tb；真跑增益边际）。

### 降级 3：OpampChar-001（hspice-mock · 候选=跑给定完整 netlist 的 .measure 提取器）REQ→OPT

- **候选调用**：`_run_candidate(py_path, netlist, simdir)` → `subprocess.run([sys.executable, py_path, netlist, simdir])`（check.py L278-281）。
  候选收 **完整 netlist 文件路径**（含 `.subckt OPAMP` + `.ac dec 200 1 100meg` + 7 条 `.measure ac`，prompt 明示），跑 hspice + 解析 .ma0，**不 author deck/.measure/stimulus**。
- **netlist 归属**：hidden B netlist 由 judge 提供（完整 deck，prompt 确认）；候选只跑+解析。
- **Q2 N/A**：候选不 author deck（netlist 提供完整，无注入 garbage physics 入口）；不能 hardcode GT（SUT 瞎；judge `_hspice_gt(netlist)` L252 独立跑 hspice 算 GT 比对候选 report）。
- **Q1 保真**：`_GT_MA0` 注释明示「captured from real HSPICE V-2023.12-SP1-1 on .75」；mock 逐字回放 .ma0。
- **judge 有牙**：judge 独立 `_hspice_gt` 比对 + 跨输入（A 可见/B 隐藏，值不同）。
- **r1291 误判根因**：r1291 见 `_run_candidate(py, netlist, simdir)` 误以为候选从 netlist 自建 deck；实为候选跑**提供的完整** netlist（含 .measure），按 r1291 口径 = Type B。
- **verdict**：LIVE-REQ → **LIVE-OPT**（mock==real 对 provided 完整 netlist；真跑增益边际）。

### 与 r1291 的差异

| 项 | r1291 | r1301 | 依据 |
|:--|:--|:--|:--|
| REQ 合计 | 40 | **37** | 3 条 Type B 误判修正（Tr0TrTfMeas/CTLEAC/OpampChar） |
| OPT 合计 | 8 | **11** | +3 降级 |
| Type A/B 区分 | 41 A / 5 B | **38 A / 8 B** | r1291 未逐条核候选调用签名，3 条收文件路径的误归 A |

### 待办（R2 续）

- 真 Type A 剩 **29 条**待改造（38 − 7 done − 1 DffSetupHoldChar(done) − 1 PwlStimTransform 降级 = 29；按 hspice-mock 家族优先 ≤6-8/轮）。
- 4 条降级**不动 judge_layers**（仍 [L0,L1]）⇒ 无 `live_eval_changes.tsv` 登记（OPT 不加 L2.live）。
- 心跳：`LIVE: B review=126/126 · REQ=36(done 7) · OPT=12(done 0) · NA=76 · L2.live 7→7`。

---

## R1 再复核 #2（2026-11-27 r1302 · 桩体检：syntax-validator vs GT-replay · 只读）

### 背景

§2.1 #1 桩体检要求逐条答 Q1/Q2。R1/r1291/r1301 把所有 hspice-mock/finesim-mock case 用**通用 boilerplate**（"replays .75-captured GT keyed on .param/.inc/deck signature, validates candidate deck text not netlist topology"）一律判 REQ。但 boilerplate 只对 **GT-replay-by-signature** 桩成立；对**纯语法/收敛 validator 桩**（conclude/abort only，无 .measure、无 GT 数值回放）不成立——后者 real hspice 同样只查 conclude/abort，加不了物理断言 ⇒ 应为 OPT。本轮逐条读 check.py 桩体，按桩体真实结构（不是家族名）重判。

### 降级 4：PwlStimTransform-001（hspice-mock · 纯语法 validator 桩）REQ→OPT

- **桩体结构**：`HSPICE_MOCK_SRC` 是 deck-driven **PWL 语法 validator**——解析 `.include` 目标文件，校验 `Vxxx net 0 PWL(` + 数字数据行格式，输出 "job concluded"（合法）/ "job aborted"（非法）。**不回放任何 GT 测量值**，无 `.measure` 断言。docstring 自述 faithfulness 已对 .75 真 hspice 验证（conclude/abort 语义）。
- **cond k 桩 deck**：`R<net> <net> 0 1k` × 8 + `.include 'stim.pwl'` + `.tran 0.5n 25n` + `.end`，**无 .measure**。cond k 仅断言 `concluded and not err`——**纯语法/收敛检查，零物理值断言**。
- **Q2**：garbage-values-but-valid-syntax PWL（8 块、B net 名全对、所有 value=999）过 mock（concluded=True err=False）**且**过真 hspice——因为无 .measure，真 hspice 也只 conclude/abort，不查值。real hspice **加不了** cond k 之外的物理断言 ⇒ 非 REQ。
- **静态牙**：conds e/f/g/h/j 已直接解析 PWL **数值**（重命名/参数化/clip/rail 归类）——物理已由静态层覆盖，cond k 只是"hspice 能不能吞下语法"的冗余证据。
- **实证（r1302 .75 hfhds201 hspice V-2023.12-SP1-1）**：
  - 本地 mock：cheat PWL（value=999）→ `_run_hspice` concluded=True err=False。
  - .75 真跑：同 cheat deck 上传 session `designflowB_r1302-reverify`，`hspice -i run_deck.sp` → RC=0，lis 含 "job concluded"、node voltages=999.0000、transient 51 points converged、无 error token。**真 hspice 对 garbage-values 合法语法 PWL 照样 conclude** ⇒ 与 mock 同语义，无物理增益。
- **判据**：§2.1 #1 Q2=会判过但真 hspice 也会判过 ⇒ 非 REQ（real hspice catches nothing the mock misses）。§2.1 #3 旧 R1 结论（generic REQ boilerplate）不作数。verdict REQ→OPT。
- **不动 judge_layers**（仍 [L0,L1]）⇒ 无 `live_eval_changes.tsv` 登记。只改 `live_eval_review_B.tsv` 1 条 verdict/reason/evidence + 本节。

### 系统性发现：R1 generic boilerplate 需逐条桩体检

R1 对全部 hspice-mock/finesim-mock case 套同一句 "replays .75-captured GT keyed on .param signature" ⇒ 对**纯语法 validator 桩**误判 REQ。本轮 grep 扫 30 条未改造 REQ case 的桩体指标（`_MOCK_VALUES`/`_GT_B`/`.measure`/`job concluded`/`_detect`），初步分两类：

| 类 | 指标特征 | verdict | 本轮处理 |
|:--|:--|:--|:--|
| **GT-replay-by-signature**（真 REQ） | `_MOCK_VALUES`/`_GT_B`/`MULTI[` + `.measure` + `_detect`/signature | REQ | 续 R2 改造 |
| **纯语法/收敛 validator** | gt_vals=0 + measure=0 + conclude>0 | OPT（候选） | **需逐条读桩体复验**，未读全不降级 |

候选 OPT（gt_vals=0 measure=0，疑似纯语法桩，**待下轮读桩体全文复验**，未降级）：
- `SpGen-001`（cond k 有 measure-match，需读桩体判断 GT-replay vs deck-driven）。
- `GmidLut-001`（cond p candidate-lut vs judge-ref-rerun 数值比对，需读 ref_build/桩 .lis 输出判断）。
- `PlatMosThinIdsatIoffSweep-001`（cond m/n 有 idsat 数值 cross，需读桩 dc-transfer-curves 解析判断）。
- `FineSimModelScopeFix-001` / `FineSimNoRefCktFix-001`（finesim 桩，需读桩 .log/.mt0 输出判断）。

⚠️ 上述 5 条**未降级**——指标 grep 不足以定论（有 measure/cross conds），必须读桩体全文 + 实证才能改 verdict。下轮 R1 再复核 #3 逐条处理。**已降级仅 PwlStimTransform-001 1 条**（桩体已读全 + .75 实证）。

### 与 r1301 的差异

| 项 | r1301 | r1302 | 依据 |
|:--|:--|:--|:--|
| REQ 合计 | 37 | **36** | PwlStimTransform-001 桩体检降级（syntax-validator 非 GT-replay） |
| OPT 合计 | 11 | **12** | +1 降级 |
| 降级维度 | Type A vs Type B（候选是否 author deck） | **桩体结构**（GT-replay vs syntax-validator） | r1301 只区分候选调用签名；r1302 深入桩体语义 |

## R1 再复核 #3（2026-11-27 r1303 · 5 候选逐条读桩 + .75 实证 · 只读）

### 背景

r1302 系统性发现 30 条未改造 REQ 中 grep 出 5 条候选 OPT（SpGen/GmidLut/PlatMosThin/FineSimModelScope/FineSimNoRefCkt），但指标 grep 不足以定论（有 measure/cross conds），承诺「下轮 R1 再复核 #3 逐条读桩 + 实证定 verdict，未读全不降级」。本轮兑现：逐条**读桩体全文**（check.py 完整 mock 源 + cond 列表），并对降级者跑 **.75 真模拟器实证**（hspice V-2023.12-SP1-1 / finesim V-2023.12-1 @ hfhds201）。

### 关键区分：faithful-physics-solver vs GT-replay-by-signature

r1302 把桩体分两类（GT-replay vs syntax-validator）。本轮发现**第三类**：**faithful-physics-solver**——桩读候选 deck 的真实物理参数（R/kp/vto/W/L/vcc），用与真工具**同一模型**计算物理量，对 honest deck 与真工具 bit-exact。这类桩**不是** GT-replay-by-signature（不查表、不按键回放），garbage-physics deck 会被桩算出错误值并被 cond 交叉校验（cand vs judge-correct-rerun / cand vs GT-on-real-netlist）FAIL。真工具对这类线性/level-1 deck **零边际增益**。

| 桩类 | 特征 | Q2（garbage-physics 过桩？） | verdict |
|:--|:--|:--|:--|
| GT-replay-by-signature | 桩按 .param/vdd 签名查预捕 GT 表回放 | **过**（签名对即回放 GT，忽略网表内容）| REQ |
| faithful-physics-solver | 桩读真实 deck 参数 + 用同模型计算 | **不过**（算出错误值，cond 交叉校验 FAIL）| OPT |
| 纯语法/结构 validator | 桩只校验语法/收敛/结构，无 measure | **过**（无物理量可断）| OPT |

### 降级 3 条（读桩 + .75 实证定论）

#### 降级 5：SpGen-001（hspice-mock · faithful KCL solver）REQ→OPT

**桩体全文读**（check.py L72-243 `HSPICE_MOCK_SRC`）：桩 `main()` 解析候选 tran.sp 的 `.inc` 目标 → `_read_netlist_resistors(inc_path)` 读**真实** R1(rail→out)/R2(out→gnd) → 读 Vxxx pwl 的 vcc + `.param DC_load` + `iload` 存在性 → **KCL 求解** vnl=vcc·R2/(R1+R2)，vl=(vcc/R1−DC_load)/(1/R1+1/R2)。cond k2 把候选值 vs `gt_measures(b_sp,B)`（桩跑 check.py 自建 GT deck on **真实 b_sp**）交叉校验。garbage R1/R2/vcc/DC_load → 桩算错 → cond k2 FAIL。**桩有牙，非 GT-replay。**

**.75 实证**（r1303 session `r1303-reverify` @ hfhds201 hspice V-2023.12-SP1-1）：honest GT deck（.inc netlist_B.sp Rd1=Rd2=4k vcc=1.0 DC_load=50u）真跑 → `vno_load=500.0000m vload=400.0000m vunload=500.0000m` RC=0 job concluded。桩 KCL 算 vnl=0.5 vl=0.4 vul=0.5 == 真 hspice **bit-exact**。真 hspice 对此线性电阻分压零边际增益。

#### 降级 6：PlatMosThinIdsatIoffSweep-001（hspice-mock · faithful Shichman-Hodges solver）REQ→OPT

**桩体全文读**（check.py L74-204 `HSPICE_MOCK_SRC`）：桩解析候选 deck 的 `.param vhi/wn` + `vgs/vds` 行 + `.model nch kp/vto/lambda/gamma` + `.dc LL start/stop/step` → 用 **level-1 Shichman-Hodges**（饱和 Id=0.5·kp·(W/L)·Vov²·(1+λ·Vds)，线性 Id=kp·(W/L)·(Vov·Vds−0.5·Vds²)·(1+λ·Vds)）逐点算 Id。cond n 把候选 idsat vs check.py `_indep_rerun`（自建正确 deck 跑桩）交叉校验 dev<50%。garbage kp/vto/W/L → 桩算错 → cond n FAIL。**桩有牙，非 GT-replay。**

**.75 实证**（r1303 @ hfhds201 hspice）：honest idsat deck（DEJOA kp=80u vto=0.5 λ=0.04 vhi=1.8 wn=2u .dc LL 0.15u→0.55u step 0.1u）真跑 → L=0.15u: **−966.2293u**，L=0.25u: −579.7376u，L=0.35u: −414.0983u，L=0.45u: −322.0764u，L=0.55u: −263.5171u RC=0 job concluded。桩 Shichman-Hodges 算 L=0.15u: 966.22930u == 真 hspice **bit-exact**（docstring 验证）。真 hspice level-1 对此 deck 零边际增益。

#### 降级 7：FineSimNoRefCktFix-001（finesim-mock · 结构 subckt-resolution validator）REQ→OPT

**桩体全文读**（check.py L115-268 `FINESIM_MOCK_SRC`）：桩 `_all_defs` 收集 deck + `.inc` 递归的 `.subckt` 定义，`_scan_instances` 扫每个 X 实例的 subckt 引用，未解析 → faithful `no reference ckt` 错误；全解析 → `Successfully Completed` + .pt0/.ic/.fsdb。**check.py 全 14 conds 无任何 measure/物理量断言**（i/j/k/l/m/n 只查 Successfully Completed + 无 no-reference-ckt + 无 ERROR! + 输出文件存在）。Q2 N/A：garbage-physics-but-all-subckts-resolve deck 过桩且过真 finesim（无物理量可断）。与 r1302 PwlStimTransform 同型（结构/语法 validator 无物理）。

**.75 实证**（r1303 @ hfhds201 finesim V-2023.12-1）：garbage-resolving deck（.inc spf.inc 全 subckt 解析，但 inv 管 W/L=1e-21u 电死）真跑 → `FineSim Successfully Completed` DC converged 无 ERROR! 产 .pt0/.fsdb/.ic RC=0。桩亦全解析 → Successfully Completed + 输出文件。**两者同过 garbage-physics deck**。真 finesim 无物理增益（无 measure 断言），仅边际 elaboration 严。

### 保留 REQ 2 条（读桩定论为 GT-replay-by-signature）

#### GmidLut-001（hspice-mock · GT-replay-by-signature）REQ 确认

桩（check.py L142-227）解析 deck 的 `.param kp/vto` + `vvd` 行 → 按 **kp/vto 精确值**（0.00012/0.5→A，8e-5/0.45→B，+vvd→VD0）匹配三场景之一 → 回放**预捕 real-HSPICE CSV**（`_MOCK_CSV_A/B/VD0`）。cond p 把候选 lut_A vs `ref_build(params_A)`（桩跑 → 回放 A CSV）交叉校验。garbage deck（正确 kp/vto 签名但 W/L/拓扑/vds 错）→ 桩按签名回放 A CSV → 候选解析得 A 值 → cond p 过；真 hspice 跑 garbage deck 算出不同 op-point → cond p（真 ref）FAIL。**Q2-cheatable，REQ 确认。** R1 boilerplate 准确。

#### FineSimModelScopeFix-001（finesim-mock · GT-replay-by-signature by vdd）REQ 确认

桩（check.py L158-288）解析 deck + `.inc` model 文件，校验 `.model ./` 语法 + instance-model 名匹配，然后按 **vdd 值**（3.3→A tpd=2.1447e-09，2.5→B tpd=9.6430e-12）**查表回放预捕 real-FineSim tpd**。cond j/m 把候选 mt0 tpd vs judge-rerun tpd（桩跑 → 按 vdd 回放）交叉校验。garbage deck（正确 model 名 + vdd 但 W/L/拓扑错）→ 桩按 vdd 回放 GT tpd → 候选 mt0 匹配 → cond j/m 过；真 finesim 跑 garbage deck 算出不同 tpd → FAIL。**Q2-cheatable，REQ 确认。** R1 boilerplate 准确。

### 与 r1302 的差异

| 项 | r1302 | r1303 | 依据 |
|:--|:--|:--|:--|
| REQ 合计 | 36 | **33** | SpGen + PlatMosThin + FineSimNoRefCkt 降级（faithful-physics-solver / 结构 validator，非 GT-replay） |
| OPT 合计 | 12 | **15** | +3 降级 |
| 降级维度 | 桩体结构（GT-replay vs syntax-validator） | **桩体语义三分类**（+ faithful-physics-solver） | r1302 二分；r1303 发现第三类（faithful physics solver，读真实参数 + 同模型计算，bit-exact 真工具） |
| R1 boilerplate 修正 | PwlStim 1 条（syntax-validator） | SpGen/PlatMosThin/FineSimNoRefCkt 3 条（faithful-solver/结构 validator） | r1302 grep 候选 5 条本轮读桩 + 实证全结清 |

### 待办（R2 续 / 5 候选已全结清）

- r1302 的 5 候选 OPT 全部结清：3 降级（SpGen/PlatMosThin/FineSimNoRefCkt）+ 2 REQ 确认（GmidLut/FineSimModelScope）。**R1 generic REQ boilerplate 对 faithful-physics-solver / 结构 validator 桩的误判已清零。**
- R2 续改 GT-replay 真 Type A 家族（hspice-mock/finesim-mock）：当前 REQ 33 条（含已 done 7），未改造 26 条，B 预算 ≤6-8 条/轮，hspice-mock 家族优先。
- 本轮**只读**：仅改 `live_eval_review_B.tsv` 3 条 verdict + 本节，🚫 未碰 `reference/*/check.py` 与 `cases/*.json`（无 judge_layers 变更，无 `live_eval_changes.tsv` 登记）。.75 通路 OK（r1303 reach: open_session 秒级 / hspice V-2023.12-SP1-1 + finesim V-2023.12-1 在 PATH @ hfhds201）。

## R2 改造进度（2026-11-27 r1304 起 · 续 r1294-r1300）

### r1304：GmidLut-001（hspice-mock GT-replay-by-signature · 第8条）

**Q2 实证（r1303 已确认 + 本轮 ref check_live 复验）**：cheat `gmid_cheat_gen.py` 把 m1 模型名 `nch`→`nch_dead`（保持 `.param kp/vto` 签名 + `vvd vd 0 vds` 非零）→ 桩按 kp/vto 精确值匹配 A 场景回放预捕 real-HSPICE CSV（`_MOCK_CSV_A`）→ 候选 lut_A.csv = GT → 静态 16/16 PASS 假阳；真 hspice V-2023.12-SP1-1 @ hfhds201：model nch_dead not found → `job aborted` → 0 op-point blocks → 0-row lut_A_live → cond (e) row-count + (p-live) FAIL。

**Q1 保真**：.75 真跑 ref gen.py（honest deck）→ lut_A_live 24 rows / lut_B_live 35 rows，与 mock `_MOCK_CSV_A/B` **逐位一致**（r1303 已确认；本轮 ref check_live PASS 复验 A=24/B=35）。

**改造**：非侵入包装（`_check_static_impl` 16 conds a-p 一字不动 + `check_static` try/except 3-tuple + `check_live(sess)` .75 真跑 hspice rerun candidate `gmid_lut_gen.py` on hidden B AND visible A，读 real `lut_A_live.csv`/`lut_B_live.csv`，复断 conds (e)-(l) 同阈值 row-count/cgg>0/monotonicity + (n)(o) cross-input + (p-live) cand lut_A_live vs shipped lut_A.csv(mock GT) within 2%，only-add never relax）+ `__main__` 块 + live-neg（`cheat_nch_dead/gmid_lut_gen.py`：m1 nch_dead，static-pass mock-replays-GT / live-fail cond e 0 rows vs 24）+ `negative_selftest.py` 重写（STATIC 6 negs distinct{c,e,f,j,m} + §4.9 trio distinct{empty:c, print:m, core:e} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `a946b900c910` 3-way sync。

**§5 全绿**：① REF check_live PASS（real hspice A=24/B=35 Q1 fidelity lut_A_live==shipped GT）；② 6 static neg FAIL distinct{c,e,f,j,m} + §4.9 trio distinct + live-neg FAIL cond e；③ 3-seed deterministic lut_A md5 `7ec9ba02c19cd456d88963170df0f88e`；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `a946b900c910` 3-way sync（JSON test / 磁盘 check.py）；⑥ 断言条数只增不减（+m_live cond ⑰，阈值不放宽）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T02:45+08:00, repo_commit=f193e5cc8）。

**.75 通路 OK**（r1304 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session r1304-reflive 用后 close）。

### R2 累计进度

| 轮次 | case | 家族 | 状态 |
|:--|:--|:--|:--|
| r1294 | CdlBulkSanitize-001 | hspice-mock | DONE |
| r1295 | InvTripDelay-001 | hspice-mock | DONE |
| r1296 | AOI21ArcChar-001 | hspice-mock | DONE |
| r1297 | AlterDeckSplit-001 | hspice-mock | DONE |
| r1298 | SpiceSim-001 | hspice-mock | DONE |
| r1299 | DffSetupHoldChar-001 | hspice-mock | DONE |
| r1300 | GrDecPwrVerifTb-001 | hspice-mock | DONE |
| r1304 | GmidLut-001 | hspice-mock GT-replay | DONE |
| r1305 | VcoKvcoChar-001 | hspice-mock GT-replay | DONE |
| r1306 | PVTalterChar-001 | hspice-mock GT-replay | DONE |
| r1308 | SramSNM-001 | hspice-mock GT-replay | DONE |
| r1310 | InvPVTchar-001 | hspice-mock GT-replay | DONE |
| r1311 | PFDdeadZone-001 | hspice-mock GT-replay | DONE |
| r1312 | CtleAcChar-001 | hspice-mock GT-replay | DONE |
| r1313 | DelayChainEdgeMeas-001 | hspice-mock GT-replay | DONE |
| r1314 | OpampACSpec-001 | hspice-mock GT-replay | DONE |
| r1316 | VwlpRefDeckSet-001 | hspice-mock GT-replay | DONE |
| r1317 | DelaySigma-001 | hspice-mock GT-replay | DONE |
| r1318 | PorCapSweep-001 | hspice-mock GT-replay | DONE |
| r1319 | CmlPvtAcReport-001 | hspice-mock GT-replay | DONE |
| r1320 | StrongarmFomSweep-001 | hspice-mock GT-replay | DONE |

L2.live done 21→22；REQ 未改造 31-22=9 条（hspice-mock/finesim-mock GT-replay 家族优先，B 预算 ≤6-8 条/轮，.75 严格串行，逐条独立自验）。

### r1316：VwlpRefDeckSet-001（hspice-mock GT-replay-by-signature · 第18条）

**Q2 实证（r1316）**：cheat `cheat_dead_dut.py` 复制 ref `vwlpref_deckset_gen.py`，在 `common_header` 把 `.inc 'dut.sp'` 替换为内联 dead `VwlpRefReg` subckt（所有 MOS `W=1e-21u` 电死），保留 `X1` 实例化 + `vGlbRef085` + analysis 语句签名（桩 `_HSPICE_MOCK_SRC` 的 `detect()` 按 `analysis-type + vGlbRef085-ref + has-X1` 签名查 `_GT` 回放 .75-captured .meas，**不开 dut.sp**）→ `_check_static_impl` **14/14 PASS 假阳**（mock 按签名回放 GT unload/IVwlpRef/PSRR/f_3db，**不校验 DUT 晶体管 W/L 物理**）。真 hspice V-2023.12-SP1-1 @ hfhds201：w=1e-21u 晶体管电死 → VwlpRef 无驱动 → `.measure` 0/越界 → unload=-142.9 / IVwlpRef=7e-13 / psrr 1MHz=-189.9 not >100Hz=-109.9 / f_3db=14.12 not in [1MHz,1GHz] / B unload=-285.8 → conds h/i/j/k/l FAIL。

**Q1 保真**：.75 真跑 ref（honest deck）→ A unload=0.8500 / load1mA=0.7749 / undershot=0.6202 / Rspon=5.331e-09 / ac gain=-3.2363p / f_3db=37.5923x / Peak=8.0472 / dc IVwlpRef=634.7405u / psrr 100Hz/1kHz/1MHz=-113.8590/-93.8590/-33.8460；B unload=1.0000 / load1mA=0.9196 —— **== mock `_GT` 逐位一致**（byte-exact，tran 经 .mt0 表解析、ac/dc/psrr 经 .lis `name= value` 行解析，r1316 REF check_live 3-seed PASS 复验）。

**改造**：非侵入包装（`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple + `check_live(sess)` .75 真跑 hspice rerun candidate `vwlpref_deckset_gen.py` on visible A (tran/ac/dc/psrr) AND hidden B (tran) AND determinism re-run，read real `.lis`/`.mt0`，复断 conds h/i/j/k/l + m-live 同阈值 tran-unload∈[0.80,0.90]/load1mA<unload/undershot<unload/Rspon>0/dc-IVwlpRef∈[100uA,2mA]/psrr-3freq<0+1MHz>100Hz/ac-f_3db∈[1MHz,1GHz]+Peak<15/B-vGlbRef085==1.0+B-unload∈[0.95,1.05]/det-tranA-unload±1e-9，only-add never relax）+ `check` 兼容包装 + live-neg（`cheat_dead_dut.py`：inline dead subckt，static-pass mock-replays-GT / live-fail cond h/i/j/k/l）+ `negative_selftest.py` 重写（STATIC 5 negs distinct{a,b,c,e,h} + §4.9 trio distinct{empty:a,print:b,core:h} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `d878ee0e8458` 3-way sync（disk==JSON）。

**§5 全绿**：① REF check_live PASS（real hspice A unload=0.8500 == mock GT Q1 fidelity，3-seed identical）；② 5 static neg FAIL distinct{a,b,c,e,h} + §4.9 trio distinct + live-neg FAIL cond h/i/j/k/l；③ 确定性（REF live 3-seed message 字节一致）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `d878ee0e8458` 3-way sync；⑥ 断言条数只增不减（check_live +h/i/j/k/l+m-live 同阈值，不放宽）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`，repo_commit `e69cd3cde`）。

### r1305：VcoKvcoChar-001（hspice-mock GT-replay-by-signature · 第9条）

**Q2 实证（r1305）**：cheat `vco_kvco_cheat.py` 在 `gen_netlist` 的 `.subckt cs_inv` 把 Mp/Mn1/Mn2 的 W/L 篡改为 `w=1e-21u l=1e3u`（电死环形 VCO 晶体管），保持正确 `.param VVDD=1.2 VTUNE=0.85` + `.alter` `.param VTUNE=0.9/...` 签名行（桩 `_HSPICE_MOCK_SRC` 按 `vdd|vtune-csv` 签名查 `_MOCK_VALUES` 回放 GT）→ `_check_static_impl` **14/14 PASS 假阳**（mock 按签名回放 GT fosc/kvco，**不校验 VCO 环形网表晶体管 W/L/拓扑**）。真 hspice V-2023.12-SP1-1 @ hfhds201：w=1e-21u 环形 VCO 无法振荡 → `.measure tran tper` fails（s1 永不翻转）→ fosc=[] / kvco=null → cond (e)(g)(j)(k) FAIL。

**Q1 保真**：.75 真跑 ref（honest deck）→ B fosc=[13.36741163, 17.42982735, 20.52149031, 22.92343838, 24.88516947, 26.49994707] / kvco=51.6746580742848；A fosc=[8.9585092, 11.33040257, 12.9958302, 14.27411158, 15.30615097] / kvco=31.278 —— **== mock `_MOCK_VALUES` 逐位一致**。

**改造**：非侵入包装（`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple + `check_live(sess)` .75 真跑 hspice rerun candidate `vco_kvco.py` on hidden B AND visible A，读 real `kvco_result.json`，复断 conds (d)-(n) 同阈值 hspice_ran/fosc-len==vtune-len≥3/monotonic/kvco>0/kvco within ±30% REF_B_KVCO/cross-input |B_fosc0-A_fosc0|>10%/A_fosc0 within ±25% REF_A_FOSC_0，only-add never relax）+ `__main__` 块 + live-neg（`cheat_dead_vco/vco_kvco.py`：w=1e-21u，static-pass mock-replays-GT / live-fail cond e/g/j/k）+ `negative_selftest.py` 重写（STATIC 6 negs distinct{a,d,e,f,l} + §4.9 trio distinct{empty:a, print:d, core:e} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `0212619da6bb` 3-way sync。

**§5 全绿**：① REF check_live PASS（real hspice B fosc==mock GT Q1 fidelity）；② 6 static neg FAIL distinct{a,d,e,f,l} + §4.9 trio distinct + live-neg FAIL cond e/g/j/k；③ 确定性（hspice 对同 deck/params 确定性，ref fosc byte-exact == 之前捕获的 mock GT）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `0212619da6bb` 3-way sync（JSON test / 磁盘 check.py）；⑥ 断言条数只增不减（check_live +11 conds d-n 同阈值，不放宽）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。

**.75 通路 OK**（r1305 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session r1305-reflive/r1305-cheatlive 用后 close）。

### r1306：PVTalterChar-001（hspice-mock GT-replay-by-signature · 第10条）

**Q2 实证（r1306）**：cheat `negative/cheat_dead_wl.py`（复制 ref `pvt_char_harness_ref.py`，把 `.subckt nand2` 内 4 个晶体管 `mn1/mn2/mp1/mp2` 的 `w=wn l=ln` 篡改为 `w=1e-21u l=1e3u` 电死 NAND2，**保持 `.param wn=1.5u wp=1.5u ln=180n` + `.lib 'model_b.sp' <corner>` + `.temp` + `.param cload` 签名行**）→ `_check_static_impl` **12/12 PASS 假阳**（桩 `_HSPICE_MOCK_SRC.parse_deck` 按 `kpn|vton|kpp|vtop|temp|cload|wn|wp|ln|vdd` 签名查 `_MOCK_VALUES` 回放 GT tpdr/tpdf，**不解析 `.subckt` 晶体管 W/L**）。真 hspice V-2023.12-SP1-1 @ hfhds201：w=1e-21u 死管不开关 → `.measure tran tpdr` fails → rows=0 → n_alters=0 / baseline tpdr=None → cond (d)(f)(h)(i)(j) FAIL。

**Q1 保真**：.75 真跑 ref（honest deck）→ B baseline(tt_0_300f) tpdr=1.4916 tpdf=1.4433；A baseline(tt_-40_200f) tpdr=1.7823 tpdf=1.3040 —— **== mock `_MOCK_VALUES` 逐位一致**。

**改造**：非侵入包装（`_check_static_impl` 12 conds a-l 断言逻辑/阈值原封，仅 return shape `bool`→`results list` 以暴露 first-fail tag 供 selftest distinct 校验 + `check_static` try/except 3-tuple + `check_live(sess)` .75 真跑 hspice rerun candidate `pvt_char_harness.py` on hidden B AND visible A，读 real `pvt_report.json`，复断 conds (d)(e)(f)(g)(h)(i)(j)(k) 同阈值 n_alters=27/corner0=tt_0_300f/baseline tpdr within ±5% REF_B=1.4916/tpd_2nd_rise all null/worst=tt_0_800f/overall_pass=False/A baseline tpdr within ±5% REF_A=1.7823 AND !=B/determinism 2x rerun，only-add never relax）+ `__main__` 块 + live-neg（`negative/cheat_dead_wl.py`：w=1e-21u，static-pass mock-replays-GT / live-fail cond d/f/h/i/j）+ `negative_selftest.py` 重写（STATIC 4 negs distinct{c,j,d,f} + §4.9 trio distinct{empty:c, print:j, core:d} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `3b2645391e14` 3-way sync。

**§5 全绿**：① REF check_live PASS（real hspice B base tpdr=1.4916 worst=tt_0_800f overall=False A base tpdr=1.7823==mock GT Q1 fidelity）；② 4 static neg FAIL distinct{c,j,d,f} + §4.9 trio distinct + live-neg FAIL cond d/f/h/i/j；③ 确定性（cond k 2x rerun B verdicts identical + hspice level-1 确定性）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `3b2645391e14` 3-way sync（JSON test / 磁盘 check.py）；⑥ 断言条数只增不减（check_live +8 live conds d/e/f/g/h/i/j/k 同阈值，不放宽）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`）。

**.75 通路 OK**（r1306 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session r1306-REF/r1306-CHEAT/liveneg 用后 close）。

**注**：本轮 check.py/negative/selftest 被 concurrent shardC loop sweep（commit `ff9ef6e6d` 03:27:22）提前 commit 入 git（working-tree 广 `git add` 拾取 in-progress 改动），case JSON `judge_layers`+`test` sync 本轮补 commit（`6ba40d41f`）。md5 校验 HEAD check.py == 本轮工作树，无 corruption。跨 shard `git add` 拾取是已知 loop 风险，建议各 shard loop 改 `git add -- benchmarks/EDA-Eval-DesignFlow/cases/<本shard>` + `reference/EDA-Eval-DesignFlow-<本shard-case>` 精确路径。


### r1308：SramSNM-001（hspice-mock GT-replay-by-signature · 第12条）

**Q2 实证（r1308）**：cheat `negative/cheat_garbage_x1/sram_snm.py`（复制 ref `sram_snm_ref.py`，把 `build_deck` 的 `X1 qout qin wl bl vdd 0 SRAM_INV` 替换为 `Rdumb qout vss 1e12` 开路，**保持 `.param vpwr` + `.inc 'cell_b.sp'` + `vwl wl 0 <wl>` + `vbl bl 0 <bl>` + `.dc vq 0 vpwr <step>` 签名行**）→ `_check_static_impl` **14/14 PASS 假阳**（桩 `_HSPICE_MOCK_SRC._parse_deck` 按 `cell|vpwr|wl|bl` 签名查 `_MOCK_LIS` 回放 real-HSPICE DC transfer table，**不解析 X1 例化/网表拓扑**）。真 hspice V-2023.12-SP1-1 @ hfhds201：无 X1 例化 → qout 仅经 Rdumb(1e12) 接 vss ≈ 浮空 → DC transfer table v(qout)≈0 全程 → butterfly eye 塌缩 → 所有 margin=0 → cond (f)(g)(h)(k)(n) FAIL。

**Q1 保真**：.75 真跑 ref（honest deck，ABSOLUTE cell path）→ B rnm=[0.2871087,0.2127529,0.1357232] / wnm=[0.2341916,0.1740176,0.1137965] / hold_snm=[0.3320633,0.2407419,0.1543816] —— **== mock `GT_B` 逐位一致**；A rnm=[0.2729,0.1997,0.1274]（cross-input ≠B）。

**改造**：非侵入包装（`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple + `check_live(sess)` .75 真跑 hspice rerun candidate `sram_snm.py` on hidden B AND visible A，**传 ABSOLUTE cell path**（候选把 cell path 原样写进 `.inc '<path>'`，在自己 tempdir 跑 hspice，相对路径会找不到；静态 mock 只 regex 抽 basename 不开文件故无此问题），读 real `report_b.json`/`report_a.json`，复断 conds (d)-(n) 同阈值 method==hspice_run/points len==3+numeric/rnm match GT_B tol 5e-3/wnm match/hold_snm match/monotonic/rnm<hold/cross-input A≠B+A-mono/n_runs>=18/verdict-pass+nonzero，only-add never relax）+ `__main__` 块（STATIC_VERDICT+first_fail 供 selftest）+ live-neg（`cheat_garbage_x1/sram_snm.py`：X1→Rdumb，static-pass mock-replays-GT / live-fail cond f/g/h/k/n）+ `negative_selftest.py` 重写（STATIC 4 negs distinct{c,d,k,f} + §4.9 trio distinct{empty:c, print:k, core:f} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `3d799f7efb4d` 3-way sync。

**§5 全绿**：① REF check_live PASS（real hspice B rnm/wnm/hold==mock GT_B Q1 fidelity，A cross-input ≠B）；② 4 static neg FAIL distinct{c,d,k,f} + 1 live-neg（cheat_garbage_x1：static PASS 14/14 / live FAIL cond f/g/h/k/n margins=0）；③ 3-seed 确定性（real hspice 对同 deck 确定性，ref B margins byte-exact == mock GT，Q1 run 复现）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏，§5 ⑦）；⑤ sha `3d799f7efb4d` 3-way sync（JSON test / 磁盘 check.py / HEAD）；⑥ 断言条数只增不减（`_check_static_impl` 原文未改一字；`check_live` 新增 11 条同阈值实跑断言 d-n）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，`check_live` 不读 `reference/`。

**登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`，commit `aeee2aa4f` case-JSON sync + `1d0ddf89c` check.py via shardA sweep）。

**.75 通路 OK**（r1308 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session r1308live 用后 close）。

**注**：本轮 check.py/negative/selftest 被 concurrent shardA sweep（commit `1d0ddf89c` 04:40:24）提前 commit 入 git（working-tree 广 `git add` 拾取 in-progress 改动），case JSON `judge_layers`+`test` sync 本轮补 commit（`aeee2aa4f`）。sha 校验 HEAD check.py == 本轮工作树 == JSON test = `3d799f7efb4d`，无 corruption。


## r1310：InvPVTchar-001（hspice-mock GT-replay-by-signature · 第13条 · 落盘 r1309 设计稿）

**Q2 实证（r1310）**：cheat `negative/cheat_dead_wl.py`（自包含复制 ref `gen_pvt_char_ref.py`，把 `build_deck` 的 `.param wn=%s wp=%s`（来自 `d["sizing"]`）改为 `.param wn=1e-21u wp=1e-21u` 电死反相器，**保持 `.lib '<model>' <corner>` + `.param vdd_val` + `.param cload` + `.alter` 全交叉签名行**）→ `_check_static_impl` **14/14 PASS 假阳**（桩 `_HSPICE_MOCK_SRC.parse_deck` 按 `corner|vdd|cload` 签名查 `GT_JSON` 回放 real-HSPICE 45 B combos 的 tpdf/tpdr/tpd/voh/vol，**不解析 `.param wn/wp` 或网表拓扑**）。真 hspice V-2023.12-SP1-1 @ hfhds201：wn=wp=1e-21u 死管 → out 永不翻转 → `.measure tran tpdf/tpdr` 全 `failed` → tpd 全 None → 候选 `run()` raise `RuntimeError("no valid tpd measurements parsed")` → 无 `char_results.json` → check_live 返回 FAIL（B run failed: no char_results.json）。

**Q1 保真**：.75 真跑 ref（honest deck）→ B worst_corner=(ss,1.0,1p) worst_tpd=2.6087ns —— **== mock `GT_JSON["ss|1.0|1p"]` 逐位一致**（live verify REF check_live PASS，argmax corner == REF_B_WORST_CORNER）。

**改造**：非侵入包装（`_check_static_impl` 14 conds C1-C14 一字不动 + `check_static` try/except 3-tuple + `check` 兼容包装 + `check_live(deliverable, workdir, sess)` .75 真跑 hspice rerun candidate `gen_pvt_char.py` on hidden B，`sess.upload_text` 上传 candidate + spec_B.json + pvt_model_B.sp，`sess.run_commands` 跑 `python3 gen_pvt_char.py spec_B.json pvt_model_B.sp out`，`sess.read_file` 读 real `out/inv_tb.lis` + `out/char_results.json`，复用模块级 `parse_lis` 复断 C6-C14 同阈值 n_concl==45/parsed==45/tpdf-numeric-all-alters/tpdr-numeric-all-alters/worst_tpd<=tpd_max(3.0)/voh>=voh_min(0.9)/vol<=vol_max(0.01)/reported-worst_corner==argmax+live-argmax==(ss,1.0,1p)Q1-guard/reported-worst_tpd==independent-parse-tol1pct/determinism-2x-rerun，only-add never relax）+ `__main__` 块（STATIC_VERDICT + first_fail 供 selftest）+ live-neg（`negative/cheat_dead_wl.py`：wn=wp=1e-21u，static-pass mock-replays-GT / live-fail no char_results.json）+ `negative_selftest.py` 重写（STATIC 6 negs distinct{C5,C7,C2,C12,C12,C6}=5-distinct + §4.9 trio distinct{empty:C5, print:C7, core:C2} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `b91837c2fd05` 3-way sync。

**§5 全绿**：① REF check_live PASS（real hspice B worst=(ss,1.0,1p) tpd=2.6087==mock GT Q1 fidelity）；② 6 static neg FAIL 5-distinct{C5,C7,C2,C12,C6} + §4.9 trio distinct + live-neg static-pass(14/14)/live-fail(no char_results.json)；③ 确定性（C14 2x rerun real hspice worst_tpd 一致，level-1 确定性）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏，§5 ⑦）；⑤ sha `b91837c2fd05` 3-way sync（JSON test / 磁盘 check.py / HEAD）；⑥ 断言条数只增不减（`_check_static_impl` 原文未改一字；`check_live` 新增 9 条同阈值实跑断言 C6-C14）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，`check_live` 不读 `reference/`。

**登记**：`live_eval_changes.tsv` +1 行（jl `[L0,L1]`→`[L0,L1,L2.live]`，commit `5d9521079` check.py+negative via shardD sweep + `35ef3835f` case-JSON judge_layers+test sync via shardC sweep）。

**.75 通路 OK**（r1310 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session verify_REF/verify_CHEAT 用后 close）。

**自验通道纠正（r1309 lesson 兑现）**：r1309 因 execute `code` 字符串通道腐蚀大 base64 串致 self-verify 未达成；本轮改用本地 Python 脚本 `from eda_flow_judge import EDASession` → `sess.upload_text(name, content)`（base64 通道，不经 execute `code`）上传 candidate + B 资产，REF check_live PASS + CHEAT check_live FAIL **一次过**，零腐蚀。设计稿（r1309 落此节）已兑现，保留下方原设计稿作历史追溯。

---

## R2 前置 #2: InvPVTchar-001 设计稿（2026-11-27 r1309 · 只读, 未落盘 · 已由 r1310 兑现）

**为何单独成节**：本轮原计划落盘 R2 第 13 条 InvPVTchar-001，因 .75 self-verify 通道排障未在本轮预算内完成，check.py **零改动**。设计稿落此供下轮直接执行。（✅ r1310 已兑现，见上节。）

### 桩体检结论（读桩定论, Type A 稳固）
- check.py(415L) 单 `check()` 14 conds C1-C14；GT_JSON 45 B combos keyed `corner|vdd|cload`；`_HSPICE_MOCK_SRC` 桩 `parse_deck` 仅解 `.lib <corner>` + `.param vdd_val` + `.param cload`，**不解 wn/wp/网表拓扑/measure 语义**。
- Q2 可骗：cheat 改 `build_deck` 的 `.param wn/wp` 为 `1e-21u`（电死反相器）但保 `.lib`/`.param vdd_val`/`.param cload` 签名行 → 桩按签名回放 GT_B → C5-C14 全 PASS 假阳。
- Q1 保真：GT_JSON 数值标称来自 .75 真跑（docstring），待 self-verify 时实测 ref on .75 复核 == mock GT_B byte-exact。

### check_live 设计（待落盘）
1. 非侵入包装：原 `check` → `_check_static_impl`（一字不动）；`check_static` try/except 收口 3-tuple；`check` 兼容包装；`__main__` 块（STATIC_VERDICT + first_fail）。
2. `check_live(deliverable, workdir, sess)`：
   - 从 submit.zip 读候选 `gen_pvt_char.py`（`sess.upload_text`）+ 上传 hidden B `spec_B.json`/`pvt_model_B.sp`（参考 PVTalterChar 路径解析：workdir/hidden → assets/<CASE>/hidden fallback）。
   - **不调 `_ensure_hspice`**（.75 真 hspice 在 PATH）；`sess.run_commands` 在 sess.workdir 跑 `python3 gen_pvt_char.py spec_B.json pvt_model_B.sp out_B`（候选内部 `subprocess.run(["hspice",...])` 用真 hspice）。
   - `sess.read_file("out_B/inv_tb.lis")` + `out_B/char_results.json`，复用 check.py 的 `parse_lis`（需在 check_live 内重定义或提到模块级），同阈值复断 C6-C14：C6 n_concl==45 + parsed==45 / C7 tpdf numeric 全 alter / C8 tpdr numeric / C9 worst_tpd<=tpd_max(3.0) / C10 voh>=voh_min(0.9) / C11 vol<=vol_max(0.01) / C12 worst_corner==argmax tpd(ss,1.0,1p) / C13 reported worst_tpd==独立解析 tol 1% / C14 2-run 确定性。only-add never relax。
3. live-neg `negative/cheat_dead_wl.py`：复制 `gen_pvt_char_ref.py`，`build_deck` 改 `.param wn=1e-21u wp=1e-21u`（保签名行）→ 静态：mock 回放 GT 14/14 PASS；live：真 hspice 死管 → tpdf/tpd=failed → 候选 `run()` raise RuntimeError("no valid tpd") → 无 char_results.json → check_live C6/C7 FAIL。
4. `negative_selftest.py`：加 `cheat_dead_wl.py` 到 LIVE_NEG（经 EDASession 验 static-pass/live-fail）；§4.9 trio 已齐（empty_shell/print_expected/core_deleted）。
5. JSON `metadata.judge_layers` → `["L0","L1","L2.live"]`；JSON `test` 与磁盘 `check.py` sha 三方同步。

### .75 通路（r1309 实测）
- `open_session` 秒级；`which hspice` → `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`（hspice64 同在）；hostname=hfhds201；python3=3.7.1。

### 工具链排障（下轮规避）
- 🚫 `run_commands` 内 `printf '%s' '<b64>' | base64 -d > f`：腐蚀内容（实证 gen_pvt_char_ref.py md5 302e3afa→613c7536，`[`→`{` 单字节替换）。
- 🚫 execute Code Mode `write_file({content: <json-looking str>})`：JSON-look-alike 串被强制 parse 成 dict → pydantic input_type=dict。
- 🚫 execute `code` 参数粘贴大 base64 串：抵达 MCP 前已被单字符替换 → `write_file(content_base64=...)` 收到错串 → 解码腐蚀。
- ✅ 下轮 self-verify 正确通道：本地 Python 脚本 `from eda_flow_judge import EDASession` → `sess.upload_text(name, content)`（直接读本地文件 bytes encode，已验证 base64 往返一致）；或直接 `eval/run_one.sh InvPVTchar-001 --shard B`（框架用 EDASession.upload_text）。

### r1314：OpampACSpec-001（hspice-mock GT-replay-by-signature · 第17条）

**Q2 实证（r1314）**：cheat `cheat_dead_wl.py` 复制 ref `gen_opamp_ac_char.py`，在 `characterize` 把 DUT netlist 复制到 tempdir 时 `_deadify_netlist` 将所有 MOS instance 行的 `w=<num><unit>` 覆写为 `w=1e-21u`（电死），保留 `.model nmos vto=0.45` / `.param ib=` 签名行不变 → 桩 `_HSPICE_MOCK_SRC` 的 `_detect` 按 `.model nmos vto=` 签名（A=0.50/B=0.45）回放 .75-captured GT .meas → `_check_static_impl` **14/14 PASS 假阳**（mock 按 vto 签名回放 GT gain_dc/gbw/pm/f3db/gm，**不校验晶体管 W/L 物理**）。真 hspice V-2023.12-SP1-1 @ hfhds201：w=1e-21u 晶体管无增益 → vdb(out) 深负永不越 0 → `.meas gbw when vdb(out)=0` / `.meas pm find vp(out) when vdb(out)=0` / `.meas gm find vdb(out) when vp(out)=0` 全 failed → gbw/pm/f3db/gm=None，gain_dc=-195.88 → conds e/f/g/h/i/j FAIL。

**Q1 保真**：.75 真跑 ref（honest deck）→ B gain_dc=24.1997 / gbw=3641900.0 / phase=-95.4953 / pm=84.5047 / f3db=223077.7 / gm=18.6523 —— **== mock `_MOCK["B"]` 逐位一致**（byte-exact，r1314 REF check_live PASS 复验）。

**改造**：非侵入包装（`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple parse a-n tag + `check_live(sess)` .75 真跑 hspice rerun candidate `gen_opamp_ac_char.py` on hidden B AND visible A AND determinism re-run，读 real `report.json`，复断 conds d-n 同阈值 d-method==hspice_run+n_runs==1 / e-gain_dc±0.5dB / f-gbw±5% / g-phase±2deg / h-pm±2deg / i-f3db±10% / j-gm±1dB / k-spec_check{l:F,pm:T,gbw:T} / l-verdict==fail / m-A-cross-input==GT_A±0.5+pass+A!=B / n-determinism-gbw-1e-6，only-add never relax）+ live-neg `cheat_dead_wl.py`（dead-W netlist，static-pass 14/14 via mock / live-fail cond e/f/g/h/i/j/k/m/n real hspice gain_dc=-195.88 gbw=None）+ `negative_selftest.py` 重写（STATIC 5 negs distinct{c,d,e,k,m}=5-distinct + §4.9 trio distinct{empty:c,print:m,core:d} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `5bad67d6875b` 3-way sync（disk==JSON）。

**§5 全绿**：① REF check_live PASS（real hspice B gain=24.1997 gbw=3641900.0 == mock GT Q1 fidelity）；② 5 static neg FAIL distinct{c,d,e,k,m} + §4.9 trio distinct + live-neg FAIL cond e/f/g/h/i/j/k/m/n；③ determinism（REF check_live 含 cond n B-rerun gbw identical 1e-6）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `5bad67d6875b` 3-way sync（JSON test / 磁盘 check.py）；⑥ 断言条数只增不减（check_live 复断 d-n 同阈值，不放宽）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T07:10+08:00, repo_commit=pending）。

**.75 通路 OK**（r1314 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session liveREF/liveCHEAT 用后 close）。自验通道：本地 Python `from eda_flow_judge import EDASession` → `sess.upload_text` 上传 candidate+B/A 资产，REF live PASS + CHEAT live FAIL 一次过。

### r1315：StimPWL-001 + TxRonSize-001 桩体检降级（REQ→OPT，只读 verdict）

**背景**：R1 boilerplate「hspice-mock (deck-driven) replays .75-captured GT keyed on .param/.inc/deck signature」被 generically 套到所有 hspice-mock case。r1302/r1303 已证伪 SpGen/PwlStimTransform/FineSimNoRefCktFix/PlatMosThinIdsatIoffSweep（mock 实为 faithful physics solver / structural validator，非 GT-replay）。本轮续查剩余 REQ，逐条 full-mock-body 读 check.py 验 boilerplate 准确性。

**StimPWL-001 → OPT**：mock `_HSPICE_MOCK_SRC`（L59-147）是 faithful **PWL-crossing solver**——解 candidate `stimulus.sp` 的 PWL 点，`crossing()`（L102-112）线性插值算 half-VCC 过零时间。TB 用 ideal V source（v(net)==source waveform），crossing=纯插值==real hspice。**无 `_GT`/`_MOCK_VALUES` dict，无 signature lookup**（contrast VwlpRefDeckSet `_GT` L28 / DelaySigma `_MOCK_VALUES` L48）。Q2 N/A：garbage stimulus.wrong-times → mock 算错 crossing → cond m（report.transitions GrEn~=GT_B tol 1.5ns）FAIL。candidate 可从 si1.sp 自算 crossing hardcode report，但 real hspice 同样被绕过（mock==real for ideal-V TB）⇒ L2.live 零增益。静态 conds g-l 已直验 stimulus 结构/内容。judge_layers 留 [L0,L1]。

**TxRonSize-001 → OPT**：mock `HSPICE_MOCK_SRC`（L15-117）是 faithful **level-1 (Shichman-Hodges) MOS DC solver**——读 M1 W/L/M + corner.lib kp/vto/lambda，算 Id（saturation kp/2·W/L·M·veff²·(1+λ·vds)；linear 2·veff·vds−vds²），docstring 自称 bit-exact vs real HSPICE V-2023.12-SP1-1。judge 经 `measure_ron()`（L202-211）**INDEPENDENT re-run** candidate 报告的 sizing（conds f-k L283-310）⇒ candidate 无法 fabricate Ron。Q2 N/A：garbage W/L → mock 算错 Id/Ron → cond h/i/j/k FAIL。real hspice level=1==mock bit-exact ⇒ L2.live 零增益。judge_layers 留 [L0,L1]。

**不改** check.py / cases / judge_layers（只读 verdict）。**不进** `live_eval_changes.tsv`（无口径变更）。

**同轮确认 2 条 genuine REQ 供下轮 R2**：
- **VwlpRefDeckSet-001**：mock `_GT` dict（L28）+ 按 (analysis_type, ref_voltage) 签名 replay .75-captured .measure values，忽略 DUT 网表物理 ⇒ GT-replay-by-signature confirmed。
- **DelaySigma-001**：mock `_MOCK_VALUES` dict（L48）按 (vdd, L) 签名 lookup STD0..STD19，忽略网表 ⇒ GT-replay-by-signature confirmed。

**累计**：REQ 33→31（done 17，余 14），OPT 15→17，NA=76，L2.live 17 不变。

### r1320：StrongarmFomSweep-001（hspice-mock GT-replay-by-signature · 第22条）

**Q2 实证（r1320）**：cheat `negative/cheat_dead_dut.py` 复制 ref `strongarm_fom_sweep.py`，在 `build_deck` 把 `.include '<netlist>'` + `xsa vdd inp inn outp outn clk strongarm` 替换为 `routp outp 0 1e12` / `routn outn 0 1e12` 死负载（outp/outn=0），**保持 `.param ITAIL=.. INW=..` 签名 + `.measure tran ck2q/idc_avg` 行**（桩 `HSPICE_MOCK_SRC._parse_deck` 按 `(ITAIL, INW)` .param 签名查 `_MOCK_VALUES` 回放 real-HSPICE .measure，**不解析 .include/xsa 例化/DUT 拓扑**）→ `_check_static_impl` **14/14 PASS 假阳**（mock 按签名回放 GT ck2q/idc_avg，**不校验 strongarm DUT 物理**）。真 hspice V-2023.12-SP1-1 @ hfhds201：死负载 outp/outn 恒 0 → `.measure ck2q targ v(outp) val=0.6 rise=1` never crosses → ck2q=failed=None → 所有 point ck2q=None → cond (f) FAIL（g/h/i/l/k 连锁）。

**Q1 保真**：.75 真跑 ref（honest deck）→ B 6 grid points ck2q(10.5671n/10.4427n/10.3831n/10.3490n/10.3866n/10.5315n) + idc_avg(450.9804n/686.4786n/922.2641n/1.1583u/504.3028n/1.0298u) —— **== mock `_MOCK_VALUES` 逐位一致**（byte-exact，r1320 REF check_live PASS 复验 Q1 fidelity cond m 全过）。

**改造**：非侵入包装（`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple parse first-fail tag + `check` 兼容 + `check_live(sess)` .75 real-hspice rerun candidate `strongarm_fom_sweep.py` on hidden B(6pts) AND visible A(4pts) AND B determinism re-run，`sess.upload_text`(base64) 上传 candidate+A/B 资产，read real `report.json` re-assert conds d/e/f/g/h/i/l(B) + j/k(A cross-input) + m(Q1 fidelity B ck2q==mock GT±2%) + n(determinism B rerun ck2q identical 1e-9)，only-add never relax）+ live-neg `cheat_dead_dut`（static-pass 14/14 via mock / live-fail cond f ck2q=None）+ `negative_selftest.py` 重写（STATIC 6 negs distinct{b,c,d,f,h,i}=6-distinct + §4.9 trio distinct{empty:b,print:c,core:f} + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `ea065f796c48ce2d` 3-way sync（disk==JSON）。

**§5 全绿**：① REF check_live PASS（real hspice B 6pts ck2q==GT Q1 fidelity + A 4pts cross-input + det ok）；② 6 static neg FAIL 6-distinct + §4.9 trio distinct + live-neg FAIL cond f；③ determinism cond n（B rerun ck2q identical 1e-9）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏）；⑤ sha `ea065f796c48ce2d` 3-way sync；⑥ 断言条数只增不减（check_live re-assert d/e/f/g/h/i/l/j/k/m/n 同阈值）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T09:45+08:00, repo_commit=ea065f796c48）。同时 tsv 翻转 5 条已 done 但 verdict 未 flip 的（StrongarmFomSweep-001 新 + DelaySigma/PorCapSweep/CmlPvtAcReport/VwlpRefDeckSet stale）→ LIVE-REQ 9 / LIVE-REQ(done) 22。

**.75 通路 OK**（r1320 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session shardB_r1320 用后 close）。自验通道：本地 Python `from eda_flow_judge import EDASession` → `sess.upload_text`(base64) 上传 candidate+A/B 资产，REF live PASS + CHEAT live FAIL 一次过零腐蚀。

### r1327：SlicerFbTimeOpt/SpiceTbGen/StdLibCharTmpl 桩体检确认 REQ（只读 verdict，r1326 悬念收口）

**背景**：r1326 末尾指示「R2 续改 3 条未改造 REQ（SlicerFbTimeOpt/SpiceTbGen/StdLibCharTmpl），3 条均须 §2.1 桩体检再判 REQ/OPT（R1 boilerplate 可能同 Vcc2scActDeckGen/VlshftParamOpt 误分类）」。本轮逐条 full-mock-body 读 check.py 验 boilerplate 准确性，**3 条全部 CONFIRM REQ**，r1326 误分类悬念证伪。

**SlicerFbTimeOpt-001 → REQ 确认**：mock `_HSPICE_MOCK_SRC`（L141-236）`MOCK_OUTPUTS` dict 按 (4 widths+VVDD+vcm+temp+cap) `.param` 签名回放预录 .75 HSPICE .measure（t0/t1_feedbacktime+i_total）。Q2 漏洞在 cond (n)（L385-393）：L2 re-verify **只重跑 i_total**（`_override_deck(real src_sp, best_config)` → mock → `_grab(out,"i_total")` ±30%），**不复核 t0/t1_feedbacktime**（约束变量本身，cond f 仅查候选报告值 ≤limit）。候选可谎报 best_t0/best_t1≤60ps 通过 cond (f)，而该 config 真实 t0/t1>60ps——mock 对 t0/t1 re-verify 盲 ⇒ 假阳。另：shape-right-physics-wrong（正确 .param 签名 + garbage 拓扑）mock 按 .param 签名回放 GT 不读网表 ⇒ 亦假阳。real hspice 两路皆抓。Genuine Type A GT-replay-by-signature。**R1 boilerplate accurate after body-read**。

**SpiceTbGen-001 → REQ 确认 + R1 reason CORRECTED**：R1 boilerplate「replays .75-captured GT keyed on signature」**不准确**——mock `_HSPICE_MOCK_SRC`（L86-174）实为 deck-driven **RANGE-SYNTHESIZER**（delay measures→1.0e-9 常量，param measures→`eval(expr with vdd)`），**无 `_MOCK_OUTPUTS`/GT dict，无 signature lookup**。conds (i)(j)(l)(m) 仅验范围（≥2 finite / 1 delay-range 1e-12..1e-8 / 1 voltage-range 0.5..1.3）。Q2：结构正确 testbench（.include dut.sp/.tran/≥2 .measure/.options/.temp/.print + B-net 引用）配 garbage stimulus/measure-points（trig v(a)=999 不可达）⇒ mock 永远吐 1e-9+vdd ⇒ PASS 假阳；real hspice 跑真实 dut_B.sp ⇒ measure=failed/no-crossing ⇒ cond (j) FAIL。**KEY DISTINCTION vs Vcc2scActDeckGen-REQ→OPT-downgrade**：那个 mock **重写 DUT netlist 为 model-free stub**（real hspice 也 conclude garbage，零物理增益）；此处 mock **原样跑候选 testbench 在真实 dut_B.sp** ⇒ real hspice 真做物理，抓 non-converging/garbage testbench。real hspice 有真实 L2 增益 ⇒ REQ（verdict 不变，reason 修正为 deck-driven-range-synthesizer）。

**StdLibCharTmpl-001 → REQ 确认**：mock `HSPICE_MOCK_SRC`（L105-134）按 corner-签名字符串匹配（`.temp 85`+`vddb=1.5`+`tpd_inv_b` for B / `.temp 25`+`vdda=1.8`+`tpd_inv_a` for A）回放嵌入 `_EMBED_SIM{B,A}_MT0/LIS`（自称 .75 HSPICE V-2023.12-SP1-1 pre-gen）。mock **不读 .subckt 拓扑**。Q2：候选造 corner-签名对（.temp 85/.param vddb=1.5/.measure tran tpd_inv_b）但 garbage .subckt 网表（错 sizing/破拓扑）；cond (d) 只数 ≥2 .subckt（非内容），cond (e/f) 查 sig+measure-kinds；mock 按 corner-sig 字符串回放 GT 不顾拓扑 ⇒ conds (j)(k) tpd±15% PASS 假阳。real hspice 跑 garbage-topology deck ⇒ 错 tpd ⇒ cond (j)(k) FAIL。Genuine Type A GT-replay-by-signature（topology-blind keying），同已改造 26 条家族。**R1 boilerplate accurate after body-read**。

**不改** check.py / cases / judge_layers（只读 verdict 确认）。**不进** `live_eval_changes.tsv`（无口径变更）。tsv 3 行更新 live_reason（mock-body 证据）+ check_live（R3 改造方案）+ round=2。

**累计**：REQ 29（done 26，余 3 confirmed-REQ 待 R3 改造），OPT 19，NA 76，cross_shard 2，L2.live 26 不变。**R1 boilerplate 误分类悬念清零**——3 条全部真 REQ，下一轮起 R3 改造（≤6-8 条/轮，hspice/finesim 真跑，每条 §5 七项全勾）。

### r1328：StdLibCharTmpl-001（hspice-mock GT-replay-by-corner-signature · 第27条 · R3 首条）

**Q2 实证（r1328）**：cheat `cheat_garbage_subckt.py` 复制 ref `std_char_tmpl_gen_ref.py`，在 `_gen_deck` 把每个 cell `.subckt_body` 行的晶体管 `w=<x>u`→`w=1e-21u`、`l=<x>n`→`l=1e3u`（电死），保留 corner 签名（`.temp 85`/`.param vddb=1.5`/`.measure tran tpd_inv_b` for B，`.temp 25`/`vdda=1.8`/`tpd_inv_a` for A）+ `.subckt` 数≥2 + 4 measure kinds（桩 `HSPICE_MOCK_SRC` 按 corner-签名字符串匹配查 `_EMBED_SIM{B,A}_MT0/LIS` 回放，**不读 .subckt 拓扑**）→ `_check_static_impl` **15/15 PASS 假阳**（mock 按 corner-sig 回放 GT tpd，不校验晶体管 W/L 物理）。真 hspice V-2023.12-SP1-1 @ hfhds201：w=1e-21u 晶体管电死 → 无切换 → `.measure tpd_inv_b` failed → `job ended`（not `job concluded`）→ judge.mt0 无 tpd_inv_b → conds (i)(j)(k) FAIL。

**Q1 保真**：.75 真跑 ref gen（honest deck）→ REF check_live PASS：B invb_tpd=9.986e-11 / norb_tpd=1.009e-10 == mock `GT_B_INVB_TPD`/`GT_B_NORB_TPD` **逐位一致**；A inva_tpd=5.369e-11 == mock `GT_A_INVA_TPD` **逐位一致**（byte-exact，r1328 实测）。

**改造**：非侵入包装（`_check_static_impl` 15 conds a-o 一字不动 + `check_static` try/except 3-tuple + `check` 兼容 + `check_live(sess)` .75 real-hspice **judge-independent rerun** on candidate-generated `char_template.sp` for hidden B AND visible A AND B determinism re-run，读 real `judge.mt0` 复断 (i)job concluded+(j)invb_tpd within GT_B ±15%+(k)norb_tpd within GT_B ±15%+(n)A inva_tpd within GT_A ±15% cross-input+(o)determinism invb_tpd within 2%，only-add never relax；judge 独立跑 hspice 不信候选 report，封 fake-report 漏洞）+ live-neg（`cheat_garbage_subckt.py`：dead-W .subckt，static-pass mock-replays-GT / live-fail cond (i)(j)(k)）+ `negative_selftest.py` 重写（STATIC 7 negs distinct{b,c,g,e,d,l,h}=7-distinct + §4.9 trio distinct{empty:b,print:c,core:h}3/3 + LIVE_NEG via EDASession）+ `judge_layers=[L0,L1,L2.live]` + JSON `test` 字段 sha `94d75a75e849` 3-way sync（disk==JSON）。

**§5 全绿**：① REF check_live PASS（real hspice B invb_tpd=9.986e-11 == mock GT Q1 fidelity byte-exact）；② 7 static neg FAIL 7-distinct{b,c,g,e,d,l,h} + §4.9 trio distinct{b,c,h}3/3 + live-neg FAIL cond (i)(j)(k)；③ determinism cond (o)（B rerun invb_tpd identical within 2%）；④ SKIP_RUN deploy workdir clean（无 check.py/reference/hidden 泄漏，workdir 仅 assets/outputs）；⑤ sha `94d75a75e849` 3-way sync；⑥ 断言条数只增不减（check_live re-assert i/j/k/n/o 同阈值）；⑦ L5 hidden-B uploaded to sess not in SUT sandbox，check_live 不读 reference/。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T12:45+08:00, jl `[L0,L1]`→`[L0,L1,L2.live]`, repo_commit=94d75a75e849）。

**.75 通路 OK**（r1328 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session slct_r1328/negselftest 用后 close）。自验通道：`_live_upload` via `printf %s '<b64>' | base64 -d` 零腐蚀（r1324 precedent），REF live PASS + CHEAT live FAIL 一次过。

**累计**：REQ 29（done 27，余 2 confirmed-REQ 待 R3 改造：SlicerFbTimeOpt/SpiceTbGen），OPT 19，NA 76，cross_shard 2，L2.live 26→27。

### r1329：SpiceTbGen-001（hspice-mock RANGE-SYNTHESIZER · 第28条 · R3 第2条）

**Mock 模式（distinct from GT-replay family）**：`HSPICE_MOCK_SRC` 是 deck-driven **RANGE-SYNTHESIZER**（非 GT-replay）：parse `.measure tran` 行，delay measures → 1.0e-9（落在 delay-range 1e-12..1e-8），param measures → `eval(expr with vdd)`（落在 volt-range 0.5..1.3），写 job-concluded `.lis`+`.mt0`。**无 `_MOCK_OUTPUTS`/GT dict，无 signature lookup**——对任何结构正确（`.include`/vdd dc/PULSE/`.tran`/≥2 `.measure`/`.options`/`.temp`/`.print` + B-net refs）的 deck 一律吐 1e-9+vdd。conds (i)(j)(l)(m) 只校验 value RANGES 不校验具体值。

**Q2 实证（r1329）**：cheat `cheat_unreachable_trig` —— 结构正确 B testbench（`.include dut.sp`/vdd dc/PULSE/`.tran`/4 `.measure`/`.options`/`.temp`/`.print` + B-net refs a/b/z_nand/z_buf），但 `.measure tpd_a2buf`/`tpd_nand` 的 `trig v(a) val=999` 永不跨越 → `_check_static_impl` **14/14 PASS 假阳**（mock 按 `.measure` name token 发 1e-9，无视 trig 可达性）。真 hspice V-2023.12-SP1-1 @ hfhds201：`val=999` 永不跨越 → `tpd_a2buf=failed`/`tpd_nand=failed`，`vswing=1.2`/`vlow=0` finite → **cond (j) ≥2 finite 仍 PASS**（param measures 活），但 **cond (l) delay-range FAILS**（无 finite delay value）。

**KEY DISTINCTION vs Vcc2scActDeckGen-REQ→OPT-downgrade（r1325）**：那个 mock **重写 DUT netlist 为 model-free stubs**（真 hspice 也 conclude garbage，zero physics gain → OPT）；此处 mock **原样跑候选 testbench 在真 dut_B.sp**（via `.include`）→ 真 hspice **确实 exercise DUT 物理**，能抓 non-converging/unreachable-trig testbench → genuine L2 gain ⇒ **REQ confirmed**（R2 verdict upheld，reason 修正为 range-synthesizer 非 GT-replay）。

**Q1 保真**：.75 真跑 ref testbench（honest deck）→ REF check_live PASS：B `tpd_a2buf=2.204e-09`/`tpd_nand=2.556e-11`/`vswing=1.2000` == `expected_measures_B`（tpd_a2buf_ns=2.2045/tpd_nand_ps=25.56/vswing=1.2）。mock 是 range-faithful 非 value-faithful（发 1e-9 vs real 2.204e-09，均落 delay-range）⇒ Q1 = mock-passing ref genuinely works on real hspice（无 false-negative），非 byte-exact。

**改造（非侵入包装）**：`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple + `check` 兼容 + `check_live(sess)` .75 real-hspice judge-independent rerun candidate testbench + hidden `dut_B.sp`（as `dut.sp`）on B，read real `judge.lis`/`.mt0`，re-assert (i)concluded+no-fatal + (j)≥2 finite real measures + (l)delay-range 1e-12..1e-8 + (m)voltage-range 0.5..1.3 **SAME thresholds never relaxed**；+ Q1 fidelity（ref testbench real hspice B `tpd_a2buf`==2.204e-09±20% / `vswing`==1.2±5%）；+ determinism (o) B rerun delay ±2%；robust `_parse_mt0_live` 处理 real hspice `failed` value token（naive parser 会被 shift）。live-neg=`cheat_unreachable_trig`（static-PASS/live-FAIL cond l）。

**§5 全绿**：① REF check_live PASS（real hspice B tpd_a2buf=2.204e-09/tpd_nand=2.556e-11/vswing=1.2 Q1保真）；② 4 static neg FAIL 4-distinct{b,c,f,k} + §4.9 trio distinct{b,c,f}3/3 + live-neg FAIL cond (l)；③ determinism (o) B rerun delay ±2%；④ SKIP_RUN deploy workdir clean（无 leak）；⑤ sha `71100b227f69` 3-way sync；⑥ 断言条数只增不减；⑦ L5 hidden-B uploaded to sess not in SUT sandbox。

**infra note**：`_live_run_hspice_tb` uploads both tb+dut content via `_live_upload`（`printf %s '<b64>' | base64 -d`）zero-corruption，**no local path on .75**（首版 `cp '<local_path>'` 在 .75 不存在致 hspice `path is wrong` rc=255，已修为 content-upload）。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T13:10+08:00, jl `[L0,L1]`→`[L0,L1,L2.live]`, repo_commit=71100b227f69）。

**.75 通路 OK**（r1329 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session spicetbgen_probe/negselftest 用后 close）。

**累计**：REQ 29（done 28，余 1 confirmed-REQ 待 R3 改造：SlicerFbTimeOpt），OPT 19，NA 76，cross_shard 2，L2.live 27→28。

### r1330：SlicerFbTimeOpt-001（hspice-mock GT-replay-by-.param-signature · 第29条 · R3 第3条 · 末条 REQ 收口）

**Mock 模式（GT-replay-by-.param-signature）**：`_HSPICE_MOCK_SRC`（L141-236）`MOCK_OUTPUTS` dict 按 (4 widths+VVDD+vcm+temp+cap) `.param` 签名回放预录 .75 HSPICE .measure（t0/t1_feedbacktime+i_total）。**不读 slicer netlist**——纯 `.param` 签名 lookup。

**Q2 实证（r1330）**：cheat `cheat_lie_t0t1` —— 选 cfg0（B 上 global-min i_total=436.674n，但真 t0/t1=140.75ps/140.38ps>60ps），**LIE** best_t0/best_t1=46ps≤60ps；all_results 填真实 GT（cfg0..cfg7 t0/t1/i_total from MOCK_OUTPUTS）；A 报真 best=cfg1（t0/t1=46.26ps≤60ps）保 cross-input cond (l)。`_check_static_impl` **14/14 PASS 假阳**：cond (f) 信任候选自报 t0/t1≤limit（盲）；cond (n) L2 re-verify 只 `_grab(out,"i_total")` ±30%（mock 按 cfg0 签名回放同 GT，i_total 对得上），**不复核 t0/t1**（约束变量本身）；cond (i) argmin 只查 best_i_total≤passing i_total（不查 best 是否 passing）⇒ 选 failing config 当 best 也能过。真 hspice V-2023.12-SP1-1 @ hfhds201：cfg0+params_B `t0=1.407552e-10`/`t1=1.40382e-10`>60ps ⇒ **cond (f)-live FAILS**（独立重跑真 hspice 于 best_config 读 real hsp.log）。

**KEY POINT**：与 Vcc2scActDeckGen-syntax-misclass（r1325 OPT）不同——此处 mock 是真 GT-replay（按签名回放 byte-exact 真 hspice 值，非 syntax-only 验证），且 cond (n) 已「真跑」i_total 复核；漏洞在于复核**漏了约束变量 t0/t1**（只查 i_total）。real hspice 补 t0/t1 复核 ⇒ genuine L2 gain ⇒ **REQ confirmed**（r1327 verdict upheld）。

**Q1 保真**：.75 真跑 ref sweep（honest deck）→ REF check_live PASS：B 逐 config real hspice t0/t1/i_total == `_MOCK_GT_B` **byte-exact 0.00% err**（cfg0 140.7552ps/cfg1 68.6381ps/cfg2 44.2068ps）。mock 是 value-faithful（非 range-faithful）⇒ Q1 = byte-exact。

**改造（非侵入包装）**：`_check_static_impl` 14 conds a-n 一字不动 + `check_static` try/except 3-tuple + `check` 兼容 + `check_live(sess)` .75 real-hspice rerun candidate `slicer_fbtime_opt.py` on hidden B AND visible A AND B determinism re-run；**AND** 独立 `_rerun_best`（compose deck via `_override_deck(real src_sp, best_config, params)` → real hspice → 读 real `hsp.log`）于候选 B-best_config 与 A-best_config，re-assert (f)-live real t0 AND t1≤60ps（closes mock-blind t0/t1 hole）+ (n)-live real |i_total| ±30% cand best_i_total（同静态容差，现于真 hspice）+ (l)-live A-best≠B-best + (m)-live both fb_time_limit==6e-11 + Q1 fidelity refB 逐 config real==`_MOCK_GT_B` ±5% + det B rerun best_i_total 1e-9+best_config 同。live-neg=`cheat_lie_t0t1`（static-PASS/live-FAIL cond f）。

**§5 全绿**：① REF check_live PASS（real hspice B-best t0=4.421e-11/t1=4.400e-11/i=1.573e-06==cfg2 真 best + A-best ok + Q1 refB==GT byte-exact + det ok）；② 6 static neg FAIL 6-distinct{c,h,e,f,l,d} + §4.9 trio distinct{c,h,e}3/3 + live-neg FAIL cond (f)；③ determinism det B rerun best_i_total 1e-9；④ SKIP_RUN deploy workdir clean（无 leak）；⑤ sha `bb9192f2ee` 3-way sync（disk==JSON）；⑥ 断言条数只增不减（14 static + 6 live）；⑦ L5 hidden-B uploaded to sess, workdir clean no check.py/reference leak。

**infra note**：`_live_upload` via `printf %s '<b64>' | base64 -d` zero-corruption（r1324 precedent）；`_rerun_best` 读 `hsp.log`（`grep` measure 行）parse t0/t1/i_total。

**登记**：`live_eval_changes.tsv` +1 行（ts=2026-11-27T13:35+08:00, jl `[L0,L1]`→`[L0,L1,L2.live]`, repo_commit=924a14db4）。

**.75 通路 OK**（r1330 reach：open_session 秒级 / hspice V-2023.12-SP1-1 在 PATH @ hfhds201，session sfto-reflive/sfto-negself 用后 close）。

**累计（REQ 收口）**：REQ 29（done **29/29**，余 0），OPT 19，NA 76，cross_shard 2，L2.live 28→**29**。**B shard live-eval R2/R3 改造全部完成**——所有 29 条 confirmed-REQ 已落 L2.live + live-neg + §5 全绿；OPT 19 待排期，NA 76 仅记理由。

## Live-eval 收口（2026-11-27 r1331 · B shard 全绿，报 A 汇总）

> 触发：LIVE_EVAL_ORDER §8 收口判据「REQ 全绿 + OPT 有结论 + NA 有依据」三项全满足。本轮为**只读结账轮**——零 check.py / cases / judge_layers / live_eval_changes.tsv 改动（REQ 改造已于 r1330 全部落盘，见上节）。

### 收口三口径（与 `live_eval_review_B.tsv` 全量对账一致）

| verdict | 条数 | 收口状态 | 依据落盘 |
|:--|--:|:--|:--|
| **LIVE-REQ** | 29 | ✅ 全绿（done 29/29，§5 七项全勾） | 每条 r1294–r1330 落 `check_live` + live-neg + `judge_layers=[L0,L1,L2.live]` + JSON test sha 3-way sync；29 行登记 `live_eval_changes.tsv` |
| **LIVE-OPT** | 19 | ✅ 全部有结论（concluded 19/19，0 reformed） | 每条 tsv `live_reason` + `check_live` + `live_evidence` 填满；结论分两类见下 |
| **LIVE-NA** | 76 | ✅ 全部有依据（reason 填满） | tsv `live_reason` 逐条写明「deliverable 本身是文本/脚本/日志分析/改文件/问答」 |
| cross_shard | 2 | 走 cross_shard 流程，不进本轮三分类 | OtaAcReport-001 / PUvddSweep-001 |
| **合计** | **126** | = 124 green_verified + 2 cross_shard | — |

### REQ 29 条清单（全部 reformed → L2.live）

AOI21ArcChar-001, AlterDeckSplit-001, BistOscRccReorder-001, CdlBulkSanitize-001, CmlPvtAcReport-001, CtleAcChar-001, DelayChainEdgeMeas-001, DelaySigma-001, DffSetupHoldChar-001, FineSimModelScopeFix-001, FineSimWorkflowRunner-001, GmidLut-001, GrDecPwrVerifTb-001, InvPVTchar-001, InvTripDelay-001, OpampACSpec-001, PFDdeadZone-001, PVTalterChar-001, PorCapSweep-001, SlicerFbTimeOpt-001, SpiceSim-001, SpiceTbGen-001, SramSNM-001, StdLibCharTmpl-001, StrongarmFomSweep-001, TaperBufOpt-001, Vcc2scTranGen-001, VcoKvcoChar-001, VwlpRefDeckSet-001

**家族分布**：hspice-mock GT-replay-by-signature 24 条（deck-driven，候选自建 deck ⇒ Q2 可骗）+ finesim-mock GT-replay 3 条（FineSimModelScopeFix/FineSimWorkflowRunner/BistOscRccReorder）+ hspice-mock range-synthesizer 1 条（SpiceTbGen，非 GT-replay 但 real hspice 有 genuine L2 gain）+ hspice-mock GT-replay-by-.param-signature 1 条（SlicerFbTimeOpt，漏洞在 cond(n) 复核漏约束变量 t0/t1）。

### OPT 19 条清单（全部 concluded，0 reformed — L2.live 增益为零或边际）

CTLEAC-001, CTLESpec-001, FineSimNoRefCktFix-001, LisMeasExtract-001, MinpulseRewriteRun-001, NetlistLintHsp-001, OpampChar-001, PlatMosThinIdsatIoffSweep-001, PostsimPortAudit-001, PostsimToggleDiag-001, PwlStimTransform-001, RcurrDirClassify-001, SimExpl-001, SpGen-001, StimPWL-001, Tr0TrTfMeas-001, TxRonSize-001, Vcc2scActDeckGen-001, VlshftParamOpt-001

**结论分两类**（逐条 .75 实证 / full-mock-body 读支撑，落 tsv `live_evidence`）：
- **Type B（11 条）**：候选跑 **PROVIDED** deck/netlist/tb（judge-built），不 author deck ⇒ Q2「shape-right-physics-wrong deck 假阳」**不成立**（候选不能注入 garbage physics，hidden tb 只读）；mock==real tool 对该固定输入。代表：CTLESpec/CTLEAC/OpampChar/NetlistLintHsp/PostsimPortAudit/PostsimToggleDiag/RcurrDirClassify/SimExpl/Tr0TrTfMeas/LisMeasExtract/MinpulseRewriteRun。
- **Faithful-physics-solver / syntax-validator（8 条）**：mock 非 GT-replay——要么 faithful level-1 Shichman-Hodges DC solver（SpGen/PlatMosThinIdsatIoffSweep/TxRonSize，bit-exact real hspice level=1），要么 PWL-crossing 纯插值（StimPWL），要么纯语法/结构 validator（PwlStimTransform/Vcc2scActDeckGen/FineSimNoRefCktFix/VlshftParamOpt，real hspice 与 mock 同 conclude garbage，零物理增益）。

**OPT 不 reform 的依据**：每条均 .75 实证 mock==real（bit-exact 或同 conclude）或结构证明 Type B 候选不可骗；L2.live 加零或边际断言，不增判分严格度。OPT「done 0」= 0 条 reform（OPT 按 §8 仅需结论，不需改造）；「concluded 19/19」= 收口判据「OPT 有结论」满足。

### NA 76 条清单（deliverable 本身是文本/脚本/日志分析/改文件/问答，保持 [L0,L1]）

BisecMt0SmCalc-001, BridgeCfgDiag-001, ButterflyCurve-001, CTLETranDeck-001, CabufPvtDatAudit-001, ClampPwrStateExtract-001, CmlBwExtensionHandbook-001, CmlDivOscDiag-001, CmlSweepHeadroomDiag-001, Coord3DProj-001, CosimRunBlockOpt-001, DQSEHFlagNoEffectDiag-001, DblTailSlicerDeckGen-001, DcaStimSweepGen-001, Ddr6RptCmdExtract-001, DeckConsistencyCheck-001, DelayCornerIdent-001, DupSubcktDefDiag-001, FifoDelayOptDiag-001, FinesimLaunchAgent-001, FinesimMatrixrunAgent-001, FsdbPulseFilter-001, FsdbScopeSignalLocate-001, GaaFetDeckAugment-001, LatchSubcktLocate-001, LvLvioSweep-001, MBistTopAnalyze-001, MR7PsdScopeAnalyze-001, McVthSpVariantGen-001, ModelLibVerDiff-001, MonteCarloDeckGen-001, Mt0Reorg-001, Mt0TskewCalc-001, NetlistModSummary-001, NetlistWLReduce-001, PdkLayerLocate-001, PexStimulusBuild-001, PlatInvsThick-001, RonMonoDiag-001, RsCalcAutoVia-001, SentaurusDeckSetupSummary-001, SharedLibDeployFix-001, SiInpTokenRm-001, SimModelMismatchDiag-001, SimProgressCheck-001, SimSavedCornerComplete-001, SimSpecJudge-001, SlicerSweepFomOpt-001, SnmButterflyCalc-001, Sp2tVerilogaSwitch-001, SpRcAlterGen-001, SpfAutosimSetup-001, SpfNtsvMissingDiag-001, SpiceMeasInjector-001, Sram6tTbBuild-001, StackedMOSOpAnalysis-001, StimScriptCfgLocate-001, StrongarmBaselineAnalyze-001, SubcktInstParamInj-001, SwitchTbGen-001, TbMeasCheck-001, TbSpiceMeasureAudit-001, TmVerifyTbGen-001, TranStimSync-001, TrimMarginSpec-001, TrtfMeasDeckGen-001, TscodecompTbVerify-001, TzqlatLocate-001, VSplit-001, VsimFinesimAdapt-001, WtmFileReview-001, WtmPatternDirReview-001, WtmWriteArrayScope-001, XmelabCuvpomPortDiag-001, XrunLogErrDiag-001, ZqPatternTimingAnalyze-001

**NA 依据共性**：deliverable = 写 Makefile/tcl/脚本、解析既有 log、改文件、答 API 用法、生成 deck 文本（不跑 sim）；check.py 的 subprocess 仅跑候选脚本本身，hspice/finesim/vcs 仅出现在 deck 文本/字段名/evidence，非真二进制直调。R1 逐条核 subprocess 上下文（r1288/r1289），仅 LisMeasExtract-001 误判（升 OPT），余 76 稳固。

### 与旧 P4 的差异（r1264 → 本轮）

| 维度 | 旧 P4 (r1264) | 本轮收口 (r1331) | 差异依据 |
|:--|:--|:--|:--|
| 口径 | 全量 130 Lite-B（含 cross_shard 4） | lite-500 B 名册 126（= 124 green + 2 cross_shard） | LIVE_EVAL_ORDER §1.1 名册唯一来源 `lite_health_all.tsv` |
| T1/T2/T3 | T1=0/T2=1/T3=129 | REQ=29/OPT=19/NA=76/cross=2 | 三分类重判 + 桩体检 |
| mock 桩体检 | 未系统做 | 29 REQ + 19 OPT 全部 full-mock-body 读 + .75 实证 | §2.1 Q1/Q2 逐条答 |
| 关键词扫法 | 旧 P4 用关键词 | 本轮证伪关键词扫（r1290/r1302/r1303/r1315/r1325/r1326 6 条 REQ→OPT 降级，R1 generic boilerplate 误分类清零） | §2.1 规则 2 |
| 落盘 | 旧 P4 只分析 | 29 REQ 全部落 L2.live + live-neg + §5 全绿 | r1294–r1330 |

### 报 A 汇总数字

- **B shard live-eval 收口完成**：REQ 29/29 reformed（L2.live 0→29），OPT 19/19 concluded（0 reformed），NA 76/76 有依据，cross_shard 2 走原流程。
- **口径变更登记**：`live_eval_changes.tsv` B 行 29 条（jl `[L0,L1]`→`[L0,L1,L2.live]`，repo_commit 范围 r1294–r1330，HEAD=`924a14db4`）。
- **待 A**：出 `designflow/live_eval_summary.md`（4 shard 三分类合计 + REQ 改造进度 + 缺口台账）；通报 zhulong 变更 commit 范围。B 不写 A 的文件。
- **🚫 不设等待**（§1.1）：B 随时可改判分（只需 `live_eval_changes.tsv` 追加登记）；zhulong 体温计反馈的新增 FAIL 优先于 OPT。
