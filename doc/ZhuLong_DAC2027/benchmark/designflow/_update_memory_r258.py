#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update MEMORY_DESIGNFLOW_A.md for r258: rewrite heartbeat line 1 + insert r258 flow line."""
import os

MEM = '/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_A.md'

with open(MEM, encoding='utf-8') as f:
    lines = f.readlines()

new_heartbeat = (
    "WAITING: 0（shard A 轮 r258：管理任务=scansync 到期执行(r256 后 2 轮, r258 到期) → "
    ".75 跑统计(最新仍 11/05 扫描, 数字同 r256: mc30=1511/pool_A_mc15=216/daily 20261109=2893 健康) → "
    "复查 BLOCKER③: r256 报\"池空\"实为只查 top-mc-not-in-A(6 全 B/C/D 域); 重跑 .75 filter_digi.py 全量 digi-lean fresh → "
    "119 unique session 真未耗尽 → 选 c6xow(lorikx@hfeg0pkn001 mc158 digital, 149 msgs/1.07MB, rtl+verilog+synopsys 主导) claim → "
    "深读: USER#0 纯目标\"调整 testbench 符合最新修改\"(A-faithful), gold=tb_sp_sram.v v9.5→v9.6"
    "(G1: CRSxE 边沿不再清阵列仅 Q=X 脉冲, 移除 5 旧检查+新增 3 任务×8 调用), 逆向 11 处编辑重建 v9.5 baseline → "
    "合成 TbAlignReport-001: 通用 analyze_tb_alignment.py 解析 manifest→note/rtl/tb 输出 11 字段 JSON, "
    "judge 在隐藏 B(重标签 CRSENL/CRSENR/G3/8.5)与 B'(结构异构 CRSLE/CRSRE/G7/7.2/仍清阵列)上跑, "
    "14 conds a-n + ah 反硬编码 · 自验: REF PASS(B+B'), 4 negative 全 FAIL distinct failsets, "
    "§4.9 三假提交(empty/print-only/strip-core)全 FAIL, empty-zip FAIL · "
    "covered=168 / target=1511 = 11.1%（r258 +1, digital 58→59）· "
    "📊 trace 覆盖率：covered=168/1511=11.1% · 🎯 通过率: 最近20条 5/20=25.0%（不变, 无 cline 实跑）· "
    "🧾 断言: 14 条 a-n k_rationale==k_check==14 · 📦 体积：TASK_A≈25KB / MEMORY_A≈24KB）\n"
)

r258_flow = (
    "> 轮 r258 流水：管理任务=scansync 到期执行(r256 后 2 轮, r258 到期; r257 跳过) → "
    ".75 跑统计(ls -dt ssh_eda_search_*/ 最新仍 11/05, 旧 10/28, 无新扫描; summary.tsv rows=5822, "
    "dedup_sessions=3896/dedup_users=268/dedup_hosts=42, mc30=1511/mc100=865/mc300=252, "
    "pool_A_mc15_dedup=216, daily log 20261109=2893 行健康>100; 全数字同 r256) → "
    "复查 r256 BLOCKER③: r256 报\"shard A 候选池彻底耗尽\"实为只查 top-15-mc 未在 A 台账者(6 个 aneeo/m2vah/58vqx/7rzyf/cgqd1/n91pk 全 B/C/D 域), "
    "并非全量 fresh 池; 重跑 .75 filter_digi.py(全量 mc≥15 + shardA 强数字工具 grep + 4-shard EXCL) → "
    "cands_A_sorted.tsv 119 unique session 真未耗尽(BLOCKER③ 修正: 池非空, r256 误报) → "
    "选 c6xow(lorikx@hfeg0pkn001 mc158 digital, 149 msgs/1.07MB, rtl/verilog/synopsys 主导, ssh 10.129.2.10 确认文件在) → "
    "claim(ledger A 262→263 entries) → 深读 149 msgs: USER#0=\"请阅读rtl/文件夹内的修改记录markdown文件，以及最新的.v文件，调整一下testbench，符合最新的修改要求\""
    "(纯目标无根因/修法, A-faithful 合格) → 提取全部 user msgs + 11 处 tb_sp_sram.v 编辑 + final summary → "
    "gold 事实: G1 黄金规则(CRSxE 边沿不再清阵列, 仅 Q=X 输出扰动脉冲); 新增 3 任务 snap_mem_cr_edge/check_qx_after_cr_edge/check_mem_cr_edge_unchanged(各 8 次调用); "
    "移除 5 处旧 'mem=X / mem not X after CRSxE' 检查; 版本 v9.5→v9.6 → 逆向 11 处编辑重建 v9.5 baseline(全部 11 处 reverse-apply 干净, 205843→201395 字节, .75 scp 验证) → "
    "重定向为 TbAlignReport-001 分析器交付(避免 judge 内写/编真实 Verilog): 通用 analyze_tb_alignment.py 读 manifest→note/rtl/baseline_tb → "
    "解析 note 提取 G[0-9]+ 规则标签; 解析 rtl 端口 CR 使能信号(排除 CR 地址信号) + 检测 always 块内 for-loop+mem+CR-gate=清阵列 + 检测输出 Q='bx 赋值=Q 脉冲; "
    "解析 tb Version: 注释 + 计 $display 行(=== 'hxx + display 含 mem+CRS) = 旧检查数/标签 → 输出 11 字段 JSON → "
    "A 资产(prompt/task_brief/modification_note/new_rtl/baseline_tb/config_a) + hidden(B 重标签 CRSENL/CRSENR/CRANL/CRANR + G3 + 8.5; "
    "B' 结构异构 CRSLE/CRSRE/CRSLA/CRSRA + G7 + 7.2 + RTL 仍 for-loop 清阵列 + TB 无旧检查) → "
    "check.py 14 conds a-n(design/tb/version/rule/cr_signals/count/labels/clears/qx/needs + B' 跨输入守卫 n) + ah 反硬编码(A_LITERALS: CRSLE/CRSRE/CRSLA/CRSRA/CRSENL/CRSENR/G1/9.5/9.6/3 任务名) → "
    "reference analyze_tb_alignment.py 全部字段动态派生, 源码无 A_LITERALS → 自验: REF PASS(B 各字段全中 + B' 跨输入 n 中); "
    "4 negative(naive_noop→{c}, print_expected→{e,f,g,h,j,n}, core_deleted→{g,h,i,j,l,m,n}, naive_count_only→{g,h,n}) 全 FAIL distinct 4/4 failsets; "
    "§4.9 三假提交(empty-zip→{a}, print-only=naive_noop→{c}, strip-core=core_deleted) 全 FAIL; "
    "k_rationale==k_check==14, test_rationale=\"14 条断言：①…⑭\" → "
    "append EDA-Eval-DesignFlow_A.jsonl(169→170 entries) → trace_ledger mark c6xow→case(TbAlignReport-001) → "
    "refresh summary_stats.json scansync.r258(no_new_scan, BLOCKER③-corrected) → "
    "covered 167→168(digital 58→59) · WAITING:0\n"
)

# Replace line 0 (heartbeat), insert r258_flow as new line 1
lines[0] = new_heartbeat
lines.insert(1, r258_flow)

with open(MEM, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('updated. line1 WAITING:', lines[0][:20])
print('line2 r258 flow starts:', lines[1][:40])
print('total lines:', len(lines))
