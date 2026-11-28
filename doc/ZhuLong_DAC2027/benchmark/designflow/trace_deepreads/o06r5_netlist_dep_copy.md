# o06r5 — ALPS SPICE 网表依赖收集 + symbol/schematic 拷贝规划深读

- **trace**: `1795525118226_o06r5.messages.json` (hairuizh @ hfeg0pkn001)
- **mc**: 218 (schematic_netlist 主导: netlist+cmos+schematic)
- **域**: schematic_netlist (ALPS/FineSim SPICE 网表依赖解析)
- **claim**: 2026-11-28 入 D 台账 domain=schematic_netlist
- **case**: `EDA-Eval-DesignFlow-NetlistDepCopyProduce-001` [L0,L1] 落库

## 用户真实意图

hairuizh 在 ALPS/FineSim SPICE 仿真上下文要「parse 一个 schematic 导出的
SPICE 网表 → 收集所有 transitively-instantiated subckts + USED MOS 模型 →
规划把它们的 symbol/schematic view 从中央 lib_tree 拷贝到本地
`local_symbol/<lib>/<cell>/<view>/`，保留 lib/cell/view 目录结构」。

目的是为 standalone 本地仿真准备自包含的 `local_symbol/` 目录——只含网表
真正用到的 cell，不含 lib_tree 里定义但网表没用的 spare/leftover。

## 网表解析语义

- `*.LIBMAP <cell> <lib>` directive：cell→lib 映射
- `.SUBCKT <name> ... .ENDS`：子电路定义 body
- `X<inst> <nodes...> <subckt_name>`：subckt 例化（最后 token 是子电路名）
- `M<inst> <d> <g> <s> <b> <model> [params...]`：MOS 例化（第 6 token 是 model）
- transitive closure：从 `top_cell` 出发 BFS `X..` 例化边，只收 reachable 的
  defined subckt

## 真实用户捕获的 2 个 pin（编码为断言）

1. **只拷贝网表 instantiate 的 MOS（非全 TECHLIB MOS）**。用户原话「你只
   需要看网表用了哪些 mos」—— lib_tree 的 TECHLIB 里还有 `markvddhv` /
   `unusedmos` 等定义，但网表没有 `M..` 引用它们，不能拷。→ check.py
   cond e（mos_used==gold）/ cond f（mos_used subset of instantiated，
   反 over-copy）
2. **只拷贝 transitively-used subckt（defined-but-unused 排除）**。网表里有
   `unused_buf` 的 `.SUBCKT` 定义但没有任何 `X..` 引用它（spare/leftover），
   不能拷。→ cond d（used_subckts==gold transitive）/ cond l（excludes
   defined-but-unused）

## 拷贝规划规则

- `lib_filter`（null 或子库列表）仅约束 **subckt** 拷贝；**MOS** 一律从
  `mos_lib` 取，不受 `lib_filter` 影响
- 缺 view 的 cell（如 `preamp_buf` 只有 schematic 没有被请求的 symbol）→
  skipped，记 `{"reason":"view not present"}`，不崩溃
- 目录结构严格 `target/<lib>/<cell>/<view>/<file>`
- report.json 含 used_subckts / mos_used / copied_cells / by_lib / skipped /
  copy_plan / total_files

## reframe

把「真实打开 OpenAccess 库跑拷贝」（强依赖 oa DB / Virtuoso）reframe 为
spec-JSON 驱动纯 Python 收集器 + 拷贝规划器
`collect_netlist_deps.py(spec)->{report.json, copy_plan.json}`：

- spec 给 `{top_cell, netlist, lib_tree, views, lib_filter, include_mos,
  mos_views, mos_lib, target_root}`
- 网表解析语义 reframe 为 spec 静态字段 + report.json 结构化判分
- 无真实 EDA 工具二进制依赖（oa/hspice 不在 eval 沙盒）
- LIVE-NA，judge_layers=[L0,L1]

## case 落库

- **A**(visible) spec_A.json: top=`lwdrq_msaq`，三库 drvqa_cmos_core /
  drvqa_cmos_stdcells / TECHLIB，8 个 `.SUBCKT` 定义（`unused_buf`
  defined-but-unused），MOS=nch/pch，lib_filter=null，preamp_buf 缺 symbol →
  skipped
- **hidden B**(token-structurally 不相交) spec_B.json: top=`io_top`，四库
  io_lib/analog_lib/digital_lib/TECHLIB_B，MOS=nio/pio，
  lib_filter=[io_lib,analog_lib]（digital_lib 被过滤 → gate_d/invd 排除），
  defined-but-unused=spare_a/spare_d
- check.py 18 conds a-r（独立 regex GT 复算 + anti-hardcode tokenize 扫描），
  6 neg distinct first-fails {c,d,g,n,d,e}，§4.9 trio distinct {c,d,g}，
  ref PASS 18/18，test sha 386c8882 3-way sync

## 关键 bug 修复（上线前捕获）

check.py 首版 specA_path 用相对路径（`./spec_A.json`，因 workdir="." 且
`./spec_A.json` 存在），但 candidate 跑在 tmp cwd（unzip dir）→
`FileNotFoundError`。negative_selftest 因 workdir=CASES_ROOT（绝对路径）未
暴露此 bug。修为 `os.path.abspath(specA_path/specB_path)` 后 REF PASS
端到端（run_one.sh 真 judge 路径 verdict=PASS）。**教训**：negative_selftest
的 workdir 须与真 runner 一致（"."），否则相对路径 bug 潜伏到上线。

## parked 候选

- `k5x28`（beartang）：wrong-domain C（layout wire+via on metal layers，
  opening intent 是 layout 非 schematic）
