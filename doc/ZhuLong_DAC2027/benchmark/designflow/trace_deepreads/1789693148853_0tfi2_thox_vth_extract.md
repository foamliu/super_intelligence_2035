# trace deepread — 0tfi2 (ThoxVthExtract-001)

- **trace**: `1789693148853_0tfi2.messages.json` (qiong1w @ hfeg0pkn003, mc=146, 252 msgs, 2.3MB)
- **keywords**: pdk:210; netlist:173; hspice:166; schematic:101; skipper:53; virtuoso:38; calibre:37; cadence:31
- **session**: zhulong/zl agent (`agent: lead`)

## 用户轮（逐字原文，红线 #2 不脱敏）
1. `zl -cli` — 用户在摸索 `zl` 命令是什么（环境探索，非需求轮）。
2. **「从PDK中提取厚氧器件在1.8V VGS下的Id-VG,check if Vth is acceptable」** — 真正的需求轮（提出目标，未给根因/修复，符合 A 档选轮规则）。

## assistant 工具链（关键节点）
- 在 `/apps/cad/bin/zl` → `/apps/imctf/cad/ai/agent/zl.sh` 找到 zl=zhulong CLI 入口（msg 41-50）。
- 收到需求后（msg 52 起）大量 `search_codebase`/`read_files` 在 PDK 模型文件 `incFile_V1_HKMG`（65K+ 行）里找厚氧器件 `ntk`/`ptk` 模型卡（CXMT V1_HKMG G6 工艺，ntuot V0 项目）。
- 找到既有仿真目录 `/rundata/ntuot/V0/simdir/finesim/workdir/qiong1w/sim_vt/`（含 1.sp/sim.sp/test.lis）。
- 最终（msg 235/249/251）创建 `/home/qiong1w/Desktop/thk_io_idvg.sp`，含 4 个 DC 测试：ntk VDS=0.1V 扫 VGS 0→1.8 提 Vth_lin(max-gm)、ptk VDS=-0.1V、ntk VDS=1.8V 提 Vth_sat、ptk VDS=-1.8V。
- 对话超时（msg 251「由于对话超时问题，我无法继续提问」），**用户未明确接受结果** → 本 trace 无干净 acceptance 点 → 取 **B 档 synthesized**（子技能忠实于用户需求，金标准由我方在 .75 上标定）。

## 子技能（可移植化）
厚氧 MOS Vth 提取：Id-VG 扫描（线性区 Vds=0.1 + 饱和区 Vds=Vdd）+ 两种独立 Vth 提取法（max-gm 线性外推含 Vds/2 修正 / constant-current 插值）+ spec 窗口 accept 判定。
便携化：foundry PDK 不可移植 .75，取 level-1 Shichman-Hodges MOS（带 theta 迁移率退化）+ HSPICE V-2023.12-SP1-1；A=nthk_a(vto=0.70)/B=nthk_b(vto=0.58)，命名/sizing/kp/theta/spec 窗口全不同。

## distinct vs 已有 B characterization case
GmidLut=Gm/Id 查找表、NmosAgeChar=老化、CTLEtranChar=CTLE 瞬态、VihTripTune=ViH 调整、ButterflyCurve=SRAM 蝶形、DffSetupHoldChar=DFF 时序、LvPmosVgVs=netlist 层次 PMOS Vg>Vs 搜索、OtaAutoTune=OTA 调谐 —— 本条=**厚氧 Vth 提取(ELR+CC 双法)+accept 判定**，shard B 首个「Vth 提取器」case，distinct ✓。

## 金标准（.75 HSPICE V-2023.12-SP1-1 标定，确定性）
- A (nthk_a, vto=0.70, W=10u/L=0.35u, kp=50u, theta=0.15): vth_elr=0.7447, vth_cc=0.7605, accept=true (窗口 [0.55,0.85])
- B (nthk_b, vto=0.58, W=14u/L=0.50u, kp=42u, theta=0.18): vth_elr=0.6312, vth_cc=0.6529, accept=true (窗口 [0.45,0.72])
- 跨输入 |B-A|/A ≈ 15% > 5% ✓（vth_elr 与 vth_cc 均不同）
