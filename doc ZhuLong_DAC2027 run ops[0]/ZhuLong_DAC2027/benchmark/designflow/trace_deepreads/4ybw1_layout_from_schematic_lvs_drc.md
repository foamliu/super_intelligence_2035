# Trace 深读笔记 · 4ybw1 · yan1zh · layout_aether 域（版图从原理图绘制 + LVS + DRC）

> 第122轮深读。session `1792487689184_4ybw1`（yan1zh @ hfeg0plg65, match_count=495, 2.5MB / 618 msgs: 326 user / 292 assistant）。
> **域**：layout_aether（pyAether 驱动版图绘制 + calibre LVS/DRC）。该域是 11 类中**最大**的（14534 命中），此前 0 条 proper case，本深读为下轮合成 `EDA-Eval-DesignFlow-LayoutAether-001` 做准备。
> **节奏**：IX §五「深读本轮 → 下轮合成 case」。本轮不出 case，只深读 + 落笔记。

## 一、真实任务（3 条 substantive user message，其余 12 条「继续」）

1. **U1**：`你能访问我的这个路径的电路图吗 /proj/train/drcoa_social/workdir/yan1zh/test_ZY/and2CSx1/schematic/sch.oa`
2. **U2**：`我想让你根据里面的电路图画一个与其相对应的版图，要能够通过 LVS 检查`
3. **U4**（U3 是「继续」后看到版图）：`我看到你画的 Layout 了，但是这样的版图是过不了 DRC 的，我需要你再次基础上进行修改，并最终通过 DRC，/apps/imctf/cad/runset/train/drcoa_social/current/calibreDRC.rule 这是 DRC rule 的路径，金属可以使用 MT2 和 M0U 两层，然后可以调用对应的 spacer`

→ 三阶段：① 读原理图 ② 画版图过 LVS ③ 修 DRC（金属 MT2/M0U + spacer）。这是**纯 pyAether 版图流程**的教科书级 trace。

## 二、电路图（and2CSx1 = NAND2 + INV，6 MOSFETs）

agent 用 pyAether（`aeOpenDesign("test_ZY","and2CSx1","schematic")` + `aeGetCurDesign()` + `.instances/.terminals/.nets`）探明并手写出 CDL（见 EDITOR#32，`phase_c2.sh`）：

```
.SUBCKT nand2CS A B Y vbulkn! vbulkp! vcc! vss!
*.PININFO A:I B:I Y:O vbulkn!:B vbulkp!:B vcc!:B vss!:B
MM4 Y B vcc! vbulkp! ptn W=WP1 L=LP1 nf=nfP1
MM0 Y A vcc! vbulkp! ptn W=WP1 L=LP1 nf=nfP1
MM5 zn1 B vss! vbulkn! ntn W=WN1 L=LN1 nf=nfN1
MM2 Y A zn1 vbulkn! ntn W=WN1 L=LN1 nf=nfN1
.ENDS nand2CS

.SUBCKT invCS A Y vbulkn! vbulkp! vcc! vss!
*.PININFO A:I Y:O vbulkn!:B vbulkp!:B vcc!:B vss!:B
MM0 Y A vss! vbulkn! ntn W=WN L=LN nf=nfN
MM1 Y A vcc! vbulkp! ptn W=WP L=LP nf=nfP
.ENDS invCS

.SUBCKT and2CSx1 A B Y vbn! vbp! vcc! vss!
*.PININFO A:I B:I Y:O vbn!:B vbp!:B vcc!:B vss!:B
XI1 A B net7 vbn! vbp! vcc! vss! / nand2CS LP1=0.162u WP1=1.476u nfP1=1 LN1=0.162u WN1=0.820u nfN1=1
XI0 net7 Y vbn! vbp! vcc! vss! / invCS LN=0.162u WN=0.820u nfN=1 LP=0.162u WP=1.476u nfP=1
.ENDS and2CSx1
```

**拓扑要点**：
- and2CSx1 顶层 7 端口：`A`(in) `B`(in) `Y`(out) `vbn!` `vbp!` `vcc!` `vss!`(均 B/body)
- 2 个子电路实例：`XI1`=nand2CS（4 MOSFET：MM0/MM4 ptn PMOS, MM5/MM2 ntn NMOS），`XI0`=invCS（2 MOSFET：MM0 ntn, MM1 ptn）
- 共 6 个 MOSFET（4 ntn? 不：nand2CS MM5/MM2 = 2 ntn, MM0/MM4 = 2 ptn; invCS MM0 = 1 ntn, MM1 = 1 ptn → **4 ptn + 2 ntn**? 重数：nand2CS ptn×2 + ntn×2, invCS ptn×1 + ntn×1 = 3 ptn + 3 ntn = 6 MOSFET）
- 内部网：`net7` = nand2CS 的 `zn1`(MM2.S/MM5.D) = nand2CS 的 `Y`... 注意 CDL 里 nand2CS 的 Y 在 and2CSx1 里接 net7（XI1.Y=net7），而 invCS 的 A 接 net7（XI0.A=net7）。**net7 是 NAND2 输出→INV 输入 的中间节点**。
- LVS 报告实测：**Ports: 7 matched / Nets: 9 matched / Instances: 6 matched**（ flattened 到 MOSFET 级，含 body 网 vbn!/vbp! 与 vss!/vcc! 分立 + net7 + A/B/Y + 衬底全局网，共 9；agent 报告原文 `OVERALL COMPARISON RESULTS: CORRECT ✓ Ports: 7 matched / 0 unmatched`）

## 三、agent 的完整工作过程（pyAether + shell + calibre + LSF）

**工具统计**：editor 158（写脚本）/ run_approved_command 97（跑脚本）/ read_files 36 / list_allowed_files 8 / RAG search_apis 6 / RAG get_api_details 3 / SandBox run_code 2 / skills 2。

**关键 pyAether API**（经 RAG_MCP_Server 查得）：
- 读原理图：`aeOpenDesign(lib,cell,view)` / `aeGetCurDesign()` / `d.instances` / `d.terminals` / `d.nets` / `i.master.cell` / `i.cdfParameter` / `i.props` / `techGetTechFile("TECHLIB")`
- 画版图：`dbCrtRect(cv=d, bbox, layer, purpose)` / `dbCrtInst(cv=d, point, lib, cell, view, inst, orient, params)` / `dbCrtPin(cv=d, net, box, layName, purName, name, dir, showName, nameOrigin, height, justify, pinnameLayName, pinnamePurName)` / `dbCrtLabel` / `dbDeleteAll(vector1D_p_emyFig)` / `dbSetInstParam(inst, paramName, value, mode)` / `i.setOrient()` / `i.setOrigin(emyPoint)` / `d.save()`
- 几何辅助：`emyPoint(x,y)` / `emyPointF(x,y)` / `emyBoxF(p1,p2)`

**Phase A — 器件放置**（`py_build_a.py` / `py_build_v2.py`）：6 个 MOSFET pcell（TECHLIB ntn/ptn）按 orient+origin 放置（v2 production pitch + 0.25 右移修 PW_ENC）：
```
PLAN = {
 "I1|M2": ("MY", 1.08, 1.093),   # nand M2 ntn  S=zn1 D=net7 G=A
 "I1|M5": ("MY", 1.62, 1.093),   # nand M5 ntn  S=vss  D=zn1  G=B
 "I0|M0": ("R0", 2.16, 1.093),   # inv  M0 ntn  S=vss  D=Y    G=net7
 "I1|M0": ("R0", 0.54, 3.539),   # nand M0 ptn  S=vcc  D=net7 G=A
 "I1|M4": ("MY", 1.62, 3.539),   # nand M4 ptn  S=vcc  D=net7 G=B
 "I0|M1": ("R0", 2.70, 3.539),   # inv  M1 ptn  S=vcc  D=Y    G=net7
}
```

**Phase B — MT2 布线 + pin**（`py_build_b.py`）：15 条 MT2 rect（zn1_tie / net7 通道 / vcc riser×3 / vss rail / A_bar / B_bar / Y_bar ...）+ 7 pin（A/B/Y/vcc!/vss! MT2pin，vbp! NWpin，vbn! PWpin）。

**Phase C — LVS**（`phase_c1..c7.sh`）：
1. `asOut` 导 GDS（layerMap/objectMap from `/apps/imctf/libs/dfii/cxmtG5_CIP/current/`，`-convertPinTo geometryAndText -view layout`）
2. 手写 CDL（上面 §二）作 source netlist
3. `calibre -spice ... -lvs -hier -hcell /proj/.../hcells -nowait -E ...rule.svrf ...rule`（经 LSF `bsub -q pv`，VCO 选 calibre 版本，`unset LD_LIBRARY_PATH` 绕过 esub hook）
4. rule 用 `INCLUDE /apps/imctf/cad/runset/train/drcoa_social/current/calibreLVS.rule` + sed patch `LAYOUT PRIMARY "and2CSx1"`
5. **结果：`LVS completed. CORRECT`**（Ports 7/7, Nets 9/9, Instances 6/6 全匹配）。agent 自报「LVS 一次通过」。

**Phase D — DRC 修复**（U4，`drc_run1.sh` + `py_build_v2.py`）：
1. `calibre -drc -hier -nowait calibreDRC_and2CSx1.rule`（deck `sed 's/AAAAA/and2CSx1/g'` 从 `/apps/imctf/.../calibreDRC.rule`）
2. 首跑 **179 violations**（TOTAL RULECHECKS EXECUTED=2322）：`PW_ENC_005_00_c`（PW enclosure）/ `MT2_W_001_00_p`（MT2 宽度）/ `MT2_S_002_00_p`（MT2 间距）/ `MT2_CL_025_00_p` / `PG_S_024_00_p` / `PC_S_012_00_p` 等
3. 对比参考 `stdcells_ac/and2CSx1`（已有 Golden 版图）跑 DRC（249 violations，说明参考本身也不全 clean，但 agent 仍以降到 32 为目标迭代）
4. **修复**：加 `spacer`（TECHLIB pcell, `dbCrtInst(... cell="spacer", params=["width=3.6"])`，覆盖 PW_ENC）+ M0U 布线（8 rect：net7 顶层 detour / Y hbar+vbar / A / B）+ PCU contact（多 rect 连 MT2↔M0U）+ 调器件间距
5. 迭代后 DRC 降到 **32**（再迭代目标 0/clean）

## 四、关键环境/路径（真实，可入 assets；非密）

- 原理图：`/proj/train/drcoa_social/workdir/yan1zh/test_ZY/and2CSx1/schematic/sch.oa`（Cadence OA 二进制）
- 库：`test_ZY`（用户工作库）/ `TECHLIB`（ntn/ptn pcell + spacer + tech）/ `stdcells_ac`（Golden 参考 and2CSx1）
- DRC rule：`/apps/imctf/cad/runset/train/drcoa_social/current/calibreDRC.rule`
- LVS rule：`/apps/imctf/cad/runset/train/drcoa_social/current/calibreLVS.rule` + `/proj/train/drcoa_social/ver/lvs/hcells`
- 层映射：`/apps/imctf/libs/dfii/cxmtG5_CIP/current/{layer.map,object.map}`
- 金属层：**MT2**（主布线）+ **M0U**（detour/上抬）+ **PCU**（contact MT2↔M0U）+ **NW**（vbp! pin）/ **PW**（vbn! pin）
- calibre：`/apps/mentor/calibre/2020.1_36/{aoi,aoj,ixl}_cal_2020.1_36.18`，LSF `bsub -q pv`
- aether：`/apps/empyrean/tools/aether_new/`，`aether -nc` + `PY_INIT_FILE` + `aether.ini`(`Py Script=`) + `lib.defs`(INCLUDE 项目 lib.defs)
- DBU=10000（1um=10000 dbu），版图 bbox 约 (-0.43, -0.14) → (3.79, 6.71) um

## 五、判分要点（下轮 case 的 test 设计依据）

真实「过 LVS」= calibre 报告 `LVS completed. CORRECT` + `Ports: 7 matched / 0 unmatched` + `Nets: 9 matched` + `Instances: 6 matched`。真实「过 DRC」= `TOTAL RESULTS GENERATED = 0`（clean）或低于阈值。

**下轮 case 取舍**：本 trace 是**纯 live-EDA 任务**（画版图需 Aether + pcell + LSF calibre），pi-SUT（本机无 live Aether）跑不了 live 部分。与已 5 条 pi-PASS（全 offline-Python）一致，下轮把 case 设计为 **offline-Python 的 LVS 网表比对工具**（layout_aether 域的 LVS 智核），即：
- 给 `and2CSx1_schematic.cdl`（§二 真实 CDL）+ `layout_correct.txt`（结构化版图网表：6 器件实例 master+terminal→net 映射 + 7 顶层端口 + 内部 net7）+ `layout_buggy.txt`（含 1 处 misroute，如 M2.G A↔B 互换 或 net7 断开）
- agent 写 `lvs_tool.py`：解析 CDL 建原理图网表 → 解析版图网表 → 比对（端口名+方向 / 网连通 / 实例 master+端子-net）→ 输出 CORRECT/INCORRECT + 比对报告
- test：correct→CORRECT(7ports/9nets/6insts) / buggy→INCORRECT 指出具体不匹配 / naive(always-CORRECT)→fail buggy / 只计数不比对→fail
- entry_point=`outputs/submit.zip`(lvs_tool.py+sample_output.txt+comparison_report.txt)，Python 双参 check，无 lang/host，mode=design_flow，trace_source.user=yan1zh 原名
- 与 Analog-001（netlist↔SPEF connectivity tracer）成姊妹：本条是 schematic-CDL↔layout-netlist LVS 比对，域=layout_aether

## 六、脱敏与红线

- 用户名 `yan1zh`、路径、电路名 `and2CSx1`/`nand2CS`/`invCS`、层名 MT2/M0U/PCU/NW/PW、calibre/aether 路径**保留**（溯源 + 真实场景，运维令 XII 要求 user 用原名）。
- license 文件里的 license server 端口串（`59001@hfds2:1881@...`）**不入库**（敏感）。
- sch.oa 二进制不直接入 assets（无法离线解析），改用 agent 手写的 CDL（已是结构化文本，可入库）。
- .75 session 已 `close_session(keep=false)` cleaned=true（红线：不留垃圾到 .75）。

## 七、结论

本 trace 是 layout_aether 域（11 类最大、14534 命中、此前 0 proper）的理想源：任务清晰（画版图过 LVS+DRC）、pyAether API 齐全、LVS 实测 CORRECT(7/9/6)、DRC 有真实违规+修复过程。下轮据此合成 `EDA-Eval-DesignFlow-LayoutAether-001`（offline-Python LVS 比对工具，real and2CSx1 CDL，correct/buggy 双版图网表，7 条件有牙 test，pi+ref 双验）。
