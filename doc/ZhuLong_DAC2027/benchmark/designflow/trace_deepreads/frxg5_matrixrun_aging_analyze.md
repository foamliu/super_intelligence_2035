# Deepread: frxg5 — matrixrun_aging 脚本 aging 部分结构化分析

- **session**: 1791787377751_frxg5
- **user/host**: hswang @ hfeg0plg64
- **mc**: 54 (domain spice_sim)
- **trace**: 16 msgs / 249KB / 1 substantive user turn
- **旧判定**: parked "consultation analyze-aging-script" (r435) → r618 reaudit 可造
- **真实路径**: /proj/drcoa/V0/simdir/finesim/drcoaF/RunFile/Vcap/Aging_Sim/matrixrun_aging (3522 行 Perl)

## 用户原话
> 我现在的工作目录是 /proj/drcoa/V0/simdir/finesim/drcoaF/RunFile/Vcap/Aging_Sim，帮我查看该目录下的 matrixrun_aging 脚本，并分析关于 aging 部分的代码

## 助手工具链
read_files(matrixrun_aging 全文) → search_codebase(aging/eageba/t01/vdpg0/vdpg1/reltotaltime/relstep/AgingModelVer/AgingStep2，超时) → 分段 read_files(1-200/800-1000/1600-2000/1994-2200/3471-3495) → 产出 10KB 中文结构化分析报告（aging 命令行参数表 / 两阶段 MOSRA 工作流 / genAgingStep1SimTestbench / genAgingStep2SimTestbench / genAgingRunFile / agingPVT corner 映射 / -eageba 自动模式 / HTOL 高压支持 / 使用示例 / 数据流图 / 总结）

## 拟造任务形态
spice_sim L1 离线「Perl 仿真脚本 aging 部分结构化分析器」(B 档 synthesized，A 档不可行 = 真实 /proj 内网工程目录 SUT 沙盒无 /proj 权限不可达)：
- A = doc/(matrixrun_aging.pl[真实 aging 相关代码逐字摘录 28KB] + script_meta.txt) + task_spec.json
- hidden B = hidden/doc/(matrixrun_aging.pl[结构不同的 hspice rel 流程 synthesized] + script_meta.txt) + hidden_manifest.json
- 任务 = 写 aging_script_analyze.py(workdir,out_dir) 解析 doc/ 产 aging_script_analyze.json 22 顶层键
- 22 断言 a-v 含 12 字段 cross-input guard(simulator/project/author/subroutines/mosra_sort/corner_mapping/units/eageba/htol_files/model_default/step2_ctrl/script_name) + A-leak guard + 真跑候选 + 确定性
- check.py 独立解析隐藏 B 计算 ground truth(无硬编码 B 值)

## 关键知识点（判分覆盖）
FineSim 覆盖仿真 / Synopsys MOSRA 两阶段老化（step1 stress simmode=0 / step2 measure simmode=1）/ eageba 退化文件 / agingPVT corner 映射(TT→mosra_mos_tt) / HTOL 高压电源(Pattern_Power_HTOL_vdpg*.sp) / reltotaltime 单位(yr/day/hr/min) / mosralife=delvth0 / mosrasort / radegfile

## 复活池变现 #32
承 r619-r649(#1-#31)。本轮 frxg5 → EDA-Eval-DesignFlow-AgingScriptAnalyze-001（Perl 仿真脚本结构化分析报告首例 + cross-input-guard 12 字段首例）。
