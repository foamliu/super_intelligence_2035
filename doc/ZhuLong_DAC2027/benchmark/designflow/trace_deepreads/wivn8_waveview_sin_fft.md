# trace_deepreads/wivn8_waveview_sin_fft.md — shard D r1032

## session
- session_file: `1794296365532_wivn8.messages.json`
- user: t0002441 ; host: hfhds201 (10.129.32.75, .75 本机) ; match_count: 174
- keywords: `waveview:461;analog:100;mixed-signal:8;binary:4;synopsys:3;rtl:3;`
- domain (shard D): waveform
- 244 msgs, 1.0 MB ; ts 2026-11-08 14:39 → 2026-11-11 13:49

## ledger history
- 2026-11-14 06:06 parked (旧规则) — note: "waveview GUI trivial (draw sin/fourier)"
- 2026-11-21 r1032 revived → claimed → case (11-15 reaudit: 旧 weak/analysis-only 判定
  全部恢复可造；waveform sin+FFT 是真实用户意图)

## user intent flow (verbatim, U# = user turn index)
- **U#1 (idx0)**: `帮我在wv中画一个sin函数` — pure need, draw sin in WaveView
- **U#2 (idx21)**: `给他做fuliye变换  给我频谱图` — pure need, FFT + spectrum  ← A-faithful 选轮
- U#3 (idx34): `你直接在我的wv界面显示最终结果`
- U#4 (idx40): `我看显示有三行最上面一行user的是什么意思`
- U#5 (idx44): `为什么三行显示的结果不一样`
- U#6 (idx46): `只保留频谱面板`
- U#7 (idx61): `给我做一个矩形波` — pure need, square wave
- U#8 (idx65): `我在waveview界面没有看到`
- U#9 (idx71): `为什么矩形波我只看到一个竖线`
- U#10 (idx79): `帮我完成一个比较复杂的waveview的任务  我想给别人展示效果`
- U#11 (idx91): `为什么第一行和第二行有两个竖线`
- U#12 (idx95): `你实现了什么功能`

## assistant tool chain (real WaveView ACE Tcl)
- RAG_MCP_Server__search_apis / get_api_details: 查 sx_create_signal / sx_append_data /
  sx_display / sx_wf_fft / sx_add_param 等 Tcl API
- SandBox_MCP_Server__run_code: 实跑 Tcl 验证
- 关键 proc:
  - `wv_plot_sin {sig_name amp npoints cycles}` — sx_create_signal analog +
    sx_append_data 逐点 + sx_display
  - `wv_fft_spectrum {sig_name freq amp cycles npoints}` — 生成 sin → sx_wf_fft
    no_of_harm/win_type/start_x/end_x → 频谱峰值定位
- 最终用户接受结果：sin 波形面板 + FFT 频谱面板在 WaveView 显示，峰值在 ~0.9-1MHz

## 为什么不可直接沙盒（synthesized-reframe 理由）
- WaveView `wv` 二进制（Synopsys 商业工具）不可在 SUT 沙盒安装
- NoMachine X display + SNPSLMD license server 网络依赖
- sx_* Tcl API 只在 live WaveView ACE 解释器内可用
- ⇒ 把「生成信号 + FFT 频谱」物化为独立 stdlib Python 信号生成+FFT 分析器

## A-faithful 选轮判定
- U#2 `给他做fuliye变换  给我频谱图` = 纯需求轮（用户提目标「FFT 频谱」，
  未给根因/未给修复方案），符合 A 档选轮规则
- U#2 隐含 U#1 的 sin 波形作为输入信号 ⇒ 交付物需含信号生成 + FFT 两步

## case 物化
- case_id: `EDA-Eval-DesignFlow-WaveviewSinFftSpectrumProduce-001`
- 交付: `signal_fft_analyzer.py --config <cfg.json> [-o out.json]`
  - 读 signal_type(sin|square)/amp/freq/npoints/cycles
  - 生成时域采样（duration=cycles/freq, fs=N*freq/cycles）
  - 单边实 DFT (stdlib cmath, O(N²)) → magnitudes + freq_bins
  - JSON: {signal_type, params, fs, time_samples, spectrum{freq_bins,magnitudes}, peak{bin_index,freq,magnitude}, dc_component}
- A config: sin, amp=1.0, freq=1e6, npoints=256, cycles=10 (peak mag=128=amp·N/2)
- B config (hidden, token 完全不相交): square, amp=1.5, freq=2e6, npoints=512, cycles=8
  (peak mag≈489=(4A/π)·N/2, 3rd 谐波≈163=peak/3, 2nd 谐波≈0, DC≈0)
- check.py 17 断言 a-q, k_check=k_rationale=17>=8 GATE PASS ✓
  - 独立 _gt_samples/_gt_dft_mag 重算（stdlib O(N²) 与 candidate 不同实现互验, 强 anti-echo）
  - 反硬编码 = 值基（B time_samples 必须是 ±1.5 方波, 非 A 的 ±1.0 正弦）,
    非子串匹配（FFT freq_bin 值会巧合含 A 参数数字, 如 4·250000=1000000）
  - 3-seed md5 确定性
  - A 金标准对账（peak 1e6/mag128/ts 公式）

## 自验
- ref 17/17 PASS on B + A gold 对账 ✓
- 3 neg (empty_stub → FAIL b/d ; print_expected → FAIL f/g/i/k/l/o 9 条 ;
  core_deleted → FAIL l/n/k 4 条) 全 FAIL ✓
- §4.9 a/b/c 三假全 FAIL ✓
