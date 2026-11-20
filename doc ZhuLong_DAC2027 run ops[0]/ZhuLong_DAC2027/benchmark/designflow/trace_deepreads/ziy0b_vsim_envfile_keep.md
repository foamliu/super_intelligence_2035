# 深读笔记：1793260738350_ziy0b — xuebaok @ hfhds201 — vsim env-file keep

## trace 元数据
- user: xuebaok · host: hfhds201 (10.129.32.75, .75 local) · session: 1793260738350_ziy0b.messages.json
- size: 315KB · msgs: 55 · tools_total: 26 (read_files×11, editor×8, run_approved_command×3, run_commands×1, search_codebase×1, list_allowed_files×1, get_agent_policy_status×1)
- spice_tools: {} (vsim 是 Verilog 仿真包装脚本，非 spice 工具；domain 归 characterization/sim-infra)
- mtime: 1793263395 (11-07 10:23)

## USER 轮（verbatim）
- **USER#0** (ts=1793260738853): `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/bin/vsim使用这个脚本跑仿真，一些文件用完会被删掉，帮我修改脚本不要删除必要的环境文件`
- **USER#1** (ts=1793261687506): `rmpatternsfile在这个函数内添加，将删除的文件的绝对路径放在一个文件夹内`
- **USER#2** (ts=1793263388971): `Could not checkout Verdi license命令行输入verdi提示没有license，帮我解决`（无关 side-task，不入 prompt）

## A-档 CLEAN 判定
- USER#0 = 纯需求轮（给目标：改 vsim 脚本保留必要 env 文件），未给根因/修复 ✓
- USER#1 = 需求细化（指明在 rmpatternsfile 函数内 + 把删除文件绝对路径存到文件夹），是 REQUIREMENT REFINEMENT 而非 root-cause/fix-plan；可入 task说明 ✓
- USER#2 = 无关 side-task（verdi license），不入 prompt ✓

## trace assistant 工具链 / 产物
1. **msg 1-19**: read_files 多段读 `/proj/dscqa/.../bin/vsim`（1734 行 Perl 脚本，分段 1-50/55-200/200-400/400-800/800-1195/1195-1450/1450-1734）+ search_codebase 找 rmpatternsfile/rmlnfile 定义
2. **msg 21**: editor 直接改 vsim — 注释 runsim 中 `&rmlnfile;` + `&rmpatternsfile;` 调用（OLD→NEW：`&rmlnfile;`→`# &rmlnfile;  # MODIFIED: keep env files`，同理 rmpatternsfile）
3. **msg 23-25**: get_agent_policy_status + list_allowed_files（policy 受限，转写独立脚本）
4. **msg 29-49**: editor 写 `/home/xuebaok/modify_vsim.py` — 系统化 Python 修改器，多 Fix 增量构建：
   - Fix 1: runsim queue path — skip rmlnfile/rmpatternsfile
   - Fix 3: runsim regression — keep A_Pattern_Sim.v（`rm -Rf + touch` → `if(-e){}else{touch}`）
   - Fix 8: B_Pattern_tasks.v dedup loop — 条件 rm（不盲删）
   - 还有 rmworklib 保 .sdf、genrunfile 保 .fsdb、runsim 保 Pattern_tasks.v 等
5. **msg 51**: run_approved_command 跑 modify_vsim.py 验证

## 原 vsim 结构（关键，用于同构重建 asset A）
- `sub rmlnfile { unlink "libs","libsdb"; system("find . -name '*.sv' -type l -delete"); }` — 删 libs/libsdb + .sv 符号链接
- `sub rmpatternsfile { rmtree "patterns"; rmtree "Regressions"; rmtree "Project"; }` — 删 patterns/Regressions/Project 目录
- `sub rmworklib { rmtree "xcelium.d"; rmtree "INCA_libs"; }`
- `sub genrunfile { 写 verilogrun; chmod }`
- `sub runsim { queue: bsub + ./verilogrun + grep log + &rmlnfile; &rmpatternsfile; + rmworklib + rm jobname; local: ./verilogrun + &rmlnfile; &rmpatternsfile; + rm A_Pattern_Sim.v + touch + rm jobname }`
- `sub dedup_bpattern { grep -v + rm B_Pattern_tasks.v + mv tmp }`
- main: `&runsim($ARGV[0] || "queue")`

## case 合成决策
- 交付 = 通用 `modify_vsim.py <input.pl> <output.pl> <save_dir>`（不依赖真实 vsim 路径，便携 Python 解析）
- A = vsim_A.pl（同构重建，~80 行，保留真实函数名 + 结构 + env 文件名）
- hidden B = vsim_B.pl（不同 env 名：test_patterns/Runs/Build + C_Pattern_Sim.v + D_Pattern_tasks.v + .vhd 链 + 不同 jobname/simlib + msiebuildusr=1）A≠B
- reference = modify_vsim_ref.py（通用 regex 解析，不硬编码目录名 → cross-input guard）
- check = k=10 断言 a-j（含 cross-input guard ⑩）
- negatives: empty / print_expected（不改脚本只写假 manifest）/ core_deleted（只禁 rmlnfile，rmpatternsfile 仍 rmtree + 空 manifest）

## 自验结果
- REF self-test: PASS（k=10 全过）
- 3 negatives: 全 FAIL（empty→[c], print_expected→[e], core_deleted→[f]）
- §4.9 trio: 全 FAIL
- 断言闸门: k_rationale==k_check==10≥8 ✓
- jsonl roundtrip ✓
