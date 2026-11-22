# Deepread: 1795138311750_tahks (cyrusrao @ hfeg0plg93)

## 基本信息
- **session**: 1795138311750_tahks
- **user**: cyrusrao
- **host**: hfeg0plg93 (10.129.8.225)
- **match_count**: 260
- **domain**: layout_aether
- **sub_type**: schematic_hierarchy_signal_trace_impact_analysis
- **messages**: 165 msgs, 673KB

## 用户真实意图 (msg[0])
> 我需要你帮我确认一下cm0_ro_BLCom这个testmode在DSCQA这个项目中会产生的影响，当他使能时为高电平。这个项目的library是/proj/dscqa/V0/libs/dscqa_top，cell是DDR6TOP

用户指定了 schematic hierarchy 路径：DDR6TOP_R → Array32GTop_0 → Array16G_PSD0 → Array2G_PSD0_BGAB → Array2G_PSD0_BGTopX2 → BnkGTopx1_BG0 → D_BankLogic_B0 → R_RasBnkLogic → R_RasBase_lv，要求分析 testmode=高 时对 Xdec 模块 PreEq 和 Iso 输出的影响。

## Assistant 工具链
1. **pyAether API 检索** (msgs 10-30): search_apis/get_api_details 查 dbOpenLib/dbOpenCV/dbTraverseGetHierNets/emyFigGroupGetAllPinNets/aeGetInstHier/dbOpenCVByType/emyLib.find/emyCellViewFind
2. **pyAether 库加载尝试** (msgs 45-130): 反复尝试 emyInitAether/emyInitDb/emyLibDefList.openLibs/dbOpenLib/dbOpenCVByType 打开 dscqa_top 库 —— **失败**：沙箱 CWD `/proj/drvsa/V0/workdir/cyrusrao` 有 cds.lib 指向 drvsa 项目，覆盖了 CDS_LIB_DEF_FILE 环境变量。尝试 chdir/重命名 cds.lib/subprocess/shell-runner 均未解决。
3. **strings+grep 直接搜 OA 二进制** (msgs 132-153): 改用 `strings __emy+__.1 | grep -E "..."` 在 `/proj/dscqa/V0/libs/*/.../schematic/__emy+__.*` 上提取信号名 —— **成功**。
4. **editor + run_approved_command(shell-runner)** (msgs 138-153): 写 .sh 脚本执行 strings/grep 搜索。

## 关键发现
- `cm0_ro_BLCom` 信号经多层 hierarchy 传播后变成 `cm0_ro_BLComEnInput`、`cm0_ro_BLComEnBot`、`cm0_ro_BLComEnTop`、`cm0_ro_BLComEnSec0~47`、`cm0_ro_BLComEnGap1~48` 到达 `XdecGapTop_DSCQA`
- `XdecGapTop_DSCQA` 同时包含 `PreEqSec0~47` 和 `Iso` 相关信号
- 结论：**testmode 高电平直接影响 Xdec 的 PreEq 和 Iso 输出** (DIRECT impact)

## 最终交付
Markdown 分析报告 (msg 164-165)，含证据表、信号可达性分析、影响判定。

## Case 合成
- **case_id**: EDA-Eval-DesignFlow-TestmodeImpactTrace-001
- **reframe**: 离线 manifest 信号追踪 —— OA schematic hierarchy 数据提取成 `schematic_hierarchy_manifest.json`（cells/ports/nets/instances/port_map），SUT 编写 `testmode_impact_tracer.py` 做 BFS 路径查找 + port_map 信号追踪 + 派生信号/受影响输出识别
- **visible A**: DSCQA/cm0_ro_BLCom → XdecGapTop_DSCQA, PreEq(24 sections)+Iso
- **hidden B**: DRVQA/cm1_ro_WlIso → XdecGapTop_DRVQA, SaPch(16 sections)+IsoVdd (DIRECT, 不同 project/signal/scale)
- **hidden B2**: cm2_dbg_TmgSel 不到达目标 → NO_IMPACT
- **17 assertions** (≥8): 结构3 + B内容7 + B2内容2 + 反硬编1 + 确定性1 + 退化3
- **3 negative samples**: neg_empty/neg_echo/neg_hardcode_a (ALL FAIL)
- **§4.9 (a)(b)(c)**: empty_zip/echo_stub/hardcode_A (ALL FAIL)
- **3-seed determinism**: sorted(set()) 去重保证跨进程一致

## 验证结果
- Reference solution: 17/17 PASS
- Negative selftest: 3/3 correctly FAIL
- check.py exit=0 on reference, exit=1 on all negatives
