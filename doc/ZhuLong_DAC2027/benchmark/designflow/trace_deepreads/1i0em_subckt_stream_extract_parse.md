# 1i0em — DRAM 115MB SPICE 网表流式 .SUBCKT 提取 + 一层解析（rongtaoy / hfeg0pkn001 / 574 mc）

**trace**: `1791526272387_1i0em.messages.json` · user `rongtaoy` · host `hfeg0pkn001` (10.129.2.10) · match_count 574 · 1.96MB / 380 msgs (205 user / 175 assistant) · 141 tool_use (editor 74 / run_approved_command 42 / read_files 38 / list_allowed_files 24 / search_codebase 2 / skills 3)。
**domain**: schematic_netlist（SPICE 网表解析，L1 离线 Python）。

## 真实任务（cimi Instruction 002 + 用户复用迭代）

rongtaoy 在 hfeg0pkn001 上分析一张 emy2netlist 导出的 DRAM hspice/ALPS 大网表 `Netlist_Vcap_20261008PM/netlist_org`（~115MB）。cimi 下发 Instruction 002：从大网表流式提取 `SpineTop` 的完整 `.SUBCKT` 定义段，解析实例层级与端口连接，确认 `ECC_LbusDrv / BankTopX2 / SpineRpt` 的实例及端口连接。三步复用流程（按目标 cell 名参数化）：
1. `_step1_locate_cell.py <cell>` —— `grep -n "^\.SUBCKT <cell>\|^\.ENDS <cell>"` 拿起止行号；
2. `_step2_extract_cell.py <cell> <start_line>` —— 流式（`open(buffering=8192*1024)` + `for line`，不 read 整文件）把 `.SUBCKT ... .ENDS` 段抽到独立文件，**depth-aware**（遇 `.SUBCKT` depth+1、遇 `.ENDS` depth-1，depth=0 止）；
3. `_step3_parse_cell.py <cell>` —— 解析端口（`.SUBCKT <cell>` 后的 token）、X 实例（`X<inst> ... <cellname>`，inst=parts[0]、cell=parts[-1]、pins=parts[1:-1]）、按 cell 分组。

用户后续要求：①脚本统一归 `scripts/`、产物归 `data/`、给 cimi 的报告归档；②脚本做成**按目标 cell 切换的复用版本**（只改参数不改编码）；③逐个 cell 跑（Array16GTop → I_Array8G_E → Array1GBK3 → m1G_TOP_E → m512Meg_U → CXSA1x2_EdgeDUM）。

## ⚠️ 关键踩坑（核心 discriminator）

用户明确抓到 bug：
> "parser 把最后一个 token 误认成 cell 名了（因为跨了 `+` 续行）"

即 naive parser **逐物理行**解析、不拼接 SPICE `+` 续行 → 一个跨 `+` 多行的 X 实例化卡片，第一行的最后一个 net 被当成 cell 名（cell 名实为拼接后整张卡片的最后一个 token，在 `+` 行末尾）。`.SUBCKT` 头的端口列表同样可能跨 `+` 行，逐行解析会丢端口。修复 = 先把 `+` 续行拼回上一行再解析。

## 合成映射 → EDA-Eval-DesignFlow-SubcktExtract-001

- **deliverable**：`extract_subckt.py`（纯标准库、ASCII、流式逐行、depth-aware `.ENDS`、`+` 续行拼接、按 `--cell` 泛化、CLI `--netlist/--cell/--out/[--extract]`、JSON 报告 subckt/found/ports/subcells[{inst,cell,pins}]/subcell_types/nets/line_range/line_count）。
- **assets A**：`netlist_A.sp`（按 Netlist_Vcap 结构裁剪：SpineTop_A + 子 cell ECC_LbusDrv_A/BankTopX2_A/SpineRpt_A/invLx4/nand2Lx2 + 基本器件 M/C/R + 注释头；端口跨 `+`、X 卡 xRP0/xRP1 跨 `+`）+ `task_brief.md`。
- **hidden B**：`netlist_B.sp`（结构全不同：DqsTop_B/WrTop_B/RdTop_B；13/5/4 端口 vs A 16；子 cell PreDrv_B/TermB_B/InvBx4/NandBx2；xTERM1 跨 **3** 行 `+`、头跨 2 行 `+`；RdTop_B 纯基本器件体→0 子 cell）。
- **check.py**：14 条件 a-n，独立 ground-truth 解析器（不复用 reference），subprocess 真跑候选于 B：(a)zip+2 件 (b)py_compile (c)B 退出 0+合法 JSON found (d)必需键 (e)subckt 名 (f)ports 匹配 B 真实(13 跨 `+`，硬编 A 16 败) (g)subcell_types 匹配 B(非 A) (h)`+` 核心：xTERM1 1 实例 cell=TermB_B 9 引脚 (i)xTERM0 1 实例 5 引脚 (j)基本器件排除(Mtgate/Rterm/Cdec/Lbond 不入) (k)nets 匹配 (l)跨输入 guard 跑 A 得 A 真实 16 端口/4 types≠B (m)随机化 3 次确定性+3 种子子集+多目标(WrTop_B/RdTop_B) (n)line_range/count+--extract 块以 .SUBCKT 起 .ENDS 止。
- **negatives**：empty_shell / print_expected / ref_core_deleted(`+` 拼接删除) / naive_no_join_hardcode_A / naive_primitives_as_cells —— 全 FAIL。
- **自验**：ref 14/14 PASS（本地）；§4.9 (a)(b)(c) 三假全 FAIL；2 naive 全 FAIL；negative_selftest ALL-OK。
- **L 级**：**L1**（离线 Python 网表解析，无 EDA 工具真跑；trace 中 agent 全程 python-runner + editor，无 hspice/finesim 二进制调用，"hspice" 关键词来自网表路径而非真跑 hspice）。

## 选料决策与 L2 现状（写入 MEMORY / 下轮 L2 计划）

本轮扫描 mc≥300 候选池发现：高命中 "hspice/netlist" trace 多为**离线网表解析**（L1），非真跑 hspice。已确认 L1 的：1i0em(rongtaoy)、jnf1q/mrwvg(jasonxu, ReadsigCM 网表文本过滤)。**真跑 L2 候选**：2vuso(tongni, hfeg0pkn003, `bsub -q fqueue3 finesim -i` 真 finesim tran 仿真 + bjobs + .meas 解析，2.0MB/510msgs，新用户)——下轮 L2 首选（finesim headless 在 .75 已验证可用，参考 TotemSC/CTLEAC/CTLESpec）。vaiob(harrywu, hspice:910) 2.85MB 超 2MB 需拆分深读。e0014566/xinqiaoz 的 calibre trace 是 L2 但用户过度代表。
