# 深读笔记 · rkdu8 · yuankong @ hfhds201 · spice_sim

## trace 概况
- session: `1793865966161_rkdu8`（epoch 1793865966161 ≈ 2026-11-06 ~11:00，trace 文件 78KB，30 msgs）
- 来源：hfhds201 local spice-dominant scout（snapshot hourly-new.2026-11-06_1300，live 已清，sp=85）
- 用户：yuankong（spice_sim 域高频用户）
- 域：spice_sim（网表/配置视图绑定定位）

## 对话流（关键轮）
- **U#0**（铺垫轮，不入 prompt）：`/proj/drcpa/V0/libs/drcpa_top/DDR5TOP/config_SpfBA_trans/mmsim.ini,记住这个路径文件先不分析，它是抽网表到配置文件` → assistant 记住路径暂不分析。
- **U#2**（铺垫轮，不入 prompt）：`/proj/drcpa/V0/simdir/finesim/drcpaF/Netlists/Netlist_SpfBA_20261104PM/netlist这是网表文件，先不分析` → 记住第二个路径。
- **U#4**（**任务说明轮，逐字用作 A-档 prompt**）：粘贴 10 条 `%28drcpa_array%5Cm384_Meg%5Cschematic%29.Imarray_N/Imsaq_N="schematic;;;"` 配置片段（含 Imarray_0/1/2/34/35/36 + Imsaq_0/1/34/35），末尾「在配置文件中除了指定到msa是schematic的，其余都是spiceld的，找出他们在网表哪一行」。**提出需求/目标轮**，未给根因/修复方案 → 符合 A-档 §①.2 选轮规则。
- **assistant（#5-#28）**：用 `list_allowed_files` 探测配置/网表根（netlist 是符号链接，指向 `/rundata/.../Netlist_SpfBA_20261104PM/netlist.postsim`，351915 行 50MB）。`read_files` 读 mmsim.ini。历经 4 版脚本 `find_schematic_insts{,2,3,4}.py`：
  1. v1：词边界 `(?<![\w])Imarray_0` → 0 命中（X 前缀挡住）。
  2. v2：广检 `Imarray`/`Imsaq` 任意出现 → 发现网表里是 `XImarray_35`/`XImsaq_33` 形式（X 前缀）。
  3. v3：词边界 `(?<![\w])` 仍被 X 前缀挡 → 0 命中。
  4. v4：枚举所有 Imarray/Imsaq 索引，按 `X`+name 精确匹配行 → 全部定位。
- **#28 金标准**：输出各 schematic 实例在网表的行号（Imarray_0→L262033 等）+ 行首内容，并标注差异——用户粘贴的 `Imarray_2`/`Imsaq_1` 在磁盘 mmsim.ini [InstBind] 中**并未**标 schematic（实为 spiceld），网表中存在但不属 schematic。`m384_Meg` 子电路块 L255355-L268044。检索脚本存 `/home/yuankong/find_schematic_insts4.py`。
- **U#29**（后续澄清轮，**不入 prompt**）：「假设我想把某行从spiceld变成schematic我[Cell]...你说的对这个才是它的配置」+ 粘全配置（[Cell]/[GlobalBind]/[ViewList]/[InstBind]），隐含修复方向 → 按 A-档 §①.2 不作任务说明。

## 三个关键判分点（金标准要点）
1. **配置文件 [InstBind] 段是 schematic 绑定权威**，非用户粘贴列表——用户粘贴含 2 个 spiceld 误标（Imarray_2/Imsaq_1），正确解必须以 mmsim.ini [InstBind] 值以 `schematic` 开头为准排除。
2. **网表实例带 X 前缀**（`XImarray_35`），词边界 `\bImarray_35\b` 不命中（X 与 I 均词字符，无边界）→ 必须按首 token `X`+name 匹配。
3. **注释陷阱行** `* <name> ...` 提及实例名但非 instantiation → 子串匹配 `<name> in line` 会命中注释行（错行），首 token 匹配才能命中 instantiation 行。

## 通用化与 case 设计
- 通用化为 `locate_schematic_insts.py`：读 mmsim.ini（仅 [InstBind] 段，值以 schematic 开头）→ 提取 schematic 实例 → 在 netlist 按首 token `X`+name 扫描 → 输出 `out.json {instance:{line,content}}`，未找到 line=0。
- A（SUT 可见）：mmsim_A.ini（8 schematic + Imarray_2/Imsaq_1 spiceld + [GlobalBind] 诱饵 Trap_0 + analog ;;;1）+ netlist_A（24 行，每 schematic 实例前有注释陷阱行）。
- hidden B：mmsim_B.ini（4 schematic：Imarray_1/34, Imsaq_0/35，不同集合）+ netlist_B（21 行不同布局/行号）。
- 判分 13 条断言（a-m）：见 check.py。discriminator：naive 词边界/子串 → 命中注释行错行（FAIL f）；非 section-aware → 含 Trap_0（FAIL d/l）；空壳 → 无 out.json（FAIL c）；硬编码 B → A 泛化失败（FAIL h）。
- 自验：ref PASS 13/13 ✓ · 4 negative 全 FAIL（distinct d/f）✓ · §4.9 三假（空壳/打印期望/删核心）全 FAIL @ c/h/f ✓ · 断言闸门 k=13==13≥8 ✓。

## 结论
CLEAN A-档 spice_sim L1，意图明确（U#4 提出需求，无根因/修复方向），金标准可复现，判分有牙。落库 EDA-Eval-DesignFlow-NetlistSchemInstLocate-001（jsonl_B 146→147）。
