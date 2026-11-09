# 深读 cdza6 — HCI Stress Extraction (waveform)

**trace**: 1793245619370_cdza6 · yh1yang@hfeg0pkn002 · mc=48 · waveview:87 + transistor:64 + cmos:6
**size**: 937KB / 225 msgs / ~5 user turns
**fetched**: docs/agent.txt (5252B 方法论), src/analyze_hci.py (15127B 最终实现), data/wave (8118 lines, Custom WaveView 格式)

## 用户轮（A 档任务说明候选）
- U#0: `阅读提示词，从wave文件中提取HCI stress`（提需求，未指根因 → A 档任务说明可用原文）
- 后续轮：refine multi-window cumulative teff、PDF 输出、文档整理（非需求轮）

## 真实任务
从 Custom WaveView 瞬态波形（ring oscillator ro1）提取 NMOS HCI 等效 DC 应力参数：
- 输入：`data/wave`（TIME / v(ro1_mid<0>)=Vgs / v(ro1_mid<8>)=Vds / v(out)=Vdd，空格分隔，8118 行，0~10ns）
- 算法（agent.txt 方法论 + analyze_hci.py 实现）：
  1. `Vdd = median(vout[vout > 0.5])`（高电平中位数）
  2. `Vth = Vdd / 3.0`（经验阈值）
  3. `mask = (vgs > Vth) & (vds > Vth)`（同时高于阈值 = 应力窗口）
  4. `rising = where(diff(mask)==1)+1`, `falling = where(diff(mask)==-1)+1`
  5. 边界处理：mask[0] True → rising 前插 0；mask[-1] True → falling 末插 len-1
  6. `n = min(len(rising), len(falling))`，配对
  7. 每窗口：`dt = t[fall]-t[rise]`, `vg_peak = vgs[rise:fall+1].max()`, `vd_peak = vds[rise:fall+1].max()`
  8. 聚合：`teff = Σdt`, `Vg_stress = max(vg_peak)`, `Vd_stress = max(vd_peak)`
- 输出：终端表格（窗口明细 + SUM + per-window stats + 最终参数）+ PDF

## A-faithful 可行性
依赖私有 wave 文件（/home/yh1yang/workspace/ai/data/wave）+ agent.txt 方法论。wave 文件可读取（已 fetch），但 B 档合成更利于判分结构化（JSON 报告 + 隐藏输入反硬编码）。→ **B-grade synthesized**

## B-grade 合成方案
- 主题保留：从波形提取 HCI 应力参数（窗口检测 + 累计 teff + 峰值应力电压）
- 候选：`hci_stress_extract.py <wave_file> <out.json>` 解析 Custom WaveView → Vdd/Vth → 窗口检测 → JSON 报告
- A：ro_wave_A.txt（Vdd≈1.2V，周期 20ps，~12 窗口）
- 隐藏 B：ro_wave_B.txt（Vdd≈0.9V，周期 30ps，~8 窗口，不同相位/占空比）—— 反硬编码
- 判分：L2 subprocess 真跑候选于 B + 16 条 a-p 结构化字段断言（含独立参考实现校验 + 跨输入反硬编码 + 3-seed md5）
