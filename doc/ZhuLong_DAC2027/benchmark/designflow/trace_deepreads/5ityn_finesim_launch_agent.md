# 深读笔记 · 5ityn (zjqiao / hfhds206 / mc404)

**session**: 1794474782925_5ityn · **user**: zjqiao · **host**: hfhds206 · **match_count**: 404
**domain**: spice_sim · **archetype**: finesim simulation launch orchestration (GUI→CLI agent)
**case**: EDA-Eval-DesignFlow-FinesimLaunchAgent-001 (L2 portable, k=17)

## 用户意图（msg[0] 原话）
> 这个代码是我进行 finesim 仿真的代码，现在我希望你能创建一个 agent，在用户说明激励文件和网表文件以后，你看可以启动该程序，将激励文件填入激励文件的位置，然后选择网表，再点击运行仿真，你可以做到吗

附件: stimulus_manager.py（DDR 仿真 Tkinter GUI，单文件 bundle 内嵌 8 模块: fields/main_window/vecgn/matrixrun 等，ASCII-only，__BUNDLE__ 里是 \u 转义的中文）。

## assistant 轨迹（584 msgs）
1. read_files stimulus_manager.py → search_codebase 找 _run_auto_all/_run_vecgn/_run_matrixrun/_build_matrixrun_cmd
2. 多次 editor/run_approved_command 尝试提取 bundle（GUI 文件 import 即起 Tk 失败，需 headless 提取）
3. 写 extract_bundle.py 到 uploads 目录，提取 8 模块源到 /tmp，读 main_window 理解仿真流程
4. 构建 CLI agent（extract_bundle.py 567 行）：load_config + build_matrixrun_cmd + run_simulation + interactive_prompt + main(argparse)
5. --dry-run 实测: `matrixrun -p dscqa -v V0 -f /tmp/test.saved -nr dn512x16 -nl netlist -i 8 -q test_queue -s primesim -Y 2025 -array -tdv -c test.ctl -wica` ✓

## 核心产物：build_matrixrun_cmd 逻辑
```
args = [matrixrun, -p project, -v version, -f stimfile, -nr basename(netfile), -nl "netlist",
        -i sim_cpu, -q queue, -s sim_simulator]
if simver: args += [-Y simver]
if opt_d: args += [-D]
if opt_append: args += [-a opt_append]
if opt_r: args += [-r opt_r]
if opt_array: args += [-array]
if opt_tdv: args += [-tdv]
if opt_noary: args += [-noary]
if opt_nobnk: args += [-nobnk]
if opt_cck: args += [-cck]
args += [-c control, -wica]
```
config.json 字段: project/version/stim_file/netlist_file/queue/control/matrixrun/sim_cpu/sim_simulator/sim_simver/opt_d/opt_array/opt_tdv/opt_noary/opt_nobnk/opt_cck/opt_append/opt_r

## case 化决策
- A 档 trace-faithful：用真实用户原话 + 真实 config.json(drvqa) 作可见输入
- 便携 L2：纯 Python 标准库，无需 EDA license；判分靠 --dry-run 解析命令结构（非真跑 finesim）
- 隐藏 B: dscqa V2 / finesim / 8cpu / opt_d+opt_noary+opt_nobnk+opt_append+opt_r（与 A 结构同构取值全异）
- cross-input guard: A 重跑得 drvqa/primesim/16/-array/-tdv（A≠B 非写死）
- k=17 断言(a-q): zip含py / py_compile / dry-run出命令 / -p/-v/-f/-nr/-nl/-i/-q/-s/-Y / -D在-array/-tdv缺席 / -a/-r / -noary/-nobnk在-cck缺席 / -c/-wica / cross-input guard
- 自验: REF 17/17 PASS ✓ + 3 negative(空壳/print-B/hardcode-A)全 FAIL ✓ + §4.9 (a)(b)(c) 三假全 FAIL ✓
