# pwk03 — GDS placement hierarchy transform 解析（physical_verify）

- session_file: `1794879096266_pwk03.messages.json`
- user: lynn1y · host: hfeg0plg44 (10.129.8.65) · match_count: 371 · domain: physical_verify
- claim: C 台账 r824 (2026-11-19 20:08 claimed → 20:43 case)
- 落库 case: `EDA-Eval-DesignFlow-GdsHierarchyTransformResolver-001` (physical_verify, L2-boundary, 档 B reframe, k_check=17)

## 真实用户意图

用户在把一套 **calibredrv TCL 脚本移植成 Python + gdspy**，目的是把 GDS 版图里子 cell 的**局部坐标**
转换成 **TOP cell (DDR5TOP) 顶层坐标**。算法核心：从顶层出发 **DFS 遍历 placement 层次树**，逐级累加
每个 instance 的仿射变换 `(a, b, c, d, tx, ty)`（2×3 仿射：`X = a*lx + b*ly + tx`，
`Y = c*lx + d*ly + ty`），得到子 cell 相对 TOP 的累计仿射，再对一批目标点输出 TOP 级坐标。

## trace 全貌（306 msgs: 154 user / 152 assistant）

会话是 **TCL→Python 移植的迭代调试**：
1. 环境搭建（Python/gdspy/calibredrv 可用性）。
2. ski-db 启动、用 dbFigItr 递归遍历 GDS placement 层次提取 instance 矩阵。
3. dbFigItr API 调用 bug（遍历顺序 / 矩阵字段提取错误）。
4. 矩阵乘法 compose 方向纠正（parent_accum @ inst_matrix）。
5. DFS visited=38959050 一次「太慢但正确」的运行（确认算法对，只是没剪枝）。

**gold 捕获于 U#7**：输出 10 个目标 cell 的 TOP 级坐标，`replaced=1634 kept=0`（1634 条 file2 记录全部
可达并替换）。

## reframe 决策（档 B）

- A 档 gold = 在 live skipper/Aether + 真 GDS 上跑 calibredrv TCL 实测坐标变换 → 沙箱跑不了
  （无 live session、无真实 GDS、calibredrv/skipper 不可用）→ **无 subprocess 牙**。
- trace 也无单一可验收交付物（是迭代调试过程，非一次性脚本交付）。
- → reframe：抽离「**GDS placement 层次仿射累加**」算法核心成纯 stdlib 解析器
  `gds_transform_resolver.py`，输入用 JSON 描述的层次树 + file2 待变换点列表，BFS 合成仿射矩阵，
  输出 file3（TOP 级坐标）+ report JSON。CLI 4-arg，确定性输出。

## visible A vs hidden B

| | A (visible) | B (hidden) |
|---|---|---|
| topcell | DDR5TOP | TOPLV |
| 直接子 cell | Array2G_Top / Array2G_Bot / Periph | AnaTop / DigTop / BiasCol |
| 目标 cell | SWD_PMOS_BIT_*/SWD_NMOS_*/lwdrx*/BufLeaf (9) | cmp_amp/vref_gen/bias_mirror/latch_set/latch_reset/dff_buf/cur_sink (7) |
| instance 数 | 12 | 10 |
| file2 记录 | 11 | 12 |
| 镜像 instance | a=-1,d=-1 (SWD_NMOS) | a=-1,d=1 (BiasCol 水平镜像) + a=-1,d=-1 (bias_mirror 中心对称) |
| 预期 | visited=12 tf_chosen=9 replaced=11 kept=0 | visited=10 tf_chosen=7 replaced=12 kept=0 |

B 显式 exercise 了 A 没有的 **a=-1,d=1 水平镜像**（BiasCol → cur_sink）和 **a=-1,d=-1 中心对称**
（AnaTop → bias_mirror），强化非单位阵仿射合成的覆盖。

## 17 条断言 (a-q)

check.py 内置**独立 oracle**（自己重算 BFS + mat_mul，不 import 参考 resolver），expected 值全部从
B 结构内联推算（非参考 resolver 输出硬编）。覆盖：zip/compile/4-arg 契约/subprocess 真跑 B/
stdout 标记/topcell 反 A/visited/tf_chosen/replaced+kept/file3 行数/cmp_amp 仿射累加/bias_mirror
中心对称/cur_sink 水平镜像逐级合成/target_cells 名集/反 A 专属字面/确定性/3-seed 随机子集。

## 自验

- ref PASS 17/17 (a-q)；交叉输入 A 跑通 (DDR5TOP visited=12 tf_chosen=9 replaced=11 kept=0)。
- 4 negative 全 FAIL distinct（neg_print_only→c/d、neg_no_traverse→g/k/l/m、neg_hardcode_a→f/o、
  neg_core_deleted→h/i）；§4.9 (a)空壳(b)只打印(c)删核心 三假全 FAIL；negative_selftest ALL GOOD exit0。
- jsonl test==disk roundtrip ✓；k_rationale=k_check=17 ✓。

## 选料备注

r822 note 「高 mc 池耗竭」实证：mc≥10 fresh 扫描（4-shard ledger 排除后）仅 11 个 C-domain 候选，
pwk03 (mc=371) 排名 #1。下一批 fresh 候选若耗尽须扫 mc≥200 段或 revival NFS-stale parked。
