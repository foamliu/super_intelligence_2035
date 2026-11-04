# =============================================================================
# cfreq_ctrl.sdc : 综合时序约束 (Synopsys Design Constraints)
# 时钟: REFCLK(25MHz 参考) / FBCLK(VCO 反馈 ~25MHz, 与 REFCLK 异步)
# 复位: RST_N 低有效异步复位 (各时钟域同步释放)
# =============================================================================

# ------------------------------------------------------------------
# 1. 时钟定义
# ------------------------------------------------------------------
create_clock -name REFCLK -period 40.0 -waveform {0 20.0} [get_ports {REFCLK}]
create_clock -name FBCLK  -period 40.0 -waveform {0 20.0} [get_ports {FBCLK}]

# ------------------------------------------------------------------
# 2. 时钟分组: 两个异步时钟域
# ------------------------------------------------------------------
set_clock_groups -asynchronous \
    -group [get_clocks {REFCLK}] \
    -group [get_clocks {FBCLK}]

# ------------------------------------------------------------------
# 3. 异步复位 false path
# ------------------------------------------------------------------
set_false_path -from [get_ports {RST_N}]

# ------------------------------------------------------------------
# 4. 输入延迟 (相对 REFCLK 域的同步输入)
# ------------------------------------------------------------------
set_input_delay  -clock REFCLK -max 2.0 [get_ports {LOOP_BREAK}]
set_input_delay  -clock REFCLK -min 0.5 [get_ports {LOOP_BREAK}]
set_input_delay  -clock REFCLK -max 2.0 [get_ports {WINDOW_LEN[*]}]
set_input_delay  -clock REFCLK -min 0.5 [get_ports {WINDOW_LEN[*]}]
set_input_delay  -clock REFCLK -max 2.0 [get_ports {THRESHOLD[*]}]
set_input_delay  -clock REFCLK -min 0.5 [get_ports {THRESHOLD[*]}]

# ------------------------------------------------------------------
# 5. 输出延迟 (RDY / CAP_CTRL_OUT 均属 REFCLK 域)
# ------------------------------------------------------------------
set_output_delay -clock REFCLK -max 2.0 [get_ports {RDY CAP_CTRL_OUT[*]}]
set_output_delay -clock REFCLK -min 0.5 [get_ports {RDY CAP_CTRL_OUT[*]}]

# ------------------------------------------------------------------
# 6. 负载 (示例)
# ------------------------------------------------------------------
set_load 0.05 [all_outputs]