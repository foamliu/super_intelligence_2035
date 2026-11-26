# r639 deepread — fhwang @ hfeg0plg105 — 1793006457236_47bm9 (mc21, physical_verify)

**source**: summary_1115_081559.tsv, fresh-pool unpeeked non-cluster candidate (C-keyword: aether:78;calibre:17;drc:13). session 23 msgs, 2 real user turns, ~140KB. via .75 ssh cat `/home/fhwang/.cline/data/sessions/1793006457236_47bm9/1793006457236_47bm9.messages.json`.

## user turns (verbatim, A档选轮)

- **U#0** 「DGX=DGX_drawing OR {CHIP NOT PDR} 解释一下」— Cadence/Aether libManager filter expression 解释 (single-turn conceptual Q&A, no artifact). scope-out: 仅 U#0 无 C produce-task，U#1 才是核心。
- **U#19 (核心 produce-task)** 「帮我仔细解读这条rule
  ```
  R_P_AT4DMY_S_04_M {
    @ Max - Space between AT4_DUMMY2 and transistor AT4 [along gate width direction]
    error1 = MERGE (EXPAND EDGE AA_gate_width OUTSIDE BY 0.781)
    error2 = MERGE (EXPAND EDGE AA_gate_width OUTSIDE BY 1.262)
    error = (error1 INTERACT AAall < 2) INTERACT (error2 INTERACT AT4_DUMMY2)
    waive1 = error2 INTERACT AAall<2
    waive2 = error2 CUT NW_drawing
    waive3 = SIZE AAplug BY 0.6 //random value for waive AA plug
    waive4 = WITH WIDTH (EXT AA_gate_width AT4_DUMMY2 <= 1.262 > 0.781 OPPOSITE REGION) < 0.41
    waive = OR waive1 waive2 waive3 waive4
    error NOT INTERACT waive
  }
  ```
  」— **Calibre SVRF DRC rule structured interpretation Q&A**。用户提需求（解读规则），未给根因/方案 ⇒ A档选轮合格。

## gold (ASST#22 逐字结构化解读，post tool-search)

assistant 产详细 markdown 解读，关键结构：
- **rule_id** R_P_AT4DMY_S_04_M（Foundry 命名 R=Rule/P=工艺模块/AT4DMY=AT4 Dummy/S=Space/04_M=编号变体）
- **check_type** Max - Space（@ 注释首段），intent = AT4_DUMMY2 与晶体管 AT4 有源区沿栅宽方向最大间距
- **error1/error2** = MERGE (EXPAND EDGE AA_gate_width OUTSIDE BY 0.781 / 1.262) → 在 AA_gate_width 边界外侧画 0.781 / 1.262 宽检测带
- **error** = (error1 INTERACT AAall < 2) INTERACT (error2 INTERACT AT4_DUMMY2) — 两步：error1 接触 <2 个 AAall 图形（孤立/边缘侧）∩ error2 与 AT4_DUMMY2 交互（dummy 落在 0.781~1.262 环带内）
- **4 waive clauses**：
  - waive1 = error2 INTERACT AAall<2
  - waive2 = error2 CUT NW_drawing
  - waive3 = SIZE AAplug BY 0.6
  - waive4 = WITH WIDTH (EXT AA_gate_width AT4_DUMMY2 <= 1.262 > 0.781 OPPOSITE REGION) < 0.41
- **waive = OR waive1 waive2 waive3 waive4** → 4 豁免合并
- **final filter** error NOT INTERACT waive → 排除豁免后的 error
- **layers** AA_gate_width, AAall, AT4_DUMMY2, NW_drawing, AAplug
- **ops** MERGE, EXPAND, EDGE, INTERACT, CUT, SIZE, WITH, WIDTH, EXT, OR, NOT, OPPOSITE
- **values** 0.781, 1.262, 2, 0.6, 0.41

## case 合成（B档 mock-behavioral grounded-extraction-tool reframe）

承 r635 PgSvrfRuleAnalyze-001 / r617 TvfSetlayerExpl / r630 LvsHcellFailReportExtract 模式。deliverable = `drc_rule_analyzer.py <rule.svrf> <output.json>` 解析单条 SVRF DRC rule block → 结构化 JSON {rule_id, annotation, check_type, edge_ops[], interact_threshold, waive_clauses[], waive_combine, waive_count, final_filter, layers_used, op_inventory{}, values[], counts{}}。

**distinct vs r635**：r635 解析 PG SVRF 规则（7 条 PG_S/PG_EXT/PG_F/PG_L 规则，单值/单 op 路径，无 waive clause）；本 case 解析单条含 **4 waive clauses + OR 合并 + final NOT INTERACT waive** 的复杂 DRC rule，focus on waive-clause 结构提取 ⇒ 新子型 `drc-svrf-rule-waive-clause-structured-extract`。

- **asset A** = rule_a.svrf（R_P_AT4DMY_S_04_M 逐字）
- **hidden B** = rule_b.svrf（R_P_M2DMY_S_07_M，Min Space，M2 gate_length，3 waive clauses，值 0.520/0.840/0.45，interact<3）
- **hidden B2** = rule_b2.svrf（R_X_AT3DMY_W_02_M，Max Width，AT3 gate_width，1 waive clause WITH WIDTH，值 0.640/1.080/0.33，interact<2）— B/B2/A 三方 rule_id/check_type/waive_count/layers/values/op_inventory 全不同 ⇒ 反硬编牙

## 判分条件 (k=15 a-o)

结构2(a:zip+py / b:py_compile) + B运行1(c:B exit0+合法JSON+顶层键) + B反硬编6(d:rule_id==B / e:check_type==B / f:edge_ops count+distances==B / g:interact_threshold==3 / h:waive_count==3 / i:waive_combine==OR) + B layers/op 3(j:layers含B M2层不含A AT4层 / k:op_inventory含CUT+SIZE / l:final_filter含NOT INTERACT waive) + B2反硬编2(m:B2 rule_id==B2 / n:B2 waive_count==1) + 确定性1(o:两跑字节一致)
