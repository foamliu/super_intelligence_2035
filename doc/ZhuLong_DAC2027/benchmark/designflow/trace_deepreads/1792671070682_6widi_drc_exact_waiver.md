# trace_deepread — 1792671070682_6widi (sherlock @ hfeg0pfn011) — physical_verify

## 选料
- layout-affinity score 排序法（r319 引入，r321 沿用）扫 summary.tsv(11-09_224902) → 1127 uniq score>=100 候选 → 扣除 4-shard ledger(3966) + AVOID 用户(xinqiaoz/ellawu/jcgu/e0045142/t0002962/e0047527/miccao) → 51 non-ledgered → peek status → completed 中挑 produce-task。
- **6widi**(sherlock@hfeg0pfn011, score=1499, mc=73, kw=drc:1278;pdk:290;calibre:117;lvs:84;cmos:42;transistor:32;pex:21, status=**completed**, 54 msgs, **1 user turn**) = CLEAN seed。

## 真实对话流（8 user turns? 否，仅 1 user turn）
- **U#0（唯一用户轮，逐字原文）**：「根据所给DRC deck，将其中的 BLR_S_004_00 改为BLR与AGT 的精确值，并且只需要BLR的一条长度为0.03的边符合条件即通过」+ 附件 `calibreDRC.rule1`（1.7M chars / 39217 行，真实生产 Calibre SVRF deck）。
- assistant 链路：read 附件 → search 定位 BLR_S_004_00 块（line 8688）→ 分析 `@Min` 语义（`EXT BLR AGT < _BLR_S_004_00_ ABUT<90 SINGULAR INSIDE ALSO REGION`）与注释掉的 `/*BLR_S_004_00 @Exact` 模板 → 推理「精确值」=把 @Min 改 @Exact（spacing != value 即违例）；「只需一条长度 0.03 的边符合即通过」= per-line waiver：每条 BLR 线（`LENGTH BLR == 0.03`）若含 ≥1 条到 AGT 精确间距 == `_BLR_S_004_00_`(=0.16) 的边则整线豁免，否则报该线非精确边 → 写 `modify_drc.py`（python-runner）逐行替换 8688-8699 块 + 删注释模板 → 写出 `/home/sherlock/calibreDRC.rule1.modified` → verify：变量 `_BLR_S_004_00_` 仍 0.16、仅目标块改变、邻接规则不变。
- **gold = 用户接受**：status=completed，单轮无纠正，assistant 终态「Verification passed」。

## 关键产物
- **新 BLR_S_004_00 块**（gold，逐字）：
  ```
  BLR_S_004_00 {
     @Exact - Space between BLR and AGT must equal ^_BLR_S_004_00_, overlap is not allowed. Only BLR edges with length 0.03 are considered.
     @Per-line waiver - a BLR line (shape having an edge of length 0.03, LENGTH BLR == 0.03) that contains at least one length-0.03 edge exactly ^_BLR_S_004_00_ away from AGT passes entirely (not reported).
     @Only BLR03 lines that contain no qualifying edge report their non-exact-spacing edges; BLR03/AGT overlap is always reported.
       BLR03      = LENGTH BLR == 0.03
       GOOD_REG   = SIZE (EXT BLR03 AGT == _BLR_S_004_00_ ABUT<90 OPPOSITE REGION) BY GRID
       NOGOOD     = BLR03 NOT INTERACT GOOD_REG
       BAD        = EXT BLR03 AGT != _BLR_S_004_00_ ABUT<90 OPPOSITE REGION
       BAD INTERACT (SIZE NOGOOD BY GRID)
       BLR03 INTERACT AGT
  }
  ```
- 变量 `_BLR_S_004_00_ = 0.16`（不变）、`_BLR_W_001_00_ = 0.03`、`_BLR_L_001_00_ = 0.13`。
- 真实 gold 脚本 `modify_drc.py` **硬编码行号 8687-8698**（只对 A 的 deck 有效）→ 本 case 改造为「通用脚本」题：候选须按块名定位、按 deck 自身变量参数化。

## case 设计（EDA-Eval-DesignFlow-DrcExactWaiver-001，physical_verify，A档 faithful，L1，k=15 a-o）
- **A**（assets/.../calibreDRC_A.rule）：合成 SVRF deck（header + LAYER MAP + VARIABLE 段含 BLR_W/L/S/ENC + PCV/PCM + 7 条规则含 BLR_S_004_00 @Min + 注释 @Exact 模板 + 邻接 BLR_S_003_00/BLR_ENC_001_00）。
- **prompt**：A档 = U#0 逐字原文 + 附件说明。
- **task_brief**：≤3 行，只写交付接口（modify_drc.py <in> <out>）+ 文件位置。
- **B/B2/B3**（hidden，结构/取值不同非改名）：
  - B：BLR_W=0.03、S=0.16，BLR_S_004_00 用 `OPPOSITE REGION`（非 A 的 SINGULAR INSIDE ALSO），规则顺序打乱，含注释模板。
  - B2：BLR_W=0.04、S=0.20，**无注释模板**，规则顺序不同，BLR_S_004_00 用 `SINGULAR REGION`。
  - B3：BLR_W=0.03、S=0.12，BLR_S_004_00 用 `<=`（非 `<`），注释模板内容不同。
- **check**：跑候选 `modify_drc.py <B> <out>` ×3 → 验 15 条件 a-o（zip/脚本/3 deck 运行/块未删/@Exact 改造/两变量不变/LENGTH BLR == <BLR_W>/== 与 != /waiver/overlap/旧 @Min 行与注释模板删除/邻接规则逐字节一致+花括号配平）。
- **negatives**：naive(copy) / print_only(只打印) / deleted_core(删块) 全 FAIL；§4.9 三假（empty_shell/print_expected/name_only）全 FAIL。ref self-test PASS ✓。
- 难度：候选须 (1) 解析 SVRF 块名定位（非行号）(2) 读 deck 自身 _BLR_W_001_00_ 参数化 (3) 推理 @Min→@Exact per-line waiver 语义 (4) 删注释模板 (5) 保邻接规则不变。A档目标≤10%。

## trace_source
- user=sherlock, host=hfeg0pfn011, session_file=1792671070682_6widi, match_count=73
- real_task_summary: 修改 Calibre DRC deck 中的 BLR_S_004_00 规则：把 @Min 间距检查改为 BLR 与 AGT 的 @Exact 精确间距检查，并加 per-line waiver——每条长度 0.03 的 BLR 边只要有一条到 AGT 精确间距满足即整线通过，否则才报非精确边
