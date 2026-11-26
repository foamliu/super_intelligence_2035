#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os

BENCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark"
MEM = os.path.join(BENCH, "MEMORY_DESIGNFLOW_A.md")
ARCH = os.path.join(BENCH, "ARCHIVE_OPERATOR_DESIGNFLOW.md")

lines = open(MEM, encoding="utf-8").read().splitlines()

snapshot_r436 = (
"WAITING: 0（📦 **2026-11-12 r436 造题轮(1 net-new-case, A.jsonl 241→242, DEBT 0)**："
"r435 peek lead kdjt3(e0039602@hfeg0pkn002 mc55 verilog:311 digital, 同 r399/r419/r428 verilog_lib_trans 项目不同 deliverable)→claim+深读(42msgs/200KB scp .75 via 10.129.8.234 autofs). "
"U#0 1-turn PRODUCE-TASK「读 result_map, AF_latqn2_CmFsUnit 这种类型需要[正确 module 模板 clk/clk0/clk1+trireg #(1,1,200)+invhiz/passg/inv_base]」未给根因→A-faithful 合格但 deliverable=修改后私有 result_map(26K 行)→A-faithful INFEASIBLE→B档. "
"agent(deepseek) run_approved_command(python-runner) 写 6 临时脚本: 定位 279 模块中 1 条 AF_latqn2_CmFsUnit 错误条目(行 1192-1413, vlgTcap #(.tdecay(300))/trireg #(1,1,100)/无 clk 门控), 按 header 名整块删(非 body 子串, CmFsUnit body 4occ 仅 1 模块命中), 验证 279→278/0 残留/边界干净, 清理脚本. "
"合成 ResultMapEntryRemover-001(digital L1 spec-driven catalog-entry-remover k=15 B档): deliverable=remove_result_map_entry.py 纯 stdlib CLI(--input/--module/--output/--report, 按 header 模块名整块删, 边界单空行, 多目标全删, not-found 退出非0). "
"A=result_map_A.txt(8 模块, 目标 AF_latqn2_CmFsUnit 中部, vlgTcap 签名); B=hidden result_map_B.txt(9 模块, 目标 B_Module_Delta 中部 keeperTcap 签名, +Epsilon body `wire B_Module_Delta;` 子串陷阱, +Iota 末条 EOF 边界). "
"自验 ref PASS 15/15, 4neg(naive_empty/print_only/core_removed[substring-remover 误删 Epsilon]/hardcoded_A)全 FAIL, §4.9(a)(b)(c)FAIL, 断言闸门 k_rationale=k_check=15✓; "
"surgicality: core_removed 误删 Epsilon→(j)(i)(h)FAIL; hardcoded_A 在 B 找不到 A 目标→(c)exit1. "
"判分亮点: check.py 独立 line-scan oracle(startswith+split, NO regex)vs ref regex; ⑩子串陷阱 Epsilon 完好击败 substring-remover; ⑬跨输入守卫 0 个 A 专属串击败 hardcoded_A; ⑭not-found 退出非0; ⑮3 次确定性. "
"ledger mark kdjt3→case(case 238→239), 清理 stale dup claim lilaj.messages.json→parked(dup of r424 lilaj dir, sid-suffix dedup bug). "
"讨论豁免(配额 last A.md r434 gap2<4, P-004 OPEN 由 A 开+A r435 已行动, B/C/D 待表态). "
"paper pdflatex 0err/0undef 14p \\Ntasks 1186→1189(A242+B274+C311+D362, D 自 r432 +2). MEMORY 归档 r410-r425 流水+11 stale WAITING 快照至 ARCHIVE, 体积 85KB→~16KB. "
"· 📊 trace 覆盖率: 184/1436≈12.8%(+0) · 🎯 通过率: 不变(最近20 5/20=25.0%, 本 case 未 pi 实跑) · 🧾 断言: k_rationale=k_check=15 ✓(今日 1/1 达标 r436) · 📦 体积：MEMORY_A≈16KB · WAITING:0, DEBT 0）"
)

flow_r436 = (
"→ r436 造题轮(1 net-new-case, A.jsonl 241→242, DEBT 0): r435 peek lead kdjt3(e0039602 hfeg0pkn002 mc55 verilog:311 digital, 同 verilog_lib_trans 项目不同 deliverable) claim+深读(42msgs scp .75). "
"U#0 1-turn produce-task「读 result_map, AF_latqn2_CmFsUnit 类型需[正确 module 模板]」未给根因→A-faithful 合格, deliverable=修改后私有 26K 行 result_map→INFEASIBLE→B档. "
"agent run_approved_command 写 6 临时脚本: 279 模块中 1 条 AF_latqn2_CmFsUnit 错误条目(行 1192-1413, vlgTcap/trireg #(1,1,100)/无 clk)按 header 名整块删(CmFsUnit body 4occ 仅 1 模块命中, 非子串), 279→278/0 残留/边界干净. "
"合成 ResultMapEntryRemover-001(digital L1 catalog-entry-remover k=15 B档): remove_result_map_entry.py 纯 stdlib CLI 按 header 模块名整块删+边界单空行+多目标全删+not-found 退出非0. "
"A=8 模块(AF_latqn2_CmFsUnit 中部 vlgTcap); B=9 模块 hidden(B_Module_Delta 中部 keeperTcap + Epsilon body `wire B_Module_Delta;` 子串陷阱 + Iota 末条 EOF). "
"自验 ref PASS 15/15, 4neg FAIL(naive_empty/print_only/core_removed[substring 误删 Epsilon]/hardcoded_A), §4.9(a)(b)(c)FAIL, k=15✓; "
"判分亮点: check.py 独立 line-scan oracle(startswith NO regex)vs ref regex; ⑩子串陷阱 Epsilon 完好; ⑬跨输入 0 个 A 串; ⑭not-found 非0; ⑮3 次确定. "
"ledger mark kdjt3→case(238→239), lilaj.messages.json stale dup claim→parked. 讨论豁免(r434 gap2<4, P-004 A 开+r435 行动). paper 0err 14p \\Ntasks 1186→1189(A242+B274+C311+D362). MEMORY 归档 85KB→16KB. A.jsonl 242, DEBT 0."
)

summary_r410_r425 = (
"→ r410-r425 流水（16 轮：r425 RegrRerunScriptGen / r424 XsCheckReportDiag / r423 Bl6CompcodeMerge / r422 SvTaskReport+TFC指标 / r421 RunRegrCaselistAdapter / r420 RegrCaseFilter / "
"r419 SvConvTimeoutSkip / r418 McuAsmGen parked复审 / r416 选料深读 / r415 VecgenProbeDiag / r414 SignalRunXref / r413 XrunTimingCompare / r412 CslWlGateMap / r411 PatternTaskXref / r410 VlibFlowRetryRewrite）原文已归档 ARCHIVE_OPERATOR_DESIGNFLOW.md「r436 归档批次」"
)

keep = []
archive = []
for i, ln in enumerate(lines):
    if i == 0:
        continue  # replaced by snapshot_r436
    if ln.startswith("WAITING: 0"):
        archive.append(ln); continue
    if ln.strip() == "":
        continue
    m = re.match(r"→ r(\d{3}) ", ln)
    if m and 410 <= int(m.group(1)) <= 425:
        archive.append(ln); continue
    keep.append(ln)

# keep[:9] should be r435,r434,r433,r432,r431,r429,r428,r427,r426 (the concise -> lines)
recent = [ln for ln in keep if re.match(r"→ r4(\d\d) ", ln) and 426 <= int(re.match(r"→ r4(\d\d) ", ln).group(1)) <= 435]
older = [ln for ln in keep if ln not in recent]
new_mem = "\n".join([snapshot_r436, flow_r436] + recent + [summary_r410_r425] + older) + "\n"

open(MEM, "w", encoding="utf-8").write(new_mem)

arch_block = (
"\n\n## 归档块 · 2026-11-12 r436（MEMORY_A 85KB→16KB 瘦身）\n\n"
+ "以下为从 MEMORY_DESIGNFLOW_A.md 移出的 11 条 stale WAITING 快照 + r410-r425 完整流水（与保留的 → rXXX 简版流水重复，原文存档备查）：\n\n"
+ "\n".join(archive)
)
open(ARCH, "a", encoding="utf-8").write(arch_block)

print("new MEMORY size:", os.path.getsize(MEM), "bytes")
print("new MEMORY lines:", len(new_mem.splitlines()))
print("archived lines:", len(archive))
print("ARCHIVE size:", os.path.getsize(ARCH))
print("recent kept:", len(recent), "older kept:", len(older))
