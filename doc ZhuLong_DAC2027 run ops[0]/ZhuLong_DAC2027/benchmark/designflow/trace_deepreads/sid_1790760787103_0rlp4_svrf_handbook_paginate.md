# 深读笔记 — sid 1790760787103_0rlp4 (e0014566 @ hfeg0pkn001 / 10.129.2.10)

- **trace**: `/home/e0014566/.cline/data/sessions/1790760787103_0rlp4/1790760787103_0rlp4.messages.json`，43 msgs，157KB，mc=51
- **domain**: physical_verify（Calibre DRC 文档处理 / SVRF 手册构建）
- **真实工具链**: pdftotext -layout（poppler）→ awk 分页；无 Python PDF 库
- **USER#0 原话（逐字）**: 「# Calibre DRC 文档 → Skill.md 构建执行指南 … 从 Calibre User Handbook PDF 出发，逐步生成一份可准确理解 DRC 逻辑关键词的 SKILL.md，并配合 RAG 实现高精度 rule 解析 …」(多 Phase 交付：calibre_handbook.md / keyword_cards / SKILL.md / references / rag / eval≥50 / build_report)。属 B-档 合成材料（用户指南本身高度规约化，给出完整方法 → 非纯意图轮）。

## 真实产物（本 session 完成的 Phase 0）
- PDF: `/apps/mentor/MRB/calibre/2020.1_36/docs_cal_2020.1_17.9/docs/pdfdocs/svrf_ur.pdf`，3250 页，原生数字 PDF，25104925 bytes，"Standard Verification Rule Format (SVRF) Manual, Software Version 2020.1, Document Revision 9"
- 工具探测: 无 fitz/pdfplumber/pypdf/PyPDF2/pdfminer；有 pdftotext/pdfinfo/gs/pdfimages/pdftoppm
- `build_corpus.sh`: `pdftotext -layout svrf_ur.pdf svrf_corpus_raw.txt` → 6977425 bytes, 139589 lines, 3249 个 form-feed(\f)
- `paginate.sh`（awk, FS="\f", RS="\n"）→ `calibre_handbook.md`（7047869 bytes, 3250 PAGE markers）:
  - 逻辑：逐行按 \f 切分；buf 累积 $1；NF>=2 时 strip buf 尾部 `[ \t\r]`，emit `\n\n<!-- PAGE pg -->\n\n` + buf，pg++，buf=$j+"\n"；END 若 buf!="" emit 末页；末尾 emit `\n## page_count_emitted=pg\n`
  - 已知坑：trailing form-feed 产生 spurious empty page（3251 vs 3250），agent 用 diag.sh/verify.py 校验 marker↔PDF page 对齐
- `diag.sh`/`verify.py`: anchor 串映射验证（特定 PDF 页的首行串 ↔ markdown 中 `<!-- PAGE N -->` 标签）

## 本轮 case 设计（B-档 synthesized, L1-boundary, physical_verify）
**case_id**: EDA-Eval-DesignFlow-SvrfHandbookPaginate-001
**任务**: 给 SUT 一段真实 SVRF `pdftotext -layout` 原文切片（\f 分页），写单文件 `svrf_handbook_paginate.py`，按 awk 分页规范产出带 `<!-- PAGE n -->` 标签的 calibre_handbook.md + stdout 摘要；判分在隐藏 B（不同切片）上真跑。
**资产（真实切片，源自 svrf_corpus_raw.txt）**:
- A（可见）: pages 1-12（标题 + TOC），62KB，12 页 → 12 markers
- B1（隐藏）: pages 100-105（Key Concepts / Summary of Rule File Elements），14.5KB，6 页 → 6 markers
- B2（隐藏）: pages 400-405（Reference Dictionary A-F / DFM Grow / DFM Histogram / DFM Jogclean），12.4KB，6 页 → 6 markers
- A/B1/B2 内容互斥（A=标题/TOC；B1=概念/规则元素摘要；B2=参考字典/DFM），cross-input guard 用 A-专属 token（Document Revision 9 / Unpublished work / Mentor Graphics Corporation / Table of Contents / Software Version 2020.1）——已验证全部不在 B1/B2 中
**reference solver**: `svrf_handbook_paginate_ref.py`（awk 的 Python 移植）已在 .75 上验证：对 A/B1/B2 产出的 markers 数与 awk 一致（12/6/6），仅末尾多一个空行（不影响判分属性）；CLI（--help/-h/无参 exit1/空文件 exit1/缺文件 exit1）已验证；stdout `Pages=/Bytes=/FirstPageAnchor=/LastPageAnchor=/Out=`
**判分 15 条断言 (a-o)**:
- a zip+py_compile ②b CLI --help/-h/no-arg/nonexistent ③c B1 exit0+写出 handbook ④d B1 首 marker=`<!-- PAGE 1 -->` ⑤e marker 数==期望(6) + `## page_count_emitted=6` ⑥f markers 连续 1..6 ⑦g anchor 对齐(PAGE1 含 Key Concepts / PAGE3 含 Summary of Rule File Elements) ⑧h 输出无字面 \f ⑨i trailing page_count_emitted 行 ⑩j 内容保留(LOCAL(LIST1)/CMACRO/Key Concepts/Summary of Rule File Elements) ⑪k stdout Pages=6/Bytes正整数/FirstPageAnchor=Key Concepts/LastPageAnchor 非空 ⑫l 跨输入守卫 B2 报告+stdout 不含 A 专属 token ⑬m 确定性 B1 两跑 stdout(减 Out/Bytes)一致+md5 一致 ⑭n 空文件 exit1+stderr+不写输出 ⑮o 单页无 \f 文件 exit0+恰一个 PAGE 1+page_count_emitted=1
- k_rationale=k_check=15>=8 GATE 设计达标

## DEBT（本轮未交付，下一轮第一件事修完）
- **未落库**: check.py / negatives / reference_submit.zip / assets(prompt.md+task_brief.md+svrf_raw_A.txt) / EDA-Eval-DesignFlow_C.jsonl 条目均未写入 repo
- **卡点**: 通过 eda_flow MCP 把 .75 上大字符串（含 \f / \n 的 raw 切片 + 嵌 base64 的 check.py）传到本地 repo 时，JS 模板字面量对反斜杠转义导致内容腐蚀；需用 base64 通道或 write 工具(JSON 转义)落地
- **下一轮恢复步骤**（数据在远端持久，秒级重建）:
  1. eda_flow open_session → ssh 10.129.2.10 跑 slicer.py 重生 A(pages1-12)/B1(100-105)/B2(400-405)（svrf_corpus_raw.txt 仍在 /home/e0014566/calibre_skill/）
  2. 在 .75 上跑 build_case.py 生成 check.py(嵌 B1B64/B2B64)+negatives+reference_submit.zip 并自验(ref PASS 15/15 + NEG_RC=0 + 3假 FAIL)
  3. 用 base64 通道把 check.py / ref solver / A.txt / prompt / brief 拉到本地 repo（write_file content_base64 已知会腐蚀 $dA→$d\x01，改用 plain content 或 run_commands 里 base64 -d 解码）
  4. 追加 EDA-Eval-DesignFlow_C.jsonl（mode=design_flow, entry_point=outputs/submit.zip, test=check.py 源, metadata{domain:physical_verify, track:faithful-seed-B-synthesized, test_rationale:15 条断言①-⑮, trace_source}）
  5. mark ledger --session 1790760787103_0rlp4 --status case --case-id EDA-Eval-DesignFlow-SvrfHandbookPaginate-001
  6. 日报 + MEMORY_C WAITING:0 DEBT:0
- **ledger 状态**: 1790760787103_0rlp4 已 claimed（未 mark case，DEBT:1）

## 选料备忘（本轮扫描）
- shard C strong-pool 扫描（mc≥30 + layout/virtuoso/calibre/innovus 关键字，排除台账 264）：
  - layout_virtuoso 候选多为 ADE/AMS 仿真（l36g5 wei9liu / 97mj2 chentong = spectre+virtuoso，归 spice_sim）或 env-bootstrap（rc0jh e0014566 = OA_UNSUPPORTED_PLAT 修 Virtuoso，与 r141 AetherEnvBootstrap 重复）
  - pg_layout 候选稀缺：xgcnn jalenwei(21 innovus) 仅 6 msg 且被 policy engine 阻断（无可用 profile），不可用
  - physical_verify 强种子：0rlp4(e0014566,180 calibre,mc51)=本次选用；0suhi(e0046686,101 calibre,mc149)、74dww(e0047434,173 calibre)、7uwtz(e0016033,63 calibre) 备用
  - 结论：本轮 pg_layout/layout_virtuoso 非 bootstrap 强种子稀缺，选 physical_verify 强种子 0rlp4（与 DEBT「继续 pg_layout 或补 layout_virtuoso」有偏离，已在 MEMORY 说明；下轮优先补 pg_layout）
