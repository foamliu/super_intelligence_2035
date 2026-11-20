# Task brief — WaveView-002 (restored image form)

交付：`outputs/submit.zip`，内含**一个** `wv_report.json`（UTF-8 JSON）。
报告 schema：`{"signals":[{name,type,n_transitions,function,period_ns,duty,vmin,vmax,n_pulses,n_levels}, ...]}`，对图中 5 个信号逐个填写（不适用的字段填 null）。
`type`∈{logic,analog}；`function` 从该信号对应集合中选一个：clk∈{clock,clk,clock_signal} / rst_n∈{reset,active_low_reset,reset_n,resetb} / data∈{data_bus,data,bus,data_signal} / vref∈{reference_ramp,analog_ramp,ramp,reference_voltage,vref} / sel∈{selector,select,enable,selector_enable,chip_select}。
答案必须从图 `wv_sigs_A.png` 读出；不要尝试用脚本解析图中的原始数据。判分器在独立目录校验报告数值（容差允许读图误差），隐藏 B 图不进沙盒。
