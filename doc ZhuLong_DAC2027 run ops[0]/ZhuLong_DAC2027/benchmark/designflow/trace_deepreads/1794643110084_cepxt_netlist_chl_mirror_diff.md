# trace_deepread: 1794643110084_cepxt — netlist L/R-mirror diff (kevin3d)

- **user/host**: kevin3d @ hfeg0pkn002 (10.129.2.11)
- **session**: `1794643110084_cepxt.messages.json` (682KB, 141 msgs, 72 user / 69 assistant, mc=161)
- **trace_source keywords**: netlist:633; lvs:303; schematic:67; analog:58; .cdl:40; hspice:22; calibre:16; aether:11

## 用户真实意图（原话）
> 「/rundata/totem/dscqa/CPM/20261110/IDD7RD_11600_TT1.025v70c/DDR6TOP.netlist 和 finesim/idd7rdap_aabbpatternx2p3-11600.23.TT1.025v70c.current/netlist 这两个 netlist 有什么实质区别，diff 出来差异很大」

两份 100MB+ HSPICE 网表：A=`DDR6TOP.netlist`（103MB/425228 行，11/14 kevin3d 新版），B=`finesim/.../netlist`（127MB，10/13 旧版）。用户已注意到 `diff` 输出差异巨大，要的是**实质区别**（不是逐行 diff）。

## assistant 工具链（63 tool_use）
1. `list_allowed_files` 列两份网表所在目录
2. `read_files` 直接读 → 两份都 >100MB 超限被拒
3. `editor` 写 `compare_netlists.py`（结构化分析：subckt 定义、实例计数、head/tail）→ `run_approved_command` 跑
4. `compare_netlists2/3/4.py`：深比对 + B 的 `inh_*` 网名规范化回 `*!` 形态
5. `extract_vwln*.py`：抽 `AG_VwlnActAmpCh` L/R 子电路体
6. `diff_pairs.py`：L/R 对逐行严格 diff
7. `patch_chl.py` / `patch_chl_min.py` / `validate_chl.py`：建 ChL 插入块、打补丁、校验
8. `check_patched.py` / `diff_bak_cur.py`：补丁后健康检查 + bak vs cur 完整 diff
9. `check_lvs*.py` / `walk_ixf*.py`：LVS `.sp`/`.ixf`/`.cdl` 层级命名交叉验证
10. `check_all_lvs.py`：扫所有 LVS 版本（0826→1109），定位 ChL 命名从 20261105 那套开始出现
11. `check_cdl.py`：`.cdl`（schematic 源网表）命名核实

## 实质差异（结论）
**B（finesim 10/13 旧版）还没做 L/R 通道拆分**；A（11/14 新版）已把 `AG_VwlnActAmp` 拆成 L/R 镜像对：

| 子块 | 左通道 (ChL) | 右通道 (Ch) |
|---|---|---|
| 核心放大器 | `AG_VwlnActAmp` | `AG_VwlnActAmp` |
| 共模子块 | `AG_VwlnampComCL` | `AG_VwlnampComCR` |
| ESR 电容 | `AG_EsrCapvwlnChL` | `AG_EsrCapvwlnCh` |

B 的具体缺陷：
- **缺 `AG_VwlnActAmpChL` 子电路定义**（只有旧的统一 `AG_VwlnActAmpCh`）
- **`AG_PumpCoreChL` 仍实例化 `AG_VwlnActAmpCh`**（左右都挂 Ch，未拆）

LVS 三方交叉验证（11/09 那套 `.cdl`/`.sp`/`.ixf`）：已经是 ChL 新命名 → schematic 拆分在 11/05 前完成。ChL 命名从 20261105 LVS 版本开始出现（≤10/17 的 LVS 都还是旧命名）。

## 交付物（真实 trace）
- 最小补丁：补 `AG_VwlnActAmpChL` 定义（复用 B 已有的 `AG_EsrCapvwlnCh`）+ 把 `AG_PumpCoreChL` 实例改指 ChL
- 完整版补丁（`chl_add.sp`，含 `AG_EsrCapvwlnChL` 定义）用于 LVS↔仿真逐层名字严格对齐
- bak：`netlist.bak.20261114`

## 合成为 case（EDA-Eval-DesignFlow-NetlistChlMirrorDiff-001）
- 用自包含小型 HSPICE 网表（LEVEL=1 MOS）保留真实子电路命名与 L/R 拆分结构
- A 档 prompt trace-faithful（用 kevin3d 原话）；netlist B/B' 档 synthesized（原 100MB+ 含晶圆设计不可沙盒外访问）
- 任务：结构化比对 A vs B → report.json + 对 B 打最小补丁 → netlist_B_patched.sp
- 隐藏 B'：结构同构、实例名/器件尺寸/电容值/全局网名全不同（vdda!/gnd! vs vcc!/vss!，`XI_AG_VwlnActAmpCh_7` vs `_1`），仍是「缺 ChL + PumpCoreChL 错挂 Ch」同种缺陷
- 判分：12 条断言（a-l），含 cross-input guard（l）防「硬编码 A 字面值」
- 自验：ref 12/12 PASS；2 negs（naive_diff / always_add）全 FAIL；§4.9 empty-shell + print-only-expected 全 FAIL
