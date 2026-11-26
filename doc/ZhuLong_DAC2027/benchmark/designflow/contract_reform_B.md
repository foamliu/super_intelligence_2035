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
