# Deepread: qb1ua — FM 瞬时频率 WaveView ACE Tcl 脚本

## Trace
- **session**: 1793095651315_qb1ua.messages.json
- **user/host**: e0023936 @ hfhds201 (mc=103)
- **size**: 421KB / 123 msgs
- **domain**: waveform (WaveView Tcl ACE)

## User turns
- **U#0 (提出需求轮)**: "编写一个 Tcl ACE 脚本，计算一个 FM 信号的瞬时频率随时间变化曲线...6 步要求: proc f_vs_t(sig,v_thr) / sx_create_signal "frequency" analog / RISE 扫描+阈值 / 1/(t2-t1) / append_data / main 打开 ./wave.dat 取 wave 调 f_vs_t" → **干净 A-faithful 提出需求轮 ✓**
- U#55: "为什么这个打不开./wave.dat" → 根因轮 (file not found), agent 加 open_wave_file 健壮化
- U#69: 重提需求 + 第7点 "结果文件单独保存在一个顶层项目中" → agent 加 sx_write_open/add_signal/close 存 frequency_result.wdf
- U#83: "帮我执行...查看结果" → agent 用合成 FM 信号跑通
- U#87: 粘贴另一版 f_vs_t.tcl (英文) → agent 执行验证
- U#97: "帮我找一个 wave.dat copy过来"
- U#102: "你自己创建一个 ./wave.dat" → agent 用 sx_open_sim_file_write + sx_save_signal 生成 wave.dat (58972B, FM 2-5Hz, 5001 pts)
- U#112: "我在waveview上看不到你结果？帮我加载出来" → agent sx_display_wave + sx_update_wv 显示

## Agent 工具链
1. RAG search_apis: sx_create_signal, sx_create_scan, sx_set_threshold, sx_scan_first/next, sx_fetch_x, sx_append_data, sx_new_wv, sx_display_wave, sx_open_sim_file_read, sx_find_wave_in_file, sx_write_open/add_signal/close
2. SandBox run_code: 探查 sx_ 命令签名 (351 个 sx_* 命令可用)
3. SandBox run_code: 合成 FM 信号验证 f_vs_t 逻辑 (freq 3.58166, 4.34405 at t=0.6665, 0.8967)
4. editor: 写 /home/e0023936/fm_freq_vs_t.tcl (113 行 4782B)
5. SandBox run_code: 生成 wave.dat (sx_open_sim_file_write + sx_save_signal)
6. SandBox run_code: sx_display_wave + sx_update_wv 显示结果

## Gold 产物
- **/home/e0031982/fm_freq_vs_t.tcl** (113 行, 4782B, ssh cat 全文可读):
  - proc f_vs_t {sig v_thr}: sx_create_signal "frequency" analog + sx_create_scan $sig RISE + sx_set_threshold $scan $v_thr + sx_scan_first + while {sx_scan_next} + sx_fetch_x + expr 1.0/($cur_t-$prev_t) + sx_append_data $freq $cur_t $f + sx_free_scan
  - proc open_wave_file: env WV_WAVE_FILE + ./wave.dat + pwd fallback
  - proc main: sx_new_wv + open_wave_file + sx_find_wave_in_file $fobj "wave" + set v_thr 1.65 + f_vs_t $wave $v_thr + sx_write_open "./frequency_result.wdf" + sx_write_add_signal + sx_write_close + sx_display_wave + sx_update_wv
- **/home/e0031982/devops/wave.dat** (58972B WDF, FM carrier 2-5Hz, Vmid=1.5, A=1.5, 5001 pts, signal "wave")

## WaveView sandbox 验证
- WaveView version: P-2019.06-SP2, DISPLAY=:142, cwd=/home/e0031982/eda_sandbox_flow/tcl_work
- 351 sx_* 命令可用, 全部关键 API (sx_create_signal/sx_create_scan/sx_set_threshold/sx_scan_first/next/sx_fetch_x/sx_append_data/sx_open_sim_file_read/sx_find_wave_in_file/sx_write_open/add_signal/close/sx_new_wv/sx_display_wave/sx_update_wv/sx_wave_to_list) 俱 HAS
- gold 脚本在 wave.dat_A 上跑通: FREQ x = 0.392292 0.670496 0.900058, FREQ y = 2.60033 3.59448 4.35613 (3 freq points, deterministic)

## 合成
- **A档 trace-faithful EDA-Eval-DesignFlow-FMFreqVsT-001** (L1-boundary waveform)
- gen_fmfreq.py 读 config.json 参数化打印 Tcl ACE 脚本
- 资产 A=config.json(wave_file=./wave.dat/signal_name=wave/v_thr=1.65/freq_signal_name=frequency/output=./frequency_result.wdf/scan=RISE)
- hidden B=config_B.json(wave_file=./wave_B.dat/signal_name=fm_sig_b/v_thr=2.0/freq_signal_name=inst_freq/output=./freq_B_result.wdf → 跨输入护栏)
- check.py 22 条件 a-v (zip+compile+跑B+proc f_vs_t 2args+create_signal inst_freq analog+create_scan RISE+set_threshold $v_thr+scan_first/next+fetch_x+公式 1/(t2-t1)+append_data+open wave_file+find_wave_in_file fm_sig_b+write_open/add_signal/close+new_wv/display_wave/update_wv+main+tclsh syntax+跨输入 A不泄漏+B出现+3seed确定性+v_thr=2.0+free_scan)
- ref=参数化 gen_fmfreq.py → 自验 ref PASS 22/22 · 4 negatives ALL-FAIL distinct{empty→c / print_fixed→r / core_deleted→j / naive_no_scan→f} · §4.9 三假(c/r/j) distinct ✓ · test==disk roundtrip EXACT(sha 0cbe6000) · k_rationale=k_check=22 ✓
