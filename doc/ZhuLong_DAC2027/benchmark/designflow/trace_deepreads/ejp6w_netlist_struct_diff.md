# ejp6w — HSPICE 网表结构化对比（trace deepread）

## 元数据
- **session_file**: `1794143556321_ejp6w.messages.json`
- **user/host**: yuchens @ hfeg0pkn004 (10.129.2.13)
- **match_count**: 549（11-09 cron log 新增，11-08 cron log 不含 → 11-08 当日新写入）
- **markers**: `549 schematic 440 netlist 172 dbGet 129 pyAether 41 cellview 38 "lang": "pyAether" 20 hspice ...`
- **domain**: characterization（HSPICE 网表对比 + Aether 原理图检查）
- **总消息数**: 230

## 用户对话流（关键轮）

| msg# | 用户原话 | 分类 |
|------|---------|------|
| #0 | 你能读取linux路径下的网表的内容吗？ | 能力询问（非任务） |
| #7 | /proj/drvqa/V0/workdir/yuchens/simulation/robin_cbcc_matleveltb_SMgap_CBCC_schematic_ALPS/robin_cbcc_matleveltb_SMgap_CBCC_schematic.netlist | 给网表 1 路径 |
| #11 | 还有一份网表，路径是/proj/drvqa/V0/workdir/huange/simulation/netlist/V2B_CBCC_NSA_PSA_Vb.netlist，这个也读取一下 | 给网表 2 路径 |
| #15 | 这两份网表有什么差异吗 | 提出需求 ✓ |
| **#53** | **两个网表对应的按理说对应的是同一个电路，为什么抽出来的网表不一样，我该怎么去检查电路呢** | **提出需求 + 表达目标（A-faithful ✓，无根因）** |
| #105 | 你能进入Aether帮我检查电路吗 | 提出需求 ✓ |
| #169 | 为什么在第一个网表里定义了kcellx16BGmdl_1，而第二个网表没有 | 用户给出具体差异点（接近根因，不选作 A 档 prompt） |
| #207 | 现在我改了一下网表，你再帮我对比一下现在还有没有差异 | 用户已修复后重验 |
| #219 | 现在还有区别吗 | 继续追问 |

**A-faithful prompt 选 msg#53**：提出需求 + 表达目标，无根因、无修复方案。

## 金标准（assistant 实际产物）

### 1. compare_netlists.py（msg#17-45 逐步编辑）
解析 `.SUBCKT` / `.macro` 块，对比两份网表的 subckt 名集，输出：
- `Subckts unique to File1` / `Subckts unique to File2`
- `Identical subckts`（同名 body 完全一致）
- `Different subckts`（同名 body 有差异）
- per-line unified diff

### 2. 首轮对比结果（msg#45，原始两份网表）
- **File1 独有**: `kcellx16BGmdl_1`, `probeI`, `VCT_kcellx1mdl_schematic_drvqa_array_core`, `VCT_kcellx1mdl_schematic_trgqx_array_core`
- **File2 独有**: `VCT_kcellx1mdl`
- 关键差异：File1 用带 `_schematic_drvqa|trgqx_array_core` 后缀的实例化名，File2 用统一名 `VCT_kcellx1mdl`；File1 多 `kcellx16BGmdl_1`（kcellx64BGmdl 内的实例名重复定义）和 `probeI`（0V DC 探针）

### 3. cxsa_diff.py（msg#224-228，用户改名对齐后）
对 `cxsa_1x4` subckt 逐行对比，捕获两类差异：
- **网名重命名**: `inh_vss` → `vb_nsa`（File1 用层次内 vss，File2 用顶层电源 net）
- **参数新增**: File2 每个实例追加 `delvtrand_<model>=dvt_<x>`（如 `delvtrand_ntnlvio_oc=dvt_oc`、`delvtrand_ntnlvio_iso=dvt_iso`、`delvtrand_ptnlvio_sa=dvt_psa`）

### 4. pyAether 检查（msg#133-181）
agent 进 Aether 打开 `robin_cbcc/matleveltb_SMgap_CBCC/schematic`（115 instances / 101 nets），下钻 `array2Meg_1` → `kcellx16BGmdl` → `VCT_kcellx1mdl`，确认 `drvqa_array_core/kcellx16BGmdl_1/schematic` 存在（36 instances），证实网表差异源于层次配置/重命名策略不同，非电路本身不同。

## 本 case 抽取（可复用子流）

**HSPICE 网表结构化对比工具**：
- 输入：两份 HSPICE 网表文件
- 输出：subckt 名集差异（only-in-1 / only-in-2）+ 同名 subckt body 行 diff（unified diff）
- 通用化：不依赖具体 subckt 名/网名，纯结构对比

**难度点**：
1. 需正确解析 `.SUBCKT`/`.macro`/`.ENDS`（大小写不敏感）
2. body 行比对要 rstrip 后逐行比较（处理行尾空白）
3. detailed diff 要输出 unified diff 格式（+/- 行）
4. 不能硬编码具体 subckt 名（A/B 结构不同）

## 资产合成

- **可见 A**：`netlist_A1.sp`（含 alpha_only_A1 独有 + gamma_diff_A 用 gnd 无 param_X）/ `netlist_A2.sp`（含 zeta_only_A2 独有 + gamma_diff_A 用 vss 加 param_X=1）
- **隐藏 B**：`netlist_B1.sp`（含 delta_only_B1 独有 + zeta_diff_B 用 inh_vss 无 delvtrand）/ `netlist_B2.sp`（含 eta_only_B2 + theta_only_B2 独有 + zeta_diff_B 用 vb_nsa 加 delvtrand_*=dvt_*）
- **B 与 A 结构不同**：B 有 2 个 only_in_2 vs A 1 个；B 的 diff 是 net 重命名 + 多参数，A 的 diff 是 net 重命名 + 单参数；subckt 名集完全不同（防硬编码）

## check.py 15 条断言（a-o）

a: zip 含 1 .py | b: py_compile | c: B exit 0 | d: only1 节存在 | e: only1==[delta_only_B1] | f: only2 节存在 | g: only2==[eta_only_B2,theta_only_B2] | h: identical 计数==4 | i: identical 名集 | j: different 计数==1 名 zeta_diff_B | k: +行含 vb_nsa | l: +行含 delvtrand_ | m: A-only 名不泄漏 | n: A 泛化 | o: 3x 幂等

## 自验
- ref PASS 15/15 ✓
- 5 negative 全 FAIL（naive_no_diff/hardcoded_b/print_expected/always_empty/del_core）NEG_RC=0 ✓
- §4.9 三假（empty/print-expected/del-core）全 FAIL ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl test sha256 == disk check.py sha256 ✓
