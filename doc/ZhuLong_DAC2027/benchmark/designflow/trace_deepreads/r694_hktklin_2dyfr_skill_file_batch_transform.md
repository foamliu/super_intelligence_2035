# Deepread: 1794450183857_2dyfr — SkillFileBatchTransform-001 (r694)

**Trace**: `/home/hktklin/.cline/data/sessions/1794450183857_2dyfr/1794450183857_2dyfr.messages.json`
- host: 10.129.8.138 (hfeg0plg87), user: hktklin, mc=50
- size: 87 KB, 39 msgs, 3 user turns, 17 tool_use
- keywords: virtuoso:46;ddgetobj:35;cellview:35;dbcreaterect:12;dbcreatepath:5;transistor:3;cmos:3;pyaether:2
- **ledger history**: parked r628 (2026-11-16, "trivial text-sub tap_p->lacaa_common + _SKILL delete, known-reject text-sub pattern"); r694 re-eval per 11-15 standard → marked case

## 用户真实意图（verbatim U#0）

> "如下路径/proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/CUT/文件中内容为tap_p替换为lacaa_common，将内容_SKILL 删除，生成新文件并替换到这个目录下"

用户在 Virtuoso SKILL PCell 开发中，要把目录下 3 个 `*_SKILL.il` 文件做批量文本变换：
1. 内容中 `tap_p` → `lacaa_common`（PCell 库名替换）
2. 内容中 `_SKILL` 删除（去除标记后缀）
3. 文件名中 `_SKILL` 删除
4. 生成新文件替换原目录

U#2 重复同一请求（验证上次已完成）。

## r628 park → r694 re-eval 理由

r628 以 "trivial text-sub, known-reject pattern" park。但 **11-15 任务初衷**明确：「没有任何预设的题型清单、难度配比或层级配额可以否决一个真实用户意图」。用户真实做了批量文本变换 + 文件重命名，这是真实 produce-task。判分有牙（16 条件验内容替换正确性 + 文件名 + 确定性 + B/B2 边界），符合 §4.3 ≥8 独立条件。**re-eval → keep → build**。

## 助手工作流（trace 实证）

1. U#0 → list_allowed_files 列 CUT 目录 → 3 个 `*_SKILL.il`
2. read_files 读 3 文件 → 识别 `ddGetObj("tap_p")` + `_SKILL` 在文件名/内容
3. 写 transform_cut_skill_v2.py: `content.replace("tap_p","lacaa_common").replace("_SKILL","")` + `fname.replace("_SKILL","")` → 写新文件
4. run_approved_command 执行 → 3 新文件生成 (6296/2547/1974 bytes)
5. cleanup_old_skill.sh: `rm *_SKILL.il` → 旧文件删除
6. read_files 验证新文件第1行 `ddGetObj("lacaa_common")` + 无 `_SKILL` ✓
7. cleanup_tmp.sh: 清理临时脚本

## Reframe（r694 build）

**case_id**: EDA-Eval-DesignFlow-SkillFileBatchTransform-001 (layout_virtuoso, L1)
**子型**: `skill-pcell-batch-transform`（mock-behavioral reframe 家族; **batch file transformation** read→transform→write+rename; distinct vs r692 manual-retrieval+diagnose / r690 report-diagnose / r688 SVRF-translate / r687 spec-generate / r685 validate-TCL / r682 deck-classify — 本例 = 批量文件内容替换+重命名，新子型）

**asset A** (visible): templates_A/ (3 SKILL .il: CM1CM2CM3_CUT_SKILL / M0C_CUT_SKILL / MGC_CUT_SKILL，含 tap_p + _SKILL) + prompt.md + task_brief.md
**hidden B** (反硬编全异文件名/内容): templates_B/ (VIA1ENC_CUT_SKILL / VIA2_CUT_SKILL / DRC_FILL_SKILL，含 tap_p + _SKILL，与 A 集不相交)
**hidden B2** (退化已变换): templates_B2/ (VIA1ENC_CUT / VIA2_CUT / DRC_FILL，无 _SKILL 无 tap_p 有 lacaa_common)

**candidate**: skill_file_transformer.py (纯 stdlib)
- `--input-dir <dir> --output-dir <dir>`
- 对每个 `*_SKILL.il`: read → replace tap_p→lacaa_common + remove _SKILL → write to new_name (去 _SKILL)
- 输出 transform_report.json (summary + transformed[] with old_name/new_name/content_changed, sorted by new_name)

**check() 16 条件 a-p**: 见 check.py CONDITIONS。negatives first-fail: empty_shell→d / only_print_A→g / no_core_logic→h / always_pass_stub→j (4 distinct)。

**自验**: gold 16/16 PASS ✓ (A/B/B2); negative_selftest ALL_NEG_FAIL + GOLD_PASS + 4 distinct ✓; §4.9 三假(空壳/只print A/删核心)全 FAIL ✓; 确定性 3x md5 一致 ✓; k_rationale=k_check=16≥8 GATE PASS ✓。
