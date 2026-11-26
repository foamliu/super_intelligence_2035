# Deepread — mi210 (zjqiao @ hfhds206, mc=148) — Compress Netlist Toggle

## trace_source
- user: zjqiao
- host: hfhds206
- session_file: 1789544872347_mi210.messages.json
- match_count: 148
- domain: schematic_netlist
- real_task_summary: 用户拿到一个 shell 脚本 Run_Compress_Netlist（把普通 SPF/Vcap 网表转成 compress-mode 网表：复制网表目录 → <name>_Compress，再按模式把 2 条 power-switch 实例行的 switch_close 改成 switch_open）。用户先让 agent 把它改写成 SKILL 脚本（compressNetlist.il），再要求增强：自动检测 Netlist_* 目录、按日期排序、支持用户选择网表并更新 shell 脚本参数。agent 产出 CompressNetlist() 过程，按 mode 在 sedPairs 里定义 4 种模式（TSV_Vcap / Norm_Vcap / Norm_Spf / TSV_Spf），每种模式 2 条 XI2_11/XI0_11 实例行（含 inh_vss/inh_vcc/vss!/vcc! 与 Yio7<15>/YioN7<15> 网名）的 switch_close→switch_open 替换对，逐行 rexReplace 后写回 netlist 文件。

## 4-mode toggle spec（取自 assistant 产出的 caseq 代码块，权威）
| mode | XI2_11 line | XI0_11 line |
|------|------------|------------|
| TSV_Vcap | XI2_11 inh_vss YioN7<15> | XI0_11 inh_vcc Yio7<15> |
| Norm_Vcap | XI2_11 inh_vss Yio7<15> | XI0_11 inh_vcc YioN7<15> |
| Norm_Spf | XI2_11 vss! YioN7<15> | XI0_11 vcc! Yio7<15> |
| TSV_Spf (default) | XI2_11 inh_vss Yio7<15> | XI0_11 inh_vcc YioN7<15> |

注：M72 末尾的对照表把 Norm_Vcap 写成 vss!/vcc!（与 caseq 代码冲突），以 caseq 代码为准（Norm_Vcap == TSV_Spf 的目标行）。benchmark 保留 4 种模式字符串，但 Norm_Vcap 与 TSV_Spf 切换结果相同。

## 为什么选这条
- 单次 produce：用户一次给出脚本意图，agent 产出完整可运行脚本（非迭代 debug / 非 skill-exec onboarding / 非 Q&A how-to）。
- 确定性可判分：转换是纯文本 sed 式替换（switch_close→switch_open），输入网表 + mode → 输出网表，oracle 可独立重算并字节比对。
- D 域契合：schematic_netlist（网表文本变换）。
- 反硬编码可设计：隐藏 B 共享 6 条目标行（任务规格）但 surrounding/decoy 全异；3-seed 追加不同 decoy 行。

## 合成方案
- 任务：写 Python 脚本 compress_netlist.py，CLI `python3 compress_netlist.py <src_netlist> <mode> <dst_netlist>`，按 4 模式把 2 条目标行的 switch_close→switch_open，其余字节不动。
- 可见 A：DdrIoTopA 网表（6 条目标行 + 4 条 decoy + 负载/comment）。
- 隐藏 B：DdrIoTopB 网表（同 6 目标行 + 不同 decoy XI3_01/XI8_42/XI6_77/XI2_11..YioN3<5> + 不同 surrounding），嵌入 check.py。
- 3-seed：每种子给 B 追加不同 decoy switch_close 行，oracle 重算期望 dst 字节比对。
- check.py 11 条断言 (a-k)：compile / 无禁止运行时+无B字面量 / A×4模式可运行 / A×4模式 dst==oracle / 非法mode退码非零 / B TSV_Vcap dst==oracle / B Norm_Spf dst==oracle / 3-seed 扰动B TSV_Spf&Norm_Vcap dst==oracle。
