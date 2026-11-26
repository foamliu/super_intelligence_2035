# 深读笔记 · r278 · xiwang@hfeg0pkn002 · 1794035650061_tmx27 · ECC/DSA 版图定位

- **trace**: `1794035650061_tmx27` (xiwang@hfeg0pkn002/10.129.2.11) · 151 msgs · 2 real user turns · 1.03 MB · **dir-based 格式** `<sid>/<sid>.messages.json`（r277 误判 NFS 全 STALE，实为 flat→dir 存储迁移；dir-based 全可读，见下）
- **U#0 逐字**：「帮我基于DDGOA spine的版图，画出ECC和DSA所在的位置」(A-faithful eligible 提需求无根因；本案做 B 档)
- **U#1**：「打开这个图」

## 真实 agent 工具链
- **SandBox_MCP_Server__run_code 41 次**（=pyAether）+ read_files 13 + run_approved_command 6 + run_commands 2 + RAG_MCP_Server__search_apis 3
- 关键操作：
  1. 读 `/ai_sandbox/ddgoa/V0/agentdir/xiwang/SpineTop_modules.csv`（列 `cell,instName,lib,x1_um,y1_um,x2_um,y2_um`，实例 bbox 已在 µm 父坐标）
  2. 读 `fullmap.json`（层次图 `parent_lib|parent_cell -> {child_cell:...}`）
  3. 按正则 `r'ECC|Ecc'` / `r'DSA|Dsa'` 过滤 ECC/DSA 实例，per-class 统计 distinct cell + bbox 并集
  4. `ae.dbOpenCVByType("ddgoa_cmos_top","SpineTop","layout")` 打开版图 + `emyGetAllInstHeaders` 列 inst headers
  5. 递归走层次（BankTopX2→EccTop→RWCBWNewV2_DDGOA_A_DSA）做 transform 合成（rot R0/R90/R180/R270/MY/MX + offset）算绝对 bbox；全展开超时 → 收窄到 ECC/DSA 路径 + 限深
- ECC cells 实例：ECC_LbusN_Unit8bit_Rev28, ECC_Lbus_Unit8bit_Rev28, EccStg_topdown/topup/botdown/botup, EccTop128x1New_DDGOA_R1A_plan5_new_Rev28, ECC_LbusDrv_2Bank_Rev28, ECC_LbusDrvN_2Bank_Rev28
- DSA cells 实例：RWCBWNewV2_DDGOA_A_DSA_Rev28, RWCBWNewV2_DDGOA_B_DSA_Rev28, DSA_SenseAmp_Rev28, DataPath_DSA_Ctl_Rev28
- 层次：SpineTop 直接挂 ECC_LbusDrv* + BankTopX2_*（含 EccStg_*）；DSA 嵌在 ECC 数据路径深处

## 为何 B 档离线化 L2
真实 OA lib（`/ai_sandbox/ddgoa/V0`，agent 以 xiwang 身份可读，本人 t0002965 权限拒）+ pyAether dbOpenCVByType/emyGetAllInstHeaders 不可沙盒复现 → 离线核心 = 给定 spine 实例清单 JSON（cell/instName/lib/bbox µm）→ 按 cell 名 delimited-token 模式识别 ECC/DSA → per-class bbox 并集 + 实例数 + distinct cells + 实例位置清单 → 输出 `ecc_dsa_map.json` + `ecc_dsa_positions.csv`。check.py 在 hidden B 上 subprocess 真跑候选脚本并结构化比较 15 条件。

## 分类规则（golden）
- ECC：`re.match(r'^(ECC|Ecc)[A-Z_]', cell)`（ECC_/EccStg/EccTop/EccStage 等 ECC 作为开头 token）
- DSA：`re.search(r'(^|_)DSA(_|$)', cell)`（DSA 作为分隔符定界的独立词：DSA_xxx / xxx_DSA / xxx_DSA_xxx）
- 子串假阳性守卫：`BANDSAW_mux` / `BANDSAW_clk` 含 "dsa" 子串但 DSA 非独立词 → 不是 DSA（挫败 naive `'dsa' in cell.lower()`）

## B-track（hidden B vs A）
| | A (visible) | B (hidden) |
|---|---|---|
| spine | SpineTop | SpineTop_R2 |
| instances | 19 | 23 |
| ECC | 9 (ECC_Lbus*, EccStg_*, EccTop128x1*) | 10 (ECC_BusDrv_X4, EccStage_up/dn, EccTop256x2, ECC_LbusN_Unit16, EccStg_midup/middn, ECC_LbusDrv_4Bank) |
| DSA | 4 (RWCBWNewV2_*_DSA, DSA_SenseAmp, DataPath_DSA_Ctl) | 6 (RWCBWV3_*_DSA, DSA_SenseAmp_X8, DSA_Ctl, WrPath_DSA_Mux, DSA_BufRow) |
| 诱饵 | BANDSAW_mux + SpineRpt*/Abus/BankTop/Array16G | BANDSAW_clk + MeSaDiv + SpineRptC/AbusBotMux/BankTopX4/PeriTop/Channel |
参数化非硬编码：A/B 不同 spine 名、不同 ECC/DSA cell 与 bbox、不同计数(9/4 vs 10/6)、两个诱饵(BANDSAW_clk + MeSaDiv)挫败子串硬编码与 print_expected_A。

## cross-input 守卫
- B ECC=10 ≠ A ECC=9（挫败 print_expected_A 的 f/h）
- B DSA=6 ≠ A DSA=4（挫败 print_expected_A 的 g/i）
- B bbox 全不同（挫败 j/k 硬编码）
- BANDSAW_clk 在 B 不在 A（挫败 naive_substring 的 g/o）
- MeSaDiv 含 "Sa" 不含 "DSA"（额外负向）

## 自验
- ref `check.py` on `reference_submit.zip` over B: **15/15 PASS**
- golden on A sanity: spine=SpineTop ecc=9 dsa=4 other=6 ✓
- 5 negatives 全 FAIL: empty_shell→b, print_expected_A→f, core_deleted→j, naive_substring→g, wrong_class→f
- §4.9 三假(empty/print/core)全 FAIL ✓
- 3-run sha256 一致（deterministic）✓
- byte-sync test==disk check.py sha256 `3320c9b35656c299a25da635d57a586e5e4a7345c1d18f625d5c39aef1155d3e` ✓
- 断言闸门 k_rationale=k_check=15(a-o)≥8 GATE PASS ✓

## DISTINCT from 现有 layout_aether 系
r272 LayoutAnalyzeReport=统计报告(无定位分类)/r274 M1ShapeDelete=按层删除/r252 LayStructExtract/r253 PinListPortOrderExtract/r254 EmyCdlNetlistExtract/r222 SchOaInventoryExtract —— 本案首次 ground on「按 cell 名 delimited-token 模式做功能模块(ECC/DSA)双类识别 + per-class bbox 并集聚合 + 位置清单 + 子串假阳性排除」，核心是名字模式双类分类+几何并集聚合+假阳性守卫，非只读统计/删除/抽取。

## ⚠️ r277 NFS 结论更正（重要，影响后续所有轮次）
r277 判「.75 全 user-home cline session 文件 NFS ESTALE」**有误**。真相：cline session 存储从 **flat 格式**(`<sid>.messages.json`/`<sid>.messages.archive.json`，路径深度 4) 迁移到 **dir-based 格式**(`<sid>/<sid>.messages.json`，路径深度 5)。flat 文件 NFS handle 已失效(ESTALE)，但 dir-based 文件**全可读**（22 用户全 OK）。r277 fresh_pool_C_r277.tsv 路径全是 flat → 全 STALE；但同 sid 的 dir-based 副本可读。**r279+ 选料一律用 dir-based 路径** `/home/<u>/.cline/data/sessions/<sid>/<sid>.messages.json`。本深读即用 dir-based 读到完整内容。
