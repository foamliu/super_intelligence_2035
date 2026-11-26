# Deepread: 1793621647806_3u5t4 — chengk@hfeg0plg96 IDD power-rail flow railMap missing-node diagnosis

**session**: `1793621647806_3u5t4` · user `chengk` · host `hfeg0plg96` · mc=70 · 158 msgs · 8M input tok · schematic_netlist-dominant (netlist:210/drc... but real task is IDD power-rail netlist flow)
**model**: deepseek-v4-flash · cwd `/home/chengk/work/code/Idd_check_power_all/code/code_v0`

## 用户轮（4 轮，全 produce/debug）

- **U[0]**: 「在 code_v0/ 执行 `main_check_power_all.tcl -proj ddgoa -version V0 -head ../../data/netlistHeader -rundir ../../output/ -vtable ../../data/vtable_real.csv -rawvir ../../data/rawVirSrc.tcl |& tee test_log` 生成的 railMap.csv 缺少 vdd2hzmbist，详细分析代码，解释原因」
- **U[102]**: 「为什么我再次运行…生成的结果中还是缺少」（用绝对路径 -rawvir）
- **U[116]**: 「在 code_v0/test/ 下重新运行，要求先将代码和输入输出文件都先 copy 到该目录，不改变源代码」
- **U[144]**: 「…tclsh ./main_check_power_all.tcl … invalid command name "dict"」（命令行把 tclsh 跟目录路径粘在一起）

## 金标准机制（助手因果实验坐实）

`main_check_power_all.tcl` 流水线：
1. **`extract_netlist_power_nodes`**（L19-47）：从 netlistHeader 提取所有 `!` 结尾电源节点 → `nodelist`（小写）。`vdd2hzmbist!` 确认在 nodelist（allresult.log L428）。
2. **`innNetlistRailTblBasic`**（L57-168）4 步：
   - Step 1：解析 `vtable_real.csv` 的 `pow_def`。每源轨：alias 用 `matchNodesInList`（glob）找真实别名；`virtual`（如 `vdd2hz*`）glob `nodelist` → 每命中虚拟节点 `dict set basicRailTbl $virtualName ... railtype "virtual"`。⇒ `vdd2hzmbist!` **进 basicRailTbl**。
   - Step 3：解析 `rawVirSrc.tcl` 的 `unmapped → zigzag → pwr/gnd` **手写正则列表** → 只这里枚举的虚拟轨被赋 `domGrp` → 只有有 `domGrp` 的进 `railGrpTbl` → 写 `railMap.csv`。
3. **根因**：`vdd2hzmbist!` 在 netlist + basicRailTbl，但 **rawVirSrc.tcl 的 unmapped→pwr 列表没枚举它** → 无 domGrp → 静默丢弃 → 不进 railMap.csv。
4. **因果实验**：删 rawVirSrc.tcl 里 `vdd2hzmbist!` 行 → railMap 1046→1045 行，vdd2hzmbist 消失；保留 → 正常出现（L126）。**唯一开关** = rawVirSrc.tcl 枚举列表有无该节点。
5. **量化**：netlist 里 71 个虚拟 `z` 轨未在 rawVirSrc 枚举 → 全不进 railMap。
6. **U[144] `invalid command name "dict"`**：用户命令行把 `tclsh` 跟目录路径粘成 `/home/.../code_v0/tclsh`（不存在），非脚本逻辑问题；`dict` 是 Tcl 8.5+ 内建。

## 关键资产（.75 hfeg0plg96，沙盒可达但生产文件不外带 → B-grade synthesized）

| 文件 | 格式 | 行数 | 说明 |
|---|---|---|---|
| `data/netlistHeader` | SPICE `.GLOBAL` + `+` 续行，`!` 结尾节点 | 24 | 全量电源节点（真实 + 虚拟 z） |
| `data/vtable_real.csv` | `name,virtual,alias,min,typ,max,intext` | 418 | virtual 列给 glob（vdd2hz*/vssz*） |
| `data/rawVirSrc.tcl` | `set rawVirGrpTbl { unmapped { zigzag { pwr {…} gnd {…} } } }` | 520 | 手写枚举的虚拟轨列表 |
| `code_v0/railMap.csv` | `rail,src,src_co,struct,polar,domGrp` | 1046 | 生成的 rail map（缺未枚举虚拟轨） |

## B-grade synthesized case 设计（RailMapMissingAudit-001）

**任务**：给 4 份输入（netlistHeader + vtable.csv + rawVirSrc.tcl + railMap.csv），写 CLI 审计工具找 railMap 里缺失的虚拟电源轨并分类。
- parse netlistHeader（.GLOBAL/+ 续行，`!` 节点）→ 全节点集 N
- parse vtable virtual 列 → glob 集 G
- parse rawVirSrc.tcl → 枚举集 E（所有 `!` token）
- parse railMap.csv 第一列 → 输出集 R
- 虚拟候选 = N ∩ match(G)；逐节点分类：`present` / `missing_not_enumerated`（不在 E 且不在 R）/ `unexpected_present`
- 输出 `missing_rails.csv`（rail,in_netlist,matches_virtual_glob,in_rawvir_list,in_railmap,reason）+ `audit_summary.json`（9 键）

**A/B/C 不相交**：
| 档 | prefix | 真实轨 | 虚拟候选 | 枚举 | 缺失 | 用途 |
|---|---|---|---|---|---|---|
| A | vdd2hzA | 5 | 10 | 7 | 3 | SUT 可见 + example |
| B | vdd3hzB | 6 | 14 | 9 | 5 | hidden（check.py 跑） |
| C | vdd4hzC | 3 | 8 | 4 | 4 | 嵌入 check.py 反硬编码 |

SUT `railmap_missing_audit.py` 纯 stdlib(re/csv/json/os/sys)，禁 subprocess/socket/urllib/ctypes/eval/exec/numpy/pandas + 禁 B/C 字面量。
check.py 14 条件 a-n 独立 oracle（独立 _oracle 复算）。ref PASS 14/14 + 4 neg 全 FAIL(empty→e/print→e/hardcode_a→g,h,j,k,l,m/core_deleted→g,h,j,k,l,m) + 3-seed sha256 一致 + jsonl round-trip PASS。k_rationale=k_check=14 ✓。

**维度正交**（vs D.jsonl 既有 case）：vs RcCellCapReport（RC report per-cell cap 求和）/ CdlPlacePlanGen（CDL 层次布局）/ GioLioAbTilingGen（GIO/LIO tiling netlist 生成）/ PwlDecodeStimGen（PWL 激励译码）/ FuseAddrCompare（fuse rpt 比对）—— 本 case 是 **power-rail flow 缺失虚拟轨审计**（netlist .GLOBAL + vtable glob + Tcl 枚举 + railMap diff），机制独有 → 非 dup ✓。

**difficulty = L1**（诚实标：SUT 纯 stdlib 文本解析，无 EDA/TCL 运行时，与 r518-r527 一致；资产在 .75 hfeg0plg96 私有工作区，沙盒虽可读但生产 netlistHeader 不外带 → synthesized）。
