# hgfso 深读 — FineSim Measure 检测 WR 第4个 CLK 上升沿

## trace_source
- user: wenwenl · host: 10.129.8.112 · session: 1790841917726_hgfso.messages.json · mc=59 · n_msgs=98
- domain: waveform (FineSim measure script)

## U#0 (逐字原文，唯一真实用户输入)
`FineSim Measure脚本，检测wr command的第4个CLK上升沿`
- 纯提需求，未给根因/修复 → A-faithful 合格
- 其余 64 个 "user" 轮均为工具结果（list_allowed_files/read_files 返回），非真实输入

## trace 演化（agent 工具链）
1. list_allowed_files 枚举 /home/wenwenl, /home/wenwenl/work, /home/wenwenl/work/DDR6 树
2. read_files 读现有测量脚本（DSCQA/sim_setup/Compare/）:
   - **meas_wr2dq.fscr** — Write→DQ 测量，无 .derived（用 `.meas tran t_wr_fall0 when v(dq0_0)=Vref_DQ fall=1`），有 tCK=rise=10→11，VmidCK=0.174，Vref_DQ=VDD*0.29
   - **meas_odt.sp** — 含 `.derived wr_detect` 块（ck_t>Vmidckt AND cs_0>VHca AND ca2_0>VHca AND ca1_0<VLca AND ca0_0>VHca），VHca=VIH_CA*0.9, VLca=VIL_CA*1.1, VIL_CA=VDD*0.29-0.075, VIH_CA=VDD*0.29+0.075, Vmidckt=0.174
   - **config_sc0** — 信号命名: signals = DQS_t DQS_c DQ5_0..DQ0_0; simulator=finesim; product_generation=DDR6
3. read_files 读 ddr6_test.sv / ddr6_tasks.sv / ddr6_package.sv → 定位 WR 命令 C0 编码 (line 592): `ca_tmp = {cid[0], ae_psd, ba, 3'b101}` → CA[2:0]=3'b101 (ca2=1, ca1=0, ca0=1)
4. 创建两文件:
   - **meas_wr4thck.fscr** (FineScript 格式)
   - **meas_wr4thck.sp** (HSPICE 兼容格式)

## 金标（agent 真实产物，B-grade synthesized 基准）
关键测量逻辑（meas_wr4thck.fscr）:
- `.option finesim_measout=1`
- `.meas TRAN VDD AVG v(vddq!) from=200n to=220n`
- `.param Vref_CA='VDD*0.29'`, `VIH_CA='Vref_CA+0.075'`, `VIL_CA='Vref_CA-0.075'`, `VHca='VIH_CA*0.9'`, `VLca='VIL_CA*1.1'`, `VmidCK=0.174`
- `.meas TRAN tCK TRIG v(ck_t) VAL='VmidCK' RISE=10 TARG v(ck_t) VAL='VmidCK' RISE=11`
- `.derived wr_detect`: ck_t>VmidCK .and cs_0>VHca .and ca2_0>VHca .and ca1_0<VLca .and ca0_0>VHca
- `.meas TRAN t_wr WHEN v(wr_detect)='VDD' RISE=1`
- **`.meas TRAN t_wr4th_ck TRIG AT='t_wr' TARG v(ck_t) VAL='VmidCK' RISE=5`** ← 核心：WR 自身所在 CK 沿=RISE=1，第4个上升沿=RISE=5 (edge_after+1)
- `.meas TRAN t_4thCK_abs WHEN v(ck_t)='VmidCK' RISE=5 FROM=0 TO='t_wr+100n'`
- `.meas TRAN t_wr4th_ck_cycle PARAM='t_wr4th_ck / tCK'`
- `.meas TRAN t_wr4th_dq0_fall/rise WHEN v(dq0_0)=Vref_CA FALL/RISE=1 FROM='t_wr' TO='t_wr+50n'`

## 关键技术事实（断言对账用）
1. WR C0 编码 CA[2:0]=3'b101 (ca2=1, ca1=0, ca0=1)
2. VmidCK = 0.174 V (VIN_BASE, CK 差分交叉电压)
3. Vref_CA = VDD*0.29; VIH_CA = Vref_CA+0.075; VIL_CA = Vref_CA-0.075; VHca=VIH_CA*0.9; VLca=VIL_CA*1.1
4. SC0 信号名: ck_t, cs_0, ca2_0, ca1_0, ca0_0, dq5_0..dq0_0 (后缀 _0)
5. 第 N 个 CLK 上升沿 (after command) → RISE = N+1 (命令自身所在沿=RISE=1)
6. .derived <cmd>_detect: ca bit=1 → .gt VHca; ca bit=0 → .lt VLca
7. tCK 测量用 rise=10→11 (稳态周期)
8. t_<cmd>_<n>th_ck_cycle = PARAM = t_<cmd>_<n>th_ck / tCK

## B-grade 合成设计
- 真实 /rundata / /proj 路径不可附加 → 合成
- 金标泛化为 gen_meas_ref.py: CLI `gen_meas_ref.py <config.json> [--out <fscr>]`
- config 字段: command, cmd_ca_bits (3-char "101"), edge_after (int), signal_suffix ("_0"/"_1"), vmidck, vddq_node, from_time, to_time, tck_rise_lo, tck_rise_hi
- A config (SUT 可见): wr/101/4/_0 (匹配 prompt)
- B config (hidden, check-only): rd/011/6/_1 (反硬编码: 不同命令名/编码/边沿数/后缀)
