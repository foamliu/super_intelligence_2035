# trace_deepread: 3lnsm (lorikx@hfeg0plg52, mc94, verilog-dominant) — lint-filelist-update-audit produce

> r1030 选料+深读轮 (0 case 落库, DEBT 下轮合成). 本 deepread 已铺路, 下轮 r1031 直接合成即可.

## trace_source
- session_file: `1795072478116_3lnsm.messages.json`
- user: lorikx ; host: hfeg0plg52 ; match_count: 94
- domain (shard D): schematic_netlist (verilog lint project)
- keywords: verilog:1979 dominant + analog:162 + systemverilog:19 + netlist:19 + schematic:5
- trace size: 86 msgs, ~ (3lnsm.json on .75 sandbox)
- ledger: claimed r1030 (status=claimed, 未 mark case)

## 用户真实意图 (A-faithful U#0 逐字原文)
```
请检查这个路径的文件/home/lorikx/1_TV1/CXTV1_FS001A/frontend/work/,是个lint项目，之前运行过，单已经很久没更新，rtl更新过，你评估一下有哪些文件需要修改，能达到最新的版本运行lint，那个路径你没有写的权限，所以你可以在FS_LINT文件夹下执行你需要做的事请
```
= "Check the lint project at .../frontend/work/, run before but long unupdated, RTL updated, evaluate which files need modification to run lint at the latest version. No write permission there → work in FS_LINT folder."

**选轮规则核验**: U#0 是纯需求轮 (用户提目标: "评估哪些文件需要修改以跑最新版 lint"), 用户未给根因/未给修复方案 → A 档合格. 后续 U#47/U#51/U#60 是用户追加 (写替换文件 / 做完整 work 文件夹 / 调试 error), 不影响 U#0 作为 A-faithful 任务说明.

## trace 关键产物 (assistant 探查所得, 真实事实)

### lint 工程现状 (work/)
- 工具: **Synopsys VC Static V-2023.12-SP1** (vc_static lint)
- 上次运行: 2026-10-28 09:10:52, by guomings (距 11-19 已 3 周多)
- Top module: **AMSGrp** (AMS IP 组, 非整 chip)
- 路径: `/proj/lacaa/TV1_TestChips/CXTV1_FS001A/frontend/work` (symlink from `/home/lorikx/1_TV1/CXTV1_FS001A/frontend/work`)
- 关键文件:
  - `lint.tcl` — 由 Makefile `write_lint_tcl` 生成的 lint TCL
  - `Makefile` — vc_static, top=AMSGrp, tool V-2023.12-SP1
  - `design_rtl.list` — 38 文件 (AMS_IP / common / SramEDABistGrp2 / libs/uv AMS_IP verilog / 1 标准单元)
  - `design_rtl_top.list` — chip_top 级 (CXTV1_FS001A.v 等)
  - `design_rtl_sram2.list` — SRAM group
  - `design_lib.list` — 空
  - `sc_target.mk`, `readme` ("make lint" / "make lint_gui"), `vcst_rtdb/reports/run.log`

### RTL 目录现状 (frontend/)
- chip_top: CXTV1_FS001A.v, stc_tc_Grp4.v, **stc_tc_fs_elvt.v (新? Makefile blackbox 只有 lvt/svt/ulvt 没有 elvt)**, CXTV1_FS001A_old.v / _tmp.v / _BMP.v, CXTV1_DBC001A_PAD.v, CXTV1_FS001A_PAD.v
- common: decode.v, esd_wrappers.v, **GPIO_TC7_instruction.v (新?)**, mux.v, tm_tcq.v
- AMS_IP: AMSGrp.v, **AMSGrp_1.v (新?)**, t_sensor_grp.v

### 核心问题 (assistant 定位的根因)
**AMSGrp.v (11-18 更新) 已把模拟 IP 从 HDBC 版换成 HFS 版**, 实例化:
```
CHHIO35HFS_ADC_TC
CHLDO35HFS_TC1, CHLDO35HFS_TC2
CHPLLA35HFS_DIV_TC, CHPLLA35HFS_TC1, CHPLLA35HFS_TC2
CHPSEN35HFS_TC
CHVREF35HFS_TC
CHVSENA35HFS_TC, CHVSENB35HFS_TC
ANAHFS_BUF
```
这些新 AMS IP 在 `libs/uv/20261030/verilog/CH*HFS...` (2026-10-30 发布).

**而 `work/design_rtl.list` 仍指向旧 HDBC 版**:
```
libs/uv/AMS_IP/verilog/CHVREF35HDBC_TC.v
libs/uv/AMS_IP/verilog/CHPLLA35HDBC_DIV_TC.v
... CHHIO35HDBC_ADC_TC ... CHLDO35HDBC ... (全是 HDBC)
```
⇒ lint 时找不到模块 (AMSGrp 实例化的 HFS 模块在 list 引用的 HDBC 文件里不存在) → lint 失败.

### 需要修改的文件 (assistant 结论)
1. `design_rtl.list` — 把 8 个 HDBC IP 路径替换为对应 HFS 路径 (libs/uv/AMS_IP/verilog/CH*HDBC*.v → libs/uv/20261030/verilog/CH*HFS*.v)
2. 可能需补 `stc_tc_fs_elvt.v` / `GPIO_TC7_instruction.v` / `AMSGrp_1.v` 等新 RTL 到 list
3. Makefile blackbox 列表需补 elvt

## 拟造 case 形态 (下轮 r1031 合成)

- **case_id**: `EDA-Eval-DesignFlow-LintFilelistVersionAuditProduce-001`
- **子型**: lint-filelist-version-audit-produce (D 域首例 verilog lint 工程 filelist 版本漂移审计 + 更新文件生成; 与 r1020 IOStaticLogicDeriveProduce 静态逻辑推导/r1027 NetlistModKwHierSearch 层次检索 互补: 本例做 lint 工程 filelist 与 RTL 目录的版本一致性审计)
- **A-faithful U#0 逐字** (上方原文, 仅掩码无 key/token)
- **synthesized-reframe**: 真实 `/proj/lacaa/...` lint 工程 (NFS + foundry-bound, 不可沙盒) → 紧凑 fixture 保留真实命名 (AMSGrp top, HDBC→HFS IP 版本迁移, design_rtl.list 38 文件, lint.tcl, Makefile vc_static V-2023.12-SP1, libs/uv/20261030/verilog/CH*HFS, libs/uv/AMS_IP/verilog/CH*HDBC, 8 个 HDBC→HFS IP 对: CHHIO35HDBC_ADC_TC→CHHIO35HFS_ADC_TC 等)
- **produce-script**: `lint_filelist_audit.py` 多参 CLI `<filelist> <rtl_root> <top_module_file> [-o out_dir]` → (1) 解析 filelist 引用的 .v 路径 + 提取版本标签 (HDBC/HFS 等正则); (2) 扫描 rtl_root 实际 .v 文件 + mtime; (3) 解析 top_module_file 的实例化模块名; (4) 对每个 filelist 条目判定 stale (引用版本 ≠ rtl_root 最新版本) / missing (文件不存在) / ok; (5) 对 top 实例化但 filelist 未含的模块标 missing_from_list; (6) 产 `updated_filelist.list` (替换 stale 为最新版路径) + `audit_report.json` {stale[], missing[], missing_from_list[], version_map{}, summary}
- **hidden B 合成** (token 完全不相交): 不同 IP 版本迁移, 例如 STD→PRO 系列: top=DataGrp, IP 对 DCHIO35STD_ADC_TC→DCHIO35PRO_ADC_TC 等, list 文件 data_rtl.list, rtl_root libs/uv/20261105/verilog/DCH*PRO, libs/uv/AMS_IP/verilog/DCH*STD, 8 对不相交 token (A-only{AMSGrp/HDBC/20261030/CHHIO35/CHLDO35/CHPLLA35/CHVREF35/CHVSENA35/CHPSEN35/ANAHFS_BUF}, B-only{DataGrp/STD/20261105/DCHIO35/DCHLDO35/DCHPLLA35/DCHVREF35/DCHVSENA35/DCHPSEN35/DATAPRO_BUF})
- **check.py ≥16 断言** (k_check≥8 硬闸门): zip 含 lint_filelist_audit.py+audit_report.json+updated_filelist.list + py_compile + 反空壳≥800B + B 子进程 exit0 产 updated_filelist_B.list+audit_report_B.json + B report 合法 JSON 含 stale/missing/missing_from_list/version_map/summary + B stale 数量==gt (独立 _gt_stale 重算 filelist 版本标签 vs rtl_root 最新) + B 每条 stale 的 old_path/new_path/version_tag 三元组结构与 _gt 一致 + B missing_from_list 含 top 实例化但 list 未含的模块 (独立 _gt_parse_instances 重解析 top_module_file) + B updated_filelist 替换全 stale 且保留非 stale + B updated_filelist 行数==原 list 行数 + B version_map HDBC→HDS 映射正确 (独立 _gt_version_map 重算) + 反硬编码 B stdout/report 零 A-only token (10 个) + 反硬编码-2 含全 B-only token + 3-seed md5 确定性 + A report 匹配 A 金标准 (8 HDBC→HFS 替换)
- **negatives**: empty_stub (FAIL size<800B) / print_expected (FAIL stale 数≠gt) / core_deleted (FAIL version_map 空≠gt) + negative_selftest.py 全 FAIL
- **§4.9 三假**: 空壳/只 print 期望/删核心 全 FAIL
- **自验**: ref 16/16 PASS on B + ref on A 产 A gold (8 HDBC→HFS) 一致

## 选料过程 (r1030)
- 快照: `summary_1120_reconstructed.tsv` (ssh_eda_search_20261120_145529, sessions=5457)
- D-pure 过滤 (dominant kw = netlist/schematic/analog/waveview/verilog/cmos/.spi/.cdl, 排 hspice/finesim/spectre/siliconsmart), mc 10-120
- 高 mc (118-120) fresh 候选深读 4 个全部不可造:
  - 91zh8 (alexli mc118 netlist): 实为 finesim 4-corner setup/hold 优化 (B spice_sim), 且是 continuation 会话无干净 U#0
  - exucf (eva1li mc118 verilog): D 域 verilog errforcebit 意义 Q&A, **但已被 shard A 造为 ErrforcebitMeaningQA-001 (2026-11-20)**, claim REFUSED
  - 11voz (joeyl mc116 netlist): 实为 WCKTop CML 5-corner 高频放大 spice 调优 (B spice_sim), 且与 r1021 lbkmz (NetlistUlvtDelvtoInject-001) 同用户同 WCKTOP 主题 near-dup
  - 3x37w (taodu mc114 netlist): 实为 A/B 两 DRAM 项目 si.inp 仿真设定对比 + SPF 寄生 RC partition 分析 (B spice_sim)
- 降 mc 89-95 找 fresh D-pure, 多为 skill-creator meta-work (a076c yunfat "写个skill测量datapath margin") / live-tool 依赖 (5qv7f hao23c "你能看到当前打开的waveview视图吗" 需 live WaveView bridge) / 已 case (euwld clarawu Ron near-dup)
- 最终挑 **3lnsm (lorikx mc94 verilog)**: U#0 纯需求轮 (评估 lint 工程哪些文件需修改以跑最新版), verilog lint 工程 filelist 版本漂移审计, D-pure, fresh (4-shard union ledger 0 命中), trace 86 msgs 适中, deliverable 可造有牙 check() (subprocess 真跑 + 结构断言 + 独立 _gt 重算 + anti-hardcode)
- ledger 3lnsm claim ✓ (status=claimed, 待 r1031 mark case)

## DEBT
- r1031 第一件事: 合成 LintFilelistVersionAuditProduce-001 (本 deepread 已铺路, 跳过深读步骤直接合成)
- discuss 配额: next due r1033 (r1029 清付后, r1030 selection 轮顺延不计 case 轮)
- PUSH-BLOCKED 仍待 infra 恢复 (origin/main broken-path ops commit f2b027e87 + non-ff; 守 2026-11-02 纪律不硬 rebase)
