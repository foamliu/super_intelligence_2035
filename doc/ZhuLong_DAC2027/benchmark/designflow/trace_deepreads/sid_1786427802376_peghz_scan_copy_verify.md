# 深读笔记：1786427802376_peghz — Scan+Copy+Verify AutoVia/PowerFill cells

- **user**: e0014566 · **host**: hfeg0pkn001 · **mc**: 151 · **domain**: layout_virtuoso
- **session**: 107 msgs · status=completed · model=deepseek-v4-flash · cwd=/home/e0014566/test_layout
- **session_file**: 1786427802376_peghz (在 .75:/home/e0014566/.cline/data/sessions/ 本轮确认可经 pyAether 读，无需 bashpool)

## 用户轮（4 个 user_input）
- **UI[0]** "read the prompt.md and do the job in it." — 引用 prompt.md（前序任务，非本案 seed）
- **UI[33]** 逐字「你能不能帮我看下 drjqa_top 下面所有的cell, 哪些包含 autovia powerfill 这些工具产出的instance」= **纯需求委托，A-档 faithful seed**
- **UI[47]** 逐字「把包含autovia 或者 powerfill 这些工具产出的 cell 都原封不动复制一份到library auto_austin_case1 中。要注意原封不动复制。复制以后比较一下，是不是完全一致。」= 需求延续（copy + verify）
- **UI[93]**「再简单比较下大小吧，看看是否一致。」= 细化

## assistant 工具链（SKILL on Virtuoso，SandBox_MCP_Server__run_code lang=skill 24 次 + editor 4 报告文件 + run_commands 14）
1. **[22-26]** 探查 DDR5TOP/layout 结构：dbOpenCellViewByType → instances/mosaics/vias/shapes/figGroups/markers/nets/terms 计数；下钻 subcells（Array16G_T/Channel/...）匹配 `_VIA`(AutoVia) / `_pgfill`(PowerFill)
2. **[37-42]** dbGetAllCells/drjqa_top → ddGetObj~>cells → **逐 cell 扫**：dbOpenCellViewByType(lib,cell,"layout","","r") → instances → master key lib/cell → rexMatchp("_VIA"/"_pgfill") → 报告 cell / AutoVia / PowerFill 计数
3. **[53-60]** 探库创建：dbCreateLib("auto_austin_case1", path) + techBindTechFile + dbCopyView/dbCopyCellView 单 cell 试复制
4. **[64-70]** **批量复制** 7 cell（Array16G_B/T、Channel、BCenterCA/DQ/L/R）：dbCopyCellView(srcCv, dstLib, cell, view, t) + file-cp fallback（mkdir -p + cp -rf + rm cdslck）
5. **[72-78]** **清单比对**：ddGetObj(src/dst cell)~>views → srcNames vs dstNames sorted → missing/extra → INVENTORY ALL OK
6. **[80-88]** **cmpLayout 深比**：bBox equal + 12 类计数(inst/mos/via/shape/fg/mrk/row/net/term/pin/bnd/blk) + instance 签名(lib|cell|orient|origin sorted) + via/shape/fg/net/term 签名 → ALL OK
7. **[88]** 确认 copy 中 AutoVia/PowerFill master 仍在
8. **editor 4 文件**：drjqa_top_autovia_powerfill_scan.txt / DDR5TOP_analysis_report.txt / size_compare_report.txt / copy_verify_report.txt

## gold 合成（B-档 synthesized：trace 原为 SKILL/Virtuoso，翻译为 pyAether Python 以便 L1-boundary 沙盒判分）
`scan_copy_verify.py`：
- `scan_library(lib, av_pat, pf_pat)`：ddGetObj→cells→dbOpenCellViewByType layout→instances→master key→匹配 `_VIA`/`_pgfill`→返回 (cell, inst_count, av_keys, pf_keys)
- `copy_cells(src, cells, dst)`：dbOpenCellViewByType src→dbCopyCellView(srcCv, dst, cell, "layout")
- `verify_copy(src, dst, cells)`：逐 cell 开 src/dst layout→比 bBox + 6 类计数(inst/via/shape/fg/net/term) + instance 签名(lib/cell/orient/origin sorted)→(cell, ok, mism)
- `main()`：argparse --src --dst --autovia --powerfill → SCAN/COPY/VERIFY 三段报告 + sys.exit(1) if mismatch

## hidden B（判分器内嵌 fake pyAether，确定性）
- libB_scan 5 cell：top_av(1 AutoVia M1_VIA +1 plain BUFx1)、top_pf(1 PowerFill M2_pgfill +1 plain INVx1)、top_both(1 AutoVia V1_VIA +1 PowerFill V2_pgfill +1 plain NAND2x1)、top_clean(2 plain 须不被报告)、top_nolay(无 layout)
- libB_dst 由 dbCopyCellView 填充；verify 深比 bBox/计数/instSig
- cross-input guard (n)：A 专属 token drjqa_top/auto_austin_case1/Array16G_T/BCenterR 等不出现在 B 输出

## check.py 16 条独立断言（k=16=k_check≥8 GATE PASS ✓）
a zip 存在 · b 含 .py · c ≥800B 无 NUL · d import pyAether · e scan/copy/verify 三函数 · f _VIA/_pgfill 模式 · g 四 API · h CLI --src/--dst · i B 上 exit0 · j 报告 3 命中 cell · k top_clean 不误报 · l 计数正确(av=1/pf=0, pf=1, both=1/1) · m copy ≥3 OK · n verify ALL OK 无 MISMATCH · o A token 不泄漏 · p 二次 run 确定性

## 自验
- ref check.py self-test → **CHECK PASS** ✓
- 4 negative 全 FAIL：empty_shell→c、print_only→c、naive_hardcode_A→d、core_deleted→e · NEG_RC=4/4 ALL-FAIL ✓
- §4.9 (a)空壳 (b)只print (c)删核心 全 FAIL ✓

## 与既有区别
ListInstCV-001(单 cellview 扁平枚举 instance)/PortPropagate-001(port 沿层次传播)/AutoViaGen-001(生成 autovia) → 本案**跨 cell 扫库+模式筛选+复制+结构深比**，主题独立，非 near-duplicate。layout_virtuoso 域 9→10。
