# 深读笔记 · nr5et · cuij@hfeg0plg86 · analog_context LVS 诊断

## trace 概况
- session: `1793932045707_nr5et.messages.json`，cuij @ hfeg0plg86 (10.129.8.137)，mc=124
- 关键词: analog:1234 cmos:813 lvs:557 mosfet:378 transistor:120 calibre:76 netlist:26 aether:26
- 工具: 38 calibre, 18 netlist, 1 schematic, 1 pyAether
- 42 msgs / 23 user / 19 asst / 16 tool_use；**4 real user turns**（其余为 tool_result）
- 目录式存储：`/home/cuij/.cline/data/sessions/1793932045707_nr5et/1793932045707_nr5et.messages.json`（754KB）

## 用户意图（4 real turns，逐字原文）
- U#0: `分析一下/proj/drvqa/V0/ver/lvs/cuij/AG_AnalogPumps_1031/这个路径下 LVS为什么没过`
- U#37: `X151/M0如何 知道这个期间的g端`
- U#39: `DEVICE MP(ptn_lv) PTN_LV PGATE(G) PDnet_MOS(S) PDnet_MOS(D) NWnet(B) NETLIST MODEL "ptn_lv" NETLIST ELEMENT "X" CMACRO PMOS_PROPERTY PTN_LV PGATE PDnet_MOS`（贴 LVS rule file 里的器件定义）
- U#41: `按照我的理解，layout报错出来g端接了vss，我查看g端的定义，是不是也是一个思路`
- ⚠️ 会话以 U#41 未答收尾（agent 未回最后一条）→ 取 msg#36/#38/#40 已交付诊断为金标准产物

## 助手工具链
1. list_allowed_files + ls → 拿到 AG_AnalogPumps_1031/ 下文件清单（.lvs.report / .cdl / .sp / _calibreLVS.rule_ / svdb/ 等）
2. read_files 分段读 `AG_AnalogPumps.lvs.report`（14761 行，共读 1-200/200-850/850-1050/10348-10500/10419-10443/10644-10720/11000-11830/13000-14761 等多段）
3. read `.lvs.report.ext` / `netlist.mapping` / `AG_AnalogPumps.sp` 辅证
4. 产出 msg#36 完整 LVS 失败分析报告（markdown）

## 真实诊断结论（msg#36）
- 总体：**INCORRECT — Connectivity errors**；2 warning（Unbalanced smashed mosfets matched / Ambiguity points resolved arbitrarily）
- 全 ~194 子单元中**唯一 INCORRECT**：`AG_VkbPumpCoreHalfUnit`，其余全 CORRECT（顶层 AG_AnalogPumps 亦 CORRECT）
- 初始器件数：Ports 15/15 ✓，Nets 15/15 ✓，MN 404/144 ✗，MP 614/148 ✗，MarkBNV 0/1 ✗，MarkNVP 0/10 ✗，switch_close 1/1 ✓，Total 1019/304（Layout 是 Source 3.35×）
- 规约后：Ports 15/15，Nets 15/15，MN 4/4，MP 8/4（不平衡规约强行匹配），switch 1/1，Total 13/13（数一致但连线错）
- **核心错误 2 个 Net**：
  - `vpchg`：Layout 5 conn / Source 9 conn；Source 侧 MM5:g/MM4:g/MM7:g/MM6:g 在 Layout **missing connection**（4 个 PMOS gate 浮空/错接）
  - `vss!`：Layout 9 conn / Source 5 conn；Layout 侧 X157/M0(24.1135,-1.3600):g / X155/M0 / X153/M0 / X151/M0(8.9035,-1.3600):g 接 vss!，Source 侧 **missing connection**（4 个 NMOS gate 接地=常关→疑似 dummy）
- 统计：1018 layout mos → 12（parallel reduction 删 1006）；284 source mos → 4（删 280）；11 source instances filtered
- correspondence ports: vcc! vss! Vinti Bst Vsrc Out Pg1 PW Ngate Pg2 Psw VBstF vpchg VNswF NW
- unequal reduced mosfets：M86/X331...↔XI1<17>/MMP 等，含多行 `** missing smashed mosfet **`

## Calibre LVS report 格式（关键结构，用于合成 A/B）
- 头：`CALIBRE SYSTEM LVS REPORT` banner + `REPORT FILE NAME / LAYOUT NAME / SOURCE NAME / RULE FILE / HCELL FILE / CREATION TIME / CURRENT DIRECTORY / USER NAME / CALIBRE VERSION`
- `OVERALL COMPARISON RESULTS`：ascii art `#     INCORRECT     #`（或 CORRECT）+ `  Error:    ...` + `  Warning:  ...`
- `CELL SUMMARY`：`  Result    Layout    Source` 表头 + `  CORRECT/INCORRECT  cell  cell` 行
- 每子单元块以 `LAYOUT CELL NAME: <cell>` / `SOURCE CELL NAME: <cell>` 起：
  - `INITIAL NUMBERS OF OBJECTS` 表（Ports/Nets/Instances[Layout/Source/Type/`*`diff]/Total）
  - `NUMBERS OF OBJECTS AFTER TRANSFORMATION` 同结构
  - `INCORRECT OBJECTS` → `INCORRECT NETS`：`DISC#  LAYOUT NAME  SOURCE NAME`，逐 net：
    ```
      N    Net <Lname>                                <Sname>
           --- K Connections On This Net ---          --- M Connections On This Net ---
           --------------------------                 --------------------------
           <Lconn or ** missing connection **>        <Sconn or ** missing connection **>
           ...
    ```
  - `INFORMATION AND WARNINGS` 表（Matched Layout/Source + Unmatched Layout/Source + Type）
  - `o Statistics:`（source filtered / layout mos reduced N→M + deleted parallel / source mos reduced）
  - `o Initial Correspondence Points:`（Ports: 列表）
  - `o Matched Mosfets Which Have Been Unequally Reduced:`（layout↔source 对，source 可为 `** missing smashed mosfet **`）
- device 路径格式：`X151/M0(8.9035,-1.3600):g` = inst_path(x,y):pin

## 合成决策
- 私有 /proj/drvqa + cuij 项目 + 真实 14761 行报告不可复刻 → **B-grade synthesized 自包含**
- 取确定性可机械判分子任务：**Calibre LVS report → 结构化诊断 JSON 解析器**（agent msg#36 的核心 produce）
- A（可见）vs 隐藏 B vs B2：cell/net/device/坐标/数量/verdict 全不相交反硬编码
- 真实 PII（AG_VkbPumpCoreHalfUnit / /proj/drvqa / hywang / cuij）不进 A/B，用合成名
- 域 analog_context；L2（真跑候选 on 隐藏 B，解析真实 Calibre 报告格式，subprocess 执行）
- 维度正交：既有 #429 ClampLeakPwrAnalyze（功耗）/#428 InstFuncDiagFix（器件功能诊断）/#398 AutoCellRmAvPf（DRC flow）/#400 AbMatchPlacementCheck（ab 匹配）；本 case=LVS 报告结构化解析诊断，机制/产物全不同
