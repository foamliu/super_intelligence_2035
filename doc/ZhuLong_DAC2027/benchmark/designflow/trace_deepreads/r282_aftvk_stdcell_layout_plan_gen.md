# r282 deepread · aftvk · stdcell layout plan generation (jieran@hfeg0pkn004)

**trace**: 1793963596117_aftvk.messages.json — jieran @ hfeg0pkn004 (10.129.2.13), mc=14,
625 pyAether / 247 "lang":"pyAether" / 208 schematic / 166 netlist / 165 dbGet / 37 calibre / 34 cellview / 9 dbCreateInst / 1 dbCreateRect.
623 msgs (320 user / 303 assistant), 2.8MB. dir-based session storage (r278 finding confirmed: `1793963596117_aftvk/1793963596117_aftvk.messages.json`).
jieran NEW (0 prior case). tool uses: SandBox_MCP_Server__run_code 225 / editor 20 / RAG_search 20 / read_files 10 / run_approved_command 4.

## 用户真实意图（real user turns, 逐字）

- U#0: netlist 路径 `/proj/dscqa/V0/workdir/jieran/simulation/dscqa_stdcells_bufLVCKx24_schematic_ALPS/dscqa_stdcells_bufLVCKx24_schematic.netlist`
- U#4: 「根据这个netlist帮我绘制版图，命名layout_tet」
- U#51: 「放在这个cell下面/proj/dscqa/V0/libs/dscqa_work/nor3IOLVx2_Dout」
- U#199: 「优先先学习这些的DRC rule:/apps/imctf/cad/runset/dscqa/v0/current/calibreDRC.rule，然后再学习这些标准的standcell的版图的绘制方法，路径为/proj/dscqa/V0/libs/stdcells_ac，只学习layout view的绘制方式...最后再尽可能地去对刚才所绘制的layout_test进行优化」
- U#291: 「希望你吧后面我给你指出的问题都记录到learning_notes_stdcell_layout.md这个文件里面 1：必须严格参考/proj/dscqa/V0/libs/stdcells_ac这里面版图设计的格式 2：standcell的绘制里面，内部的连接我们只会用到MT2/MOU或者pg drwing,其中MT2主要用于PG的连接，所有的输入输出Pin都必须打在MOU上，而且处于spacer的中间位置 3：power的Pin我们主要是打在左上角而且pin的大小统一为0.02x0.02 4：管子能merg的地方一定要给我merg起来，把面积做到最小 5：同时需要把DRC/LVS都clean掉」
- U#448: 「我下面会交给你我们绘制standcell的完整流程：1：首先调出spacer...放置在(0.0)的位置 2：根据XL关系调出管子...将管子S/D自带的MOU拿掉 3：管子和spacer左边边界对齐，P管在上，N管在下，Gate朝向中间 4：MT2用来连接PGATE，mou用来连接S/D，MT2和mou是通过PCU来连接的 5：打输入输出Pin和power pin」
- U#481: 「/proj/dscqa/V0/libs/dscqa_work/nand2LVSx6根据这个cell提供的电路，把版图绘制出来」
- U#556: 「绘制这个cell的layout.../proj/dscqa/V0/libs/dscqa_work/nand2IOLVIOx1」

多轮 produce-task（netlist/circuit → stdcell layout + DRC/LVS clean + stdcell 规范），A-faithful eligible（U#4/U#448 提需求未给根因），本案做 **B 档离线化**（真实 Virtuoso/OA/pyAether 不可沙盒复现）。

## 真实 assistant 产物（grounding）

1. **netlist 解读**（m2 tool_result + m3 assistant 分析）：bufLVCKx24 = 两级反相器 buffer，invLV 子电路（ntn_lv NMOS XMM0 + ptn_lv PMOS XMM1，端口 A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss，参数 WN/LN/nfN/WP/LP/nfP）。顶层 XI0 (A→net5, nf 7/7) + XI1 (net5→Y, nf 20/20)，寄生电容 cg1/cout1。
   - invLV mos 终端顺序：`XMM0 Y A inh_vss inh_vbulkn ntn_lv` → D=Y G=A S=inh_vss B=inh_vbulkn（ntn_lv 4 端 D G S B）。
2. **create_layout_tet.py**（m149-m195 editor，pyAether）：`pya.dbNewCellView("dscqa_work","layout_tet","layout")` + `dbCrtWire(layer="M1",...)` + `dbCrtNet` + `dbCrtRect`，调用 ntn_lv/ptn_lv master。真实跑遇 pyAether API TypeError（getOrigin emyPoint），多次迭代修复。
3. **learning_notes_stdcell_layout.md**（m226-m598 editor，结构化规则，从 stdcells_ac 13 cell 50+ device 实例分析得出）：
   - **§8 Cell Format**：Cell Height = 7.570um（FIXED）；Cell Boundary 起点 x=-0.832um；左/右 margin = 0.832um。
   - **§14 FIXED VERTICAL POSITIONS**：NMOS top edge（gate side）FIXED y=2.563um（gate 在 top，向下延伸）；PMOS bottom edge（gate side）FIXED y=2.889um（gate 在 bottom，向上延伸）；spacer top y=7.140，bottom y=-0.430；gate 之间 gap ~0.3-0.6um 走内部 routing。
   - **§15 INTERNAL CONNECTION RULES**（3 层）：**MT2** = gate/PG routing（vertical path 连 N-gate↔P-gate，宽 0.080-0.348um，载 gate 信号）；**M0U** = S/D metal（rect 覆盖 S/D 区，载 VCC/VSS/Y 等 S/D 信号）；**PCU** = via 桥接 MT2↔M0U（horizontal bar ~0.192×0.886um，跨 cell 宽）。PG 来自 spacer。
   - pin 规则（U#291）：power pin 左上角 0.02×0.02；所有 I/O pin 打在 M0U 上、处于 spacer 中间；MT2 主要用于 PG 连接。
   - merg：管子能 merg 的地方一定 merg（同类型共享 power S/D 的相邻管子）。

## 为何 B 档离线 L1

真实产物依赖 jieran 服务器上的 Virtuoso/OA + pyAether + TECHLIB/spacer + stdcells_ac 库，.75 沙盒不可复现（pyAether 在沙盒可跑但无 dscqa 库/spacer/master）。离线核心 = **给定 stdcell SPICE netlist + tech rules config → 结构化 layout_plan.json**：
1. 解析 netlist、flatten mos 子电路、解析 W/L/nf 参数（含子电路参数传递）
2. 按规则放置（P 上 N 下、gate 朝中、固定 gate Y、spacer 左对齐 column）
3. net 分层（power→MT2/pg；gate→MT2/gate；S/D signal→M0U/sd_signal；gate∩S/D→bridged 标 PCU）
4. pin 生成（power pin 0.02×0.02 M0U 左上角；signal pin M0U spacer_mid_x）
5. merge_groups（同类型共享 power S/D 的管子分组）
6. pcu_bridges（既是 gate 又是 S/D 的 net）
7. boundary + drc_lvs_checklist

参考 r274 M1ShapeDelete / r238 LayoutFloorplanGen 离线化范式：SUT 提交脚本，check.py 在 hidden B 上 subprocess 真跑。

## B-track 参数化（非硬编码）

- **A**（可见）：bufLVCKx24（两级反相器 buffer，canonical netlist，invLV 子电路 + 顶层 XI0/XI1，参数 nf 7/7 与 20/20）。flatten 后 4 mos（2N+2P），ports [A,Y,vbn!,vbp!,vcc!,vss!]，gate nets {A,net5}，net5 既是 gate 又 S/D → 1 pcu_bridge，merge_groups 2（vcc!/P、vss!/N），6 pins。
- **hidden B**：nor3LVSx2（3 输入 NOR，扁平顶层直接实例 mos，3 P 串联 + 3 N 并联，W=1.8e-6/nf=2 与 1.2e-6/nf=2）。flatten 后 6 mos（3N+3P），ports [A,B,C,Y,vbn!,vbp!,vcc!,vss!]，gate nets {A,B,C}（纯 gate，无 S/D 交叉）→ **0 pcu_bridge**，merge_groups 1（vss!/N 3 members；vcc!/P 仅 1 member 不成组），8 pins。
- **结构性差异**：cell 名 / 端口数 / mos 数(4 vs 6) / top 结构(子电路嵌套 vs 扁平) / pcu_bridge(1 vs 0) / merge_groups(2 vs 1) / pin 数(6 vs 8) —— 挫败 print_expected_A 与硬编码。

## 去重（DISTINCT from 现有 layout_aether 系）

r274 M1ShapeDelete=按层删图形；r238 LayoutFloorplanGen=floorplan 布局；r264 ScmosCrossProbeCsvGen=OA inst hierarchy CSV；r278 EccDsaLocate=坐标定位；r222 SchOaInventoryExtract=OA inventory 抽取；r214 YamlToGds=YAML→GDS；r213 InvLayoutGen=inv 生成；r206 DupViaPriorityCheck=dup via。本案首次 ground on「**stdcell SPICE netlist → 结构化 layout plan（flatten + 固定 gate Y + MT2/M0U/PCU 三层角色 + power/signal pin + merge group + PCU bridge）**」，核心算法 = SPICE 解析+子电路 flatten+参数解析+规则化放置+net 分层，不同输入类型不同核心。

## avoid / 回退

aftvk 已 claim（ledger_C claimed 1）。回退候选（fresh-window 余）：163xg/hs4sv/a5mxr/hc9mk。avoid: xinqiaoz/e0014566/miccao/adminai/ellawu/e0044587/jackjia/e0029308/jkxu。
