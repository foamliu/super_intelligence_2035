# deepread: t5osd — 带限高斯噪声 PWL 生成器（joeyl @ hfeg0plg49）

## trace
- session: `1790572773219_t5osd.messages.json`（joeyl, hfeg0plg49, 10.129.8.86）
- 嵌套路径: `/home/joeyl/.cline/data/sessions/1790572773219_t5osd/1790572773219_t5osd.messages.json`
- 268 msgs, 681KB, hspice=50 waveview=25 cmos=10 spectre=6 netlist=4 (spice-dominant ✓)
- 来源: 11-05 summary.tsv（10-28 快照）directive ②3 漏网候选（前轮未扫 plg 系列）

## 用户意图（A-faithful 选轮）
**U#2（idx2，提出需求，逐字作 prompt）**：
> 我想在电路仿真中加一个电源噪声，它是高斯分布，还要有一些可变参数，比如噪声开始时间，噪声带通下限和上限，保证可复现的随机种子，最终目标是生成一个可以直接被testbench inc的PWL文件，你可以帮我写这么一个生成脚本吗？如果我有没考虑到或者没说清楚的地方，请先与我讨论再开工

- ✅ A档选轮：提出需求/表达目标，无根因、无修复方案。
- 后续轮（U#3 提供路径格式+handbook 要求 / U#5 确认参数原则 / U#7 不要乱加噪声 / U#8 testbench .inc 工作流 / U#9 临时文件清理）= 需求补充，不入 prompt（A-faithful 只取提出需求轮）。

## assistant 工具链（金标准）
1. 探查 `/rundata/.../C2C` 目录结构（tran=NON-RFB + Tran_RFB，各 46 tr0）→ 误判为分析任务后用户澄清是生成任务。
2. U#2 后转向**生成器**：写 `generate_noise_pwl.py`（频域合成法）：
   - `bandpass_mask(N,dt,flow,fhigh,rolloff)`：余弦平滑过渡带通掩码 H[k]∈[0,1]，避免 Gibbs 振铃。
   - `synthesize_noise(N,dt,sigma,flow,fhigh,seed)`：`RandomState(seed).randn(N)` → FFT → ×H → IFFT → 缩放至 sigma。
   - `apply_envelope(noise,tstart_idx,ramp_len)`：t<tstart 置零，余弦渐变上升。
   - `write_pwl(filename,t,values,vname,pnode,nnode,header_lines)`：SPICE PWL 格式 `Vname pnode nnode PWL(` + `+ time val` + `+)`。
   - `validate_args`：sigma≥0/dt>0/tstop>tstart/fhigh>flow/fhigh<Nyquist/rolloff∈[0,0.5]。
   - argparse CLI：--sigma --seed --mean --dt --tstart --tstop --flow --fhigh --rolloff --output --vname --pnode --nnode --plot --plot-only --plot-file。
3. 中途 `/rundata/.../C2C` 目录被移到 `3_C2C`（外部重命名），assistant 适配路径继续。
4. U#3/U#5/U#8/U#9：补 HANDBOARD.md（参数确认原则、testbench 定位规则、.inc 接入流程、临时文件清理）。临时脚本自毁（os.remove）。
5. **session 末尾（idx267）**：assistant 确认 HANDBOARD.md 更新完成，用户无拒绝 → 接受金标准。

## 金标准产物（fetch from host 10.129.8.86）
- `/home/joeyl/noise_generator/generate_noise_pwl.py`（13222B，2026-09-28 11:11）
- `/home/joeyl/noise_generator/HANDBOARD.md`（10722B）
- `noise_vss_spectrum.png`（167KB，频谱验证图）
- `verify_vss_injection.py` / `patch_tb_vss.py`（VSS 注入验证）

## 通用化（generate_noise_pwl_ref.py）
- 剥 `/apps/local/python/python-3.7.1` shebang → `#!/usr/bin/env python3`。
- 算法逐行不变（bandpass_mask / synthesize_noise / apply_envelope / write_pwl / validate_args / argparse）。
- 输出格式：`*** Band-limited Gaussian Noise PWL ***` + `*** <params> ***` + `Vname pnode nnode PWL(` + `+ %.15E  %.15E` + `+)`。

## 判分设计（check.py 15 断言 a-o）
- B（隐藏）：sigma=0.02 seed=999 flow=5e6 fhigh=200e6 tstart=20e-9 tstop=2e-6 dt=2e-12 mean=1.2 vname=Vnps pnode=vps nnode=gnd。
- A（泛化）：sigma=0.015 seed=7 flow=2e6 fhigh=800e6 tstart=50e-9 tstop=1e-6 dt=1e-12 mean=0.0 vname=Vclk pnode=clkn nnode=0。
- 解析 PWL：`+ float float` 行 + `Vname pnode nnode PWL(` 头 + `+)` 尾。
- 高斯/带通：numpy FFT，noise=values-mean，|noise mean|<sigma*0.25 + std∈[sigma*0.6,sigma*1.4]；带内[flow,fhigh]能量占比>0.55。
- tstart：t<tstart 段 RMS<sigma*0.06（包络置零验证）。
- 带宽敏感：不同 flow/fhigh → 频谱重心偏移（防硬编码带宽）。
- A 泛化：A 参数头用 A vname/pnode/nnode，B vname(Vnps) 不泄漏入 A（防硬编码 B）。

## 自验
- ref PASS 15/15 ✓
- 4 negative（naive_constant/hardcoded_b/print_expected/del_core）全 FAIL distinct ✓
- §4.9 三假（empty/print-expected/del-core）全 FAIL ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl test==disk sha 7abf2df2c59b ✓
