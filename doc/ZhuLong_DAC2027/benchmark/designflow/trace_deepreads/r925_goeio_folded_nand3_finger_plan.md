# r925 deepread — goeio (kepeim @ hfeg0plg90, mc=223, session 1794363615663_goeio)

**Shard C revival** (11-15 令: parked-without-deepread 可 revive). r537 旧判 "Q&A/sim/run-existing REJECT" 现作废——analysis-Q&A 是合法真实意图。

## Trace 概况
- 152 msgs / 86 user · 66 assistant · 1.4MB · 11-13 15:49
- 工具：read_files / RAG_MCP_Server__search_apis / run_approved_command (aether)
- 附件：nand3LVSx1_pc60.png (用户截屏 stdcell layout)

## 真实意图（操作域 = layout_aether，非 keyword 误判的 physical_verify）
kepeim 在 **Aether 中阅读 stdcell 库里的 nand3LVSx1_pc60 版图**，逐层学习 folded-NMOS NAND3 的 finger 摆放与 S/D 排列。核心提问链：

- msg 0/52/53: "我在学习画 nand3LVS_pc60 这个 stdcell，教教我如何理解这个器件，以及 schematic 和 layout"
- msg 85: "我在画 nand3，上拉三个并联，nf=1，下拉三个串联，nf=2，我看 stdcell 库里面画的下拉拆成了六个单独的。然后接的时候作为同一个 nmos 的两个器件分别在对称到两侧，我不是很理解这种接法"
- msg 104: "我对串并联关系尤其是像在 nand3 中将一个 nf=2 的 nmos 在 layout 中拆分成两个单个但仍要满足 schematic 对应关系这些连接与摆放不是很清楚"
- msg 110/111: "拆成 6 个后下面的管子如何依次摆放，从 s 到 d 以及电流方向这一层级给我解释清楚"
- msg 121: "如图，vss 如何接到他们上面，目前从左到右依次是 dsdsdssdsdsd，对不对"
- msg 124: "俩 s 如果在并联的正中间，那当 vss 接入时不是把两个并联的连接到一起短路了吗？所以我看标准件中是 sdsdsd，中间两个 d 的排布，两根线在左右两边接入 vss，是不是这样才是对的"

## Gold 答案（trace msg 112/122 assistant 实证）
- 6 poly gates (A,B,C 左 + A,B,C 右对称) 切 N+ active 成 **7 段**
- S/D 序列（左到右逐段）: D | SD | SD | SS | DS | DS | D → 拼接 = **"dsdsdssdsdsd"** (12 chars)
- **VSS tap** = 第 4 段 (0-based index 3)，标签 "SS"（两条串联链的 Source 汇合点，电位最低）
- **Y tap** = 第 1 段 (index 0) 与 第 7 段 (index 6)，标签 "D"（两条链的 Drain 端）
- 左链电流 Y→VSS (top→bottom)，右链电流 VSS→Y (bottom→top)，相向汇合于中段
- nf=2 → 每个 series NMOS 拆 1 finger 左 + 1 finger 右（symmetric fold）

## 派生公式（N = series PDN 晶体管数, symmetric_folded, nf=2）
- num_fingers = 2N · num_poly_gates = 2N · num_segments = 2N+1
- power_tap_segment = N (0-based center) · label "SS"
- output_tap_segments = [0, 2N]
- sd_sequence = "D" + "SD"×(N-1) + "SS" + "DS"×(N-1) + "D"
  - N=3 → "dsdsdssdsdsd" ✓ · N=2 → "dsdssdsd" ✓

## Case 设计（档 B reframe）
- **case_id**: EDA-Eval-DesignFlow-FoldedNandFingerPlanAnalyzer-001
- **domain**: layout_aether
- **形态**: 给定 folded-CMOS stdcell 版图的符号化结构描述 (layout JSON: mos_groups + series/parallel topology + nf + nets)，agent 写 `finger_plan_analyzer.py` 产出 finger-plan 分析报告 (JSON: num_poly_gates / num_diffusion_segments / num_fingers / sd_sequence / power_tap / output_taps / chains / topology)
- **A (可见)**: nand3LVSx1_pc60, PDN=3 series NMOS nf=2 folded + PUN=3 parallel PMOS → N=3, seq="dsdsdssdsdsd", VSS tap idx=3
- **B (hidden)**: nand2LVSx1_pc60, PDN=2 series NMOS nf=2 folded → N=2, seq="dsdssdsd", VSS tap idx=2 (规模/取值/结构均不同)
- **k=16 teeth** (≥8): zip 含 analyzer.py + py_compile / --help / B exit0+report.json+keys / num_poly_gates=4 / num_segments=5 / num_fingers=4 / sd_sequence="dsdssdsd" / power_tap{VSS,idx2,SS} / output_taps=[{Y,0},{Y,4}] / chains left+right direction+transistors / topology PDN=series PUN=parallel / sd_sequence 长度=2N / power_tap idx=(segments-1)/2 / output_taps=[0,segments-1] / anti-hardcode seq≠A / anti-hardcode tap idx≠3 / 3-seed ordering-invariant determinism
- **§4.9 三假**: (a) empty stub → tooth3 fail (b) only-print → tooth3 fail (c) delete S/D derivation → tooth6/7/8 fail
- **3-seed**: B 晶体管列表 3 种乱序 (seed1/2/3)，analyzer 必须按 gate 排序后派生，3 次输出 byte-identical 且全正确

## 串台检查
- 4-shard ledger: goeio 仅 C ledger (parked→claimed r925)，无他 shard
- 4-shard jsonl trace_source: 无 goeio
- 同 domain 已落库 case: Nand3LefDeriveAudit-001 (pg_layout, LEF 头部派生，不同), LayToolFingerprintAudit-001 (工具指纹，不同), AetherLayerPurposeExplainer-001 (layer 用途解释，不同) — 无 fold/finger/S-D 排列主题，正交
