# Deep-read: pt63j (jinsongl @ hfeg0pkn005, mc=48)

- **session_file**: `1792216997704_pt63j.messages.json` (98 KB, 48 msgs)
- **domain**: schematic_netlist
- **user/host**: jinsongl / hfeg0pkn005 (10.129.2.14)
- **A-faithful轮**: U#0 (纯提需求，未给根因/修复)

## U#0 (逐字)
> 请帮我写一个perl脚本，脚本的目的是读取网表，并且获取指定前缀的cell 和library和对应的pin抓出来（pin不需要去抓取以inh_开头的pin），要求前缀通过option给进去，下面我会给你一个例子，说明输入和输出  此时给定的前缀是scmos（大小写不敏感）
> 输入：* Library : decqa_digital / * Cell : SCmosEnBufP1060N530 / .subckt scmosenbufp1060n530 scmosen vnen vpenn inh_vbn inh_vbp inh_vcc inh_vss ... .ends
> 输出：library cell port / decqa_digital SCmosEnBufP1060N530 scmosen vnen vpenn / decqa_digital SCmosEnFtBufN1000 floatfooter scmosen vnen

## trace 演化
1. U#0 → agent 写 `extract_cells.pl` (Getopt::Long `-prefix`/`-file`/`-out`，逐行解析 `* Library :`/`* Cell :` 头 + `.subckt <name> <ports>`，按 `.subckt` 名大小写不敏感前缀匹配，输出 `library\tcell\tport...` 排除 `inh_` 前缀 pin，缺 `-prefix` 报错，`.ends` 清 cell 上下文防泄漏)。
2. U#17: 以样例 netlist 前缀 `scmos` 验证 → 2 cell (SCmosEnBufP1060N530 / SCmosEnFtBufN1000)，ports `scmosen vnen vpenn` / `floatfooter scmosen vnen`（inh_vbn/vbp/vcc/vss 排除）。exit 255 来自缺 `-prefix` 的预期报错。
3. U#19 "以现在的netlist为例，前缀为buf" → 真实 `/home/jinsongl/netlist` 前缀 `buf` → **93 cell / 4 library** (stdcells_ac, drcpa_stdcells, drcpa_digital, drcpa_array)，ports `a y` (buf*) / `d lat latn pdn pupn y` (bufen_*)。注意 `buf` 前缀也匹配 `bufen_*`（前缀语义，agent 确认符合预期）。
4. U#35 "结果需要输入到文件" → agent 给 `extract_cells.pl` 加 `-out PATH` 选项（写文件，默认 stdout 兼容）。
5. U#46: 验证 `-out` → 93 行写入 `buf_cells.txt`，exit 0。

## 金标 (extract_cells_ref.pl)
忠实复刻 trace 逻辑：`-prefix`/`-file`/`-out` (Getopt::Long)，缺 `-prefix` die，逐行匹配 `* Library :`/`* Cell :` 头，`.subckt <name> <ports>` 按 `lc(name)` 前缀 `lc(prefix)` 匹配，输出 cell 优先取 `* Cell :` 头值(保留大小写)否则回退 subckt 名，ports 排除 `^inh_` (大小写不敏感)，`.ends` 后清 cell。

## 资产可达性
真实 `/home/jinsongl/netlist` 与 `/home/jinsongl/extract_cells.pl` 已被用户清理（.75 ssh → No such file or directory）。故取 **B-grade synthesized 资产**：合成 cadence netlist（保留真实结构：`* Library/Cell/View/Inherited view list` 头 + `*****` 分隔 + `.subckt/.ends` 块 + inh_ pin + 不匹配 cell）。

## 选定 case
**EDA-Eval-DesignFlow-CellPrefixExtract-001** (schematic_netlist, A-faithful, L1, 16 asserts)
- A = netlist_A.sp (4 library: decqa_digital/stdcells_ac/drcpa_digital/drcpa_array；scmos 2 cell + buf 4 + bufen 2 + 不匹配 nand/inv)
- hidden B = netlist_B.sp (3 library: drcqa_io/stdcells_xy/dffqa_core；6 个 dff cell 含混合大小写 INH_VDD/INH_VSS/inh_rst/INH_vcc/INH_clk + 不匹配 buf/nand/scmos)
- 跨输入护栏: A 副本 + 前缀 buf (8 cell) ≠ B 前缀 dff (6 cell) 击败硬编码
- check.py 16 条件 a-p；7 negative 全 FAIL (distinct b,c,d,g,m)
