# r597 deepread — xinqiaoz / 1790073354031_syox0 — LDR F-type 0 占位 bug 存档

## trace meta
- session: `1790073354031_syox0.messages.json` (xinqiaoz @ hfeg0pkn002, 10.129.2.11)
- mc=77, keywords: drc:630;pdk:330;calibre:152;cmos:16
- 40 msgs, 2 user_input, 147KB
- domain: physical_verify (DRC LDR value check)

## user 真实意图（trace-faithful）
UI#1 = pdkQaSystem Issue Handler skill 指令（auto-injected workflow），agent 执行步骤 1 构建 base/ 环境（prepare_base.py，copied:9 / INCLUDE 展开 1 / collision:1，oldDrc 同名冲突手动 cp -L 固化）。
UI#2 = **核心 produce-task**（逐字原文）："现在我大概说一下这个问题，这个问题你无需按照流程解决，你就写一个 README 做一个存档记录就好了。" + 完整 bug 分析（背景：BORD_F_001_00 旧版报 drc with unmatched value 新版不报；根因：F 类型 forbidden/pattern check 的 0 是占位符，compareLdrValueWithDrc0() 把 0 当普通数值去 DRC 里找，找不到误报；结论：新版 LDR value 0→Check 绕开误报分支）。

## agent 实际交付
1. grep base/ LDR 两版验证事实：
   - 旧版 LDR 第 1740 行：`BORD,LDR_CMOS,F,BORD_F_001_00, ,0, ,0,Check,Check,Chip Boundary definition = BORD (301;0)` → value=0 占位
   - 新版 LDR 第 1092 行：`BORD,LDR_CMOS,F,BORD_F_001_00,Check,Check,Check,Check,Check,Check,Chip Boundary definition = BORD (301;0)` → value=Check
2. grep 代码定位：`DRC/text/DrcValueCheck.py:468` def compareLdrValueWithDrc0()，`:418` 调用点
3. 写 85 行结构化 README.md：标题 + 问题总览表 + base/构建记录 + 问题分析记录（现象→数据核对表→根因分析→后续建议）+ 结论

## B档 reframe（C 线 mock-behavioral 模式，承 r588/r594）
真实意图 = "写 README 存档 F 类型 0 占位 bug"。B档 reframe = 写参数化 Python 脚本 `ldr_value_bug_archive.py`，读 LDR old/new CSV + 代码文件，自动识别 F 类型 0→具体值 改动的 rule，定位 compareLdrValueWithDrc* 函数，产结构化 markdown README。意图核心（文档化 F 类型 0 占位 bug）保留，形态从手动 doc-writing 转 scripted doc-generation（利离线 check + hidden B 反硬编）。

## case 设计
- **case_id**: EDA-Eval-DesignFlow-LdrFtypeZeroArchive-001
- **接口**: `python3 ldr_value_bug_archive.py <ldr_old.csv> <ldr_new.csv> <drc_value_check.py> <out_readme.md>`
- **输入A**: ldr_old_A.csv (BORD_F_001_00 val=0 + 4 干扰 rule) / ldr_new_A.csv (BORD_F_001_00 val=Check) / drc_value_check_A.py (compareLdrValueWithDrc0 faithful fixture)
- **隐藏B**: ANGL_F_003_01 (val 0→Check) + drc_value_check_B.py (compareLdrValueWithDrcCheck)
- **隐藏B2**: MERG_F_007_04 (val 0→Skip) + drc_value_check_B2.py (compareLdrValueWithDrcZero) — 反硬编
- **14 条 a-n**: zip含脚本/py_compile/B exit0产md/md有#标题/B rule_id(ANGL_F_003_01)非A(BORD_F_001_00)/旧版val=0/新版val(Check)/B函数名(compareLdrValueWithDrcCheck)非A(compareLdrValueWithDrc0)/F类型forbidden/0占位符placeholder/unmatched value/结构化章节≥2/B2反硬编(B2 rule+func 非B)/确定性两跑字节一致
- **自验**: ref 14/14 PASS / 3 neg(empty/print_only/deleted_core) 全 FAIL / NEGATIVE_SELFTEST ALL-FAIL-OK / embedded test==disk roundtrip OK / k=14≥8

## 谱系
produce-task 第 N 子型：ldr-bug-archive-doc-gen（physical_verify DRC LDR value check 域，doc-synthesis→scripted-doc-gen reframe）。anti-hardcode dual-hidden-fixture（B ANGL_F_003_01+compareLdrValueWithDrcCheck / B2 MERG_F_007_04+compareLdrValueWithDrcZero）。承 r588 DrcLog4ModTruncOpt / r594 DeckRuleParseExtract 的 "write Python script that parses EDA artifact + produces structured output" 模式。
