# trace_deepread — r602 · claire1l · 8dkdw · QuantusLayerSetupDocGen-001

- **session**: `1794380399121_8dkdw.messages.json` @ hfeg0plg76 (10.129.8.124), user claire1l
- **match_count**: 70 (cadence:447 lvs:303 pdk:64 techfile:61 transistor:23 calibre:11 mosfet:10 cmos:10; tools: innovus×2 netlist×1 calibre×1)
- **domain**: physical_verify (Quantus techgen layer_setup = LVS/PEX techgen PDK setup)
- **msgs**: 123 (5 user_input)
- **历史**: r578 peek 旧判 REJECT「comprehension/doc layer_setup syntax summary→md→pdf」(旧规则 analysis-only 判 weak)；pool_reaudit_C.tsv r590 新判 **可造**（Q&A/analysis: check 验答案结构+关键事实+hidden B）。2026-11-15 令「B 类被误杀该复活」典型实例。r601 选料结论：fresh top-mc(70-79) 旧规则全 parked，回复活池选料，优先 8dkdw doc-grounded extraction 原型。

## 用户意图（原话逐字，A 档选轮规则：取"提需求/表达目标"轮）

- UI#1 (idx=0): 「读取这个路径下的所有文档：/apps/cdsmgr/cadence_tools/QRC/QUANTUS23.10.000/doc/quantusTechgen/，并且总结下layer_setup文件的写法」
- UI#2 (idx=16): 「输出一个文档，介绍layer setup文件，包括其作用、文件架构，语法规则等」← 核心 produce-task
- UI#3 (idx=46): 「md文件怎么打开」
- UI#4 (idx=48): 「将这个md文件转换为pdf格式」
- UI#5 (idx=51): 「输出一个pdf文档，介绍layer setup文件，包括其作用、文件架构，语法规则等」

→ 真实意图：读 Cadence Quantus techgen 文档目录 → 产出介绍 layer_setup 文件的结构化指南（作用/文件架构/语法规则），md→pdf。属 doc-grounded extraction（D r699 grounded-extraction-tool reframe 合用：source-type=manual/doc-grounded）。

## agent 工具链（idx 序）

1. `list_allowed_files` 列 quantusTechgen/ 目录
2. `read_files` 批量读 6+ HTML：The_Layer_Setup_File / Using_Techgen_to_Create_the_Technology_File / Contents_of_the_Quantus_AoT_PDK / Defining_the_layer_setup_File / Mapping_Conductors__Diffusion__and_Substrate / Mapping_Contacts_and_Vias / Layer_Naming_and_Derived_Layers / Stamping_in_Quantus（含 start_line/end_line 翻页）
3. `editor` 写 `/home/claire1l/layer_setup_文件介绍.md`（345 行，10 章节：作用/文件架构与组织/通用语法规则/导体-扩散-衬底映射/接触孔-过孔映射/派生层与层命名/未映射层处理/衬底Stamping/与Techgen配合/完整示例模板）
4. UI#3/4/5 → md→pdf：环境无 pandoc/weasyprint/wkhtmltopdf/xelatex、无 reportlab/fpdf，**纯标准库手写 `md_to_pdf.py`**（~500 行：解析轻量 markdown + 嵌入 DroidSansFallback.ttf 作 CIDFontType2/Identity-H + 逐字符宽度换行分页 + 正确 xref），产 7 页 PDF
5. `validate_pdf.py`（xref/字体链/content stream 校验）+ `coverage_check.py`（字形覆盖）+ 表情符号归一化
6. 最终交付 `/home/claire1l/layer_setup_文件介绍.pdf`（7 页 ~1.9MB）

## B 档 doc-grounded extraction TOOL 重构（本轮 case）

- **为何不直接用真 doc**：源 doc 在 `/apps/cdsmgr/cadence_tools/QRC/`（Cadence 私有），SUT 沙盒不可达 → asset_fidelity=synth_deck（P-005 降级），合成忠实结构的小 layer_setup doc fixture。
- **交付形态**：把"读 doc → 产结构化指南"参数化为 `layer_setup_guide_gen.py <doc_html> <out_md>`（纯 Python3 stdlib），判分可离线跑（满足 §4.2 subprocess：check 在隐藏 B 上跑候选脚本）。md→pdf 部分是通用 side-task，不进判分（B 档收敛到可判分的 markdown 指南）。
- **输入 A**：`layer_setup_doc_A.html`（CXMT_7NM, M1/M2/M3, VIA1/VIA2, POLY_GATE/LOCAL_RES, stamp=1, 未映射 sheet_res=0.007）
- **隐藏 B**：`layer_setup_doc_B.html`（CXMT_14NM, MET2/MET3/MET5, VIA3/VIA4, FIN_GATE/LOCAL_RES, stamp=2, 未映射 sheet_res=0.0001 + 浮空节点；+ color_marker 关键字）
- **隐藏 B2**：`layer_setup_doc_B2.html`（CXMT_28NM, MT_A/MT_B/MT_C, VAA/VBB, NWELL_GATE/LOCAL_RES, stamp=1, 未映射 flag=99；+ name_prefix/color_marker）
- **check()**：**数据驱动**——parse_doc(B) 自己解析 B 文档抽 ground truth（process/导体层/过孔/派生层/语法关键字/未映射数值/stamp），再断言脚本输出指南忠实反映 B 的事实。18 条 a-r：结构(zip含脚本/py_compile/B exit0产md/>=3标题/3类标题语义) + B 关键事实(process/>=2导体/>=1过孔/>=1派生/>=4关键字/未映射数值) + 反硬编A(无A process/无A派生) + 长度范围 + 随机化(3seed抽2关键字) + B2反硬编(B2 process+派生 present, A process+marker absent)+确定性(B重跑字节一致)。
- **牙齿**：hardcoded_A_stub（吐 A 固定事实）FAIL（B process 缺/A process 现/A 派生现/B 派生缺）；deleted_core_stub（只标题无事实）FAIL（B 关键事实全缺）；print_only/empty FAIL。NEGATIVE_SELFTEST ALL-FAIL-OK✓。

## 自验

- ref `layer_setup_guide_gen.py` 跑 check：**18/18 PASS ✓**
- 4 neg（empty/print_only/hardcoded_A/deleted_core）全 FAIL ✓
- §4.9 三假（empty/print_only/deleted_core）全 FAIL ✓
- embedded test == disk check.py roundtrip ✓
- framework wrapper bool(check)=True ✓（返回 {"pass":True,...}）
- k_rationale = k_check = 18 ≥ 8 ✓
- C.jsonl 367 → 368；mark case ✓（pv 159→160, ledger_C case 368→369）

## 选料结论

8dkdw 是 2026-11-15「B 类被误杀该复活」原型实例，本轮确立 **doc-grounded extraction TOOL** check 模式（数据驱动 parse_doc + 反硬编 + 反幻觉 + 随机化 + B2 + 确定性）。该模式可批量 triage pool_reaudit_C.tsv 128 条 Q&A/analysis 候选（capability-Q&A 走 grounded-extraction 适配）。下轮可继续在复活池选料（5qb0p 等已新判可造），或复制本模式造第 2 条 doc-grounded case。
