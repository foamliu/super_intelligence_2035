# Deepread: 1793078373656_wqhsu (xiwang / hfeg0pkn003, mc=289)

- session: 1793078373656_wqhsu.messages.json (249 msgs)
- user: xiwang ; host: hfeg0pkn003
- domain: schematic_netlist (电路结构判别 / hierarchical instance closure)
- keywords: cmos:7974 aether:297 schematic:290 netlist:182 pyaether:137 .cdl:82 analog:52
- 真实文件 `/proj/ddgoa/V0/libs/...` e0031982 **可读**（list_allowed_files confirmed；但 find 全库超时 SIGKILL）。
- 该 user 同 host 已交付 l0qrf=DevUsageExtract-001（不同 session、不同任务：器件盘点 vs SCMOS 结构闭包）。

## A 档任务说明（user 原话逐字，提出需求轮）

**msg[0]（首轮，提出需求）**:
> DDGOA电路中，SCmosDataDPCtrlNew_DDGOA_add和SCmosConTopVdd2h这两个cell就是常见的SCMOS电路，帮忙找出来DDGOA V0中所有的SCMOS电路

**msg[59]（第二轮，仍是目标澄清，非根因/非修复方案）**:
> 不仅仅是从cell名字上匹配关键词，也需要对比电路本身的结构

> 选轮规则核验：msg[0] 提需求、msg[59] 澄清目标（"也要对比结构"）——均非"已指出根因/已给修复"。后续 msg[99]"把这些cell导出成文件crossprobe"、msg[~150]"对比DDGOA vs DDCPC 尺寸"是后续独立需求，不进本轮 A 档任务说明。

## 真实工具链与事实（agent 工具结果）

1. **名匹配种子**：全库 cell 名含 `scmos`（大小写不敏感）= **1401** 个唯一 cell，跨 10 个库；主库 `ddgoa_cmos_digital` 795 个。
2. **基准 cell 结构**（msg[87] scmos_subcells.py 结果）：
   - `SCmosDataDPCtrlNew_DDGOA_add` → 直接实例化 `SCmosDataDPCtrl`, `SCmosDataPad`（均 SCmos 前缀子块）
   - `SCmosConTopVdd2h` → 直接实例化 `SCmosConTopVdd2hBuf`, `SCmosConVdd2h`
   - 即 SCMOS = **层级化电路族**，结构特征 = 在 instance 引用链上实例化 SCmos* 子块（不是用 ntn/ptn/vcc/vss 这些全库通用裸器件）。
3. **结构判别法**（msg[88-95] scmos_hierarchy.py + scmos_final_report.py）：
   - 从每个 cell 的 `sch.oa` 提取实际引用的 master/sub-cell 名 → 建 `cell → child` 实例图
   - seeds = 名含 `scmos` 的 1401 cell
   - **递归层级闭包**：seeds ∪ {沿引用链向父辈传递性包含 seed 的 cell}
4. **终局结果**（msg[95], msg[98] 用户接受）：
   | 类别 | 数量 |
   |---|---|
   | 名含 scmos 的 cell（seeds） | 1401 |
   | 结构上引用 SCMOS 子块但名字不含 scmos（纯结构判别增量） | **490** |
   | └ 直接实例化 SCMOS 子块 | 342 |
   | └ 传递性祖先（更深一层才碰到 SCMOS 块） | 148 |
   | **结构闭包总数** | **1891** |
   - 代表性 structural-only：`BGCasShare`(→SCmosBGCasShare), `BufLeft/BufRight`(→DPBufMidSCmos/SCmosDataBufMid/SCmosColBufMid), `CACWrGen_DDGOA`(→SCmosEnVdleq), `BistOsc`(→SCmosmBistOscPVT), `BkShareEccLogic_DDGOA`(→SCmosCas_PN1p76/SCmosEccLogic/SCmosEnBKShare), `CCRAryBuffer`(→CCRSCMOS_unit_buffer_*)。
5. **crossprobe 导出**（msg[99-112]，后续独立需求，不进 A 档）：crossprobe-ready（schematic+layout 双视图齐备）870 个。

## 失败/超时路径（agent 走过）
- token 级签名（数 ntn/ptn/vcc/vss 出现）→ 被通用器件主导，普通反相器 BTI_inv/PM_inv 也高分 → **判别力不足**（msg[84]）。→ 必须沿层级引用链做闭包。
- `find` 全库 netlist grep 超时 SIGKILL；struct_scan.py 一次扫 795 OA 超时 → 改 struct_scan2.py 逐文件增量（msg[80-83]）。

## 合成策略（A 档 trace-faithful）
- 真实 sch.oa 为 OpenAccess 二进制，无法合成；改用 **CDL/Verilog .SUBCKT 网表**（文本可验、与 domain 一致）表征 cell→child 引用图。
- A 资产 = 一批 .cdl 文件，每个 `.SUBCKT` 一个 cell，`X` 实例 = 子 cell 引用；保留真实命名族（SCmos* / BufLeft / BGCasShare / CACWrGen_DDGOA / BistOsc / BkShareEccLogic_DDGOA 等）与真实结构特征（基准 cell 实例化 SCmos* 子块；structural-only 直接/传递分层）。
- **降采样**：真实 1891 cell → A ~26 cell（10 seeds + 5 struct-direct + 3 struct-transitive + 8 non-scmos），结构性质（名匹配 seeds / 层级闭包 / direct vs transitive / non-scmos 排除）全保留。
- hidden B = 不同 cell 名 / 不同计数 / 不同图结构 / 不同基准 cell，杀硬编码。
- 交付 = 通用 `find_scmos.py <library_dir> <out_json>`，seeds = 名匹配 /scmos/i，闭包 = 传递性祖先；check 跑 B 验 B 计数。

## 合成交付决策（r107 落地）

- **档位**：B-档 synthesized L1-boundary（离线 fixture 库树探索器，stdlib-only，确定性）。
  - A-档 faithful 不可行：真实 gold 依赖 live `sch.oa`（OpenAccess 二进制，在 /proj/ddgoa/V0 内网）+ live pyAether 沙盒（trace 中沙盒连接被拒 10.129.8.235:50640），无法打包进交付件 → 解禁为 B-档。
- **fixture 表征**：每个 cell = 一个子目录，内含 `schematic.cdl`（简化 CDL：`.SUBCKT`/`X` 子 cell 引用/`M` 器件/`.ENDS`，含注释与续行）+ 可选 `views` 文件（每行一个视图名）。X 的 master=子 cell（图边），M 的 model=器件（ntn/ptn/ntn_m/vcc/vss/vbn/vbp/vdd2h/inv，非 cell、不延展闭包）——这正是判别力来源。
- **gold 算法** `scmos_struct_id.py`：解析 cdl → 提取子 cell/器件 → name 种子(scmos 大小写不敏感) → 建 cell→child 图(仅库内 cell) → 传递性闭包 → 按优先级分类 name_seed > structural_direct(直接引用种子) > structural_transitive(深度≥2 才碰到种子) > non_scmos；crossprobe_ready = SCMOS 族 ∩ {schematic+layout 双视图}。
- **资产 A**（忠实，27 cell）：保留真实命名族与结构——2 个基准 cell(SCmosDataDPCtrlNew_DDGOA_add→SCmosDataDPCtrl+SCmosDataPad；SCmosConTopVdd2h→SCmosConTopVdd2hBuf+SCmosConVdd2h)、12 name 种子(含 SCmosCaUnit 仅 schematic 视图、SCmosLeafInv 仅器件的命名叶)、5 structural-direct(AbusChanMidPrc/Act42Nn3NBa/BufLeft/BGCasShare/CACWrGen_DDGOA)、3 structural-transitive(BistOsc/BkShareEccLogic_DDGOA/SysWrapper)、4 器件-only 普通反相器(BTI_inv/PM_inv/NandA/InvBuf，判别力 guard)、3 引用非 scmos 子 cell 的 non_scmos(DigiBlock/AddrDec/ClkTree)。
- **hidden B**（不同命名/计数/图，25 cell）：SCmosCoreTop_DDGOA_add/SCmosClkTopVdd2h 基准、11 种子(SCmosBiasRef 仅 schematic)、5 direct(DataPathA/CtrlBlkB/ClkGater/PwrMgmt/LatchWrapper)、3 trans(SysTop/ChipCtrl/GlobalClk)、4 器件-only(InvA/InvB/NorA/MuxA)、2 非 scmos 子 cell(LogicBlock/PreDec)。A↔B 计数(27/25、12/11 种子、19/18 crossprobe)不同 → 杀硬编码。
- **check.py 16 条断言 a-p**(k=16)：a zip+py_compile / b CLI B exit0+JSON+13 必需键 / c cells_total / d name_seed / e structural_direct(击穿 name-only) / f structural_transitive(击穿 depth-1-only) / g 器件-only 非命名 cell 必为 non_scmos(击穿 flat-token，trace 核心判别力) / h SysTop 必为 transitive 非 direct(深度正确) / i graph children 排除器件 / j 命名种子保持命名 + non_scmos 闭包无种子 / k 命名优先于 direct(SCmosClkDivider) / l 确定性 3×md5 / m A↔B 交叉 guard + 忠实基准 cell 在 A 的 name_seed / n non_scmos_count / o crossprobe_ready + 仅 schematic 种子排除 / p 命名叶(仅器件)仍为 name_seed。
- 自验：ref PASS 16/16 + 3 negative(naive_name_only/flat_token/crippled_no_transitive)全 FAIL + §4.9 三假(empty_shell/print_expected 硬编码 B/core_deleted)全 FAIL ✓。
