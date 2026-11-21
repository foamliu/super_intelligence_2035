# flxzl (e03179) 深读 + r1091 选料轮发现 — 2026-11-22

## 选料轮背景
r1091 为造题主线选料轮（上轮 r1090 紧急数据恢复 0 case，本轮预算 40min）。eda_flow open_session OK（workdir shardD_20261122-r1091_D-r1091-case_0，已 close）。

## D-pure 候选池扫描（mc≥5, d≥c, D域 keyword 主导）
在 .75 summary.tsv(20261121_151844) 上跑 D-pure filter（d=waveview/netlist/spectrum/analog/schematic/spiros/cosmos/skill/.cdl/.spi/transistor 权重和, c=drc/lvs/calibre/virtuoso/.gds/gdsii/innovus/pdk/rtl/skipper/aether/pyaether/techfile/cellview/dbopen/dbget/dbcreate/floorplan/adexl/synopsys 权重和, 保留 d≥c）。dedup by slug 得 674 条 D-pure 候选（dpure_dedup.tsv）。

## 🔴 关键发现：高 mc D-pure 候选已全部 ledgered
对 40 条高 mc（≥100）D-pure 候选 full-slug 交叉验证 4-shard 台账（_excl_slugs_r1091.txt, 4210 unique slugs）：**全部 LEDGERED**（case/parked/claimed/deepread）。包括：xinm9/ak41b/upag1/98xca/zpvgj/wz59k/wduge/2n1bs/hoh52/lq00u/p3107/4vmtg/ppwfb/bjkmi/95kx2/1550c/p64wo/6c3cw/sr0ca/tw1rj/b1w28/2zbgo/4a852/it6n4/xq4ge/xd7ut/i5ubq/bqgpm/vb4si/a7ied/36yj3/ujxtn/g5bbp/3ugoq/1g0xs/rcx51/1nsgi/0gv3z/hpy3y/vklwe 等。
⇒ 与 ledger stats 一致（covered=572/2072=27.6%, 剩余可做≈233，且剩余 fresh 为低 mc 5-50）。**高 mc D-pure 池已采空**，后续造题须 (a) 降门槛到低 mc fresh 或 (b) 对 parked 题做 reconsideration（需谨慎，prior operator 已 parked）。

## flxzl 重深读（已 parked，本轮重看以判断 reconsideration 可行性）
- trace: .75:/home/e03179/.cline/data/sessions/1793148627756_flxzl/1793148627756_flxzl.messages.json, 860KB/125msgs, D-pure d=3808 c=79 mc=162
- 台账状态：D ledger **parked 2026-11-05**，note「vam-agent cell建模推荐分析非clean produce」
- 真实意图：用户走 vam-agent **方案二**（数字 block Verilog-A 替换），「仿真路径是 /proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_DDR6TOP/primesim.Golden008_Perbank_ActWrRd_Dqtoogle_SC0_WPre_4s4t_WPst_4p5_RPre_4s4t_RPst_0p5_RPs_2_CAParity_ENA_CMDBLK_ENA_MD_16b_tCH50_2b16g_BLs_11600_FF_ZERO_PAD.X2P3_11600.FF1.23V-40C.X2P3，帮我查看下哪些cell可以直接替换」+「确认建模」
- agent 流：read vam-agent skill/gen_bnk_va → resolve netlist symlink → /rundata/dscqa/.../netlist.presim → 搜 DSIM products（D_CRCR10_CRCTop_in/_io/_out, *_pwl, *_power）**未找到** → 扫 netlist 的 crcr10/crctop → 跑 gen_bnk_va → 输出「CRC mode: DISABLED (constant)」「CRC target cells: d_crcr10_crctop」
- netlist.presim 实含 D_CRCR10_* 子电路（trace tool_result msg78 实录）：
  - D_SpareCrcTop
  - D_CRCR10_CRCConfig（端口含 CRCMode<1> CRCMode<0>）
  - D_CRCR10_CRCAlertGen
  - D_CRCR10_CRCRdOut
  - D_CRCR10_CRCxor14 / D_CRCR10_CRCxor10
  - D_CRCR10_CRCTop（目标 cell）
- 兄弟 run dir 有 CRC_01 命名（primesim.Golden019_..._CRC_01_...）→ CRC-enabled 变体，可作 hidden B 对比素材
- **真实交付**：CRC-mode 判定（DISABLED→输出常量→可替换）+ 可替换 cell 识别（D_CRCR10_CRCTop）；.va 生成因 DSIM 产物缺失而**受阻**（agent 诚实报告 blocked）
- 🔎 reconsideration 评估：prior「非clean produce」判断针对的是 .va 生成受阻（无最终 .va 文件）。但**子交付 = CRC-mode 判定 + 可替换 cell 识别** 是可离线 checkable 的（给定 netlist + sim path → 输出结构化 JSON: crc_mode / replaceable_cells / digital_cell_count / crc_keywords_found）。reframe 为脚本交付 crc_replace_scan.py 可造 L1 case。**判据**：可 reconsideration，但须 prior operator 未否定该子意图；下轮可据此 unpark 重造（保守起见先在 MEMORY 标注，不自行 unpark）。
- asset A 素材已就绪：trace 已捕获 D_CRCR10_* 子电路签名（含 CRCMode 端口）；netlist.presim 文件本身 e0031982 无读权限，但 trace tool_result 已含足够结构。

## 本轮结论
- 0 case（守「宁可慢造不造 weak」+ 止损；预算耗于选料+flxzl 重深读+池扫描）
- 非「连续 3 轮 0 case」（r1088 造了 GenguiVariantAudit-001，r1089 修 GAP，r1090 紧急恢复）
- DEBT: 1 份 flxzl 重深读（可 reconsideration 为 CRC-replace L1 case，下轮决定是否 unpark 重造）
- 增益：高 mc D-pure 池已采空（事实），后续造题须降 mc 门槛或 parked reconsideration
- eda_flow session 已 close（清理）
