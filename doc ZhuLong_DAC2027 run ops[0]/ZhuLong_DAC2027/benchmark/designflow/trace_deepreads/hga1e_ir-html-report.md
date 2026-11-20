# Deepread: 1789717466435_hga1e — IR-drop HTML report (U#179)

**Session**: 1789717466435_hga1e · **User**: thomasz @ hfeg0pfn060 (10.129.32.75) · **mc**: 243
**Domain**: pg_layout (Totem IR-drop analysis) · **Size**: 189 msgs / 833KB
**Selected user intent (A 档)**: U#179 — "回到/home/thomasz/zl_test/DRCOA_V0907_IDD5B_vpcsg_rerun/路径下。我在想自动生成的报告除了pdf格式，生成html是不是也可以？毕竟我最核心的需求还是说图能清晰的放进报告里去，或者有其他格式的报告也行啊"

## Trace flow (relevant turns)
- U#9: 读取 /home/thomasz/zl_test/DRCOA_V0907_IDD5B/ (dir with report/worst_ir_summary.dr + picture/node_ir_*.png)
- U#13: 生成 PDF 报告 (Part 1 = worst_ir_summary.dr 内容, Part 2 = 各电源网络 IR-drop 图) → 已入库 IRReportPdf-001
- A#13-50: assistant 写 gen_ir_pdf.py (纯 stdlib PDF 生成器: zlib/struct 解 PNG + 手写 PDF 对象)
- U#170: debug 性能 (图片变大后处理慢) → 优化 load_png 快速路径 + zlib level 6
- **U#179: 想 HTML 替代 PDF (核心需求: 图清晰放进报告)** ← 本 case 取此轮
- A#179-188: assistant 写 gen_ir_html.py (base64 内嵌 PNG, 自包含单文件 HTML, Part 1 表格 + Part 2 各网 <img>)

## Data files (real, from /home/thomasz/zl_test/DRCOA_V0907_IDD5B/)
- report/worst_ir_summary.dr: 14 power nets (vad2e!/vad2o!/vap2!/vblh!/vcc!/vdleq!/vintlp!/viso!/vkb!/vncsgn!/vpcsg!/vss!/vwln!/vwlp!) with Peak/Avg IR (mV). 原始值: vss!=367.13/275.88 (最高), vap2!=0.00/0.00 (最低)
- picture/node_ir_<net>.png: 14 IR-drop heatmap PNGs (vad2e 70KB ... vss 165KB)

## Case design (A 档 trace-faithful)
- case_id: EDA-Eval-DesignFlow-IrDropHtmlReport-001
- domain: pg_layout (least-covered C-domain, 48→49 cases)
- track: A-trace-faithful (user verbatim U#179 as prompt)
- level: L1 (offline Python, stdlib HTML generation)
- prompt: U#179 verbatim + 交付接口 task_brief
- A assets: original worst_ir_summary.dr (with `!` suffixes + original values) + 14 real PNGs
- hidden B: 10 different nets (vdd1/vdd2/vddio/vcore/vpll/vref/vbias/vana/vterm/vclamp), different values, synthetic PNGs
- check.py: 13 conditions (a-m), subprocess re-run on B, base64 image verification, no-hardcode check
- negatives: 3 (empty stub, hardcoded-A, print-only) — all FAIL
- self-verify: reference PASSES, 3 negatives FAIL ✓

## Distinct from IRReportPdf-001
- IRReportPdf-001: U#13 intent (PDF report), B-synthesized track, normalized data (no `!`, different values)
- IrDropHtmlReport-001: U#179 intent (HTML report), A-trace-faithful track, original trace data (with `!`, original values)
- Different deliverable (HTML vs PDF), different user intent, different track
