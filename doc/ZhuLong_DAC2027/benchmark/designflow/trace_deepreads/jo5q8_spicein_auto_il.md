# trace_deepreads/jo5q8_spicein_auto_il.md · shard B · 2026-11-10 11:0x

## trace 来源
- sid: `1793272819713_jo5q8`  user: `sierraw`  host: `hfeg0plg76` (10.129.8.124)
- summary.tsv: mc=116, keywords `.cdl:816;virtuoso:424;netlist:408;schematic:352;hspice:125;pdk:122;spectre:110`
- 工具计数: netlist 356 / schematic 280 / spectre 88 / hspice 88 / virtuoso 71 / cellview 23 / pyAether 15 / skill 3
- domain: **characterization**（CDL→cellview 反标回库，Virtuoso SpiceIn）
- mtime: 2026-10-30（≥10-28 时间窗 ✓）
- messages.json: 584KB / 119 msgs（live session 已 GC，从 snapshot hourly-new.2026-11-10_0700 取回）

## 用户轮（4 条 user turns）
- **U#0 (msg 0)**「我现在在virtuoso中通过CIW窗口点击File-Import-Spice，在Input中填上包含所有cell的总CDL文件路径，Output填入电路库名，在Overwrite Cells中选择覆盖所有cell。简单来说是将cdl反写回cell改变电路结构，能写个.il文件实现这个功能吗」→ **CLEAN produce-task** ✓（提出需求，未给根因/修复）
- U#1 (msg 82)「帮我在virtuoso中尝试，目前virtuoso已启动，在V0_FS_Virtuoso_test环境下，库是FSP51H204L6W35T6_MB_ULVT_schematic，cdl在/proj/lacaa/.../FSP51H204L6W35T6_MB_ULVT.cdl」→ 给真实路径/环境
- U#2 (msg 92)「告诉我写skill脚本在哪里？」→ 问脚本位置
- U#3 (msg 99)「skill脚本位置用法和目的明确写明，整理test路径」→ 要求文档化+整理

## assistant 工具链（关键发现路径）
1. skills/RAG 检索 `spiceIn` → 无命中 → 降级查 CAD 源码
2. run_approved_command/editor 写 find_spicein.py 递进探查 IC6.1.7 安装目录
   - 定位 CDSHOME=`/apps/cdsmgr/CRB/IC617ISR23`
   - 读 `doc/sktransrefOA/skspicein.html` + `transrefOA/chap3.html`/`appC.html` → 拿到 spiceIn 命令行用法 + 参数文件格式（`overwriteCells "all"`）
3. 读官方示例 `tools/dfII/samples/spiceIn/param.il` + CIW 菜单 `ciw.menus` + `spiceInGui.cxt` 字符串表
   - **关键发现**：GUI 内部 = `spcinGuiDisplay()` 建表单 → 点 OK 后 `_spiceInCB()` 写 `/tmp/spiceInParam.il` → `ipcBeginProcess("spiceIn -gui -param /tmp/spiceInParam.il")`
   - Virtuoso 里没有注册成 SKILL 函数的直接导入 API（只有 GUI 表单函数）
4. editor 写 `spiceIn_auto.il`（msg 62-72 增量构建）+ 静态验证（ASCII/括号配平）
5. U#1 后用真实路径核对：CDL 79KB/12 subckt/1116 MOS（model 仅 nulvt_fs/pulvt_fs）；目标库 12 cell 与 CDL 一一对应
6. 找到上次 GUI 成功日志 `spiceIn.log` → 复刻参数（refLibList=`35HFS + 输出库自身`, language=spice, simName=spectre, overwriteCells=all）
7. 更新脚本配置 + 写中文 README + 整理到 `spiceIn_test/` 目录

## 金标准
- **真实 .il**：`/home/sierraw/spiceIn_auto.il`（17834B / 381 行，已 scp 提取到 workdir）
  - 配置 DPL `spiceInAutoCfg`（netlistFile/outputLib/refLibList/language/overwriteCells="all"/...）
  - IPC handler 三件套（`spiceInAutoDataHandler` 流式输出 / `spiceInAutoErrHandler` / `spiceInAutoPostHandler` 报 exit status + 归集 c2s 日志）
  - 主过程 `spiceInAuto(?cfg ?wait ?noAsg)`：校验必填 → 建 outputLib → 写 `/tmp/spiceInParam_<lib>_<pid>.il` → 定位 `$CDSHOME/bin/spiceIn` → `ipcBeginProcess("spiceIn -param <paramFile>")`
  - 便捷封装 `spiceInAutoMB` / `spiceInAutoBase` / `cdlIn` / `batchCdlIn`
- 真实 CDL 在 `/proj/lacaa/V0_FS_Virtuoso_test/...` → e0031982 无权限读 → **按文档化结构 B-synthesized 资产**

## case 取舍（B-synthesized L1）
- 取可测试核心：**参数文件生成 + 命令构造 + 必填校验 + overwriteCells=all**
- deliverable = Python 工具 `spicein_param_gen.py`（check.py 无法执行 SKILL，故取 Python 复刻 gold-standard 的 fprintf 参数文件生成块）
- 真跑候选：check.py 在隐藏 B1/B2 配置上 subprocess 执行候选脚本，断言 14 项独立条件
- 隐藏 B：B1(MultiBank_8T_SVT, language=spice, simName=spectre) / B2(CacheCell_12T_ULVT, language=cdl, simName=hspiced, topCell="") — 反硬编码 + 交叉泛化
- 6 negative（naive_empty/hardcoded_a/no_overwrite/only_print/ref_core_deleted/empty_shell）全 FAIL
- §4.9 三假：empty_shell→c / only_print→c / ref_core_deleted→h 全 FAIL
- 断言门 k_rationale=k_check=14≥8 ✓；test 字段与盘上 check.py 字节同步 ✓

## 结论
jo5q8 = CLEAN produce-task（U#0 提需求未给根因）→ characterization B-synthesized L1 → 交付 EDA-Eval-DesignFlow-SpiceInAutoIl-001。
