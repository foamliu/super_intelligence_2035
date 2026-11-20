# itvhk — PowerFill 后端流程（RSCALC→AutoVia→PowerFill 降阻 flow）深读笔记

- **trace**: `1785846039627_itvhk.messages.json`，user `e0014566`，host `hfeg0plg58`，match_count 689
- **cwd**: `/home/e0014566/test_layout_rscalc_flow_4`（layout resistance-reduction flow 第 4 次迭代工程）
- **规模**: 1.49 MB，356 msgs（178 user / 178 assistant），tool_use：run_commands 111 + read_files 24 + search_codebase 13 + SandBox_MCP_Server__run_code 10 + editor 10
- **关键字**: virtuoso:672 / calibre:187 / cellview:29 / hspice:1
- **领域判定**: layout_virtuoso（Virtuoso SKILL 驱动 RSCALC/AutoVia/PowerFill 流程；与 m2vah/ResFlow-001 同 family，本 trace 多了 PowerFill 第 3 段 + calibredrv GDS 审计 + calibre DRC short-check）

## 11 条 substantive user msg（`<user_input mode="act">` 标签包裹）

1. `请完整跑一下 prompt_flow.md 整个的过程` — 驱动整个 flow
2. `到目前为止,请你总结一下碰到的问题`
3. `请你帮忙排查下 PowerFill 未生成任何填充的原因. Power fill 也有一个 powernet, 这个我是留空的, 意思是自己去找到所有合适的 Powernet, 都填上.` — **PowerFill pwrnet 自动发现**
4. `要的, 修复吧.`
5. `OK，现在你能把整体流程的核心步骤描述一下吗？`
6. `当中的一个关键点是 gds 文件的传递。你循环两次，明确说一下，每一步的 gds 是如何获取的。`
7. `上面在 powerfill 这一步，如果检测到gds文件已经存在，你会怎么做，直接用这个已经存在的gds文件吗？还是说用生成的，把这个已经存在的覆盖了。`
8. `这样不对，应该用新生成的，覆盖已有的 GDS` — **GDS 传递 bug 修正：用新生成覆盖旧**
9. `上面在 autovia 这一步，如果检测到gds文件已经存在，你会怎么做...`
10. `要的, 修复吧.`
11. `好的，你再举两个循环的例子，说一说 GDS 文件的传递流程。`

## flow 主线（三段迭代降阻）

```
RSCALC (run_rscalc_nogui.il, Virtuoso SKILL)
  └─ 跑电阻 → 产 *.rvn → awk 解析 baseline_rpoints.csv (key=net_layer_purpose, val=rpoint)
AutoVia (run_autovia_nogui.il)
  └─ 插 via → 生成 testa_via1 cell (cellName=testa → outCellName=testa_via1)
PowerFill (genPowerFill.py + run_powerfill_nogui.il + calibre DRC short-check)
  └─ 电源填充 → pwrnet 留空自动从 GDS text label 发现 (vdd/vss/vbb)
                → 跑完在 cell 树加 *_auto_pgfill marker cell
                → 生成 testa_opt1 (cellName=testa_via1 → outCellName=testa_opt1)
                → calibre -drc 10G4plus_Short_Check.rule on testa_via1.gds → short.results/short.summary
迭代: testa → testa_via1(AutoVia) → testa_opt1(PowerFill) → testa_via2(AutoVia on opt1) → ...
```

## calibredrv GDS 审计（本 case 抽取的可复用子流）

trace 用 `calibredrv -a layout peek <gds> ...` headless 审计 PowerFill 输出 GDS：
- `-topcell` / `-cellcount` / `-cells` / `-layers` / `-bbox` / `-precision` / `-format` / `-units` / `-celltext <cell>`
- 组合调用：`peek <gds> -topcell -cellcount -precision -format -units -bbox`
- pwrnet 自动发现 = 从 topcell celltext 取 text label unique 集合 → 排除层名 token(M1/V1/CT 形如 `^[A-Z]\d+$`) → 折叠 Cadence 全局 bang(vdd! → vdd) → 剩余即 pwrnet
- `*_auto_pgfill` cell = PowerFill 真跑过的 marker（在 cell 树里）

## .75 calibredrv 沙盒实测

- 路径：`/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibredrv`
- 版本：Calibre DESIGNrev v2020.1_36.18（headless，无需 X11，license 无需额外）
- 可用 flag：`-topcell`/`-cellcount`/`-cells`/`-layers`/`-bbox`/`-precision`/`-format`/`-units`/`-celltext <cellname>`/`-cellhlayers`/`-celllayers`/`-cellproperty`/`-cellcount`/`-topcells`/`-format`/`-emptycells`/`-undefcells`
- ⚠️ `-all` 在 v2020.1 **不存在**（`Unknown request: "-all"`）—— trace 里用的 `-all` 是更高版本的 flag
- ⚠️ `layout text` **不是** subcommand（`layout [all|copy|copy2|create|delete|droasis|filemerge|filtershapes|merge|overlays|peek|tbmode]`）
- calibredrv 会在 cwd 建一个 `.calibredrv_workspace` 目录（正常副产物）

## 真实 artifacts ground truth（scp hfeg0plg58 → .75 实测）

| 字段 | A = testa_via1.gds | B = testa_opt1.gds |
|:--|:--|:--|
| 路径 | /proj/.../drc/austin_rscalc2/testa_via1/genPowerFill/testa_via1.gds | /proj/.../rscalc/e0014566/testa_opt1/testa_opt1.gds |
| filesize | 221184 | 243712 |
| topcell | testa_via1 | testa_opt1 |
| cellcount | 29 | 31 |
| cells 含 *_auto_pgfill | **无** | **有** (testa_via1_auto_pgfill) |
| bbox | {3530 -21410 1196470 57410} | {3530 -21410 1196470 57410}（同） |
| precision | 4000.0 | 4000.0（同） |
| format | GDS | GDS（同） |
| units | 0.00025 | 0.00025（同） |
| text_labels (celltext top) | {M1, vbb, vdd, vdd!, vss} | {M1, vbb, vdd, vdd!, vss}（同） |
| pwrnets (auto-detect) | {vbb, vdd, vss} | {vbb, vdd, vss}（同） |

A 是 B 的前一段迭代产物（AutoVia 出来还没跑 PowerFill），几何结构未变，只是 B 多跑了 PowerFill 加了 `_auto_pgfill` cell + 2 个 VIA cell。**判别字段**：topcell / cellcount / has_auto_pgfill / filesize（bbox/layers/text_labels/pwrnets 相同）。

## calibre DRC short-check（trace 旁路，未在本 case 用）

- rule: `10G4plus_Short_Check.rule`（DRAM PowerFill short-check，Calibre TVF v2017.2 生成，ChangXin Memory Technologies，V2.8 2025/09/18）
- 调用：`calibre -drc -hier -turbo -xhla` on `test.svrf`（LAYOUT PATH testa_via1.gds, LAYOUT PRIMARY testa_via1）
- 产物：`short.results`（ASCII, 0 results = clean）/ `short.summary`（DRC-H summary report）
- 本 case 不用此步（需完整 rule file + layer.map + tech，移植到 .75 风险高）；只用 calibredrv 结构审计（自包含，仅需 GDS）。

## 抽取的 case

**EDA-Eval-DesignFlow-PowerFill-001**（physical_verify 域扩量#4, L2）：
- deliverable = `pf_audit.py`（纯标准库，calibredrv subprocess → JSON report 13 字段）
- assets A = gds_A.gds (testa_via1) + task_brief.md
- hidden B = gds_B.gds (testa_opt1, 结构不同: topcell/cellcount/has_auto_pgfill/filesize)
- check.py 13 条件 a-m，跨输入 guard A=testa_via1/29/无pgfill/221184 ≠ B=testa_opt1/31/有pgfill/243712
- 关键 discriminator：`*_auto_pgfill` cell-tree marker + pwrnet 自动发现（M1 排除 + vdd!/vdd 折叠）+ 跨输入 guard
