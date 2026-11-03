# Deep-read: sid 1789350621467_fymcr (miccao, hfeg0plg92, mc=407)

- **session**: `/home/miccao/.cline/data/sessions/1789350621467_fymcr/1789350621467_fymcr.messages.json` (1.23MB, 268 msgs, 11 real user_input)
- **user/host**: miccao @ 10.129.32.47 (hfeg0plg92)
- **domain**: layout_aether (Empyrean AutoCell automatic layout/GDS generation)
- **tools used**: run_commands(109) · editor(15) · read_files(10) · skills(1) — heavy CLI orchestration, no pyAether direct
- **match_count**: 407 (matched `aether`/`layout` keywords via autocell/netlist/GDS paths)

## UI 轮（逐字原文）

- **UI#1 (idx=0)** — 纯需求 A-档 seed 候选：
  `/home/miccao/autocell/ddcpc/netlist/train_proplus_decqa_20260903/netlist_dir_20260807这是网表路径，依据/home/miccao/autocell.1.2026.7/g5_ddcpc/config/cell_constraints_template.txt里面的设置，生成所有的gds，放到/home/miccao/autocell/ddcpc/gds下面，/apps/proplus/autocell.1.2026.8这是autocell的安装包`
  → 给定网表目录 + cell_constraints_template + autocell 安装包，批量生成所有 cell 的 GDS。**用户只给目标，未给根因/修复**。
- UI#2 (idx=131): 你用到的pcell.tcl在哪里
- UI#3 (idx=135): /proj/drgqa/V0/libs/TECHLIB_release 这是我新工艺的techlib，依据他做一套pcell.tcl，放到/home/miccao/autocell/v1/pcell下
- UI#4 (idx=177): /proj/train/ddcpc/libs/TECHLIB_RELEASE 依据这个做一套，放到/home/miccao/autocell/g5下
- UI#5-8 (idx=189-199): 比较两套 pcell 是否逻辑相同 / 参数是否合理
- UI#9 (idx=213): 那当然，开始吧（批准批量跑）
- UI#10 (idx=259): 再次比较 pcell 套
- UI#11 (idx=263): 生成pcell.tcl的过程包装成一个skill,依据现有模板和用户指定的techlib路径下的文件，用户也可以指定脚本放的位置，skill叫pcell_tcl_create

## Agent 行为与产物

1. **探索** (idx=1-20): ls 网表目录(544 .cdl 文件)、cat cell_constraints_template.txt、ls autocell 安装包、cat rule.json、cat lib.ini、head and2x1.cdl。
2. **autocell 试跑** (idx=15-25): 解决 license (PRIMARIUS_LICENSE_FILE=15281@hfds2:1521@hfds1)、LD_PRELOAD、python 版本 (python3.11)，跑通单 cell `and2GF47x1` GDS 生成。
3. **batch_generate.sh** (idx=25-86 多轮 editor): 构建批量脚本，核心组件：
   - **map_kit() bash case 语句**（first-match-wins，镜像 rule.json）：cell 名前缀 → kit 名。关键顺序：`mxi2GFD*`/`mxi2PFD*` → FD_MT2 必须在 `mxi2GF*`/`mxi2PF*` → F_MT2 **之前**，否则 PFD cell 被通用 PF 规则吞掉。
   - **flatten_netlist.py** (idx=13): 把层级 .cdl 网表展平（提取顶层 .SUBCKT，丢弃嵌套 subckt 定义）。
   - **per-cell autocell 调用**: `timeout $CELL_TIMEOUT $AUTOCELL_BIN $kit_tcl -d cell_name=...,netlist_path=<flat>,gds_path=...,placement_path=... --msg_level 1 --output $GDS_DIR --log_file ...`
   - **skip-on-existing**: 若 GDS 已存在则跳过；**timeout(124) 处理** + 部分GDS清理。
   - 计数 SUCCESS/FAIL/SKIP，写 failed_generation.txt / failed_unknown_kit.txt。
4. **pcell.tcl 生成** (idx=131-213): 依据 techlib 做一套 pcell.tcl。
5. **skill 包装** (idx=263): 把 pcell.tcl 生成包装成 `pcell_tcl_create` skill。

## A-档 vs B-档判定

- UI#1 是纯需求 A-档 seed（用户只给目标：批量生成 GDS）。
- 但 trace 末尾 (UI#11) 转向 pcell.tcl skill 包装，**无单一工具产物被用户干净接受**（无 byte-faithful accepted gold）。
- 真 L2（真跑 autocell 1.26.8 + license + Calibre 环境）不可在沙盒复现。
- → **A-档 disqualified → B-档 synthesized, L1-boundary**。

## 合成设计 (gold = autocell_orchestrator.py)

把 trace 的 `batch_generate.sh + map_kit + flatten_netlist.py` 的**可验证核心**抽成离线 Python 编排器：
- 读 netlist 目录（.cdl cells）+ 有序 rule.json（first-match-wins pattern→kit）+ config
- **有序 first-match-wins kit 映射**（核心难度：specific pattern 在 general 之前）
- **顶层 SUBCKT 提取**（flatten，丢弃嵌套 subckt）
- **dry-run autocell 命令生成**（不执行，无需真 autocell）
- **skip-on-existing-GDS** + timeout 包装
- 输出确定性 run-plan JSON（total/mapped/unmapped/skipped/per_kit_counts/cells/unmapped_cells）

判分在隐藏 B 上 subprocess 真跑候选；B 与 A 规模/取值/结构全不同（A=13 cells x2 suffix + x_MT2/L_MT2/FD_MT2/F_MT2/S_MT2/STD kit 名；B=16 cells x1 suffix + K_DUAL/K_FAST/K_SLOW/K_LOW/K_BASE/K_STD kit 名 + 2 unmapped + 1 pre-existing GDS）。

## 与既有 case 区别

- DeckIncludeResolve=SVRF deck INCLUDE 闭包+条件编译；LVSLogFilter/LVSDiag=LVS rep；DRConnTiming/DRCTimeStats/DRCSFCompare=DRC log；NetHierTrace/CCKDriverFind=netlist 拓扑；AutoViaPFAudit=instance 分类；RNodePlan=RTEXT/RNODE 放置；PowerFill=GDS 审计。
- 本案 = **AutoCell 批量 GDS 生成编排 + 有序 first-match-wins kit 映射 + 顶层 SUBCKT 展平**，主题/断言独立。
