# trace_deepread: pchuf (harrywu@hfeg0pkn002, mc=728) — DecEn_PwrUpLock 静态功耗分析

- **session**: `1794133519350_pchuf.messages.json` (582 msgs, 2.1MB, model deepseek-v4-flash)
- **domain**: analog_context (静态/漏电功耗分析) — shard D
- **produce-task**: U#1 "理解该路径下的所有文件，并对 Cell DecEn_PwrUpLock 进行功耗分析，需要在 SecEn=1/0 两种情况下的静态功耗分析，这里主要分析 MP4 和 MN4 造成的静态功耗，需要修改 testbench，加入电流分析以及 meas 脚本，仿真自己提交，我只需要结果"
- **refined spec**: U#2 (corner TT/1.025V/98C，参考其他 testbench，中文交流) + U#3 (详细：64 banklogic 复用、Idle/Active 场景、MP4/MN4 漏电占比、基线增量、netlist 拓扑 XI92/XI61/XI8 + XMMP4/XMMN4)
- **drift**: U#4+ 转 FSDB 波形提取（finesim-fsdb-reader skill）→ U#8+ 转 signal-chain-trace 平台（wave_tracer.py/cell_delay_mapper.py/report_generator.py）。功耗分析是 U#1-U#3 的闭环，后续是另一条线。

## agent 工具链（功耗主线，idx 0-260）
1. `list_allowed_files` 探 `/proj/dscqa/V0/agentdir/harrywu/simulation/pwrup_issue/psf/` → input.sp / netlist / Pattern_Power.sp / POR_pwr.sp / Powerup_pwr.sp / pwr_result.sp / pwrup_signal.sp / RaPreDec_pwr.sp / block_sim/ / 多个 result_Vcap_*/
2. `read_files` 读 netlist + 各 .sp deck
3. `editor` 写 `DecEn_pwr.sp` (v1: pvcc=1.2 ptemp=110 ff, .meas I_MP4/I_MN4/I_VCC/V_NET3/V_NET5/V_SEC, .tran 10p 5n FROM=3n TO=5n, .step seclevel list 1 0, .inc netlist_pwr + Pattern_Power)
4. `run_approved_command` 跑 FineSim 本地 + bsub queue
5. U#2 后改 TT/1.025V/98C：写 `DecEn_pwr_tt.sp` (SecEn=1) + `DecEn_pwr_sec0_tt.sp` (SecEn=0)，.lib model.sp tt，.inc Pattern_Power_norm.sp
6. 写 setup_netlist.sh / run_pwr_tt.sh / poll_tt.sh / cleanup_tt.sh
7. 读 `result_DecEn_pwr_tt_20261108_1833/DecEn_pwr_tt.mt0` 结果
8. U#3 后加基线（无钳位）：`DecEn_pwr_base_tt.sp` / `DecEn_pwr_base_sec0_tt.sh`，netlist_noclamp
9. U#5 确认 gate 端电压（钳位管正常态关闭）→ 读 FSDB 波形验证 PwrOn3=1.025V/PwrOn3F≈0
10. `editor` 写 `DecEn_PwrUpLock_power_report.md`（最终报告）

## 真实产物（agent 交付）
- testbench+meas: `DecEn_pwr_tt.sp` / `DecEn_pwr_sec0_tt.sp`（有钳位）；`DecEn_pwr_base_tt.sp` / `DecEn_pwr_base_sec0_tt.sp`（基线）
- 网表: `netlist_pwr`（含 MP4/MN4 漏端 0V 电流表 vmp4/vmn4）、`netlist_noclamp`（基线）
- 结果: `result_DecEn_pwr_tt_20261108_1833/` 等 4 个结果目录
- 报告: `DecEn_PwrUpLock_power_report.md`（Idle/Active per-bank + 64-mux totals + MP4/MN4 漏电占比 + 基线增量 + FSDB 波形确认表）

## 报告关键数值（agent 实测）
- Idle(SecEn=0): I_VCC=82nA, 单 bank P=84.1nW, MP4+MN4 clamp P≈0.35pW（Vds≈0）
- Active(SecEn=1): I_VCC=410nA, 单 bank P=420.3nW, MP4=40.04nA/41.0nW, MN4=65.81nA/67.5nW, clamp P=108.5nW
- 基线(无钳位): Idle 82nA/84.1nW, Active 304.2nA/311.8nW；增量 Idle≈0, Active +108.5nW
- 64-mux: Idle 5.38µW, Active 5.72µW；钳位贡献占 active 总静态 1.9%
- 漏电分解: XMMP4 37.8%, XMMN4 62.2%

## B-grade 合成（本 case）
- **DEBT④**: `/proj/dscqa/V0/agentdir/harrywu/simulation/pwrup_issue/psf/` 私有，e0031982 无读权限 → B-grade synthesized
- A=合成 DecEn_PwrUpLock 网表(XI92 invGSx2 + XI61 invLVx8 + XI8 invLx1 + XMMP4 ptn_lv 12u/176n nf4 + XMMN4 ntn_lv 8u/176n nf4) + Pattern_Power_A.sp(TT/1.025V/98C)
- B=合成 ClampEnLatch 网表(4 invs: XI92+XI61+XI13+XI8, 信号名 En/EnN/EnBuf/EnBufN/PwrOn/PwrOnF, XMMP4 6u/90n nf2 + XMMN4 5u/90n nf2, MN4 drains EnBuf) + Pattern_Power_B.sp(TT/0.9V/85C) + mux 48
- 候选 power_leak_analyze.py: 解析 CDL(subckt+XI* inv+XMMP/XMMN clamp w/l/nf)+Pattern_Power(.param+vsrc)→logic 传播 enable=0/VCC 过 inv 链→算各 clamp |Vds|→自含亚阈值漏电模型(Ioff*(W/L)*nf*(1-exp(-|Vds|/VT)))→Idle/Active per-bank + mux totals + 基线(仅 inv 链)增量 + MP4/MN4 占比→power_report.json+md
- 17 条 a-q：含 e idle clamp≈0 / f,g active leak>1e-9 / h clamp_total=(i_mp4+i_mn4)*pvcc / i,j mux math 精确 / k delta_idle≈0 / l delta_active>0 / m,n,o,p 反硬编码(w/cell/ptemp/mux) / q 3-seed 确定性

## 选料
- cand_1109.tsv(11-09 cron fresh 池) → cross-ref trace_ledger_D.tsv → pchuf(harrywu mc=728 netlist:47 hspice:37 schematic:6) fresh, D-domain analog_context 完美匹配
