# Deepread: e5k8y — HCI Stress Window Extraction (waveform)

- **trace**: `1793254849618_e5k8y.messages.json` · yh1yang @ hfeg0pkn002 (10.129.2.11) · mc=53 · waveview:118
- **session**: 278 msgs, 8 real user turns, dir-based storage `/home/yh1yang/.cline/data/sessions/<sid>/<sid>.messages.json` (1.08MB)
- **workspace**: `/home/yh1yang/workspace/ai/` (src/analyze_hci.py 406 lines, data/wave 8118 lines Custom WaveView, docs/agent.txt prompt, output/hci_stress_windows.pdf, skill/hci-stress-skill.mdc)

## 真实任务流
- **U#1 (选题)**: "阅读提示词，计算wave文件7~10n的stress" — 用户让 agent 读 docs/agent.txt 提示词，运行 analyze_hci.py 切片 7~10ns 算 HCI 应力。agent read_files(agent.txt)+run_approved_command(python analyze_hci.py -f 7e-9 -t 10e-9)。结果：4078 数据点，Vdd=0.7997V，Vth=0.2666V，12 个应力窗口，t_eff/Vg_stress/Vd_stress。
- U#2: 把计算条件+表格输出到 PDF（plot_stress_windows GridSpec 升级）
- U#3-U#7: matplotlib 表格字体/布局修复（set_text_props fontsize 不生效 → 直接操作 Text 对象；最后发现是 GridSpec hspace 太小导致 plot 标题侵入表格）
- U#8: 整理代码+文档方便维护（agent 多次 editor 编辑把文件搞乱，反复重建，最终用 gen_script.py 生成器重写）

## 核心算法 (extract_hci_params) — 确定性、纯 Python 可复刻
Custom WaveView 表格格式（空格分隔）：
```
#format table ## [Custom WaveView] saved ...
TIME  v(ro1_mid<0>)  v(ro1_mid<8>)  v(out)
 0.000E+00  5.308E-14  5.308E-14  2.526E-14
```
信号映射 (NMOS HCI)：col1=Vgs(栅源), col2=Vds(漏源), col3=Vout(电源参考)

算法：
1. parse_wave_file: 跳过 `#`/`TIME` 头/空行，split 取 float(col[0..3]) → time, vgs, vds, vout
2. trim_to_range: mask = (time >= t_from) & (time <= t_to)
3. vdd = median(vout[vout > 0.5])  (高电平中位数)
4. vth = vdd / 3.0
5. above = (vgs > vth) & (vds > vth)  (布尔)
6. np.diff 检测上升/下降沿 → rising/falling 索引
   - 边界: above[0] True → rising 前插 0; above[-1] True → falling 后插 len-1
7. n_windows = min(len(rising), len(falling))
8. 每窗口 i: dt=t[fall]-t[rise], vg_peak=max(vgs[rise:fall+1]), vd_peak=max(vds[rise:fall+1])
9. t_eff=sum(dt), Vg_stress=max(vg_peak), Vd_stress=max(vd_peak)
10. 输出: 终端表格 + PDF (matplotlib, 可选)

## 选题判断
- **确定性子任务**: U#1 的 HCI 应力计算 = 纯算法（parse+trim+Vdd+Vth+窗口检测+峰值），无 EDA 工具依赖，纯 Python/numpy 可复刻，子进程可跑、可独立验算。
- **私有不可复刻**: 真实 data/wave (8118 行 RO 波形) + matplotlib PDF 布局 + skill 文件 → 不进 case。
- **B-grade synthesized**: 自包含 A/B wave 文件（合成 RO 风格波形，信号名/值/窗口数/时间窗全不同反硬编码）+ SUT 交付 hci_stress_calc.py(--wave/--from/--to/--outdir) 纯 stdlib(argparse/json/math/os/sys) 输出 stress_summary.json。
- **判分**: check.py 子进程真跑 SUT 脚本 on 隐藏 B + 内嵌独立 oracle (纯 python 重推导 Vdd/Vth/窗口/峰值) + ≥8 条件 + 反硬编码(A 也跑通 + A∩B 不相交) + 3-seed 行序稳定。
- **维度正交**: 既有 waveform case #475 FsdbPowerWindow(功耗窗口对比)/#468 IVCurve(IV 曲线分类)/#483 EyeAperture(VREF 眼孔径)/#465 SmBisecMargin(bisection margin) — 本 case=HCI 应力窗口检测(Vgs&Vds 双阈值连续区间+峰值提取)，机制/产物全不同。

## 真实产物已读全文
- /home/yh1yang/workspace/ai/src/analyze_hci.py (406 行，已 scp 到 .75 workdir analyze_hci.py)
- /home/yh1yang/workspace/ai/data/wave (8118 行，header+TIME+v(ro1_mid<0>) v(ro1_mid<8>) v(out))
- /home/yh1yang/workspace/ai/docs/agent.txt (任务说明+算法核心逻辑+使用方式)
