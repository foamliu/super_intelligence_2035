# Deepread: 1789635000404_9568y (junxu@hfeg0pkn004, mc=91, waveform, 327 msgs / 1.08MB)

## 真实意图（用户原话）
> /wv-cli skill 中的相对路径按照文件本身路径来解析
> /proj/train/iejoad_test/workdir/junxu/simulation/fifo_3x8 是 fifo_3x8 的仿真目录，检查一下波形，这个电路功能正不正常

两条任务合一轮：
1. 修 wv-cli skill 的相对路径解析（相对脚本自身目录，而非 CWD）
2. 用 wv-cli 检查 fifo_3x8 仿真波形，判定电路功能是否正常（5 个 PVT corner）

## 电路
3 级 FIFO 移位寄存器，8 位数据宽度。
- 信号：RSTN, CLK, SHIFT, DIN<7:0>, DOUT<7:0>, EMPTY, FULL, s0q<7:0>, s1q<7:0>, cnt0, cnt1
- CLK：5ns 周期（200MHz），首个上升沿 10ns
- RSTN：0-5ns 低，之后高
- 5 个 PVT corner：TT_25c_0.9v / SS_-40c_0.88v / SS_130c_0.88v / FF_130c_1.15v / FF_-40c_1.15v
- FSDB：raw/finesim.fsdb(+#1..#4)

## agent 工具链
- read_files 读 wv-cli.py / SKILL.md / wv_socket_server.tcl
- editor 改 4 处：SESSION_FILE→SCRIPT_DIR join / cmd_start cwd=SCRIPT_DIR / wrapper_name=全路径 / cmd_stop cwd=SCRIPT_DIR
- run_commands 语法校验（env -u PYTHONHOME /usr/bin/python3 py_compile）
- skills 调 sim-view skill
- run_commands: wv-cli start --fsdb ×5 --timeout 120（LSF bsub 提交 WaveView TCP server）
- 中途发现 LSF -o 输出非实时 → 改 status_file 轮询机制（又改 wv-cli.py）
- wv-cli exec 'SWITCH <n>' 切 corner + exec -f /tmp/analyze_c0.tcl 查信号
  - analyze_c0.tcl: sx_signal 取句柄 + foreach t {..} { sx_get_real_at_x } 拼接结果
- 发现并发连接报 "Server is busy" → 改顺序 SWITCH 再 exec
- cat > /tmp/build_session.tcl 建 WaveView session 文件（sx_add_wv/sx_append_panel/sx_append_line）
- wv-cli stop 释放 license + 清理
- git commit

## 5 corner 分析结论（agent）
| corner | VDD | DOUT0 上升沿 | 计数器 | 判定 | failure_mode |
|---|---|---|---|---|---|
| TT_25c_0.9v | 0.9V | 3rd edge(~20.5ns) ✓ | 边沿触发 0→1→2→3 ✓ | PASS | — |
| SS_-40c_0.88v | 0.88V | 正常上升 | 正常 | FAIL | DOUT0/S0Q0/S1Q0 始终 ~0.88V，1→0 转换 50ns 内未完成（stuck_high / fall_transition_timeout） |
| SS_130c_0.88v | 0.88V | 3rd edge ✓ | 边沿触发 ✓ | PASS | — |
| FF_130c_1.15v | 1.15V | 2nd edge(~15.5ns) ✗ 太早 | CNT0 跟 CLK 电平变（level-triggered）✗ | FAIL | early_rise（hold violation）+ counter_level_triggered |
| FF_-40c_1.15v | 1.15V | 3rd edge ✓ | 边沿触发 ✓ | PASS | — |

## 沙箱障碍
- WaveView 需要 live license + LSF bsub 提交 → 离线判分不可行
- 句柄不跨 SWITCH 持久 → 每次切 corner 后重新 sx_signal
- LSF -o 输出非实时 → agent 自行改 status_file 轮询

## 抽纯 Python 内核（r1092 范式）
agent 真正的"分析"逻辑 = 拿到每个 corner 的「时间→各信号电压」采样表后：
1. 检测 CLK 上升沿
2. 判计数器是否边沿触发（CLK 低电平期 CNT0 是否稳定）
3. 判 DOUT0 上升时机（应在第 n_stages 个上升沿后，n_stages=3 → 第3沿 ~20ns）
4. 判 1→0 转换是否在仿真窗内完成（DIN 拉低后 DOUT0 是否最终拉低）
5. 判级联传播顺序（S0Q0 先于 S1Q0 先于 DOUT0 上升）
→ 输出每 corner {verdict, failure_modes, evidence}

这层逻辑与 WaveView/LSF/license 无关，可纯 Python 离线判分。

## case 设计：EDA-Eval-DesignFlow-FifoPvtCornerAudit-001
- domain: waveform, L1
- 内核 = fifo_corner_audit.py：解析 WaveView sx_export_data 风格信号采样表（ASCII），逐 corner 分类 PASS/FAIL + failure_mode
- A（给 SUT）：5 corner × 3-stage FIFO（信号 clk/rstn/shift/din0/dout0/s0q0/s1q0/cnt0/cnt1/empty/full）
  - TT=PASS / SS_cold=FAIL(stuck_high) / SS_hot=PASS / FF_hot=FAIL(early_rise+level_triggered) / FF_cold=PASS
- B1（hidden）：6 corner × **4-stage** FIFO（信号多一级 s2q0，n_stages 从 metadata 读，不能硬编码3）
  - 失败模式分布 ≠ A：stuck_high / early_rise / stage_propagation_broken
- B2（hidden）：5 corner × 3-stage FIFO，不同 CLK 网格（period=4ns, first_edge=8ns）
  - 失败模式分布 ≠ A ≠ B1：stuck_low / early_rise
- A/B1/B2 结构性不相交（corner 名/数量/n_stages/CLK 网格/信号集/失败分布全不同）
- k_check=15（①zip含脚本 ②B1 exit0+JSON ③B1 corner集合 ④B1 verdict集合 ⑤B1 TT=PASS/SS_cold=FAIL(stuck_high) ⑥B1 FF_hot=FAIL(early_rise) ⑦B1 TT_lowv=FAIL(stage_propagation) ⑧B2 corner集合≠B1 ⑨B2 verdict分布≠B1 ⑩B2 SS_a=FAIL(stuck_low) ⑪B1≠B2 ⑫反硬编码A(B1≠A) ⑬确定性md5 ⑭随机化打乱corner序3种子 ⑮n_stages泛化(B1=4≠A=3)）
