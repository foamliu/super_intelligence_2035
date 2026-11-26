# 深读笔记 · rbllu · clarawu@hfeg0pkn004 · 2026-11-07 19:2x
# session: 1792573855361_rbllu (mc=279, spice-dominant sp=56) · 46 msgs · 140KB
# 域: spice_sim (SPICE netlist 器件参数注入) · A-档 faithful · L1

## 选轮
USER#6 (msg 27, 逐字):
> 帮我写一个python脚本，将@/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_DqFinalDrv_Ron_pdnrvt_smallW/hspiceD/schematic/netlist/netlist 中Cell name: DqFinalDrvPu里的nulvt_ckt管delvto_user=0后面加上_delvto=-0.2

**A-档 CLEAN 判定**: 纯需求轮 —— 用户给出目标(写脚本)+具体对象(cell=DqFinalDrvPu, device=nulvt_ckt, anchor=delvto_user=0, inject=_delvto=-0.2)，**未给根因/未给修复脚本**。前 5 轮 (TURN0-5) 是电路功能咨询 + gvim how-to，与本任务无关；TURN6 是独立的新需求。✓

## trace assistant 行为 (msg 28-45)
1. list_allowed_files → 列出 netlist 目录
2. search_codebase("Cell name: DqFinalDrvPu"...) → 超时(大网表)
3. run_commands grep → 被禁 (raw shell disabled)
4. editor 写 inspect_mrodt.py → run_approved_command(python-runner) 跑：
   - total lines: 270
   - `** Cell name: DqFinalDrvPu` @ line 54
   - `.subckt DqFinalDrvPu dq pumain vddqsw zqpu0 zqpu1 zqpu2 zqpu3 zqpu4 zqpu5 inh_vss` @ line 56
   - `.ends DqFinalDrvPu` @ line 84
   - 块内 nulvt_ckt 器件行 64-81 (18 个)，每行以 `delvto_user=0 _delvto=-0.2` 结尾
   - **发现**: 真实网表**已含** `_delvto=-0.2` (修改已存在)
5. read_files(56-84) 确认 → 块内每条 nulvt_ckt 行已带 `_delvto=-0.2`
6. editor 写 **add_delvto_mrodt.py** (金标准脚本):
   - find_block(lines, cell): 正则 `^\.subckt\s+<cell>\b` ... `^\.ends\s+<cell>\b` 定位块 [start,end]
   - 遍历块内行 (start+1 .. end, 不含 .subckt/.ends 行):
     - 仅处理含 `nulvt_ckt` AND `delvto_user=0` 的行
     - **幂等**: 若 `delvto_user=0` 后紧跟(去空格) `_delvto=` → skip
     - 否则 `ln.replace(KEY, KEY + " _delvto=-0.2", 1)` (仅替换首处)
   - in-place 写回 (或 --out 路径)
   - CLI: `python3 add_delvto_mrodt.py [netlist] [--out OUT] [--cell CELL]`
   - 打印 changed/skipped 统计
7. editor 写 run_test_delvto.py (验证: 真实文件上跑=幂等 no-op + 剥离 _delvto 的副本上跑=加回)
8. run_approved_command → **code_sidecar_sigterm** (验证被信号终止, 但脚本已写好)

## 真实网表结构 (从 inspect 输出提取, 用于 A 资产忠实复现)
端口: `dq pumain vddqsw zqpu0 zqpu1 zqpu2 zqpu3 zqpu4 zqpu5 inh_vss`
nulvt_ckt 器件 (示例, 真实参数):
- XMN_puzq0 net013 zqpu0 net034 inh_vss nulvt_ckt w=1.5e-6 l=30e-9 sd=100e-9 ... delvto_user=0
- XMN_puzq0c net021 zqpu0 net035 inh_vss nulvt_ckt w=1.5e-6 l=30e-9 ... delvto_user=0
- XMN_puzq0b net025 zqpu0 net021 inh_vss nulvt_ckt ... delvto_user=0
- XMN_puzq0a net034 zqpu0 net025 inh_vss nulvt_ckt ... delvto_user=0
- XMN_puzq0_main net036 pumain dq inh_vss nulvt_ckt ... delvto_user=0
- XMN_pumain net049 pumain dq inh_vss nulvt_ckt w=6e-6 l=30e-9 nf=4 ... delvto_user=0
- XMN_puzq4 net013 zqpu4 dq inh_vss nulvt_ckt w=3e-6 l=30e-9 nf=2 ... delvto_user=0
- XMN_puzq1 net013 zqpu1 net018 inh_vss nulvt_ckt ... delvto_user=0
  (共 18 个 nulvt_ckt 器件, 行 64-81)
真实网表已带 `_delvto=-0.2`; A 资产用"前态"(无 _delvto) 以使脚本有活干。

## 金标准 (USER 实际接受的产物形态)
add_delvto_mrodt.py 的行为: 在指定 cell 的 .subckt/.ends 块内, 对含 device+anchor 的器件行, 在 anchor 后追加 inject (幂等). 通用化为 gen_param_inject.py <netlist> <cell> <device> <anchor> <inject> <outdir>.

## case 设计
- id: EDA-Eval-DesignFlow-SubcktInstParamInj-001
- domain: spice_sim, track: faithful, level: L1
- A: netlist_A.sp (DqFinalDrvPu + nulvt_ckt + delvto_user=0, 前态, ~14 器件 + decoy 子电路)
- hidden B: netlist_B.sp (cell=DqOutTopM6, device=pulvt_ckt, anchor=delvto_user=0, inject=_delvto=-0.15, ~10 器件 + 同 device 的 decoy 子电路用于 scope 隔离测试)
- 交付: gen_param_inject.py <netlist> <cell> <device> <anchor> <inject> <outdir> → netlist_modified.sp + report.json
- check.py 仅跑 B, ≥8 条独立断言
- 与现有 SetNetlistParam-001(shell var 编辑)/StdcellDeckParamModify-001(deck .para/.tran)/NetlistMisModCompare-001(对比) 均不同 —— 本 case 是 subckt 块内**器件实例行参数注入**(transistor instance line param injection), 幂等 + scope 隔离。
