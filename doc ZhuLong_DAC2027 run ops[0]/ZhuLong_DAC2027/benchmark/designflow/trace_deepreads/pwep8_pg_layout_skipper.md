# pwep8 — PG Cell Layout Build via Skipper (deepread note)

- **trace**: `1792563683776_pwep8.messages.json`, user `jianhaiq`, host `hfeg0plg88` (10.129.2.x), match_count 517, cwd `/home/jianhaiq/...`, model glm-5.x, status completed exit 0, 2026-10-xx.
- **规模**: 494 msgs (277 user / 217 assistant), 272 tool_use = 72 editor + 66 run_approved_command + 53 read_files + 34 search_apis + 余 continue/其它。4 条 substantive user msg（其余 continue/yield）。
- **真实任务（user 原话）**:
  1. "帮忙写一个 tcl 脚本 PG_check.tcl；脚本用法：PG_check.tcl list；list 文件提供两行三列（mos: <cdl> <gds> / res: <cdl> <gds>），由空格隔开；第一步抓 mos 行第三列（GDS）调用；第二步抓 res 行第三列（GDS）调用；第三步用这两个文件生成 test_ptn_to_ptn.gds，注意：1. 调用了两次 mos 文件，两颗 mos 的放置位置和如何排放的；2. 中间放置的 res 是如何放置的；3. mos 和 res 使用 PG_drawing layer 连接；4. 使用 PG_pin layer 打 label，分别打在左侧 mos 上 PG_PCH 和 AT4_PCH 重叠的区域，和右侧 mos 上 PG_PCH 和 AT4_PCH 不重叠的区域；5. 使用 skipper 工具产生 test_ptn_to_ptn.gds，不使用 aether 工具。"
  2. （续）补充 PG_drawing/PG_pin 层号确认（97.0/99.0）。
- **agent 流程**:
  1. 先用 **pyAether**（host=aether）写 `PG_check.py` 失败（GUI/环境问题）。
  2. 改用 **Skipper Tcl** 批处理：`skipper <tcl> <args> -noterm`，写 `PG_check.tcl`。
  3. 用 search_apis(34) 查 Skipper Tcl API：dbImport/dbLibGetId/dbLibTopCell/dbCellGetBBox/dbCellGetLayerBBox/dbLibCreate/dbCellCreate/dbCreateInst/dbCreateRect/dbCreateLabel/dbCellExport/dbFindInst/dbFindLabel/dbFigGet。
  4. 反复 editor(72) 编辑 tcl + run_approved_command(66) 调 skipper 跑 + read_files(53) 看输出，迭代调试 parse_list（用 regex split，遇 backslash 转义问题）、bbox 解包（dbCellGetBBox 返回 1-元素列表需 lindex）、绝对路径（dbImport 需绝对路径）、MY 镜像坐标映射。
  5. 最终在 skipper 上跑通，生成 test_ptn_to_ptn.gds。
- **.75 Skipper 沙盒实测**（经 eda_flow run_code host=skipper / run_commands）：
  - 二进制 `/apps/empyrean/tools/skipper/bin/skipper`，版本 2020.06.sp3，批处理 `skipper <tcl> <list> <out> -noterm` 退出 0，license SKI_VIEWER/SKI_EDITOR。
  - **可用 API**：dbImport(abs path)→h / dbLibGetId / dbLibTopCell / dbCellGetBBox→`{xl yl xh yh}`(um) / dbCellGetLayerBBox -layer <lpp> / dbLibCreate -dbu 1000 / dbCellCreate / dbCreateInst(-instPos (x,y) -instOrt R0|MY|MX|...) / dbCreateRect(-lpp <num> -box {(x1,y1),(x2,y2)}) / dbCreateLabel(-lpp -txtPos -string -height) / dbCellExport -fileName / dbCountInst / dbFindInst -masterNamePattern / dbFindLabel -strPattern ""（空串返所有 label，`*` 返 0）/ dbFigGet（inst: `inst cell:TOP cell:MASTER {x y} ORT {bbox} 1.0 inst {}`；label: `label cell:TOP 99 0 {bbox} {x y} TEXT 0.2 R0 ...`）。
  - **关键坑①**：`dbCellGetBBox`/`dbCellGetLayerBBox` 返回 **1-元素列表**包着 4 坐标字符串（`llength`==1），必须 `lindex $v 0` 解包后再 `lassign` 取 4 分量。reference 用 `bbox4` helper 处理。
  - **关键坑②**：`dbImport` 要求 **绝对路径**；listf/outgds 若相对路径须 `[pwd]/$p` 拼。
  - **关键坑③**：`dbCreateRect -lpp` 用**数值** lpp（`97.0` = layer 97 datatype 0），不用层名。
  - **关键坑④**：reference tcl 必须**无反斜杠**（regex backslash 经 JS template/upload 会损坏）——parse_list 改用 string ops（string first/string range/split）而非 regex。
- **asset 几何 ground truth**（.75 实建 GDS，dbLibCreate/dbCellCreate/dbCreateRect/dbCellExport，无 tech）：
  - **A** `mos_a.gds`(306B) cell MOS_A：PG_PCH 11.0=(0,0,2.0,1.0)、AT4_PCH 14.0=(0,0,1.4,1.0)、body 1.0=(0,0,2.0,1.0) → 重叠区**左** [0,1.4]、非重叠区**右** [1.4,2.0]。`res_a.gds`(178B) cell RES_A：body=(0,0,0.8,1.0)。MP1 R0@(0,0)、R1 R0@(2.5,0)、MP2 MY@(3.8,0)。VDD 期望世界 (0.7,0.5)∈[0,1.4]；VSS 期望世界 (2.1,0.5)∈MP2-MY 映射后 [1.8,2.4]。
  - **B（隐藏）** `mos_b.gds`(306B) cell MOS_B：PG_PCH=(0,0,3.0,1.2)、AT4_PCH=(1.2,0,3.0,1.2) → 重叠区**右** [1.2,3.0]、非重叠区**左** [0,1.2]。`res_b.gds`(178B) cell RES_B：body=(0,0,1.2,1.2)。MP1 R0@(0,0)、R1 R0@(3.5,0)、MP2 MY@(5.2,0)。VDD 期望 (2.1,0.6)∈[1.2,3.0]；VSS 期望 (4.6,0.6)∈MP2-MY 映射后 [4.0,5.2]。
  - **跨输入判别**：A 重叠左/B 重叠右 + 尺寸不同 → VDD/VSS 世界坐标不同；硬编码任一输入坐标在另一输入上败。MP2 MY 映射：cell (cx,cy)→world (mp2.x−cx, mp2.y+cy)。
- **case 抽取**：`EDA-Eval-DesignFlow-PGLayout-001`（skipper domain 0→1 扩覆盖，L2 真跑 Skipper）。deliverable=pg_layout.tcl（读 list→dbImport mos+res→dbLibCreate/dbCellCreate 顶层 test_ptn_to_ptn→dbCreateInst MP1(R0)+R1(R0)+MP2(MY)→dbCreateRect 97.0 连接→dbCreateLabel 99.0 VDD 在 MP1 重叠中心/VSS 在 MP2 MY 映射非重叠中心→dbCellExport）。A=mos_a/res_a/list_a/guideline_A/layer_map/task_brief，隐藏 B=mos_b/res_b/list_b/guideline_B。check.py 14 条件 a-n（subprocess 真跑 skipper run+report + 跨输入 guard + 3-run 确定性 + MP1 原点）。ref 14/14 PASS + §4.9 三假（empty/print_expected/ref_core_deleted）FAIL + 2 naive（hardcode_B_coords 经跨输入 guard 败、labels_at_origin 经 (j)(k) 败）FAIL + negative_selftest ALL-OK（均在 .75 实跑验证，skipper 2020.06.sp3，python3 3.7.1）。
- **关键字**：skipper:2564 / tcl:517 / gds:331 / pg_pin:132 / layout:109 / pg_drawing / PG_PCH / AT4_PCH / VDD / VSS / MY mirror / dbCreateInst / dbCreateLabel。
