# pspw5 深读 — WR_time corner 对比报告生成器

## trace 来源
- session: `1793847350187_pspw5.messages.json`
- user: t0002616 / host: hfeg0pkn004 / mc=29 / domain: waveform
- tools: 130 netlist + 53 schematic + 2 hspice（FineSim .mt0 测量分析）
- 40 msgs / 9 user turns

## 用户意图（逐轮原文，未脱敏）
- U#0「在运行SAtest开头的四个激励文件后的结果中，为什么后缀为slow的WR_time要比fast的小」+ 11 attachments（4×SAtest_wiArray_{slow,slowest,fast,fastest}.sp + EDR_261103.inc + finesim_option + ideal_stimulus_OC.sp + pattern_power.sp + netlist + wr_data_all1.sp + wr_data_mid1.sp）
- U#5「WR_time仿真结果是slow<slowest<fast<fastest」
- U#7「这是按后缀对应的结果文件」+ 4×.mt0（wr_slow/slowest/fast/fastest.mt0）
- U#9「对激励文件进行来修改，分析alter2的wr_time的error原因」+ SAtest_wiArray_fastest.sp + wr_fastest.log
- U#11「这是ss/-40的波形文件」+ wr_fastest#1.fsdb
- U#28「trig v(mat0_bla<19>,mat0_blb<19>) val='0' cross=1  td='...' 这条的作用是什么」
- U#30「这个波形是不是不太对，BL交叉不是从0/1开始的」
- U#32「和ff/110波形对比为什么ss/-40的波形有异常」+ wr_fastest#2.fsdb
- U#38「修改激励文件后出现报错，分析原因」+ SAtest_wiArray_fastest.sp + wr_fastest_wooc.log

## assistant 工具链
- list_allowed_files（看 uploads）→ read_files（读 .sp/.mt0）→ skills(finesim-fsdb-reader) → editor(写 fsdb_driver.py) → run_approved_command（跑 fsdb 解析）→ 多轮对比分析
- 关键产出：A#8 把 4 个 .mt0 的 wr_time 取值列成二维表（背景×写pattern），纠正用户「fast<fastest」与后缀的实际反序；A#27/A#37 用 fsdb 波形对比 ss/-40 vs ff/110 定位「写入提前完成」根因

## 真实 .mt0 格式（FineSimPro measurement output）
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
.TITLE '***add finesim option*********'
   near_dvbl0_0 ... near_dvbl0_7  far_dvbl0_0 ... far_dvbl0_7  twlon  vmsn_n_max  vcs_90p  tcs0  twldelay  twlrise_far  wr_time  temper  alter#
    <25 个科学计数法值>
```
- 25 列：16 个 dvbl 测量 + 6 个时序测量(twlon/vmsn_n_max/vcs_90p/tcs0/twldelay/twlrise_far) + wr_time + temper + alter#
- wr_time 单位秒（如 1.8417e-09 = 1.8417 ns）
- 每文件单 data row（alter#=1）；多 .alter 时会有多行

## 真实 A 数据（4 文件 wr_time, ns）
| 文件 | wr_time(ns) | temper | alter |
|---|---|---|---|
| wr_slow.mt0 | 1.8417 | 98 | 1 |
| wr_slowest.mt0 | 2.0890 | 98 | 1 |
| wr_fast.mt0 | 2.2620 | 98 | 1 |
| wr_fastest.mt0 | 2.0951 | 98 | 1 |
- 升序: [wr_slow, wr_slowest, wr_fastest, wr_fast]（注：后缀名 slow/fast 与实际 wr_time 大小无对应——这是本 case 的反硬编码轴）

## A-faithful 判定
- U#0 是纯「提出需求」轮（问为什么），无根因/无修复方案 → 满足 A-faithful 选轮规则
- 但 U#0 是「why」解释题，gold=assistant 的解释性分析，断言只能对事实（数值/排序）不能对措辞 → 判分客观性弱
- **结论：B-grade synthesized**。重述为 produce 任务：「FineSim .mt0 corner 对比报告生成器」——解析多 corner .mt0 文件，提取 wr_time，产出 comparison.json + report.md。真实 .mt0 文件作为 A 资产（忠实于 trace 的真实数据），hidden B/B2 合成不同 corner 名/值/列数/行数。

## 合成 plan
- **生成器**：`wr_corner_cmp.py --mt0-dir <dir> --outdir <dir>`
  - 解析目录下所有 `*.mt0`：$DATA1 header（SOURCE=FineSimPro 校验）+ .TITLE + 列头 + data rows
  - corner 名 = 文件名 stem（去 .mt0）
  - 提取 wr_time（→ ns）、temper、alter#；多 alter 取 alter#==1 为 base wr_time，n_data_rows 记录行数
  - 输出 `comparison.json`：{source, version, n_corners, corners:[{name, file, wr_time_s, wr_time_ns, temper, alter, n_data_rows, all_alters:[{alter, wr_time_ns}]}], ordering:[corner names 升序], summary:{fastest_corner, slowest_corner, min_ns, max_ns, range_ns, span_pct}}
  - 输出 `report.md`：corner × wr_time 表 + ordering 行 + fastest/slowest 声明
- **A**（visible）：4 真实 .mt0（wr_slow/slowest/fast/fastest）
- **hidden B**：5 合成 .mt0（corner_tt/ss/ff/fs/sf，不同值，不同列数=20，不同 corner 名，5 文件非 4）
- **hidden B2**：3 合成 .mt0（run_typ/slow/fast），每个 2 data rows（多 alter），3 文件
- **反硬编码轴**：A corner 名 wr_* + 4 文件；B corner_tt_* + 5 文件 + 20 列；B2 run_* + 3 文件 + 多 alter。三档 corner 名/数/列/行全不同 → 硬编 A 者 B/B2 全 FAIL

## check 16 条件 a-p 草案
a. 解 zip 防泄漏（无 check/reference/negative/jsonl）+ py_compile
b. B-run exit 0 + 产 comparison.json + report.md
c. comparison.json 顶层键：source/version/n_corners/corners/ordering/summary
d. n_corners == B 文件数（5）
e. 每-corner 字段：name/file/wr_time_s/wr_time_ns/temper/alter/n_data_rows/all_alters
f. wr_time_ns 与 B 期望值容差内匹配（±0.5%）
g. ordering 升序正确（== 期望排序）
h. summary.fastest_corner == ordering[0]；slowest_corner == ordering[-1]
i. summary.min_ns == min(values)；max_ns == max(values)；range_ns == max-min
j. report.md 含所有 B corner 名（markdown 表）
k. report.md 含所有 B wr_time 值（ns）
l. report.md 含 ordering/fastest/slowest 声明文本
m. B2-run：处理多 alter（n_data_rows==2，all_alters len==2，wr_time_ns==alter1 值）
n. B2 n_corners == 3（非 A 的 4、非 B 的 5）→ 反硬编码
o. 跨输入守卫：B-run 与 B2-run comparison.json 不同（corner 名/数/值全异）→ 杀 print_expected
p. 确定性：3× sha256(comparison.json) 一致

## 备注
- L1 离线（纯文本解析，无 EDA 工具依赖，无需 .75）
- 真实 .mt0 = trace 实际产物（FineSimPro V-2023.12-1），忠实于 trace 数据
- L1/L2 比例债仍存（本轮 L1），但 fresh mc>=30 池耗尽 + 40min 预算 + L2 需 live binary 不可移植 → 取 L1 produce
