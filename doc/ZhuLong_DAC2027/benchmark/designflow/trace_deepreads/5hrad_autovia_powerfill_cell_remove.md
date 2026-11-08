# 深读笔记 · 5hrad · autovia/powerfill 生成 cell 识别与清除

- **trace_source**: user=e0014566, host=hfeg0pkn005 (10.129.2.14), session_file=1787318451519_5hrad.messages.json, match_count=328
- **_msgs_: 266（1 个 user 轮 + 265 assistant/tool_result）· 文件 939KB · 2026-04-14（基于 sid 时间戳 1787318451515）
- **域名判定**: analog_context（analog layout cellview 上下文：识别 autovia/powerfill 自动生成的 cell 并从 layout 中清除）；兼涉 schematic_netlist（cell/instance 结构操作）

## 用户原始意图（唯一 user 轮，逐字）
> 请你识别到 Library: auto_austin_case1,  cell: BCenterCA_rscalc , 中 layout 的布局，识别出  autovia 和 powerfill 生成的cell, 并把这些 cell 去除。

## 真实任务脉络
1. **库/单元**: `auto_austin_case1 / BCenterCA_rscalc / layout`（lib 路径 `/proj/train/V0_Austin/workdir/e0014566/auto_austin_case1`，cds.lib 定义）
2. **实例规模**: 234 个 top-level instance，77 个 unique lib/cell pair
3. **识别规则（从 autovia/powerfill runner 脚本与日志反推）**:
   - autovia 生成 cell：cell 名含大写 `VIA` 且带 8 位日期后缀 `YYYYMMDD`（如 `BCenterCA_20250619_VIA_TOP`、`M3VIA_20250621_CAP`）
   - powerfill 生成 cell：cell 名含 `power_fill` / `powerfill` / `improve`（如 `BCenterCA_vddqca_improve`、`I_signal_power_fill_vdd`）
4. **陷阱 cell（名字像但手画，必须保留）**: `INVIA_hand_rx`（含 VIA 无日期）、`VIA_TEST_manual`（VIA 无日期）、`powerdown_ctrl`（含 power 非 fill）、`power_ring_hand`（power 非 fill）
5. **匹配结果**: 8 个 autovia/powerfill instance（3 autovia + 5 powerfill）待删除
6. **pyAether API 链**: `emyInitAether` → `emyInitDb` → `aeOpenDesign(lib,cell,view,mode)` → `emyGetAllInstHeaders(design)` → 遍历 `emyInstHeader.cellName/libName/instName` → `dbDelete(header)` → `dbSaveCV(cv,lib,cell,view)`
7. **执行路径**: pyAether sandbox 与 SKILL sandbox 均一度不可用 → 转用命令行 Virtuoso batch（`-nocdsinit` + 手工 `LD_LIBRARY_PATH` 含 OpenAccess 64-bit lib + 自建 cds.lib）跑 SKILL 脚本 `remove_autovia_powerfill.il`
8. **结果**: 8 个 instance 删除成功，`layout.oa` 保存（21:57 修改时间），验证脚本确认 234→226，剩余 autovia/powerfill=0，**SUCCESS**
9. **结尾**: msg#265 assistant 给出完成总结（识别/删除/保存/验证全闭环），无用户后续回复（会话于成功后结束）

## 合成判断
- **不适用 A 档**：trace 仅 1 个 user 轮且为单一意图（虽任务完成，但无多轮 user 反馈/接受记录可佐证 A 档所需的「用户接受迭代」信号）
- **适用 B 档**：提取语义主题 = 「给定 layout cellview spec + instance 清单，用 pyAether API 链打开→枚举 instance→按命名规则识别 autovia/powerfill 生成 cell→dbDelete 删除→dbSaveCV 保存→出 removal 报告」
- **可离线判分**：pyAether API（aeOpenDesign/emyGetAllInstHeaders/emyInstHeader/dbDelete/dbSaveCV）可被 Python mock 录制 stub 替换（mock 读 instance_manifest.json 构建 header 列表，录制所有调用到 __rec.json）；判分用 subprocess `python3` 跑候选 + mock，断言录制 + removal_report.json 结构
- **真跑候选**: mock 录制 = 候选确调用真 pyAether API 调用链（L2，非纯离线文本匹配）
- **反硬编码**: 隐藏 B 换 lib/cell（auto_austin_case2/BCenterDQ_rscalc）+ 不同 instance 清单（221 vs 189）+ 不同 autovia/powerfill 计数（11 vs 8）+ 不同陷阱 cell，候选须读 spec.json 参数化执行

## 金标准（合成）
- A: lib=auto_austin_case1, cell=BCenterCA_rscalc, 189 instance, 删 8（3 autovia: BCenterCA_20250619_VIA_TOP/BCenterCA_20250620_VIA_M2/M3VIA_20250621_CAP + 5 powerfill），4 陷阱（INVIA_hand_rx/VIA_TEST_manual/powerdown_ctrl/power_ring_hand），剩 181
- B (hidden): lib=auto_austin_case2, cell=BCenterDQ_rscalc, 221 instance, 删 11（4 autovia: BCenterDQ_20250702_VIA_M1/BCenterDQ_20250703_VIA_M3/VIA_20250704_M4_DQ/BCenterDQ_20250705_VIATOP + 7 powerfill），5 陷阱（INVIA_hand_dq/VIA_RDQ_manual/powerdown_ctrl_dq/power_ring_hand_dq/VIAdq_hand），剩 210（与 A 全不同）

## 选料决策
- fresh（台账无 5hrad）· mc=328 · analog_context 域（覆盖 50，本 case 增 1）· 真实 autovia/powerfill cell 清除场景保真度高 · 与 #395 RsCalcFlow-001（autovia/powerfill 生成/优化 flow 编排）方向相反（清除 vs 生成），不重复
- pyAether layout API 链已用 pyAether.get_api_details 验证（aeOpenDesign/emyGetAllInstHeaders/emyInstHeader/dbDelete/dbSaveCV/emyInitAether/emyInitDb/emyString 均为 canonical 名）
