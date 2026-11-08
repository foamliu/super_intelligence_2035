# 深读笔记 — trace 1790154228796_wp6o1（yzwang @ hfeg0pkn001 / 10.129.2.10）

- **trace**: `1790154228796_wp6o1`（mc=174，kw=`drc:1031;calibre:189;pex:62;lvs:50;transistor:12;pdk:8;.gds:7;virtuoso:4`）
- **user**: yzwang（NEW user，本 shard 首个 case；agent=lead）
- **size**: 1.55MB，62 msgs，REAL_USER=2（U#0 idx=0、U#38 idx=38，两次提出需求）
- **domain**: physical_verify（Calibre SVRF DRC 规则生成）

## 用户真实意图（逐字原文）

- **U#0**（提出需求，未给根因）：
  > LDR有一个描述，要求M1的width最小是0.159，请你写出这条rule的DRC查法。
- **U#38**（提出需求，未给根因）：
  > LDR有一个描述，要求VSH_cmp与VSH_cmp的space最小是0.028，请你写出这条rule的DRC查法。

两条都是「给出 LDR 自然语言描述（图层 + 检查类型 width/space + 阈值）→ 要 DRC 检查规则写法」。

## grounding（agent 真实工具链）

1. read_files 读 `/home/yzwang/calibreDRC.rule`（22,533 行）逐段扫（10211 行起 M1 DRC 段，10223-10232 行既有 `M1_W_001_00_c`/`_p` width 规则；14004-14050 行 PG_CMP/AT4_CMP spacing 规则；10250-10261 行 `M1_S_008_00_c` 同层间距 EXT）。
2. 提取既有 deck 的书写规范：`VARIABLE  _<rid>_ <val>` → `<rid> {` → `    @ <desc> [^_<rid>_]` → `    <OP> <LAYER> < _<rid>_ ABUT<90 SINGULAR REGION` → `}`。
3. 算子语义：width → `INT`（内部宽度）；space → `EXT`（外部间距）；修饰符固定 `ABUT<90 SINGULAR REGION`。
4. 输出：版本 A（core/peri 统一）+ 版本 B（拆分），逐块遵循既有 deck 规范。

## 为何 B 档（重定义为参数化生成器）

- 真实 deck `/home/yzwang/calibreDRC.rule` 对 e0031982 在 .75 不可访问（用户私有项目），无法取真实 22533 行 deck 作 A 输入。
- 但 trace 的 grounding 价值在「规范提取」—— agent 把既有 deck 的写法抽象成一条格式契约，可参数化生成任意 LDR→SVRF 规则块。
- 故重定义为 `ldr_to_svrf.py <ldr_rules.json>`（stdlib only）：解析 JSON 数组 `[{rule_id,layer,check,value,desc}]` → 按 `svrf_convention.md` 逐块输出 SVRF DRC 规则到 stdout。
- 规范文档 `svrf_convention.md` 直接落地 agent 提取的格式契约（VARIABLE 行双空格、@ 行 4 空格缩进、检查行 `OP LAYER < _RID_ ABUT<90 SINGULAR REGION`、值去尾零、块间空行）。

## DISTINCT from 现有 physical_verify 系

- r241 SvrfPvrsRuleTranslate-001：SVRF→PVRS **跨语言翻译**（已写好的 SVRF deck 转 PVRS），方向相反、对象是 deck 文本。
- r243 VssPunchRuleGen-001：**单一** vss via-punch 规则生成（输入 config，输出含 CONNECT/DFM SPEC FILL/STEP 的完整 via-punch SVRF 片段），结构固定。
- r245 RectAspectRuleCheck-001：检查矩形长宽比是否违规（分析既有 shape），不生成规则块。
- r239 DrcRuleTimeRank-001：按执行时间排序 DRC 规则（分析 deck），不生成规则。
- 本 case：**LDR 自然语言 → 参数化 SVRF DRC 规则块生成器**，输入任意 LDR spec 数组，按既有 deck 规范批量生成 width(INT)/space(EXT) 检查块——更纯粹的「规范理解 + 算子选择」判分。

## 判分设计（14 条断言 a-n，与 check() 一一对应）

- a  zip 合法 + 含 ldr_to_svrf.py（≥300B/UTF-8/无 NUL）
- b  py_compile 通过 + 仅标准库（禁 calibre/numpy/pandas/gdspy/skill/...）
- c  隐藏 B 跑 exit0 + stdout 非空 + stderr 无 Traceback
- d  out_B 恰 len(B)=5 个规则块（5 VARIABLE + 5 块头）
- e  每块 VARIABLE 行 rule_id + 值正确（数值容差 1e-9）
- f  每块 @ 行含 spec.desc 子串
- g  width→INT、space→EXT（算子与 check 类型匹配）
- h  每块检查行图层名正确
- i  每块检查行变量引用 `< _<rule_id>_`
- j  每块含 ABUT<90、SINGULAR、REGION 三修饰符且按序
- k  反硬编码：out_B 含所有 B rule_id 且不含任何 A rule_id
- l  随机化：3 个随机子集跑值正确 + sha256(out_B) 3 次稳定（确定性）
- m  out_B 块顺序与 B spec 顺序一致
- n  可见 A 跑 exit0 + 2 块（M1 width 0.159 INT + VSH_CMP space 0.028 EXT）

## 隐藏 B vs A

- A（可见）：2 条规则（M1 width 0.159、VSH_CMP space 0.028）
- B（隐藏）：5 条规则（M3 width 0.2、VIA1 space 0.14、PG width 0.18、M2 space 0.16、AT4 width 0.12）
- 规模/取值/结构均不同（非换名）；check() 只跑 B。

## 难度判断

- L1（离线 Python 复刻，纯 stdlib 解析 JSON + 文本生成），与 r240/r241/r243 同档。
- 反硬编码（条件 k）+ 随机子集（条件 l）+ 算子匹配（条件 g）+ 修饰符顺序（条件 j）共同把"只背 A 答案"的方案挡在外面。
- Calibre license 在 .75 不可用（实测 `calibre -svrf` 报 `Unable to acquire calibrehdrc license` RC=4），故判分不真跑 calibre，但要求生成器产出的 SVRF 文本在结构上与真实 deck 一致（agent 真实 grounding 自 22533 行 deck，文本规范可信）。
