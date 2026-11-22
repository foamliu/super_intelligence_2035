# Deepread: bowenguo@hfeg0pfn120 — drcpa_analog nicap cell-map capacitance analysis

**Session**: 1795156640138_cnxqz (bowenguo @ hfeg0pfn120, mc=85)
**Scan keywords**: drc:3602; schematic:2581; netlist:2465; analog:1812; pdk:318; cmos:198; lvs:87; cadence:21
**Date**: 2025-11-20 (session ts 1795156640)
**Domain**: physical_verify (PDK/DRC library cell-map + nicap characterization)
**Freshness**: 4-shard ledger grep → 0 hit (truly fresh)

## User intent (msg #0, verbatim summary)

用户要求在 `drcpa_analog` 库中找出 13 个 `AG_CapYdec...` decoder capacitor cell:
- AG_CapYdecfarTopLTop, AG_CapYdecfarTopCenterTop, AG_CapYdecfarTopLNormal, AG_CapYdecfarTopCenterNormal, AG_CapYdecfarBotLNormal, AG_CapYdecfarBotCenterNormal, AG_CapYdecfarTopRTop, AG_CapYdecfarTopRNormal, AG_CapYdecfarBotRNormal, AG_CapYdecnearTopTopL, AG_CapYdecnearTopNormalL, AG_CapYdecnearTopTopR, AG_CapYdecnearTopNormalR

**统计 nicap 的类型和容值**，参考用户给出的 1S/2S Nicap 表格格式：
- 1S Nicap 表：cell 名 | 容值(pF) | 各 net-pair 列(vad2o!-vss!, vwln!-vss!, vblh!-vss!, vad2e!-vss!, vcc!-vss!, vintlp!-vss!, vdleq!-vss!, vncsgn!-vss!, vkb!-vss!, vpcsg_vcc) 下方填每个 cell 在该 net-pair 上的实例数，最后一行"总容值"
- 2S Nicap 表：cell 名 | 容值(pF) | vwlp!-vcc! | viso!-vss!

## Assistant 工具链 (71 msgs)

1. `list_allowed_files` — 探索工作目录结构
2. `run_approved_command` — 查找 drcpa_analog 库、cell_map 文件位置
3. `read_files` — 读取 cell_map 文件内容 + SPICE model (G5_CIP_Model_D5_v0d9_rev01.sp) 中的 nicap 定义
4. `editor` — 写 `find_nicap.py` (msg #55)：扫描 `/home/bowenguo/.empyrean/cell_map/` 找匹配 13 个目标 cell 的 `.netlist.map` 文件，打印 cell_map 内容（sub-cell 列表），再搜 SPICE model 中 nicap/cxcap 定义
5. `run_approved_command` — 执行 find_nicap.py（多次重跑，最终被 SIGKILL/aborted）

## 关键产物

### cell_map 文件格式 (`.drcpa_analog__<CellName>__schematic.netlist.map`)
```
drcpa_analog/AG_CapYdecfarTopLTop/schematic		AG_CapYdecfarTopLTop
drcpa_analog/AG_CXcap1S151x167/schematic		AG_CXcap1S151x167
drcpa_analog/AG_CXcap1S199x167/schematic		AG_CXcap1S199x167
...
```
- 第一行 = 父 cell（目标 cell），后续行 = sub-cell 实例（AG_CXcap1S/2S 变体）
- Tab 分隔，两列：library/cell/schematic 路径 + cell 名

### AG_CapYdecfarTopLTop 的 sub-cell 列表（19 个）
AG_CXcap1S151x167, AG_CXcap1S199x167, AG_CXcap1S151x119, AG_CXcap1S271x167, AG_CXcap1S175x119, AG_CXcap1S103x167, AG_CXcap1S223x167, AG_CXcap1S631x95, AG_CXcap1S295x167, AG_CXcap2S223x80, AG_CXcap2S415x56, AG_CXcap2S175x56, AG_CXcap1S79x167, AG_CXcap1S511x167, AG_CXcap1S175x167, AG_CXcap1S295x119, AG_CXcap1S199x119, AG_CXcap1S439x95

### SPICE model nicap 定义
- 文件：`/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9_rev01/G5_CIP_Model_D5_v0d9_rev01.sp`
- Line 46: `**nicap copy from G5_CIP_LP6`
- Lines 176-356: `.lib 'incFile_G5_CIP' nicap` (多处引用 nicap subckt)

### 1S Nicap 参考容值表（用户提供）
| Cell | 容值(pF) |
|---|---|
| AG_CXcap1S439x95 | 208.525 |
| AG_CXcap1S151x119 | 89.845 |
| AG_CXcap1S295x119 | 175.525 |
| AG_CXcap1S223x191 | 212.965 |
| AG_CXcap1S295x191 | 281.725 |
| AG_CXcap1S247x191 | 235.885 |
| AG_CXcap1S319x119 | 189.805 |
| AG_CXcap1S511x503 | 1285.165 |
| AG_CXcap1S175x119 | 104.125 |
| AG_CXcap1S199x503 | 500.485 |
| AG_CXcap1S271x503 | 681.565 |
| AG_CXcap1S151x503 | 379.765 |
| AG_CXcap1S223x119 | 132.685 |
| AG_CXcap1S103x503 | 259.045 |
| AG_CXcap1S175x503 | 440.125 |
| AG_CXcap1S247x503 | 621.205 |
| AG_CXcap1S463x215 | 497.725 |
| AG_CXcap1S103x191 | 98.365 |
| AG_CXcap1S295x503 | 741.925 |
| AG_CXcap1S199x119 | 118.405 |
| AG_CXcap1S247x119 | 146.965 |
| AG_CXcap1S391x119 | 232.645 |
| AG_CXcap1S223x503 | 560.845 |

### 2S Nicap 参考容值表（用户提供）
| Cell | 容值(pF) |
|---|---|
| AG_CXcap2S199x56 | 27.860 |
| AG_CXcap2S127x248 | 78.740 |
| AG_CXcap2S175x56 | 24.500 |
| AG_CXcap2S319x200 | 159.500 |
| AG_CXcap2S175x248 | 108.500 |

## Session 结局

Assistant 只找到 1/13 cell_map（AG_CapYdecfarTopLTop），脚本被反复重跑后 SIGKILL。用户任务未完成。但**任务意图清晰**：parse cell_map → 提取 sub-cell 列表 → 按 nicap_spec 查容值 → 按 net-pair 汇总。

## Case 合成判断

- **子型**: `nicap_cell_map_cap_summary` — 解析 drcpa_analog cell_map（AG_CapYdec 父 cell → AG_CXcap sub-cell 实例），按 nicap_spec (容值表) 查值，按 1S/2S 类型 + net-pair 汇总容值分布 → report.json
- **DoD**: SUT 写 `nicap_analyze.py`，读 cell_maps/ + nicap_spec.tsv，输出 report.json（per-cell subcells/types/total_cap/netpair_dist/cap_by_netpair + summary）
- **判分有牙**: check.py 18 条独立断言，hidden B（4 cells/56 subcells）与 A（5 cells/67 subcells）不同 cell 名/sub-cell 组合/net-pair 分布；anti-hardcode A-swap；3-seed 确定性；§4.9 三假全 FAIL
- **沙盒**: 纯 Python 标准库，无需 EDA 工具
- **跨 shard 正交**: bowenguo 4-shard ledger 0 hit；C.jsonl 无 bowenguo；子型 `nicap_cell_map_cap_summary` 首例
