# Deep-read: fux29 (e0029308 / hfeg0pkn001 / mc212)

session_file: 1792487428780_fux29.messages.json
domain: schematic_netlist (Verilog functional 拆分 for AMS)
track: A-faithful
case: EDA-Eval-DesignFlow-VfunctionalSplit-001

## 会话主线
用户 e0029308 在 /proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/ 下做 STD_T_DBC_BASE 的 AMS 仿真批量准备。383 msgs / 25 user turns。主线演进：
- U#1-4: 问 finesim/AMS 网表、能否用 Maestro/finesim 跑混合仿真
- U#5: 提需求——批量跑 AMS 仿真，ADE 没法批量改网表，几百个 Cell 太慢，需要 Terminal 指令仿真方法
- U#6: 选 OCEAN 方案，要模板文档(标注 ADE 对应设置 + 流程 + 环境配置)
- U#7-9: 输出路径约定 /proj/lacaa/.../BK/AI/；问 Verilog 文件位置、是否要 Virtuoso 逐个建
- **U#10 (msg 156): 提需求——「我现在只有现成所有Cell放在一起的.V，没有一个一个Cell的functional文件，能帮我写个脚本批量生成AMS仿真需要的functional文件吗」** ← A-faithful 任务说明（逐字原文）
- U#11-19: 回到 AMS 主线；OCEAN 跑不通 → 转一键仿真脚本；登录机讨论
- U#20-25: 仿真失败排查 / 波形路径

## gold 重建（U#10 的 agent 产物）
agent 在 msg 157-191 用 editor 分块写 `/home/e0029308/split_verilog_to_functional.py`（因 new_text>6000 限制分多次 insert）。msg 179 做了 3 处去重修复（重复 import / 重复 collect_vfiles 尾段 / 重复 run_importer 尾段）。msg 193 收尾「脚本已生成在 /home/e0029308/split_verilog_to_functional.py，含 --mode import/files/dry」。脚本磁盘已删（cat NOFILE），从 editor new_text 逐块重建。

### 核心逻辑（faithful 复刻 → reference/gen_functional_split.py）
1. `strip_comments(s)`: 字符级扫描，`/* */` 整块跳到 `*/`，`//` 跳到行尾 → 避免注释里的 `module/endmodule` 误判
2. `MOD_START = ^\s*module\s+([A-Za-z0-9_]+)`，`MOD_END = ^\s*endmodule`
3. `split_modules(text)`: 先 strip_comments，再逐行状态机，depth 计数处理嵌套 `module` 关键字行，`endmodule` 使 depth-1，depth==0 时产出 (name, src+'\n')
4. `collect_vfiles`: --file / --dir 收集 .v/.sv，去重
5. `write_functional_files(dest, mods)`: 写 `<dest>/<CELL>/functional/verilog.v`
6. `run_importer`: --mode import 调 ncimport/xrun -import（评测不测此模式，无 Cadence 环境）
7. `main`: argparse → 读 vfile → split → dedup by name (last wins) → sorted → write + out_list

## 评测化设计（A-faithful, L1-boundary, schematic_netlist）
- 资产 A (SUT 可见): combined_A.v(5 module: AIOI21/ND2D0/INVX1/MB2SDFQ/cxmt_buf，含 /* */ 注释陷阱 `module fake_should_not_split` + `// module` 行注释) + config.json(vfile/dest/mode/out_list) + prompt.txt(U#10 逐字) + task_brief.md(交付接口≤3行)
- 隐藏 B (check 跑): combined_B.v(7 distinct module: AOI211/ND3D1/INVX2/OAI21/DFFRX1/cxmt_inv/XNOR2，XNOR2 重复定义测 dedup-last-wins，INVX2 内 /* */ 含 `module phantom` 测 strip) + config.json(dest=out_lib_B, out_list=module_list_B.txt)
- 交付件: gen_functional_split.py 打包 outputs/submit.zip
- check.py 15 条件 a-o: zip含gen / py_compile / 跑B退0建dest / 7 cell 各一 verilog.v / cell数==7 / module开头endmodule结尾 / 无注释残留 / 注释陷阱不分裂 / XNOR2 last-wins / 模块体保留 / 每 file 1 module+1 endmodule / out_list 7 排序名 / 跨输入护栏(A token不泄漏+B token齐) / 3跑 sha256 一致 / strip 后 INVX2 体完整
- ref PASS 15/15 · 4 negatives ALL-FAIL distinct{fake_empty→c / fake_print_fixed_A→d / core_deleted→f / naive_no_strip→g} · §4.9 三假(c/d/f) 3-distinct ✓ · test==disk EXACT(sha 9e103aebd362) · k_rationale=k_check=15 ✓

## 教训
- D 域 68 条交付后 clean single-deliverable 候选仍可挖：fux29 靠 AMS 仿真准备的 Verilog 拆分子任务(U#10)落 L1-boundary；高 mc(212) 会话的多轮里常有独立可截取的提需求轮
- peek 首轮用户文本多为 meta/analysis/根因；需 dump 多轮(U#1-15)才找到 clean 提需求轮(U#10)
- agent editor 因 new_text>6000 分块写 + 并行 edit 留下重复段(msg 179 修 3 处)——重建 gold 须以最终去重态为准
- 698 台 cline session 路径 = `<anchor>/<anchor>.messages.json` 目录级；fux29 在 hfeg0pkn001 的 e0029308 home 下找到（hfeg0plg77/49 对 chentong 的 97mj2 NOFILE，说明 session 实际只在某一台——选 host 须以 summary.tsv 记录的为准，但同一 session_file 多机复用时取首个可达）
