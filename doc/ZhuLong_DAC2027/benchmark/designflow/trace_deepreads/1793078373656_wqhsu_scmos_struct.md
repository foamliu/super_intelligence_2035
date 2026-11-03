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
