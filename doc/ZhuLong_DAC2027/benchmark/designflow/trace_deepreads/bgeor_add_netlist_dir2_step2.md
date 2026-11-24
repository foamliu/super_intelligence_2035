# Deepread: bgeor — Add Netlist_Dir2 + Netlist_File2 to DDR5 Sim Tool (Aging Sim Step2)

## trace_source
- **session_file**: `1795438412247_bgeor.messages.json`
- **user**: rongjiez
- **host**: hfeg0plg58 (also on plg54/53/52/43/15/pkn005/pkn002/pjn170)
- **match_count**: 59 (netlist:547;analog:3;verilog:1)
- **domain**: schematic_netlist (D shard)
- **size**: 109 msgs / 457KB
- **codebase**: `/home/rongjiez/sos_wv/dsim_coverage/` (Qt/C++ DDR5 sim coverage tool, NOT git)

## 真实意图 (2 轮对话)
用户 rongjiez 在维护一个 DDR5 仿真覆盖率 Qt 工具。后台脚本 `matrixrun` 有 aging-sim Step2 路径。

**第 1 轮**: 在 `DDR5SimOptions` 前端的 Aging Sim → Step2 区域新增 `Netlist_Dir2` 参数（参照已有 `Netlist_Dir`），脚本输入参数 `-nr2`。不考虑 `Netlist_Link`。
**第 2 轮**: 再加 `Netlist_File2`（对应 `Netlist_Dir2`，参照 `Netlist_File` 对应 `Netlist_Dir`），脚本参数 `-nl2`。

## agent 工作流
1. `list_allowed_files` 探索 codebase → 发现 5 个关键文件
2. 创建 `_grep.py` 辅助脚本搜索 `runMatrixAgingSim`/`Netlist_Dir`/`AgingSimStep2` 等
3. `read_files` 精读 mainwindow.cpp (slot_simOptionsClicked/slot_simOptionsApplied/runMatrixAgingSim)、ddr5simoptions.cpp (initUI/slot_updateNlFile/OK-clicked)、ddr5simoptions.ui (gridLayout_AgingSimStep2)
4. `editor` 工具做 10+ 处编辑，跨 5 文件
5. 清理临时脚本

## 关键产物 (修改的 5 文件 + 具体改动)

### mainwindow.h (241 行)
- 新增成员: `QString Netlist_Dir2;` (在 Netlist_Dir 后) + `QString Netlist_File2;` (在 Netlist_File 后)

### mainwindow.cpp (3359 行)
- `slot_simOptionsClicked()` DDR5 分支 (line ~415): `OptionInfo<<AgingSimStep2CtrlFile<<AgingSimModel<<AgingSimReltotalTime<<Netlist_Dir2<<Netlist_File2;`
- `slot_simOptionsApplied()`: 新增 `else if(name=="Netlist_Dir2"){Netlist_Dir2=value;}` + `else if(name=="Netlist_File2"){Netlist_File2=value;}`
- `runMatrixAgingSim()` 两条分支 (Netlist_Link!=空 / ==空): aging 段尾追加 `-nr2 %17 -nl2 %18`，`.arg(...)` 链尾追加 `.arg(Netlist_Dir2).arg(Netlist_File2)`

### ddr5simoptions.h (55 行)
- 新增 `void slot_updateNlFile2(const QString &dirName);`

### ddr5simoptions.cpp (715 行)
- 构造函数: `connect(ui->comboBox_NlDir2,SIGNAL(currentTextChanged(QString)),this,SLOT(slot_updateNlFile2(QString)));`
- `initUI()` AgingSim 分支: `ui->comboBox_NlDir2->clear(); addItems(getNetlistDirList());` + 读 `OptionInfo.value(20)`(NlDir2)/`value(21)`(NlFile2) 回填 + `slot_updateNlFile2(...)` 联动填充 NlFile2
- 新增 `slot_updateNlFile2()`: 仿 `slot_updateNlFile`，扫 `/proj/<proj>/<ver>/simdir/finesim/<proj>F/Netlists/<dir>` 填充 `comboBox_NlFile2`
- `slot_pushButton_OK_clicked()`: 读 `NetlistDir2`/`NetlistFile2`，simOptions 追加 `<<"Netlist_Dir2;"+NetlistDir2<<"Netlist_File2;"+NetlistFile2` + 非空校验

### ddr5simoptions.ui (911 行)
- `gridLayout_AgingSimStep2` row 4: label_22 "Step2 Netlist Dir:" + comboBox_NlDir2
- row 5: label_23 "Step2 Netlist File:" + comboBox_NlFile2

## 判分内核离线化设计
**deliverable**: `outputs/submit.zip` 含 `patch_netlist_dir2.py` — 给定 codebase 目录，自动完成上述 5 文件改动。
**A (visible)**: 原 codebase 5 文件 (需从 .75 当前 modified 版本 reverse agent diffs 还原 original)。
**B (hidden)**: 变体 codebase — 同结构但标识符改名 (Netlist_Dir→NlDirectory, comboBox_NlDir→cmbNlDir, -nr→--netlistdir, getNetlistDirList→getNlDirectoryList, gridLayout_AgingSimStep2→gridAgingStep2 等)，使硬编码 A 的精确 patch 在 B 上 FAIL。
**check()**: 在独立 tmpdir 解 zip → `subprocess` 在 B 上跑 `patch_netlist_dir2.py <B_dir>` → regex/AST 解析 B 修改后 5 文件，断言结构属性。

### k_check 草案 (13 条断言 ≥8 ✓)
① mainwindow.h 声明 Netlist_Dir2 + Netlist_File2 成员变量 (QString)
② mainwindow.cpp slot_simOptionsClicked OptionInfo 链含 Netlist_Dir2 + Netlist_File2 (AgingSim 分支)
③ mainwindow.cpp slot_simOptionsApplied 有 name=="Netlist_Dir2" 解析分支
④ mainwindow.cpp slot_simOptionsApplied 有 name=="Netlist_File2" 解析分支
⑤ mainwindow.cpp runMatrixAgingSim 两条分支 (Link!=空 / ==空) 均含 -nr2 flag
⑥ mainwindow.cpp runMatrixAgingSim 两条分支均含 -nl2 flag
⑦ runMatrixAgingSim .arg() 链尾含 .arg(Netlist_Dir2).arg(Netlist_File2) (两分支)
⑧ ddr5simoptions.ui 含 comboBox_NlDir2 widget 定义
⑨ ddr5simoptions.ui 含 comboBox_NlFile2 widget 定义
⑩ ddr5simoptions.cpp 含 slot_updateNlFile2 定义 (函数体非空)
⑪ ddr5simoptions.cpp initUI 在 AgingSim 分支 populate comboBox_NlDir2 (clear+addItems)
⑫ ddr5simoptions.cpp OK-clicked simOptions 含 "Netlist_Dir2;"+.. + "Netlist_File2;"+..
⑬ ddr5simoptions.h 声明 slot_updateNlFile2
+ 3-seed 随机: 对 B 做 3 次微扰 (改现有 param 名/行号偏移) 跑 patch，结论一致

### negative (2 个错解全 FAIL)
- `fake_print_only`: 脚本只 print "done" 不改文件 → 13 断言全 FAIL (文件未变)
- `fake_core_deleted`: 脚本只 touch 5 文件不加内容 → 同上

## 下轮合成 ETA
- 还原 A: scp 5 modified 文件 → reverse 10+ diffs (trace 有精确 diff) → original A
- 造 B: sed 批量改名 (Netlist_Dir→NlDirectory 等 ~15 个标识符) 在 A 副本上
- check.py: 13 regex 断言 + subprocess 跑 patch + 3-seed
- negatives + selftest
- 预计 1 轮可交付

## domain 判定
netlist:547 keyword 主导 → schematic_netlist (D)。codebase 是 netlist 仿真工具，新增 netlist 目录/文件参数属 netlist 配置管理。✓ D 归属。
