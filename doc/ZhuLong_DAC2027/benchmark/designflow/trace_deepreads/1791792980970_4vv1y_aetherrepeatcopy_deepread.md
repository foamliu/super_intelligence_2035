# Deepread — 1791792980970_4vv1y (lizwen) — Aether 连续 Copy howto-Q&A

**Session**: `1791792980970_4vv1y` · **User**: lizwen · **Host**: 10.129.2.11 (hfeg0pkn002) · **mc**: 138 (layout_aether)
**Source**: `scp 10.129.2.11:/home/lizwen/.cline/data/sessions/1791792980970_4vv1y/1791792980970_4vv1y.messages.json` (541 KB / 94 msgs)
**Round**: r741 · **Case**: EDA-Eval-DesignFlow-AetherRepeatCopyHowto-001 · **Shard**: C (layout_aether) · **Reclaim**: 旧 parked 2026-11-08「Q&A how-to 连续copy aether skill, 纯文档推荐无交付物」pre-11-15 误判 → 11-15 §二 revival (analysis-Q&A 复活)

---

## ① 用户真实意图（U#0 逐字）

> 调用aether的skill，怎么连续copy

单一明确 howto-Q&A 意图：用户问 Aether 工具中如何实现「连续 copy / Repeat Copy」操作，期望得到 bindkey / 菜单 / Tcl 命令等可操作答案。属于 analysis-Q&A / explain-howto 类（用户未要求修改文件、跑测试、生成脚本，符合 A 档选轮规则——只取 U#0，分离后续可能的中途追加任务）。

## ② Assistant 行为（94 msgs 概览）

- RAG 检索 Aether 参考手册 → 命中 Ch53.3 (Copy) / Ch53.4 (Repeat Copy) / Ch120.22 (dbCopyFig Tcl command)
- 读 bindkey cheatsheet → 命中 `win+c` (repeat copy row) + 手册键 `H`
- 综合产出 how-to answer，含：
  - **bindkey**: `H` (manual) + `win+c` (cheatsheet)
  - **menu**: Edit → Repeat Copy
  - **chapter**: Copy 53.3 / Repeat Copy 53.4 / Tcl cmd 120.22
  - **Tcl cmd**: `dbCopyFig -fig <figId> [-dst <cellview>] [-orient <orient>] -offsetPoint <point> [-mag <mag>]`
  - **required params**: `-fig`, `-offsetPoint`；**optional**: `-dst`, `-orient`, `-mag`
  - **orient values**: R0 / R90 / R180 / R270 / MY / MYR90 / MX / MXR90
  - **snap modes**: Orthogonal / Diagonal / AnyAngle / XOnly / YOnly
  - **Repeat Copy form options**: Release Direction / Keep Selected / To Layer / Resize / Delta X / Delta Y / Rotate / Snap Mode / Synchronize Group / Chain Mode

## ③ reframe = mock-behavioral `aether-repeat-copy-howto-Q&A`

- **reframe class**: ③evidence-only (P-006 r618 (C)-(A) 分流，同 r736/r740)
- 真实 Aether 工具 path-dependent（需 Aether 安装 + license + GUI）→ mock-stdlib：SUT 仅读固定 Aether 参考手册片段 + bindkey cheatsheet（.txt），抽取「连续 copy / Repeat Copy」相关事实到结构化 JSON 报告，每条事实附 evidence（来源文档名 + 文档中确切源行）。
- distinct vs r736 LayoutElementAttribution（枚举+归属 layout 域）/ r737 ScriptReconAnalysis（AST 静态分析脚本域）/ r740 TestSuiteStatusAnalysis（test-suite 状态枚举测试域）= 本例 **ref-manual + cheatsheet 文档抽取 howto-Q&A（layout_aether 域，C 域首例 aether-howto doc-extraction 子型）**

## ④ 三 fixture 设计（反硬编码 / 反背题）

| 维度 | A (sample_input) | B (hidden) | B2 (hidden) |
|---|---|---|---|
| bindkey manual | H | K | Q |
| bindkey cheatsheet | win+c | Ctrl+Shift+C | Alt+R |
| menu | Edit → Repeat Copy | Layout → Repeat Copy | Draw → Repeat Copy |
| chapter Copy | 53.3 | 61.7 | 77.2 |
| chapter Repeat Copy | 53.4 | 61.8 | 77.3 |
| chapter Tcl cmd | 120.22 | 148.14 | 205.3 |
| Tcl cmd name | dbCopyFig | dbCloneFig | dbDuplicateFig |
| Tcl required params | -fig, -offsetPoint | -src, -translate | -obj, -move |
| Tcl optional params | -dst, -orient, -mag | -target, -rotation, -scale | -into, -facing, -zoom |
| orient values | R0/R90/R180/R270/MY/MYR90/MX/MXR90 | N/E/S/W/FlipH/FlipV/FlipH90/FlipV90 | U/D/L/R/MirrorH/MirrorV/MirrorH90/MirrorV90 |
| snap modes | Orthogonal/Diagonal/AnyAngle/XOnly/YOnly | Ortho/Diag/Free/X-Only/Y-Only | Right/Cross/Free/Horizontal/Vertical |
| Repeat Copy form options | Release Direction/Keep Selected/To Layer/Resize/Delta X/Delta Y/Rotate/Snap Mode/Synchronize Group/Chain Mode | Lock Direction/Retain Selection/Layer Swap/Scale/Pitch X/Pitch Y/Angle/Snap Mode/Sync Group/Chain Select | Hold Direction/Keep Picked/Alt Layer/Grow/Step X/Step Y/Turn/Snap Mode/Pair Group/Chain Pick |

A/B/B2 在 bindkey / menu / chapter / Tcl cmd / params / orient / snap / form-options 八个维度全不同 → 任何硬编 A 的 print-gold stub 在 B 上 d-l 八条断言全 FAIL。

## ⑤ check.py 16 断言 a-p（k_rationale == k_check = 16 ≥ 8 GATE PASS）

| letter | 断言 | 反硬编码点 |
|---|---|---|
| a | submit.zip 合法且顶层含 solve.py | 结构 |
| b | solve.py 在隐藏 B 上 exit 0 且产非空 b_report.json（真跑候选 §4.2） | anti-stub |
| c | B report 含全部 14 必需顶层键 | 结构 |
| d | B bindkey_manual == 'K' | 反 A 的 'H' |
| e | B bindkey_cheatsheet == 'Ctrl+Shift+C' | 反 A 的 'win+c' |
| f | B menu == 'Layout → Repeat Copy' | 反 A 的 'Edit → Repeat Copy' |
| g | B tcl_cmd_name == 'dbCloneFig' | 反 A 的 'dbCopyFig' |
| h | B tcl_required_params == ['-src','-translate'] | 反 A 的 ['-fig','-offsetPoint'] |
| i | B orient_values 集合 == {N,E,S,W,FlipH,FlipV,FlipH90,FlipV90} | 反 A 的 R0.. |
| j | B snap_modes 集合 == {Ortho,Diag,Free,X-Only,Y-Only} | 反 A 的 Orthogonal.. |
| k | B chapter_repeat_copy == '61.8' | 反 A 的 '53.4' |
| l | B repeat_copy_form_options 集合 == B 真值 10 项 | 反 A 的 Release Direction.. |
| m | B evidence 可溯源性：每条 evidence 须 cite 真实文档 + 文档中确切源行 | 防 print-gold stub 伪造 evidence |
| n | B2 跨输入 guard：bindkey=Q / cheatsheet=Alt+R / cmd=dbDuplicateFig / ch=77.3 / orient={U,D,L,R,Mirror*} | 跨 A/B/B2 三向防背题 |
| o | B2 evidence 亦须真实可溯源 | 跨输入 evidence 完整性 |
| p | 空目录防崩（all-None report + evidence={}）+ 确定性（B 3 跑 md5 字节一致） | anti-stub + determinism |

## ⑥ 自验结果

- **reference solve.py PASS 16/16** ✓（B/B2 全部内容 + evidence + 空目录 + 确定性）
- **3 negatives 全 FAIL distinct**：
  - `solve_empty.py` → 15 assertions FAIL（a 通过，b-p 全 block）
  - `solve_print_gold.py`（硬编 A gold）→ 13 assertions FAIL（d-l 内容全错 + m/o evidence 伪造 + n B2 错 + p 确定性虽过但内容全错）
  - `solve_no_evidence.py`（抽事实但无 evidence）→ 10 assertions FAIL（m/o evidence 缺失）
- §4.9 退化提交（空壳/print-gold/无 evidence）全 FAIL ✓
- k_rationale = k_check = 16 ≥ 8 GATE PASS ✓
- test 字段 = on-disk check.py（byte-iden，jsonl round-trip 验证）

## ⑦ 落库

- `cases/C/EDA-Eval-DesignFlow-AetherRepeatCopyHowto-001.json` (source of truth, test 字段含完整 check.py 15805B)
- `build_jsonl.py --shard C` 重建 `EDA-Eval-DesignFlow_C.jsonl` (462 → 463)
- `assets/EDA-Eval-DesignFlow-AetherRepeatCopyHowto-001/`：sample_input/docs/(3 .txt) + prompt.txt + task_brief.md + hidden/{b,b2}/docs/(各 3 .txt) + hidden_manifest.json + reference/(solve.py + check.py) + negative/(3 stubs + negative_selftest.py)
- `trace_ledger_C.tsv` mark 4vv1y → status=case --force（reclaim，旧 parked 行保留作历史；D shard 也有 parked 行，本次 reclaim 仅在 C ledger）
- 本 deepread

## ⑧ 纪律

- SUT 沙箱只含 `sample_input/docs/` + `prompt.txt` + `task_brief.md`；`hidden/` + `reference/` + `negative/` 不进 SUT ✓
- 不脱敏（user=lizwen / host=10.129.2.11 / session_file=1791792980970_4vv1y 真值）✓
- 只动 C shard 文件 ✓
- check.py 隐藏路径解析走 `workdir/hidden/{b,b2}/docs`（同 r740 pattern，NOT `__file__` dir）✓
