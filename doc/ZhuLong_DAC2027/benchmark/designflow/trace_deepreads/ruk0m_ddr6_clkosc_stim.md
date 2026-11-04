# Deepread: ruk0m — DDR6 CLKOSC 激励生成

- trace: `1791956738036_ruk0m` (jinyuli / hfeg0plg91, mc=29)
- domain: waveform  | shard: D
- case-id: EDA-Eval-DesignFlow-ClkOscStim-001
- level: L1-boundary (deterministic config-driven generator, no real FineSim run)

## 用户目标 (U#0 逐字)
> 帮我生成一个激励，用于DDR6 CLKOSC

单轮干净提需求轮；无后续用户消息（trace 全程 agent 自主探索 + 写文件）。

## Agent 行为链
1. 探 workspace：`ls` 当前目录 → 发现 `45corners.txt`、`devices_file.txt`、`python_plot/`。
2. 读 `45corners.txt`（PVT 角点命名表 tt/ff/ss/sf/fs × 25/110/m40 × 1p1/0p9/0p98/1p3）+ `devices_file.txt`（DDR6 IO 信号上下文：`vcm1_io_CLKOSC_LatEn`、`vcm1_io_ClkOscTrim<2:0>`、电源 `vvddq`/`vvdd2dq`/`vvss`/`vvssz`）。
3. 先写 `DDR6_CLKOSC_stim.sp`（90 行模板 SPICE testbench：全局 .OPTION、电源 PULSE 爬升、LatEn PULSE @TENABLE、Trim<2:0> PULSE 步进扫描、.TRAN、.MEAS Fosc/Tstartup、.PROBE）。
4. 再写 `gen_ddr6_clkosc_stim.py`（174 行生成器：argparse + CORNERS dict{10 角点} + header()/control()/dut_ref()/sim_meas()/build_stim()/filename()/main()，control() 发固定码 V_TR0/1/2，每角点×每 trim 一份 .sp）。因 6000-char editor 限制分多次 edit 写入。
5. 末轮 `run_approved_command` 被 desktop approval REJECTED，trace 终止于该 rejection——但磁盘上两文件已落地，即为 agent 实际产出（gold）。

## Gold 取定
- 主 gold = `gen_ddr6_clkosc_stim.py`（L1-boundary 配置驱动生成器）。
- 辅 gold = `DDR6_CLKOSC_stim.sp`（trace 首版单文件模板，作为 faithful 文体参考）。
- reference 复刻版重排了 control() 至 main() 之前（原 trace 中 control() 定义在 `if __name__` 之后，属编辑碎片，复刻时规整），并改造为读 `config.json` 以支持隐藏 B 输入。

## A / B 设计
- A (config_A): DDR6, 5 supplies(vvss/vvssz/vvdd/vvddq/vvdd2dq), signals vcm1_io_CLKOSC_LatEn / vcm1_io_ClkOscTrim, 10 corners, trim 0..7, stopt=3u, prefix=0, spname=clkosc → 80 files.
- B (config_B): DDR5_IOX, 2 supplies(vdd_core/vss_io), signals LatEn_iox / TrimIox, 3 corners{ss_130_0p9/ff_25_1p3/tt_m40_1p1}, trim 0..5, stopt=5u, prefix=clk, spname=osc → 18 files. 结构/数值/命名全异。
- cross-guard: A-only{DDR6,vvdd2dq,vvddq,vvssz,vcm1_io_ClkOscTrim,vcm1_io_CLKOSC_LatEn,tt_25_1p1} vs B-must{DDR5_IOX,vdd_core,vss_io,LatEn_iox,TrimIox,ss_130_0p9,ff_25_1p3,tt_m40_1p1}。

## check.py 15 条件 (a–o)
a zip 含 gen_ddr6_clkosc_stim.py  b py_compile  c config_B 运行 exit0 出 .sp
d .sp 数 == 角×trim(18)  e header 含 B 角点/温度/电压  f .OPTION+.TEMP
g B 电源源 V_VDD vdd_core + V_VSS vss_io  h LatEn PULSE@TENABLE 用 B laten 名
i Trim<2:0> 固定码按 filename trim 的 bit 值  j .TRAN 含 B stopt(5u)+MAXSTEP
k .MEAS Fosc=1/Tosc + Tstartup  l .PROBE on B TrimIox<0/1/2>
m cross-input guard A 缺 B 现  n 3-seed sha256 稳定
o §4.9 三假(empty/print_fixed_A/core_deleted) 全 FAIL 且穿透 >=3 不同条件

## 自验
- gold check.py: PASS 15/15
- negatives: fake_empty/fake_print_fixed_A/fake_core_deleted 均 FAIL (rc=1)；selftest OK
- A 侧 80 文件全含 A token、零 B token；B 侧 18 文件全含 B token、零 A token → 护栏非空泛
- k_rationale == k_check == 15
