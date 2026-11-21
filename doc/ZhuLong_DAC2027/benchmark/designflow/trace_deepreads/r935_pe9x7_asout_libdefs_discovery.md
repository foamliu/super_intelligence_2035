# r935 · pe9x7 deepread · Aether asOut stream-out + lib.defs discovery

## 选料
- **sid**: `1795165924170_pe9x7` · felixw @ hfeg0pkn004 (10.129.2.13) · mc=59
- **keywords**: drc:133 / lib.defs:80 / aether:63 / cmos:40 / pyaether:30 / .gds:29 / calibre:9 (C-dominant physical_verify)
- **fresh check**: 4-shard ledger 0 hit + 4-shard jsonl trace_source 0 hit ✓ (claim r935)
- **size**: 92KB / 33 msgs (19 user / 14 assistant) / 8 SandBox_MCP_Server__run_code + 4 run_approved_command + 3 read_files + 2 list_allowed_files
- **date**: 2026-11-20 15:0x (single-turn)

## 真实意图 (msg #0)
felixw (CXMT DRGQX layout engineer) 想跑一个 calibre DRC，所有文件放在 `/proj/drgqx/V0/agentdir/felixw/DRC_test` 下；目标 cell = `A_felixw_test` lib 下的 `test1` cell。明确给出 asOut 命令模板：
```
asOut -lib $libName -cell $cellName -view $viewName -gds $gdsfile -logFile $strmOut.log \
  -convertPinTo geometryAndText -maxVertex 4000 -layerMap $layerMap -text cdba \
  -subMasterInfix _CDNS_ -objMap $objMap > /dev/null 2>&1
```
参数解析规则：libName/cellName 必须用户提供（缺失提醒）；viewName 默认 `layout`（默认时提醒用户）；gdsfile 默认 `<drc_dir>/<topCell>.gds`；layerMap 通过 Aether python console `print(leGlobalVariables.layerMap)` 查询；objMap 由 layerMap 路径去掉最后一级文件名替换为 `object.map`。
用户最后说：「你先帮我抽一个gds看看，能抽出来我们继续下面的步骤」—— 单轮任务，止于 stream-out 成功。

## trace gold (msg #1–#32)
1. **msg #1**: agent 解析需求，列出已知/未知参数，提醒 viewName=layout 默认值，调用 `run_approved_command` (失败: "Dynamic profile 'shell-runner' requires filePath") + `SandBox_MCP_Server__run_code` (pyAether `print(leGlobalVariables.layerMap)`)
2. **msg #3**: layerMap 查到 = `/apps/imctf/libs/dfii/cxmtG4C/current/layer.map`；objMap 推导 = `/apps/imctf/libs/dfii/cxmtG4C/current/object.map`
3. **msg #5–#14**: agent 多次 run_approved_command 失败（policy-engine 限制：filePath outside dynamicFileRoots），转用 SandBox_MCP_Server__run_code + read_files + list_allowed_files 探查 DRC_test 目录
4. **msg #18**: 确认 `asOut` 可执行 (`/apps/empyrean/tools/aether_new/bin/asOut`)；pya 不可直接 import；PATH 含 calibre/2022
5. **msg #19**: agent 构造完整 asOut 命令（无 -libDefFile）通过 pyAether subprocess 调用 → **msg #20 报错**: `ERROR: (ASSTRM-10009): Cannot read library A_felixw_test in lib.defs because it is not open or it does not exist.`
6. **msg #21–#29**: agent 诊断 → `find /proj/drgqx -name lib.defs -maxdepth 4` 找候选；查每个 lib.defs 是否含 `A_felixw_test` DEFINE 行 → `/proj/drgqx/V0/lib.defs` 不含；**`/proj/drgqx/V0/workdir/felixw/lib.defs` 含** `DEFINE A_felixw_test /proj/drgqx/V0/workdir/felixw/A_felixw_test` + `ASSIGN A_felixw_test libMode shared`
7. **msg #30**: agent 重新跑 asOut **加 -libDefFile /proj/drgqx/V0/workdir/felixw/lib.defs** → exit 0, 0 errors, 58 warnings, GDS 2048 bytes, 1.94 秒 → ✅ stream-out 成功
8. **msg #32**: agent 汇总参数表 + 结果统计

## trace gold 知识点
- **asOut 命令完整签名** (10 个 flag): `-lib` `-cell` `-view` `-gds` `-logFile` `-convertPinTo geometryAndText` `-maxVertex 4000` `-layerMap` `-text cdba` `-subMasterInfix _CDNS_` `-objMap` (本 case 额外学到 `-libDefFile`)
- **layerMap 查询**: `print(leGlobalVariables.layerMap)` → 返回 PDK layer.map 绝对路径
- **objMap 推导**: dirname(layerMap) + "/object.map"
- **lib.defs 发现**: ASSTRM-10009 表示 lib 不在当前 lib.defs 搜索路径 → `find <root> -name lib.defs` + 逐文件 grep `DEFINE <libName>` → 命中文件即为 -libDefFile 值
- **lib.defs 语法**: `DEFINE <libName> <path>` + `ASSIGN <libName> libMode shared` + `INCLUDE <path>` + `##SOFTINCLUDE <path>`
- **viewName 默认 + 提醒**: 用户未指定时使用 `layout` + 在参数报告中明确提醒

## 跨 shard 串台检查
- 4-shard ledger pe9x7 仅 C；4-shard jsonl trace_source 无 pe9x7 ✓
- 同 domain (physical_verify) 已落库 case 全正交：
  - CalibreDrcLayoutPathBlankDiag-001 (gohxq felixw r930) = "Layout Path cannot be blank" runset 根因诊断 — 不同 bug、不同工具（calibre -gui -drc -batch）
  - CalibreDrcRunsetConfigValidator-001 (wv66o felixw r909) = calibre DRC runset 配置校验
  - PyAetherBridgeDiagClassifier-001 (930zw felixw r933) = pyAether 沙箱 bridge 协议诊断
  - LvsPinCaseMismatchDiag-001 (felixw) = LVS pin 大小写不匹配
  → 本 case 子型 "aether_asout_libdefs_discovery" 首例，与 calibre runset/bridge/lvs 全正交 ✓
- felixw 已有 4 case (DRGQX layout engineer 真实多任务，非凑数)

## reframe 决策 (档 B fixture-driven)
- A 档不可行：live workdir READ-ONLY + Aether/calibre license + SUT 沙箱无 asOut 二进制
- B 档 ACCEPT：把 "asOut 命令构造 + lib.defs 发现" 抽成离线 Python `asout_planner.py`，SUT 不需跑 asOut，只需产出结构化 plan.json
- 真实意图保真：用户 prompt 用 felixw 真实场景（libName/cellName/drc_dir/layerMap 查询/objMap 推导/lib.defs 发现/-libDefFile 修复 ASSTRM-10009）

## A/B 差异化（5 维全异）
- libName: A=`A_felixw_test` / B=`B_qa_test`
- cellName: A=`test1` / B=`dq4`
- PDK layermap: A=`/apps/imctf/libs/dfii/cxmtG4C/current/layer.map` / B=`/apps/imctf/libs/dfii/cxmtG5/current/layer.map`
- lib.defs 候选数: A=3 (only #3 含 lib) / B=4 (only #2 含 lib, 不同位置破"always last"硬编)
- drc_dir: A=`/proj/drgqx/V0/agentdir/felixw/DRC_test` / B=`/proj/drgqx/V0/agentdir/qa_user/drc_run`

## 交付
- case-id: `EDA-Eval-DesignFlow-AetherAsoutLibDefsDiscoveryPlanner-001`
- domain: physical_verify
- k_check 预计 ≥16 (结构 + 参数解析 + lib.defs 发现 + 反硬编 + 3-seed + 反 delete-core)
