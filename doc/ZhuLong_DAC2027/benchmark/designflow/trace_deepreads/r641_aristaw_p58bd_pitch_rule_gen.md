# r641 deepread — aristaw@hfeg0plg68 / session 1793794370969_p58bd

**user**: aristaw  **host**: hfeg0plg68 (10.129.8.106)  **mc**: 15  **domain**: physical_verify
**session**: 1793794370969_p58bd.messages.json (38 msgs, 4 real user turns, ~160KB)
**keywords**: drc:92;calibre:13;.gds:10;gdsii:9

## 真实任务（逐字 user turns）

- **U#0**：「分析/home/aristaw/Grid/checkInteger_newV3_0624.rule 做了什么检查」
- **U#4**：「根据上面到rule重新生成一个相同格式的rule，检查AR_ARRAY和WL_ARRAY两层到内间距设计pitch(74nm和74nm）。」
- **U#16**：「gap值为22nm」（覆盖 agent 建议的 37nm）
- **U#22**：「在这个检查里增加SN1_ARRAY 和SN2_ARRAY，进行相似的检查，SN1同ARZ，SN2同WL」
  - ask_question 澄清层号 → user 答「SN1_ARRAY: Layer 2 Datatype 7, SN2_ARRAY: Layer 3 Datatype 7」

均为「提出需求/表达目标」轮（未给根因/方案）→ 符合 A 档选轮规则。

## 原始 rule（checkInteger_newV3_0624.rule，65 行，格式参考）

Calibre SVRF DRC deck，检查 AR_ARRAY(L1D7→8015) 与 WL_ARRAY(L28D7→9612) 两层内部间距是否符合设计 pitch 整数倍：
- 全局：LAYOUT PATH/PRIMARY/SYSTEM GDSII, RESOLUTION 1, PRECISION 10000, UNIT LENGTH U, DRC RESULTS DATABASE/SUMMARY/MAXIMUM, FLAG ACUTE/OFFGRID/SKEW/NONSIMPLE, VIRTUAL CONNECT COLON NO, LAYOUT DEPTH ALL
- VARIABLE GRID 0.0001
- checkInteger_ARWL 块，2 个 check sub-block：
  - AR: A=INTERNAL AR_ARRAY == 0.073 OPPOSITE REGION; B=DFM SPACE A <= 15 BY EXT HORIZONTAL; E=DFM PROPERTY B [L=(REMAINDER((EW(B)+0.073),0.112)==0)?1:0]==0; F=DFM SHIFT EDGE [E] OUTSIDE BY GRID; G=EXPAND EDGE F INSIDE BY GRID; COPY G  (pitch 0.112, gap 0.073, range 15)
  - WL: A1=INTERNAL WL_ARRAY == 0.083 ... pitch 0.132, gap 0.083, range 500

## gold（最终接受态 checkInteger_pitch74nm.rule，102 行，agent 生成 + user 接受）

4 层检查：AR_ARRAY / WL_ARRAY / SN1_ARRAY(L2D7→8025) / SN2_ARRAY(L3D7→8022)，统一 pitch=0.074, gap=0.022, range=15：
- 层映射新增 SN1_ARRAY(8025)/SN2_ARRAY(8022)
- checkInteger_ARWL 块 4 个 check sub-block（A/B/E/F/G, A1..G1, A2..G2, A3..G3），每块：
  - `A<sfx> = INTERNAL <layer> == 0.022 OPPOSITE REGION`
  - `B<sfx> = DFM SPACE A<sfx> <= 15 BY EXT HORIZONTAL`
  - `E<sfx> = DFM PROPERTY B<sfx> [L=(REMAINDER((EW(B<sfx>)+0.022),0.074) == 0) ? 1 : 0] == 0`
  - `F<sfx> = DFM SHIFT EDGE [E<sfx>] OUTSIDE BY GRID`
  - `G<sfx> = EXPAND EDGE F<sfx> INSIDE BY GRID`
  - `COPY G<sfx>`
- 注释头描述 4 层 + 公式 `(measured_space + 0.022) % 0.074 == 0`
- SN1 复用 AR 参数，SN2 复用 WL 参数（本版 pitch/gap 一致）

## agent 工具链
read_files(rule) → markdown 分析报告 → read_files 全文 → ask_question(gap 值) → user 指定 → editor 创建 checkInteger_pitch74nm.rule → read_files 验证 → editor 改 gap 0.037→0.022 → read_files 验证 → ask_question(SN1/SN2 层号) → editor 加 LAYER MAP + 2 check blocks → editor 改注释头 → read_files 最终验证 → markdown 总结。

## 交付形态
**generation task** — 用户要一个生成好的 .rule FILE（非解析）。gold = 最终 4 层 .rule 文件。

## B档 reframe（generator-tool，新子型 svrf-pitch-rule-generator）
真实 .rule 不可达沙盒 + 隐藏 B 防硬编 → deliverable=`pitch_rule_generator.py <spec.json> <output.rule>` 读 JSON spec（layers/pitch/gap/range/derived_id/...）→ 生成结构同构的 Calibre SVRF DRC rule。check() 在隐藏 B spec 上 subprocess 跑候选 → 解析输出 .rule 验结构。
- **distinct vs r635 PgSvrfRuleAnalyze / r639 DrcSvrfRuleWaiveExtract**：r635/r639 = extraction tool（parse existing rule→JSON），本 case = generation tool（spec JSON→emit rule）。方向相反，新子型。
- asset A = reference_rule.svrf（原始 65 行 rule 作格式参考）+ spec_a.json（4 层 74nm/22nm spec，mirror trace gold）
- hidden B = 3 层 88nm/33nm/range20 spec（AR/WL/BL，BL=L5D7→8035）
- hidden B2 = 2 层 102nm/44nm/range25 spec（反硬编交叉校验）

## trace_source
{user: "aristaw", host: "hfeg0plg68", session_file: "1793794370969_p58bd.messages.json", match_count: 15, real_task_summary: "分析 Calibre SVRF DRC rule（checkInteger_newV3_0624.rule，AR/WL 两层 pitch 整数倍内间距检查），按相同格式重新生成 4 层（AR/WL/SN1/SN2）74nm pitch、22nm gap 的 DRC rule 文件"}
