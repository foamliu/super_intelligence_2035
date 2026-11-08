# Deepread: bqszj — Cosine Wave Analyze (WaveView Tcl)

## Trace
- session: 1793842177177_bqszj
- user: e0023936
- host: hfhds201
- mtime: 2026-11-05 09:52
- msgs: 54
- spice keyword count: 26
- domain: characterization (waveform analysis)

## User task turn (A-faithful, U#0 = MSG#0)
> 使用tcl代码，帮我画一个余弦波并计算过零点、估算频率与峰值。

- 提出需求 (requirement, no root cause/fix) → A-faithful ✓
- U#17 = retry of same prompt (identical)
- U#48 = separate task (askeda virtuoso lookup, NOT part of this case)

## Gold standard (assistant MSG#42, editor tool_use)
File: `/home/e0023936/tcl_code/analyze_cosine.tcl`
Proc: `analyze_cosine {args}` with optional -freq/-amp/-np/-pts/-name

### Algorithm
1. **Generate cosine wave**: `v = amp * cos(2*pi*freq*t)`, t from 0 to nper*period, total=nper*pts points
2. **Build wave object**: `sx_add_wave $sname analog 1` + `sx_append_real $wobj $t $v` per point
3. **Plot**: `sx_new_wv` + `sx_display_wave $wv $wobj`
4. **Zero crossings**: count sign changes `(prevY<0 && yv>=0) || (prevY>=0 && yv<0)` → zc
5. **Frequency estimate**: collect rising zero-crossings (neg→pos), avg spacing → freqEst = avg(1/dT)
6. **Peak estimate**: max |yv| across all points → peak, peak_time
7. **Return**: `dict create peak $peak peak_time $peakT zero_crossings $zc frequency $freqEst period [expr {1.0/$freqEst}]`

### Verification (MSG#45)
- freq=1.0e9, amp=1.0, np=5, pts=400 → zc=10, freq≈1.0e9, peak=1.0 ✓

## Case design
- **A (visible)**: prompt = user's original words; task_brief = ≤3 lines delivery interface
- **Hidden B**: freq=2.5e9, amp=0.7, np=8, pts=500 → expected zc=16, freq≈2.5e9, peak≈0.7
- **check.py**: extract .tcl from zip → create WaveView API stubs → run tclsh with B params → verify 14 conditions
- **Stubs**: sx_add_wave/sx_append_real/sx_new_wv/sx_display_wave/sx_release as no-ops (computation logic runs in standard tclsh)
- **Negatives**: empty_shell, print_expected_B, core_deleted (no zero-crossing), naive_hardcode_A

## 14 断言 (a-n)
① zip 含且仅含 1 个 .tcl 文件
② .tcl 定义了 proc (含 analyze_cosine 或等价命名)
③ .tcl 使用 sx_add_wave (波形创建 API)
④ .tcl 使用 sx_append_real (数据点追加 API)
⑤ .tcl 含过零点检测逻辑 (符号翻转/prevY/crossing)
⑥ .tcl 含频率估算逻辑 (1.0/ 或 period 或 freqEst)
⑦ .tcl 含峰值估算逻辑 (abs( 或 max 或 peak)
⑧ .tcl 返回结构化结果 (dict create 或 return $result)
⑨ tclsh 运行 exit 0 (语法正确、stub 兼容)
⑩ B 参数下 zero_crossings == 2*np (16)
⑪ B 参数下 frequency ≈ freq (2.5e9 ±5%)
⑫ B 参数下 peak ≈ amp (0.7 ±5%)
⑬ 无 A 特定硬编码值 (1.0e9/1.0/np=5/pts=400 不在计算路径中作字面量)
⑭ 3 次幂等 (sha256 输出一致)
