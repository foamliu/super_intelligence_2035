# Deepread: 1794466237270_iyyzq (2026-11-20 shard A, r846)

## 结论
**可造 → 已造 EDA-Eval-DesignFlow-CornerNameConvertProduce-001** (B档 synthesized
L1 produce-task, eda_other, k=15/15)。这是 2026-11-15 候选池重审「24 待深读」第 3 条
落地（r844 jeij7 / r845 l4tre / r846 iyyzq 三连）。

旧判（2026-11-14 r? note）parked 为「Linux/sed 文本处理，非 design_flow」——按 2026-11-15
任务初衷重审，**文本/脚本编辑是合法 L1 produce-task 用户意图**（与 l4tre→ReleaseNoteEmptyFix-001
同构），旧判作废，复活造题。

## trace 元数据
- session: 1794466237270_iyyzq, user jerrychu, host hfeg0pkn003 (10.129.2.12)
- mc15, agent=lead, 49 msgs, 162953 bytes (subdir-path ALIVE: sessions/<sid>/<sid>.messages.json)
- domain: eda_other（PDK corner 名文本处理；scan 的 innovus/lvs/calibre/pyaether 关键词
  均为 list_allowed_files 目录名假命中，非真实 EDA 工具执行——但 11-15 后「无真实工具执行」
  不再否决 L1 produce-task）

## 真实用户意图（3 次递进，原话）
- U#22（重复 5 次）：「Need a linux command to convert from ssgnp_0p675v_0c to ssgnp/TYPICAL/0.675/0」
- U#37：「...to ssgnp_mos_varactor_dbc/TYPICAL/0.675/0」（追加 _mos_varactor_dbc）
- U#43（最终）：「...to ssgnp_0p675v_0c=ssgnp_mos_varactor_dbc/TYPICAL/0.675/0」（保留原始=转换后）

最终形态为 `原始=转换后` 映射，自然涵盖前两步。

## 真实转换规则（assistant 在 trace 中验证过的 sed + python）
corner 格式 `<prefix>_<volt>v_<temp>c`：
- 电压 `0p675v` → `0.675`（p→`.`，去末尾 `v`）
- 温度 `0c`→`0`、`125c`→`125`、`m40c`→`-40`（去末尾 `c`；前导 `m`→`-`）
- 前缀保留；插入字面量 `_mos_varactor_dbc/TYPICAL/`
- 最终行 `原始=转换后`

**真实 ordering bug**（assistant 第一版踩到）：voltage 规则用 `$`-anchor，temp 替换后行尾
已变成 `/NN`，`v` 不再在行尾 → voltage 规则失效。修复=去掉 voltage 规则的 `$` anchor。
此 bug 被编码为 neg_core_del（去掉 voltage p→. 转换 → FAIL）。

## 16 真实 corner（A fixture，trace U#18 原文）
ssgnp_0p675v_0c / ffgnp_0p825v_125c / tt_0p75v_85c / ssgnp_0p675v_125c / ffgnp_0p825v_0c /
tt_0p85v_85c / ssgnp_0p765v_0c / ssgnp_0p765v_125c / ffgnp_0p935v_0c / ffgnp_0p935v_125c /
tt_0p75v_25c / tt_0p85v_25c / ssgnp_0p675v_m40c / ffgnp_0p825v_m40c / ssgnp_0p765v_m40c /
ffgnp_0p935v_m40c

## 合成（B档）
- A档不可行核验：真实交付是 sed one-liner（shell 命令），headless 自包含 check 用 Python
  脚本形态更稳；但转换规则、corner 名、ordering bug 全部从 trace 原文（assistant text +
  editor tool_use，**未被 sandbox 剥离**，与 l4tre/jeij7 read_files 被剥不同）忠实提炼。
  → B档 synthesized，deliverable = convert_corners.py（trace 中 assistant 的真实产物名）。
- hidden-B：12 corner，与 A 大多不同（新前缀 sslp、多位电压 1p05/1p1/1p0/0p55、新温度
  150c/m55c、2 条与 A 重叠测一致性），judge-only 不进 SUT 沙箱。
- check 15 条独立断言：zip/py_compile/exit/行数/`=`分隔/原始保留/结构标记/多位电压/正温度/
  负温度/零温度/全B逐行精确匹配oracle/反硬编新前缀/3seed随机子集/合成泛化。
- 自验：ref PASS 15/15 + 3 neg(empty/print_only/core_del)全FAIL + §4.9(a)(b)(c)全FAIL
  + jsonl test sha == disk check.py sha byte-identical + k_check==k_rationale==15≥8。
- ref 在 A fixture 上输出与 trace verified output 逐字一致。

## 台账动作
- ledger: iyyzq parked → case (EDA-Eval-DesignFlow-CornerNameConvertProduce-001, --force override 旧 parked)
- pool_reaudit_A.tsv: iyyzq 行 新判定「不可造(待深读)」→「可造(已造r846)」
- A.jsonl 417→418, cases/A +1
