# Deepread — 1789092579396_tgs17 (miccao @ 10.129.35.73 / hfeg0plg37)

- **user**: miccao  **host**: 10.129.35.73 (hfeg0plg37)  **mc**: 378
- **domain**: schematic_netlist (keywords: netlist:1038; lvs:158; pex:84; rtl:41; .cdl:37; hspice:34; .gds:32; calibre:164 — netlist/CDL/GDS dominant, D-pure)
- **D ledger status (r940)**: parked (empty note, parked under old rules) → **revival candidate, 0 hits in main jsonl, not yet cased**
- **size**: 1,290,843 B / 374 msgs / 17 user turns / agent=lead
- **real task (一句话)**: 开发/使用 `autocell-tcl-flow-generator` skill，从 CDL 网表 + 工艺 pcell 库生成 GDS（pcell 调用而非自画管子），并产出 cell 约束模板配置文件

## 用户轮逐条（verbatim 关键句）

| # | verbatim 要点 | 类型 |
|---|---|---|
| U#0 | `/autocell-tcl-flow-generator /home/miccao/autocell.1.2026.7/g5_ddcpc 这个路径下的配置里是怎么做到pcell直接调用现有工艺库中的pcell的` | 提问-howto |
| U#30 | 要适配一个新工艺，我要调取这个工艺中的pcell，那我需要提供给你什么文件 | 提问-howto |
| U#35 | 所以只要给你pcell库的位置，你就知道怎么调用pcell了是吧？你可以找到pcell的call back? | 提问-确认 |
| U#42 | 那我提供pcell库路径，这个skill要能通过这个路径在生成cell的时候调用相关pcell,而不是自己画管子 | 需求-功能 |
| U#65 | 你的意思ddcpc是自己画的管子，而不是调用的pcell？那gds导进aether就没有pcell了？ | 提问-机制 |
| U#81 | `用 g5_ddcpc 配置，根据 and2GF47x4/schematic/sch.cdl 生成一个 gds，放到 g5_ddcpc/gds 目录下` | **produce-act** |
| U#115 | 为什么能生成出pcell和gut这些下层cell啊？我不用这份文件就生成的是一个flatten的gds | 提问-机制 |
| U#126 | gds2pcell.py 是怎么让gds里的图形变成pcell的 | 提问-机制 |
| U#134 | 目前我们的skill里又涉及到将gds倒进aether库里的步骤么 | 提问-确认 |
| U#158 | 帮我做到现在的skill里，作为一个可选功能，用户说要依据对应的pcell做成对应的库才执行 | 需求-功能 |
| **U#231** | `生成一个模板，里面列举了所有的ddcpc这套库用到的cell的约束条件，这个模板以后会作为我给你的配置文件，请你尽量写的详细，模板为txt格式，位置放到 .../g5_ddcpc/config下` | **★ produce-act（首选锚点）** |
| U#283 | prepr.tcl 为什么没有体现在模板里，是因为没用到吗？ | 提问-补全 |
| U#301 | 模板里有体现pcell库吗 | 提问-确认 |
| U#311 | 我现在就给你一份这个模板文件，你能跑通流程么 | 需求-验证 |
| U#327 | `/autocell-tcl-flow-generator .../netlist_dir_20260807 这是网表路径，依据 cell_constraints_template.txt 里面的设置，生成所有的gds，放到 .../ddcpc/gds 下面` | produce-act |
| U#372/373 | go on / 继续执行 | 续跑 |

## GOLD（A#282，对 U#231 的交付）

文件 `/home/miccao/autocell.1.2026.7/g5_ddcpc/config/cell_constraints_template.txt`（**590 行，10 个 section**）：

| Section | 内容 | 条目 |
|---|---|---|
| 1. GLOBAL PROCESS PARAMETERS | 工艺类型、autocell 路径、tech.tcl、DRC/LVS deck、cell_height、gate_length、poly_pitch、power rail 宽度、pin 位置、M1/M2 参数、track 坐标 | ~35 参数 |
| 2. DEVICE CLASS DEFINITIONS | 12 种晶体管（7 NMOS + 5 PMOS），每种 model/channel_width/poly_extension/CDF 参数名/类型/默认值 | 12 `[nmos_type]`/`[pmos_type]` |
| 3. LAYOUT SPEC DEFINITIONS | 9 个 layout_spec（F_ZPower, FD_ZPower, B, S, L, M, V, W, x），pmos/nmos type、gate_length、poly_pitch、boundary_pcell、grid_map、folding range | 9 `[layout_spec]` |
| 4. KIT DEFINITIONS | 15 个 kit（F, FD, F_MT2, FD_MT2, F_pin33, F_pin44, F_short_pin, F_buf, B, S, L, M, V, W, x），layout_gen_file、pin_template、cell_tcl、MT2_offset、hierarchy_mode、special_options | 15 `[kit]` |
| 5. CELL-NAME TO KIT MAPPING | rule.json 映射（and→F/FD/S, mxi2→MT2, xord2→pin33/pin22, ff→pin33, aoi/oai→pin22, passgt→passgtF/M/Vx/Wx10, fallback *PF*→F 等） | ~70 条规则 |
| 6. PREROUTE CONSTRAINTS | 8 类：join_net 模式、prohibit_zpower 三种 + forbidden rect 坐标、vssz/vccz preroute via 参数、CT forbidden、input/pin net M0U/M1/MT2 forbidden 区域 | 8 小节 |
| 7. VIA DEFINITIONS | PC/PCU/CT 三类 viadef，pcell 名、cut_layer、layer1/2、cut_size、enclosure、CDF 参数 | 9 viadef |
| 8. EXAMPLE CELL DEFINITIONS | 5 个 cell 完整约束：netlist_file、kit、layout_spec、pmos/nmos_type、pin_template、gds_output、gut_cell_name、hierarchy_mode、join_net、prohibit_zpower、vssz_M0U_via、pins、每 device 的 model/l/w/nf/S/D/G/B、folding | 5 `[cell]` |
| 9. GENERATION COMMAND | 单 cell 生成命令模板 + and2GF47x4 完整示例 | — |
| 10. GDS-TO-PCELL | 可选 gds2pcell_wrapper.py 调用方式 | — |

## r941 合成方案（建议）

- **锚点**：U#231 verbatim「生成一个模板，里面列举了所有的ddcpc这套库用到的cell的约束条件...模板为txt格式」—— A档合规（提出需求/表达目标 ✓；未给根因/修复 ✗）
- **范式**：manual-grounded howto Q&A → produce reframe（承 r928-r939 D 域系列），asset_fidelity=synthesized-reframe
- **A**：基于 GOLD A#282 合成结构化 markdown 手册（10 section 框架 + 真实 cell/kit/device 名 + 参数表）+ question_A.txt（verbatim U#231）
- **B (hidden)**：平行场景——另一套工艺库（如 `g6_ddrph` / 或 digital-standard-cell 套）的 cell-constraints 模板，结构同构 token 不相交（ddcpc/and2GF47x4/nmos_type/P_ZPower ↔ ddrph/nand2GHx6/pmos_type/PH_ZPower 等）
- **candidate parser**：通用 cell-constraints-template 解析器（INI-style `[section]` + key=value + table 行解析），输出 JSON{global_params, device_classes, layout_specs, kits, cellname_kit_rules, preroute_constraints, via_defs, example_cells, generation_cmd, gds_to_pcell}
- **check.py 12 断言 a-l**：zip+py / py_compile / A JSON 10 键 / B JSON 10 键 / B kit 名含 ddrph 非 ddcpc / B device_classes ≥10 + 期望 B-only 名 / B cellname_kit_rules ≥40 / B preroute_constraints ≥5 / B via_defs ≥3 / B example_cells ≥3 / report 含 ≥2 模板 kw / 反硬编码 B 0 个 A-only token word-boundary / 3-seed md5 一致
- **l1_subgrade**：L1-realrun-python（续标）
- **domain**：schematic_netlist（CDL netlist → GDS 流，netlist:1038 dominant）

## 注意

- tgs17 是 374-msg 长会话；只锚 U#231（单轮 produce 模板），不要把整条 skill 开发史塞进判分
- U#327（用模板跑全流程生成 gds）是另一独立 produce 候选，可作 r942 第二案（2nd-case-same-session，承 r939 范式）
- cross-shard check：tgs17 0 hits in main merged jsonl + 0 in all4 ledger except D-parked → 无跨 shard 碰撞，可 claim

## r942 U#327 GOLD 扩展（autocell-tcl-flow-generator produce-task）

**fetch**: r942 eda_flow open_session(shardD-r942-probe) + ssh .75→10.129.35.73 cat `1789092579396_tgs17/1789092579396_tgs17.messages.json` (1,290,843B, 374 msgs)

**U#327 verbatim** (msg[327], id=msg_mu0jmh2y_nio):
> `/autocell-tcl-flow-generator /home/miccao/autocell/ddcpc/netlist/train_proplus_decqa_20260903/netlist_dir_20260807这是网表路径，依据/home/miccao/autocell.1.2026.7/g5_ddcpc/config/cell_constraints_template.txt里面的设置，生成所有的gds，放到/home/miccao/autocell/ddcpc/gds下面`

**意图分型**: **true L2 produce-task**（用户 invoke autocell-tcl-flow-generator skill 跑全流程：netlist_dir_20260807 含 544 .cdl 文件 + cell_constraints_template.txt → 生成所有 GDS 到 ddcpc/gds/）。**非 howto Q&A**——用户要"跑"不是"解释"，reframe 成 manual-grounded howto 会违反 11-15 任务初衷第 1 条（任务形态=用户意图）。

**assistant 执行链** (msg 328-374, 47 msgs):
- A#328: tool_use `skills` autocell-tcl-flow-generator (skill invocation)
- A#330: run_commands `ls netlist_dir_20260807/` → 544 .cdl 文件 (and2GF47x1-4, and2PF47x1-4, and2x1-4, and3GF47x1-3, ...)
- A#332: `head -5 and2GF47x1.cdl` → `*and2GF47x1 / Type: cdl / Tool: AETHER-SE` + 检查 rule.json kit 映射
- A#334: `ls | sed 's/\.cdl//' | sort` 列全 543 cell
- A#340 (A-text 117字): "网表中存在子电路（层级结构）。AutoCell 期望顶层 .SUBCKT 与单元名称匹配。我来编写一个批处理脚本..."
- A#348 (A-text 95字): "问题——这个网表是层级化的（包含子电路 nand2PF 和 invGF），但原始的 g5_ddcpc 网表是扁平的。AutoCell 需要扁平化的网表..."
- A#350 (A-text 154字): "新网表是分层的，包含子电路调用（XInand2PF_0、XIinvGF_0）...需要编写一个预处理器将分层网表扁平化..."
- A#364 (A-text 139字): "实例名称前缀使用 Inand2PF_0 而不是 XInand2PF_0...原始网表会加上子电路调用名称作为内部网表的前缀..."
- A#368 (A-text 88字): "第 65 行缺少 params = {} 的初始化...添加 params = {} 并将调用名称前缀设为 X..."
- msg 374 = trace 末尾（assistant 仍在调试 netlist flattening 脚本，**未产出最终 GDS**）

**GOLD 状态**: **incomplete** — assistant 在 trace 末尾仍调试 netlist 扁平化预处理器（层级 .cdl → 扁平 .cdl 供 AutoCell 消费），未跑到 AutoCell 生成 GDS 阶段。无 clean final deliverable 可作 gold-standard。

**r942 判定**: U#327 是 **true L2 produce-task deferred to r943+**：
- **非 manual-grounded howto reframe 候选**（用户意图=run 非 explain，reframe 违反任务初衷）
- **需 full L2 pipeline 重建**：A=netlist_dir 子集（~10-20 .cdl）+ cell_constraints_template.txt + 扁平化预处理器脚本；candidate=扁平化 + AutoCell schematic 命令 + GDS streamout；check=GDS 文件结构 + cell 数 + 扁平化等价性 + 端口匹配（≥8 断言真跑 subprocess）
- **预算估计**: 60-90 min（fetch GOLD + 重建扁平化逻辑 + 合成 B 平行 netlist + 真跑 AutoCell check + 3 neg + §4.9）
- **r942 40-min budget 不足**（mandatory discuss 15min + infra probe 5min + U#327 fetch/scan 10min ≈ 30min 已用，余 ~10min 不够 L2 pipeline）

**r943 建议**: ① 若 budget 充裕（>60min）可 attempt U#327 L2 produce-task（需 eda_flow run_code pyAether 跑 AutoCell schematic + GDS streamout，hidden B 平行 netlist 库）；② 否则选 fresh mc≥10 D-pure 候选做 manual-grounded howto reframe（11 例范式快速复用）；③ yv34j mc=11 .cdl:992 D-pure r788 claim-by-exception 可直接 claim。
