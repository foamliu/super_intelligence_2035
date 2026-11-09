# 深读 · 9dytw (e0039602 @ hfeg0plg103, mc=446) — stdcell 转换结果按状态分区

## trace 概况
- session: 1793755896858_9dytw, 426 msgs, 11 user turns, 211 tool uses (editor 79 / run_approved_command 63 / read_files 44)
- 用户: e0039602（同 j26fe，stdcell 网表→SV 转换工具 verilog_lib_trans 项目，不同 session）
- 域: schematic_netlist（stdcell 网表→SV 转换 + tbfamily skill 验证 + 状态分区）

## 用户轮意图流
1. 「根据 outputs 里 result_map_20261103_194521_fc43.txt（run.py --netlist final_merged_netlist_stdcells_ac.v --block-list block_name_stdcell_ac.log --workers 8 生成），用 tbfamily skill 检查并重写错误的」→ 提出需求（A-grade seed）
2. 「现在什么情况，你还能继续工作吗」→ 状态确认
3. 「final 文件里只有 879 个转换，没有那错误的 4 个对吗」→ 确认
4. 「生成新 final 文件，把四个无法验证的去掉」→ 去除 NODUT
5. 「运行过程产生很多仿真文件，给 skill 加定期清除功能」→ skill 增强
6. 「查看确认 AIout1104.sv 当中是不是本次生成的 879 个正确 model」→ 验证
7. 「AIout1104 的 879 挑任意 100 个用 TB 再跑一遍，任意挑选不要只选前 100」→ 随机抽样回归
8. 「测测之前没通过、经 skill 改写才通过的那几十个在 AIout1104 里对不对」→ 改写项回归
9. **「把一次生成就正确的和改过之后才正确的分开成两个文件，一次生成就正确的存 AIout1104_true.sv，改过才对的 36 个存 AIout1104_retrue.sv」** ← 本 case 选题
10. 「这 36 个文件重写之后有通过 TB 测试吗」
11. 「/home/wellesc/runStdCellTB/tb_family 确定和我目录下一样吗」→ 工具一致性

## 选题 (User#9) 分析
- 意图类型: 提出需求（分区成两文件 + 命名），用户未给根因/算法 → 合格 A-grade seed
- 但依赖私有: AIout1104.sv（用户机器产物）、result_map（run.py+tbfamily skill 产物，私有工具链）、tbfamily skill 本身 → 不可在沙盒复刻 → **B-grade synthesized 自包含**
- 收敛状态（trace 末尾 agent 自述）: 879 PASS + 4 NODUT = 883；36 个经 skill 改写后才 PASS

## result_map 格式（trace 真实，MSG#91）
```
[check] total=7 done=0 todo=7 unmapped=0
[done] and2DSx1                 PASS     miss=0
[done] xor2DSx1                 FAIL     miss=4
[nodut] passgtLVSx1             NODUT
[check] summary: {'PASS': 7}
```
- `[done] <cell> PASS/FAIL miss=N`：转换后 TB 检查结果
- `[nodut] <cell> NODUT`：无 DUT/库重定义冲突，不可验证
- summary dict 汇总各类计数

## 分类口径（本 case）
- one_shot_correct: initial=PASS ∧ final=PASS
- rewritten: initial=FAIL ∧ final=PASS（skill 改写后通过）
- dropped: NODUT（initial 或 final）∨ final 仍 FAIL → 不进任一输出文件
- SV 文件只含已转换 module（PASS+rewritten），不含 NODUT

## 合成设计 (B-grade)
- A（SUT 可见）: AIout1104_A.sv (20 module) + result_map_initial_A.txt + result_map_final_A.txt + task_brief + prompt
- 隐藏 B: AIout1104_B.sv (23 module, 不同族/计数) + 两 result_map_B
- 交付: partition_and_audit.py，CLI `<sv> <map_initial> <map_final> <out_dir>`，产 true.sv / retrue.sv / audit.json
- 判分: 子进程真跑 B + 12 条独立条件 + 反硬编码(跑 A 也正确) + 3-seed 行序稳定
- 与 j26fe(#457 StdcellRerunCollect) 区别: j26fe=收集错误+rerun脚本；本 case=按状态分区成 true/retrue + 审计完整性，交付与判分完全不同
