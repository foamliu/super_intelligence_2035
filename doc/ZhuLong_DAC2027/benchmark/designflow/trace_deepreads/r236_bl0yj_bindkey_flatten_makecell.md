# r236 深读 — weizhao/bl0yj (SKILL bindkey flatten/makecell)

> 日期 2026-11-08；shard C r236；trace=1790306446486_bl0yj（weizhao@hfeg0pkn004/10.129.2.13, mc=33, 40 msgs, agent=lead）。
> case=EDA-Eval-DesignFlow-SkillBindkeyFlattenMakeCell-001（layout_virtuoso, B-synthesized, L1, k=18 a-r）。DEBT 清零。

## 选料
- r234/r235 两轮选料 0 case（DEBT:2）。本轮嵌套 find 验 existence + ledger_C(401)+cross-shard excl(643) 联合排除 + 饱和用户过滤，mc>=15 layout-affinity 打分。
- 647 fresh 候选。深读 top 候选：xxchen 84qb3(physical_verify, mc=334, drc:675/calibre:191, L2 但 drcConnect 工具上下文复杂)、e0045260 8fudf(layout_virtuoso, per-cellview layer display, Q&A 偏解释)、weizhao bl0yj(layout_virtuoso, SKILL bindkey, 交付物清晰)。
- 选 bl0yj：NEW user weizhao@hfeg0pkn004，单轮明确需求「数字键9=flatten, ctrl+m=make cell」，assistant 40 步完整闭环(14 RAG + 3 get_api_details + editor 写 .il + read_files 验证)，交付物=bindkey_flatten_makecell.il，可静态判分。domain layout_virtuoso(54→55，低于 physical_verify 81)。
- 跨 shard excl 已查（bl0yj 不在 643 名单）；ledger_C 之前未动过。

## 用户原话（U#0, idx 0）
`<user_input mode="act">1.帮我写一个skill脚本 实现 数字键9 = flatten功能，ctrl+m = make cell</user_input>`
- 单轮，提出需求（未给根因/修复）→ A-faithful 合格；但 cellview 未在 trace 中打开、无用户附件 → 做 B-synthesized（与 r232/r233 同口径）。

## assistant 流（40 msgs, 14 RAG, 3 get_api_details, 2 editor, 2 read_files）
1. RAG 搜 hiSetBindKey / flatten / make cell / bindkey shortcut（14 次）→ 定位 API：`hiSetBindKey(t_appType t_key t_skillCmd)`、`leHiFlatten`/`leHiMakeCell`（GUI form opener，leHi 前缀）、`leFlatten`/`leMakeCell`（编程式，需传参）。
2. get_api_details 确认 leHiFlatten/leHiMakeCell 签名。
3. list_allowed_files 查可写目录 → `/home/weizhao/.cline/scripts/data/`。
4. editor 写 `bindkey_flatten_makecell.il`（先写到 /home/weizhao/ 被策略拒，改写到 .cline/scripts/data/）。
5. read_files 验证文件内容。
6. 交付总结（表格 + load 用法 + 操作流程）。

## 关键 SKILL 决策（= 8 pitfall 的来源，都来自真实 trace）
- **app type = `"Layout"`**（Layout Editor，非 "Layout XL"/"Schematic"）。
- **数字键 9 事件串 = `"None<Key>9"`**（`None` 前缀 = 无修饰键，不是裸 "9"）。
- **Ctrl+M 事件串 = `"Ctrl<Key>m"`**（`Ctrl` 首字母大写，按键字母 `m` 小写）。
- **用 `leHiFlatten()`（GUI 表单 form opener）而非 `leFlatten()`（编程式，需传展平层级数）**——用户要交互式「按弹出表单」。
- **同理 `leHiMakeCell()` 而非 `leMakeCell()`**。
- **`load("/home/weizhao/.cline/scripts/data/bindkey_flatten_makecell.il")`** 加载。
- **`printf("Bindkeys loaded successfully...")`** 向 CIW 打印确认。
- **`hiSetBindKey("Layout" "None<Key>9" "leHiFlatten()")`** + **`hiSetBindKey("Layout" "Ctrl<Key>m" "leHiMakeCell()")`**。

## 生成的 .il（trace 原文，editor idx 35）
```skill
hiSetBindKey("Layout" "None<Key>9" "leHiFlatten()")
hiSetBindKey("Layout" "Ctrl<Key>m" "leHiMakeCell()")
printf("Bindkeys loaded successfully:\n")
printf("  [ 9 ]      -> leHiFlatten()   (Flatten)\n")
printf("  [ Ctrl+M ] -> leHiMakeCell()  (Make Cell)\n")
```

## case 设计
- SUT 写 `bindkey_gen.py`（CLI <manifest.json> -o <out.json>, stdlib only），读 manifest{meta,app_type,load_path,script_name,bindkeys[{id,modifier,key,label,command,gui_form,programmatic_alt}]}，生成 SKILL bindkey 代码（避开 8 坑）+ bindkeys_report + pitfalls_avoided + summary，输出 4 顶层键 JSON。
- A_run=trace grounded(app=Layout, 2 bindkeys: None<9>→leHiFlatten, Ctrl<m>→leHiMakeCell, load_path=/home/weizhao/.cline/scripts/data/bindkey_flatten_makecell.il)。
- 隐藏 B=3 个不同键(None<F2>→leHiSave, Shift<d>→leHiDelete, Ctrl<a>→leHiSelectAll, 反硬编码 A)；B2=编程式 gui_form=false command="leFlatten(32)"(杀总是-leHi)；B3=app_type="Schematic"(杀总是-Layout)。
- 18 条 a-r：(a)zip+1py (b)py_compile+stdlib (c)A JSON+4keys (d)A exit0 (e)hiSetBindKey [P8] (f)"Layout" [P1] (g)None<Key>9 [P2] (h)Ctrl<Key>m [P3] (i)leHiFlatten且非leFlatten( [P4] (j)leHiMakeCell且非leMakeCell( [P5] (k)load( [P6] (l)printf+loaded [P7] (m)pitfalls==8规范ID (n)bindkeys_report==金标A (o)B 含 B 的 bindkey 串+命令[反硬编码] (p)B2 leFlatten(32)且非leHiFlatten[杀总是-leHi] (q)B3 "Schematic"且非"Layout"[杀总是-Layout] (r)3-seed 确定性。
- k_check=18=k_rationale ①-⑱ ≥8 ✓。
- self-verify: golden 18/18 PASS；5 negative 全 FAIL(empty_shell/print_expected/core_deleted/naive_hardcode_a/stub_no_skill_code)；§4.9 三假提交(empty/print_expected/core_deleted)全 FAIL；3-seed STABLE；test 字段==disk check.py 字节相等；E2E jsonl test PASS。

## 台账
- ledger_C: 403 已动过（case 229·parked 174·claimed 0·deepread 0）。
- jsonl C 第 229 行。
- DEBT: 0（r234+r235 两轮选料债清零）。
