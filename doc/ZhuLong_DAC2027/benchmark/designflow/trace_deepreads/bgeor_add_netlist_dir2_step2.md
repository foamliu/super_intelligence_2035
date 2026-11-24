# Deepread — bgeor: Add Aging-Sim Step2 Netlist_Dir2(-nr2) + Netlist_File2(-nl2) to DDR5 sim Qt tool

> **重建说明**：r1246 深读笔记文件丢失 + session 文件 `1795438412247_bgeor.messages.json` 已在 hfeg0plg58 上被清理（2026-11-24 复测 `No such file`）。本笔记由 **codebase ground truth**（`/home/rongjiez/sos_wv/dsim_coverage/`，5 个 Nov-24 修改文件）+ r1246 daily 摘要重建。codebase 仍存活（2026-11-24 10:26 复测 OK）。

## trace_source
- user: rongjiez
- host: hfeg0plg58
- session_file: 1795438412247_bgeor.messages.json（已清理，不可复读）
- match_count: 59（netlist:547; analog:3; verilog:1）
- domain: schematic_netlist（D）
- real_task_summary: 用户在 DDR5 sim Qt 工具（`/home/rongjiez/sos_wv/dsim_coverage/`，dsim.pro 工程）新增 Aging-Sim **Step2** 的 `Netlist_Dir2`(-nr2) 与 `Netlist_File2`(-nl2) 两个 netlist 选择项，使 matrixrun 第二段 aging sim 可独立指定 netlist 目录/文件。agent 用 editor 精确编辑，2 轮对话（第1轮 Dir2，第2轮 File2），跨 5 文件 10+ 处改动，模式完全镜像已有 Step1（`Netlist_Dir`/-nr/`comboBox_NlDir`/`slot_updateNlFile`）。

## 5 文件 Step2 增量清单（exact，重建 A 的依据）

### 1. `ddr5simoptions.h`（成员/slot 声明）
- L23 区: `QStringList getStep2ModelList();` 声明
- L36 区: `void slot_updateNlFile2(const QString &dirName);` 声明（紧跟 `slot_updateNlFile` 后）

### 2. `ddr5simoptions.cpp`（UI init + slot 实现 + 输出收集）
- L30: `connect(ui->comboBox_NlDir2, SIGNAL(currentTextChanged(QString)), this, SLOT(slot_updateNlFile2(QString)));`
- L61: `QStringList step2ModelList = getStep2ModelList();`（initUI 内）
- L120-121: `ui->comboBox_NlDir2->clear(); ui->comboBox_NlDir2->addItems(getNetlistDirList());`
- L148: `ui->comboBox_NlDir2->setCurrentText(NlDir2);`
- L150: `slot_updateNlFile2(ui->comboBox_NlDir2->currentText());`
- L153: `ui->comboBox_NlFile2->setCurrentText(NlFile2);`
- L363-392: `slot_updateNlFile2(...)` 整段实现（clear comboBox_NlFile2 → 扫目录加 fileName → count==0 则 setEnabled(false)）
- L533-536: AgingSim && comboBox_NlDir2 非空时的 link 路径 `.arg(...NlDir2...NlFile2)`
- L560-562: `NetlistDir2`/`NetlistFile2` 局部变量 + `simOptions<<"...Netlist_Dir2;"+NetlistDir2<<"Netlist_File2;"+NetlistFile2`
- L673+: `getStep2ModelList()` 实现

### 3. `mainwindow.h`（成员变量）
- L84: `QString Netlist_Dir2;`
- L86: `QString Netlist_File2;`

### 4. `mainwindow.cpp`（OptionInfo 收集 + 解析 + matrixrun 命令）
- L415: `OptionInfo<<AgingSimStep2CtrlFile<<AgingSimModel<<AgingSimReltotalTime<<Netlist_Dir2<<Netlist_File2;`（AgingSim 分支内）
- L474-477: `else if(name=="Netlist_Dir2") Netlist_Dir2=value; else if(name=="Netlist_File2") Netlist_File2=value;`
- L953/955 与 L958/960: matrixrun 命令串追加 ` -c2 %15 -f2 %16 -nr2 %17 -nl2 %18 ` 及对应 `.arg(...Netlist_Dir2).arg(Netlist_File2)`（两条分支：Netlist_Link 非空/空）

### 5. `ddr5simoptions.ui`（Qt Designer XML，26KB）
- L518: `<widget class="QComboBox" name="comboBox_NlDir2">` 整块（属性+布局 item）
- L556: `<widget class="QComboBox" name="comboBox_NlFile2">` 整块
- （可能还有 label widget、layout stretch 调整 — 合成时需 dump L500-600 完整段核对）

## A 还原方案（A = Step1-only 起点，给 SUT）
从 modified 5 文件按上述清单**逐项删除** Step2 增量即得 A。删除点均为局部行/块，不涉及 Step1 逻辑改动。注意：
- `.ui` 删除两个 comboBox widget 块时需同步删除其父 layout 内对应的 `<item>`/`<widget>` 节点，保持 XML 合法。
- mainwindow.cpp L415/474-477/953-960 删除后，AgingSim 分支仍保留 Step1 + AgingSimStep2CtrlFile/AgingSimModel/AgingSimReltotalTime（这些是 Step1 已有的 aging 参数，**不是** Step2 增量）——核对时只删 `Netlist_Dir2`/`Netlist_File2`/`-nr2`/`-nl2`/`%17`/`%18` 及其 `.arg`，**保留** `-c2 %15 -f2 %16`（这些是 Step1 aging 已有的 Step2 控制文件/模型文件参数，命名混淆需小心）。
  - ⚠️ 命名陷阱：`-c2`/`-f2` 是 **Step1 已有** aging 参数（AgingSimStep2CtrlFile/AgingSimModel 相关），**不是** bgeor 本轮新增。bgeor 新增仅 `-nr2`/`-nl2` + `Netlist_Dir2`/`Netlist_File2`。还原 A 时**保留** `-c2 %15 -f2 %16`，**只删** `-nr2 %17 -nl2 %18` 与对应 `.arg(Netlist_Dir2).arg(Netlist_File2)`。

## B 变体方案（hidden，sed 批量改名 Step1 标识符）
B 必须与 A **结构相同但 token 不同**（不是换文件名）。对 A 全 5 文件 sed 改名（同步改 Step2 目标 token，使候选脚本必须泛化）：
| A token | B token |
|---|---|
| `Netlist_Dir` | `Netlist_Path` |
| `Netlist_File` | `Netlist_Name` |
| `Netlist_Dir2` | `Netlist_Path2` |
| `Netlist_File2` | `Netlist_Name2` |
| `comboBox_NlDir` | `comboBox_NlPath` |
| `comboBox_NlFile` | `comboBox_NlName` |
| `comboBox_NlDir2` | `comboBox_NlPath2` |
| `comboBox_NlFile2` | `comboBox_NlName2` |
| `slot_updateNlFile` | `slot_updateNlPath` |
| `slot_updateNlFile2` | `slot_updateNlPath2` |
| `-nr ` / `-nr2 ` | `-nd ` / `-nd2 ` |
| `-nl ` / `-nl2 ` | `-nn ` / `-nn2 ` |

B 生成命令（在 .75 workdir，对 A 副本跑）：`sed -i -E 's/Netlist_Dir2/Netlist_Path2/g; s/Netlist_File2/Netlist_Name2/g; s/Netlist_Dir\b/Netlist_Path/g; s/Netlist_File\b/Netlist_Name/g; s/comboBox_NlDir2/comboBox_NlPath2/g; ...'`（注意顺序：先长后短，先 `2` 后普通，避免误替换）。

## k_check 草案（13 断言，≥8 ✓）
`check(deliverable, workdir)`：在独立临时目录解 submit.zip，取候选 patch 脚本 `add_step2_netlist2.py`，对 **B**（hidden，5 文件）执行，3 seed 随机抽 B 子集目录名跑 3 次结论一致。
1. zip 内含 `add_step2_netlist2.py`（候选脚本），无其他可执行。
2. 脚本在 B 上执行 exit 0，产出 5 个修改后文件（不就地改 B 副本以外的 hidden）。
3. `ddr5simoptions.h` 含 `slot_updateNlPath2(const QString &)` 声明 + `getStep2ModelList()` 声明。
4. `ddr5simoptions.cpp` 含 `connect(ui->comboBox_NlPath2, SIGNAL(currentTextChanged(QString)), this, SLOT(slot_updateNlPath2(QString)))`。
5. `ddr5simoptions.cpp` 含 `slot_updateNlPath2` 实现，实现内含 `ui->comboBox_NlName2->clear()` 与 `setEnabled(false)` 分支。
6. `ddr5simoptions.cpp` 输出收集段含 `"Netlist_Path2;"+` 与 `"Netlist_Name2;"+`（B 改名后 token）。
7. `mainwindow.h` 含 `QString Netlist_Path2;` 与 `QString Netlist_Name2;` 成员。
8. `mainwindow.cpp` OptionInfo 段含 `<<Netlist_Path2<<Netlist_Name2`（AgingSim 分支）。
9. `mainwindow.cpp` 解析段含 `else if(name=="Netlist_Path2")` 与 `else if(name=="Netlist_Name2")` 赋值分支。
10. `mainwindow.cpp` matrixrun 命令串含 `-nd2 %17 -nn2 %18`（B 改名后 flag）。
11. matrixrun `.arg` 链含 `.arg(Netlist_Path2).arg(Netlist_Name2)`，且两条分支（Netlist_Link 非空/空）均含。
12. `ddr5simoptions.ui` 含 `name="comboBox_NlPath2"` 与 `name="comboBox_NlName2"` 两个 QComboBox widget，且 XML 仍合法（`xmllint --noout` 通过）。
13. 3-seed 一致性：随机抽 3 组 B 子目录名（netlist 候选池随机子集），脚本产出文件中 Step2 token 结构断言（3-12）3 次全 PASS。

## anti-hardcode 分析（§4.9 三假必 FAIL）
- **fake_print_only**（只 print 期望串）：FAIL —— check 在 B 上 subprocess 执行脚本并解析**产出文件**结构，print 到 stdout 不写入文件 ⇒ 断言 2-12 全 FAIL。
- **fake_core_deleted**（空壳脚本，不修改文件）：FAIL —— 产出文件无 Step2 token ⇒ 断言 3-12 FAIL。
- **fake_hardcode_a**（硬编码 A 的 token `Netlist_Dir2`/`-nr2`）：FAIL —— B 用 `Netlist_Path2`/`-nd2`，脚本写死 A token ⇒ B 产出文件含错 token ⇒ 断言 4-11 FAIL（强制泛化）。

## 交付物与 reference
- 候选交付：`submit.zip` 内 `add_step2_netlist2.py`（python3，用正则/字符串替换对 5 文件做 Step2 增量，**泛化**：从 Step1 token 派生 Step2 token，不硬编码具体名）。
- reference 解：`reference/EDA-Eval-DesignFlow-Step2NetlistParamPatch-001/solution.py` —— 用 regex 定位 Step1 模式（comboBox_NlDir/slot_updateNlFile/Netlist_Dir/-nr）并在其后镜像插入 Step2 版本，token 名从 Step1 派生（`X` → `X2`，`-xy` → `-xy2`）。
- negatives：`naive_stub.py`（空）、`always_print.py`（print 不改文件）、`hardcode_a.py`（写死 Netlist_Dir2/-nr2）+ `negative_selftest.py` 全 FAIL。

## 预算与节奏
- A 还原（5 文件逐项删 Step2）+ B sed 改名 + check.py 13 断言 + reference + 3 neg + selftest + .75 自验 ≈ 1.5–2 轮专注合成。
- 本轮（r1247）仅重建深读笔记（笔记丢失 + session 清理），**不合成**，DEBT 保留。下轮 r1248 直接用本笔记合成，ETA 1 轮（若 .ui XML 块边界核对顺利）。
- 关键风险：`.ui` XML 块删除需保持合法；matrixrun 命令串 `-c2/-f2`（Step1 已有）vs `-nr2/-nl2`（Step2 新增）命名陷阱，还原 A 时勿误删 `-c2/-f2`。
