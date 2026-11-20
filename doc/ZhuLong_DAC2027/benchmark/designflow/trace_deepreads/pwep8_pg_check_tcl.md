# pwep8 深读 — jianhaiq / hfeg0plg88 / mc517 — schematic_netlist

session: `1792563683776_pwep8.messages.json` (1.93MB / 494 msgs / 277 user)
路径: `/home/jianhaiq/.cline/data/sessions/1792563683776_pwep8/1792563683776_pwep8.messages.json`
scp 拿到完整 trace；磁盘 `/home/jianhaiq/PG_check.tcl`（126 行 / 5713B）最终态亦 ssh cat 读取。

## 任务演化（4 个用户需求轮）
- **U#0**：初版 — 写 py 脚本 `PG_check.py`，用法 `PG_check.py list`；list 两行三列 `mos: <cdl> <gds>` / `res: <cdl> <gds>`；抓 mos 行第三列、res 行第三列；用两个文件生成 `test_ptn_to_ptn.gds`。agent 用 pyAether 写了 PG_check.py（dbImport/dbCreateInst/...）。
- **U#164**：报错 `ModuleNotFoundError: No module named 'pyAether'`（用户指出根因 → **不作 A 档任务说明**）。agent 大量 RAG/list_allowed_files 找 aether 环境，最终改写脚本加友好错误提示，建议在 aether -batch -python 中运行。
- **U#220**：重提需求（py 版）+ 5 点细化：①两次 mos 的放置与排放 ②中间 res 放置 ③连接 layer ④PG_pin label 位置 ⑤**用 skipper 不用 aether**。agent 转向 skipper Tcl，大量读 `/apps/empyrean/skipper/.../doc/manual/html/db.html`（dbImport/dbCreateFig/dbCellExport/dbCellCreate/dbCellGetBBox/dbCellGetLayerBBox），写 PG_check.py 生成 Tcl。
- **U#441（A 档任务说明，逐字采用）**：最终版 — 写 **tcl 脚本 `PG_check.tcl`**；5 点最终态：①两次 mos ②res 中间 ③**PG_drawing layer 连接** ④**PG_pin layer label：左 mos 上 PG_PCH∩AT4_PCH 重叠区、右 mos 上不重叠区** ⑤**skipper 不用 aether**。agent 写出最终 `/home/jianhaiq/PG_check.tcl`（126 行）。

## 金标准（磁盘最终态 PG_check.tcl 126 行）
- 全局变量：OUT_GDS / PG_DRW="PG_drawing" / PG_PIN="PG_pin" / PG_PCH / AT4_PCH / SP=0.5 / CW=0.2 / BM=0.2 / LH=0.2 / M1=MP1 M2=MP2 R1=R1 / TOP=test_ptn_to_ptn
- `parse` proc：正则 `(\w+)\s*:\s*(.+)$` 抓 mos/res 行，`regexp -all -inline {\S+}` 取第 2 个 token（即第三列 GDS 路径）。
- `gen` proc 8 步：
  1. dbImport mos GDS → dbLibGetId / dbLibGetAllCells → mC
  2. dbImport res GDS → rC
  3. dbCellGetBBox 算 mW/mH/rW
  4. dbCellGetLayerBBox 取 PG_PCH(pB)/AT4_PCH(aB)；算重叠 oL/oB/oR/oT；hasOv → l1=(overlap 中心), l2x=(oR+aB.x1)/2 若<=oR 则 (aB.x0+oL)/2, l2y=(aB.y1+aB.y3)/2；无重叠用默认 mW*0.25/0.75
  5. dbCellCreate TOP
  6. dbCreateFig 摆 MP1 (0,0) R0 / R1 (rx=mW+SP,0) R0 / MP2 (m2x=rx+rW+SP,0) **MY**
  7. dbCreateFig -rect PG_drawing 连接 (mW,cy)-(rx,cy2) 与 (c2l,cy)-(m2x,cy2)，cy=mH*0.4 cy2=cy+CW
     dbCreateFig -label PG_pin：VDD at (l1x,l1y) [左重叠区]；VSS at (l2xx=m2x+mW-l2x, l2y) [右非重叠区，MY 镜像变换]
  8. dbCellExport -fileName OUT_GDS
- `main`：argv 取 list 文件 → parse → gen。

## 降级（L1-boundary）
真实 skipper 不可在评测沙箱执行 → 改为确定性 Python 生成器 `gen_pg_check.py` 读 config.json（mos/res bbox、layer 名、路径、spacing、labels）→ 产出**已实例化坐标**的 PG_check.tcl + layout_manifest.json（携带 overlap/label/placement 几何，供无 skipper 的判分器校验）。生成器逻辑忠实复刻 gold 的 overlap/placement/label-mirror 计算。

## 资产
- A: config_A.json（mos 1.0×0.6, pch [0.1,0.3,0.9,0.6], at4 [0,0,0.4,0.4], overlap [0.1,0.3,0.4,0.4]；res 0.5×0.2；OUT=/home/pdk/.../test_ptn_to_ptn.gds；labels VDD/VSS）+ list_A.txt + prompt.txt(U#441 逐字) + task_brief.md
- hidden B: config_B.json（mos 1.2×0.8, pch [0.2,0.4,1.0,0.8], at4 [0,0,0.5,0.5], overlap [0.2,0.4,0.5,0.5]；res 0.6×0.3；OUT=/proj/pdk/b07_PG_split/out/ntn_to_ntn.gds；mos/res GDS 路径不同）+ list_B.txt + hidden_manifest.json
- reference: gen_pg_check.py（ref）+ check.py（15 条件 a-o）+ negative/（4 假：empty/print_fixed_A/core_deleted/naive_no_mirror）+ negative_selftest.py

## 自验
- ref 跑 A、B 各出 PG_check.tcl + manifest；B manifest overlap [0.2,0.4,0.5,0.5]、MP2 (2.8,0) MY、labels 左 (0.35,0.45) overlap / 右 (3.9,0.25) non_overlap —— 与手算一致。
- check.py 对 ref submit.zip **PASS 15/15**。
- 4 negatives ALL-FAIL（empty/print_fixed_A/core_deleted/naive_no_mirror）distinct。
- §4.9 三假（empty/print_fixed_A/core_deleted）全 FAIL ✓。
- test==disk EXACT（sha 9eee2f79e30c）。
- k_rationale==k_check==15 ✓。
- D.jsonl 75→76 行。
