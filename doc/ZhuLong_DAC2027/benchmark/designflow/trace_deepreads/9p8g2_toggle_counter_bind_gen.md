# 深读笔记 — 1790596559451_9p8g2（clwang @ hfeg0pkn005, mc=100, verification/digital 域）

## trace 概况
- 704 msgs（user 362 / assistant 342），3.4MB。助手工具：editor 158 · read_files 107 · search_codebase 7 · run_approved_command 4 · run_commands 2 · RAG 6。新用户 clwang（diversity）。
- 真实 build 会话（非 Q&A）：用户逐字提需求，助手反复改 python 脚本 + 真跑验证。68 个用户文本轮。

## 用户轮（A 档 faithful 候选）
- **轮 0（clean 提需求，A 档任务说明，选为本 case）**：「输入件目录是/home/clwang/test；编写一个python脚本，通过bind的方式，对文件cellname中的cell的输入输出信号添加信号翻转计数，具体的cell定义在cell_define.sv文件中，自己定义一个统计信号翻转的module，把定义的moudle和bind代码放在一个文件,文件名叫toggle_counter.sv」——无根因/无修复方案 → 符 A 档规则②。
- 轮1-29：修改输入件重跑 / 统一module单输入 / inout识别+vbn/vss/vpb/vcc忽略 / ignore_keyword文件 / 多cell_define文件+打印事件toggle_counter_print_event / %m层次 / not_found_cell报错→改打印 / 删print_event参数 / enable条件TOP.toggle_counter_enable / **轮24 重写脚本(输入libs+cellname.sv,在module最后添加,排除电源信号,copy修改文件,输出modified+not_found)** / 宏模板TOGGLE_COUNTER_TEMPLATE(signal,cell_name) / 不找不到cell打印到txt / cellname不用双引号 / 没修改的lib不copy / 输出目录已存在报错解决 / 同层次信号toggle分组 / 不限文件后缀 / out_dir参数。
- 轮30-32：aether原理图调线宽（离题，弃）。

## 助手真实产物（金标准来源）
- **add_toggle_v2.py**（8468B，最终接受版）：扫描 libs/* 中 module 定义 → 对 cellname.sv 每个 cell 找 input/output 端口（排除 inout 电源轨 vcc/vss/vbp/vbn/vkb/vccz/vssz/vpcsg/vwlp/vdd1）→ 在 endmodule 前插入 `` `TOGGLE_COUNTER_TEMPLATE(signal, cell_name) `` 宏 → 只写改过的 lib 到 out_dir → 输出 modified_cells.txt(lib_file,cell_name) + cellname_not_found.txt。
- parse_toggle_log.py（3995B）：解析 toggle 日志。
- run_approved_command 真跑脚本验证 toggle 输出（USER#34 贴了 [info] TOP.Chip...nand3GFx1.A toggle=72 等真实结果）。

## 资产可取性
- /home/clwang/test/ 全树 e0031982 可 ssh 直读（非 owner-only）。
- add_toggle_v2.py(8468) · cellname.sv(10908, 真实cell列表blcnand2GFx1...每行一个) · libs/cell_define.sv(262KB, 含invx1..invx16等module, input A/output Y/inout vcc/vss/vbn/vbp) · libs/cell_define1.sv · parse_toggle_log.py(3995) · modified_cells.txt · cellname_not_found.txt。
- A 档用真实子集：8 个 inv cell(invx1/2/4/6/8/10/12/16) + 2 ghost(invx99_fake/invx100_fake)。

## case 设计（EDA-Eval-DesignFlow-ToggleCounterBindGen-001）
- 交付=submit.zip{gen_toggle_counter_bind.py(=add_toggle_v2.py重命名)}。
- A 可见=cellname.sv(8 real inv + 2 ghost) + libs/cell_define.sv(8 inv module 真实子集) + prompt(USER#0逐字) + task_brief(≤3行交付接口)。
- B 隐藏=合成 b_libs/cell_define.sv(5 cell: tinv_x1/tnd2_x1/tnr2_x1/tbuf_x1/txr2_x1, 不同名/端口, inout vcc/vss/vbn/vbp) + b_libs/cell_define_extra.sv(decoy 未修改lib) + b_cellname.sv(5 found + 2 ghost_cell_a/b)。cross-input guard: B cell名/端口结构与A零重叠。
- **L1-static**：check.py subprocess 真跑候选于 B，解析输出结构（modified_cells.txt/cellname_not_found.txt/修改后lib的TOGGLE_COUNTER_TEMPLATE调用）。
- check.py 15 conds(a-o)：a zip含py b py_compile c [B]退出0 d [B]modified_cells.txt header e [B]not_found含2 ghost f [B]lib含TOGGLE_COUNTER_TEMPLATE g [B]电源轨端口不出现在template h [B]信号端口(a/b/y)出现 i [B]5 found cell在modified_cells j [B]2 ghost不在modified_cells k [B]decoy未修改lib不被复制 l [B]template第二参数=cell名 m [A]反硬编守卫(候选跑A真实子集产A正确:invx命中+fake进not_found) n 源码无B字面量(tinv_x1等) o [B']随机化(seed7打乱cellname顺序)found/not_found集合一致。
- 反硬编：guard m 候选跑 A 真实 invx 子集验 A 正确(invx1..invx16 命中 + invx99_fake/invx100_fake 进 not_found)；guard n 源码无 tinv_x1/ghost_cell_a 等 B 字面量；guard o B' 随机化结构一致。

## 自验（本地 /nasdata）
- ref PASS 15/15（check.py on reference_submit.zip → True）。
- 4 negatives 全 FAIL distinct：naive_noop→(d) / hardcoded_b→(m) 反硬编守卫 / print_only→(d) / core_deleted→(f)。
- §4.9 (a)(b)(c) 三假全 FAIL ✓（naive_noop=empty shell→d / print_only→d / core_deleted=core removed→f）。
- negative_selftest PASS（REF_PASS True, ALL_NEG_FAIL True, DISTINCT_CONDS=3≥2）。
- k=15 闸门 PASS（15 个 ①-⑮ 断言标记, k_rationale=k_check=15≥8）。

## 去重检查
- 与 lorikx sim-Makefile 案例(bw2u5/6yrpu)不同：本 case 是 cell-lib toggle 计数生成器，非 sim Makefile。
- 与 SpecNotifClassify/SimFailParse 等不同：本 case 生成 SV 翻转统计代码插入 lib module。
- 新 case 种类（toggle-counter-bind generation），无重复。
- 注：本轮先选 lku2o/gu1m2 均为已做 case 的 duplicate（lku2o=ckulq/r200 RdcViolCatalog, gu1m2=bw2u5/r84 VCSMakefile，11/05 rescan 捕获的重试），已 park。
