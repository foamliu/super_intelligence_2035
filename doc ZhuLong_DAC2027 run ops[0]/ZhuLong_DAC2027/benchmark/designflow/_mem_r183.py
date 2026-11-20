#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archive r181 + r180 full flow bodies from MEMORY_DESIGNFLOW_A.md to MEMORY_A_archive.md,
replace with 1-line summaries, then prepend the r183 flow line + update first-line snapshot."""
import os, re

BENCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark"
MEM = os.path.join(BENCH, "MEMORY_DESIGNFLOW_A.md")
ARCH = os.path.join(BENCH, "MEMORY_A_archive.md")

with open(MEM, "r", encoding="utf-8") as f:
    lines = f.readlines()

# find the r181 and r180 full-body lines (start with "> 轮 181 流水" / "> 轮 180 流水")
def find(roundn):
    prefix = "> 轮 %d 流水" % roundn
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            return i
    return None

i181 = find(181)
i180 = find(180)
assert i181 is not None and i180 is not None, "r181/r180 lines not found"

body181 = lines[i181].rstrip("\n")
body180 = lines[i180].rstrip("\n")

# archive block
batch_header = "\n\n## 归档批次 94（2026-11-07 轮 183 体积维护）\n\n"
archive_block = batch_header + body181 + "\n\n" + body180 + "\n"

with open(ARCH, "a", encoding="utf-8") as f:
    f.write(archive_block)

# replacement 1-line summaries
summary181 = "> 轮 181 流水已归档至 MEMORY_A_archive.md（归档批次 94，2026-11-07 轮 183 体积维护）。摘要：r181 scansync 到期(数字一致无新扫描, daily log 2916 行健康) + tyk6x(shanliny@hfeg0pkn001 mc102 verification) 合成交付 VcheckMacroAdd-001(verification B档 synthesized L1-static 16 conds) · 1 case · 无 cline 实跑 · covered 99→100 · WAITING:0\n"
summary180 = "> 轮 180 流水已归档至 MEMORY_A_archive.md（归档批次 94，2026-11-07 轮 183 体积维护）。摘要：r180 池充足跳过 scansync + jzlbn(lorikx@hfeg0pkn001 mc395 verification) 合成交付 FsdbVerdiInteg-001(verification A档 faithful L2-static 16 conds) · 1 case · 无 cline 实跑 · covered 98→99 · WAITING:0\n"

lines[i181] = summary181
lines[i180] = summary180

# new r183 flow line
r183 = "> 轮 183 流水（2026-11-07 03:3x-03:5x，evxj6 合成交付 ParamRecon-001 · 1 case · 无 cline 实跑）：**① scansync 未到期(下次 r186)**，候选池充足(216 mc15)跳过。**② 选料**：col6 kw:count digital-dominance 过滤(dig_share>=0.5, 排除 systemverilog>=1000/synopsys>=2000 污染)→164 真 digital-dominant fresh。选 evxj6(xuluo@hfeg0pkn001 mc333 verilog:1251 rtl:804 systemverilog:42 dig_share=0.73, 新用户, verification 域)。claim(ledger 178→179)。**③ 深读 evxj6**：scp messages.json(1.83MB,293 msgs/159 user/134 asst, agent=lead)。真·DRAM RHR(Pow Hammer Refresh) python 行为模型 vs Verilog RTL+TB+netlist 参数对齐分析 trace。USER#0 逐字「分析这个目录下的代码，这是python下对应的参数，告诉我两者参数有何不同{...params...}」(clean A-faithful 需求轮)。assistant(deepseek-v4 lead) 58 editor + 36 run_approved_command + 24 read_files：产出 para_compare_dbcoa_v2.csv(7 列: 类别/Python参数/Python值/对应Verilog文件(行号)/Verilog对应机制/Verilog实际值/结论)。关键实测结论：tRFC/tRC 实际=rhr_driver.sv task #延时逐条求和(pkg tRFC=280000 为死参数仅注释; ref_cmd 33 条延时和=380.100ns; act_cmd 10 条和=60.0ns)；tREFI=pkg 表达式含加速倍数(test env 4x=15600ns / regression 8x=31200ns)；OSC 周期=#翻转延时×2(260/440/860)；under2=netlist AND6(全<=2)&cm1_ro_DisUnder2→DiscardSkipN=NAND(Under2,RH_POINTER_Pre)；RHDiscardRate 2'b00→Hat4÷16；nREFinBurst_replace 无 replace 双档。真实 /proj/dbcoa verilog 对 e0031982 不可读(permission denied)→B档 synthesized assets(忠实裁剪 verilog 摘录, 真值+真延时和取自 trace tool_results)。**④ 交付接口**：param_compare.py <params.json> <verilog_dir> <out_csv> → 7 列 CSV。**⑤ hidden_B 结构反转**：verilog_B 8x 加速(vs A 4x)/tRFC pkg 活 380000(vs A 死 280000)/OSC 200/360/700(vs A 260/440/860)/RHDiscardRate 2'b10→÷32(vs A 2'b00→÷16)/LFSR init 5(vs A 4)/ref_cmd 22 延时和 380.250(vs A 33 和 380.100)/act 8 延时和 60.0(vs A 10 和 60.0)。A/B gold >=8 字段不同。**⑥ check.py 15 conds(a-o)**：(a)zip含param_compare.py (b)py_compile (c)CLI 3 位置参数 exit0 产出 out_csv (d)7 列表头 (e)tREFI 行反映 8x 加速且结论非一致 (f)tRFC 行实际=独立求和 B ref_cmd 延时(~380.25)±1ns 且一致 (g)tRC 行实际=独立求和 B act 延时(~60.0)±1ns 且一致 (h)OSC1_T 行实际=2×#延时=200 且一致 (i)OSC4_T 行 Verilog 无 (j)nREFinBurst_replace 行 Verilog 无 (k)DiscardUnder2 行识别 AND6 链+DisUnder2=1 且极性一致/保护开启 (l)DDRDiscardRateMode 行 2'b10→÷32(独立解码)且一致 (m)lfsr_init 行实际=5 且一致 (n)跨输入守卫 B CSV 不泄漏 A 字面量(15600/260ns/440ns/860ns/2'b00→÷16/33条/280000/4x加速) (o)反stub 源含 re.*+open(+写入机制(csv.writer/.write)。**⑦ check 独立重推 gold**：check.py 自行对 B verilog 求 ref_cmd/act 延时和、解码 rate、解析 pkg/LFSR init，与候选 CSV 比对→击败硬编 A 答案。**⑧ 自验全绿**：ref reference_submit.zip→check() PASS 15/15 + negative_selftest 3 negs(naive_stub/always_pass/ref_delete_core)全 FAIL NEG_RC=0 + §4.9 (a)empty_shell→FAIL (b)print_only→FAIL 12/15 (c)ref_delete_core→FAIL 三假全 FAIL + jsonl test 字段端到端(写 _test_from_jsonl.py 在 ref dir 跑)→check() PASS 15/15 + disk check.py 与 jsonl test sha 同步(8e973da22a83bf18)。**⑨ 断言闸门**：k_rationale=k_check=15>=8 PASS。**⑩ leak 隔离**：assets/ 只 prompt/task_brief/params.json/verilog_A/(6 文件)+hidden(manifest+verilog_B+params_B), 无 check.py/reference/negative/hidden_B/reference_submit.zip。**⑪ 与既有 case 区分**：SimFailParse-001=仿真失败 rpt/log 解析;VcheckMacroAdd-001=UVM ref_model 宏注入;本 case=python-vs-verilog 参数对齐分析(求延时和+解码 rate+netlist 链还原), 交付形态/判分字段全不同。**⑫ 累计**：71v/21P/49F=29.6% rolling-20 5/20=25.0% 不变(无 cline 实跑, ParamRecon 待入窗);covered 101→102;A jsonl 103→104;verification 域 18→19。**提交**：super_intelligence main + EDA-Flow-Bench master。**下轮 r184**：scansync 下次到期 r186;可 cline 实跑入窗(backlog 31 条,含 ParamRecon/CrEdgeAlignFix/VcheckMacroAdd/FsdbVerdiInteg/SimFailParse);或继续出 case(fresh digital-dominant 候选 ~163, next: 3s3zx mc347/b1w28 mc344/8ylkn mc331/im5c1 mc261 等);rolling-20 25.0% 目标中段。**WAITING:0**）。\n"

# new first-line snapshot
new_first = "WAITING: 0（shard A 轮 183：scansync 未到期(下次 r186)跳过+col6 kw:count digital-dominance 过滤(dig_share>=0.5)→164 fresh→选 evxj6(xuluo@hfeg0pkn001 mc333 verification)→深读(293-msg DRAM RHR python-vs-verilog 参数对齐分析;USER#0 逐字「分析这个目录下的代码,这是python下对应的参数,告诉我两者参数有何不同」clean 需求轮;真 /proj/dbcoa verilog 对 e0031982 不可读→B档 synthesized assets 忠实裁剪 verilog 摘录真值+真延时和取自 trace)→合成交付 ParamRecon-001(verification, B档 synthesized, L1-static, 15 conds a-o, check 独立求 B ref_cmd/act 延时和+解码 rate+解析 pkg/LFSR init 击败硬编 A)·1 条 case 交付·无 cline 实跑·累计 71v/21P/49F=29.6% rolling-20 5/20=25.0% 不变·covered 101→102·A jsonl 103→104·verification 18→19·WAITING:0）。\n"

# replace first line
out = [new_first] + lines[1:]
# insert r183 line right after first line
out.insert(1, r183)

with open(MEM, "w", encoding="utf-8") as f:
    f.writelines(out)

print("archived r181+r180 bodies; inserted r183; new MEM size:", os.path.getsize(MEM))
