# Deepread — r251 · 92xei · zlhou · LVS ambiguity diagnosis

**session**: `1793783868972_92xei.messages.json` (10.129.2.14 / hfeg0pkn005, user zlhou, mc=51)
**keywords**: lvs:682 calibre:196 .cdl:69 netlist:137 transistor:17 schematic:17 aether:11
**N msgs**: 45 (1u organic + 2u follow-up + 42a)
**agent**: lead, wrote `/home/zlhou/analyze_dec_crr.py` (recovered, 3 iterations)

## 用户真实意图（organic）

- **U#0** (提出需求，未给根因): `现在的工作目录是/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/svs/svs_10_15，未经允许禁止修改现有文件，我的svs结果在svdb中，看一下问题出在哪里`
  - SVS (schematic-vs-schematic) Calibre LVS 流程，结果在 svdb 里，要诊断问题
- **U#41** (澄清): `我就是用0_run_bk运行的`（说明实际用 0_run_bk 而非 cmd 脚本，澄清 Calibre 版本）
- **U#43** (追问概念): `HCELL/匹配约束是什么`（问 HCELL 概念）

A 档 rule2 检查：U#0 是「提出需求、未给根因」，A 档合格；但 /proj/lacaa 资产对 e0031982 权限拒绝（见下），故走 B 档重定义。

## agent 工具链与产物

1. `list_allowed_files` 探 `/proj/lacaa/.../svs_10_15` 与 `svdb/`
2. `read_files` 读 `lvs.rep`（87-460 行）+ `query_results` + `cmd` + `0_run_bk`
3. `search_codebase` 搜 `subckt I_DEC_CRR` / `CRADD\[2\]`（超时，网表太大）
4. `editor` 写 `/home/zlhou/analyze_dec_crr.py`（3 版迭代）：
   - v1: grep + extract_subckt（正则 `.subckt <name>` 起、`.ends <name>` 止）
   - v2: 修文件格式探测
   - v3: extract HC2PFS_DEC24 → HC2PFS_NANDDEC_RBUF + HC2PFS_INVF2D1 → 解析 lvs.rep 的 DISC# net headers + Error/Warning/INCORRECT/Property/SUMMARY 行
5. `run_approved_command` (profile=python-runner) 跑脚本

## 关键发现（agent 结论）

- lvs.rep 头部 `CALIBRE VERSION: v2023.3_14.8`，与 `0_run_bk` 用 `ds/calibre/2023.3_14` 对上 → 这次跑**成功完成**
- `cmd` 脚本用的是 v2020.1_36.18 + 加密规则文件，iamlog 报 `DECRYPT2` 解密失败 → 与本次无关
- 报错只集中在 `I_DEC_CRR[1]`（子电路 HC2PFS_DEC24）：2 条网（`I1/I_DEC_CRR[1]/BN`、`I1/CRADD[2]`）、6 个器件挂接（I_0~I_5）
- 抽取 HC2PFS_DEC24 / HC2PFS_NANDDEC_RBUF / HC2PFS_INVF2D1 在 source .netlist 与 layout .cdl 中的定义**完全一致**
- **结论**：报错是「匹配歧义（ambiguity）伪报错」——4 个同构 NAND（HC2PFS_NANDDEC_RBUF）使 Calibre 把 I_4↔I_5、B↔BN 错配；修复方法是加 HCELL/匹配约束（拷规则文件到可写目录加约束再跑，不动原始 .lvs），不是真改版图

## BLOCKER

- `/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/svs/svs_10_15/` 对 e0031982 **权限拒绝**（lvs.rep / .netlist / .cdl 不可读）
- 但 agent 的 `analyze_dec_crr.py` 已完整恢复（在 ~/，e0031982 可读）→ 提供 extract_subckt 正则 + lvs.rep 解析逻辑的 grounding
- 真实子电路名（HC2PFS_DEC24 / HC2PFS_NANDDEC_RBUF / HC2PFS_INVF2D1）与「4 同构 NAND 导致歧义」机制作为 B 档重建依据

## B 档重定义（参数化离线诊断器）

SUT 写 `lvs_ambig_diag.py <lvs.rep> <source.netlist> <layout.cdl> -o <out.json>`（stdlib only）：
1. 解析 lvs.rep：`CALIBRE VERSION` 版本号 + `DISC NET:` 不一致网数 + `DISC DEV:` 错误器件数 + `SUSPECT SUBCKT:` 嫌疑子电路名（按出现顺序去重）
2. 对每个嫌疑子电路：用正则 `.subckt <name>` ... `.ends <name>`（大小写不敏感）从 source.netlist 与 layout.cdl 抽完整定义块；任一缺失 → verdict=SUBCKT_NOT_FOUND
3. 拓扑等价比对：去注释行（`*`）+ 空行、实例行折叠空白、**按字典序排序**实例行（SPICE 顺序不影响拓扑）、拼接比较；相等 → `AMBIGUITY_FALSE_POSITIVE`，不等 → `REAL_MISMATCH`
4. 输出 JSON（indent=2, sort_keys=True）：calibre_version / total_disc_nets / total_error_devices / suspect_subckts[{name,verdict,source_line_count,layout_line_count}] / summary{total_suspects,ambiguity_count,real_mismatch_count}

## DISTINCT from 现有 physical_verify 系

- r250 HcellPairGen：从 CCI-LVS 缺失日志**生成** hcells 配对文件（generation）
- r237 DrcLogTeardownReport：DRC log 4 模块拆解（DRC，非 LVS）
- r240 WlAdjacentPairParse：.rep PAIR 邻接表解析（DRC .rep）
- r245 RectAspectRuleCheck / r243 VssPunchRuleGen / r242 SaqpIntAngleEqSplit / r241 SvrfPvrsRuleTranslate：DRC deck 生成/改写
- 本案：**LVS connectivity 报错的真伪诊断**——解析 lvs.rep 报错 + 抽取嫌疑子电路在两份网表中做拓扑等价比对，分类「匹配歧义伪报错」vs「真拓扑不一致」。**首次 ground on Calibre LVS ambiguity false-positive 诊断**（agent 真实脚本 analyze_dec_crr.py 的 extract_subckt + 比对逻辑）

## case 资产（代表性，grounded on trace）

- A (visible): SRAM_512X8 译码器, v2023.3_14.8, 2 DISC NET / 6 DISC DEV / 3 嫌疑(DEC24/NANDDEC_RBUF/INV2D1) 全一致→全 AMBIGUITY
- B (hidden): ADC_12B 译码器, v2024.1_22.5, 3/8/4 嫌疑(ADC_DEC8/ADC_NAND2 一致 + ADC_MUX/ADC_LATCH 不一致)→2 AMBIGUITY + 2 REAL_MISMATCH
- B2: LVS CORRECT 无报错→空嫌疑
- B3: PLL_PFD, v2022.4_30.1, 2 嫌疑(PFD_NAND/PFD_DFF) 全不一致→全 REAL_MISMATCH, ambiguity_count=0

## 自验

- golden_solution.py 16/16 PASS ✓
- 5 negative(empty_shell/print_expected/hardcoded_A/core_deleted/stub_no_extract) 全 FAIL ✓
- §4.9 三假提交(empty/print-expected/core-deleted) 全 FAIL ✓
- k_rationale=16=k_check(a-p)≥8 ✓，已落 jsonl_C(241 行)+ledger mark case
