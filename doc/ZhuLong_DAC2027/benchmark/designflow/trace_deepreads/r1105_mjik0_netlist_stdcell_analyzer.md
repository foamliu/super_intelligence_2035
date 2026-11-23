# Deepread: mjik0 — netlist stdcell/transistor analyzer

**session**: 1794895310954_mjik0.messages.json
**user/host**: vincentz @ hfeg0plg58 (10.129.35.82), mc=63
**domain**: spice_sim (shard B)
**size**: 323KB / 58 msgs
**scan keywords**: cmos:370;netlist:168;transistor:118;lvs:71;schematic:43;mosfet:32;hspice:10;analog:8
**trace_source**: real cline session, file at `/home/vincentz/.cline/data/sessions/1794895310954_mjik0/1794895310954_mjik0.messages.json`

## 用户意图（4 个递进分析子任务）

用户给一个 AETHER-SE 生成的 HSPICE 网表路径
`/proj/drgqa/V0/workdir/vincentz/simulation/drgqa_top_WOWTOP_schematic_ALPS/netlist`，
依次问：

1. **U#1**：网表里有多少个 stdcell 用到了 L=36nm 的器件
2. **U#4**：列出包含 L=36nm 器件的**最小的子电路**（叶子）以及所属 library 库
3. **U#5**：整理所有用到的 stdcell，计算**使用次数**以及**使用频率**
4. **U#6**：按管子 **Length 第一级分类**，里面再按**管子类型**分类，计算**管子占比**

## assistant 工具链（7 个 python 脚本，均 python-runner 执行）

关键发现逐条：

### 网表格式（explore_netlist.py / explore_netlist2.py）
- AETHER-SE HSPICE 格式；`* Library : <name>` 与 `* Cell : <name>` 注释行
- 器件**不是** `M` 开头原始 MOSFET，而是 `X` 开头子电路实例：
  `XMMN9 InN In inh_vss inh_vss ntn w=796e-9 l=36e-9 nf=2`
  （最后一个非参数 token = wrapper/model 名，如 `ntn`/`ptn`/`ntn_lv`/`ptn_lv`/`ntk`/`ptk`）
- 续行以 `+` 开头
- 含 `l=36e-9` 的行 = 2049；含 `36e-9` 任意位置 = 2852（含 W 等命中）
- first-char 分布：X=397479, R=1707, C=1695, V=20...

### L=36nm 在哪些库（analyze_l36_stdcell.py）
- 2049 个 l=36e-9 器件，分布在 3 个库：
  `drgqa_cmos_io`: 2009, `drgqa_cmos_digital`: 31, `drgqa_cmos_core`: 9
- **24 个 subckt 直接含 l=36e-9 器件**（distinct cell count = 24）
- 两个真正 stdcell 库（`stdcells_ac` 884 单元、`drgqa_cmos_stdcells` 564 单元）**都不含 l=36e-9**
  → 回答 U#1：stdcell 里用 L=36nm 的 = 0

### 库普查（census_libs.py）
- 网表所有库及 subckt 定义数；stdcell 库 = stdcells_ac(884) + drgqa_cmos_stdcells(564)

### 叶子 subckt（leaf_l36_subckts.py）
- leaf = 直接含 l=36e-9 且**不**实例化其他 container 的 subckt
- 结果：24 个 container **全是 leaf**（IO_TX_FFE_PATH 疑似父级但实际未实例化其他 container）
- 输出表：subckt / library / L36dev / TotalDev

### stdcell 使用统计（stdcell_usage.py）
- 建 subckt 层级，topological order + multiplier 传播算**flat instances**（2483086）
- direct text refs = 94786；per-cell flat_inst + freq%
- top: invLx1(107144, 4.315%), dlyg2Ls2_gut1(73991, 2.980%), nand3x1_GSRowred(65408, 2.634%)...

### 管子两级分类（transistor_L_type.py）
- 探查 wrapper 名（explore_wrappers.py）：35 个 wrapper；ntn/ptn/ntn_lv/ptn_lv/ntk/ptk/ptk_lv/ntn_m...
  + 电阻 wrapper `rndiff_3t_ckt`(1324) / `rnpo_2t_ckt`(921)（需排除）
- 排除电阻 wrapper 后：50952 direct 器件行，147 个 distinct L 值
- 按 L → type(NMOS/PMOS wrapper) 分类 + direct%/flat%
- L=36nm: 2049 direct (4.02%), 1027 NMOS / 1022 PMOS

## reframe（本题）

**case_id**: EDA-Eval-DesignFlow-NetlistStdcellAnalyzerProduce-001
**deliverable**: `netlist_stdcell_analyzer.py <netlist.sp> <spec.json> <out.json>`
**level**: L1 纯 Python 无 EDA 依赖
**domain**: spice_sim

把 4 个分析子任务程序化为单一脚本，输出结构化 JSON：
- `libraries`: 所有库 + subckt 定义数
- `l_analysis`: target_l 器件总数 + container subckts + leaf subckts（层级判定）
- `stdcell_usage`: stdcell 库单元的 direct 引用计数 + frequency%
- `transistor_classification`: 按 L → wrapper type 两级分类 + 占比（排除电阻 wrapper）

### A（visible，源自 vincentz 真实结构）
- 5 个库：stdcells_ac(6), drgqa_cmos_stdcells(3), drgqa_cmos_io(5), drgqa_cmos_digital(2), drgqa_cmos_core(1)
- target_l = 36e-9；8 个 container，7 个 leaf（IO_TX_FFE_PATH 实例化 IO_MuxStage1_ffe → 非叶子，构成层级齿）
- stdcell 库 9 单元全不含 l=36e-9（与真实一致）
- wrapper: ntn/ptn/ntn_lv/ptn_lv（NMOS n* / PMOS p*）

### hidden B（与 A 五重异构）
- 库名全异（core_stdcells/analog_blocks/io_phy/digital_top/sram_core）
- target_l = 34e-9（非 36e-9）
- 不同 container/leaf 结构（2 级父子链 A→B→C，仅 C 为叶子）
- 不同 stdcell 集 + 不同 direct_count
- 不同 wrapper 名（nmos_lvt/pmos_lvt/nmos_hvt）+ 不同 L 值（28e-9/34e-9/40e-9）

### check.py 12 条独立断言
①(a)zip+.py+compile+size ②(b)B exit0+有效JSON ③(c)libraries 结构+特定库 subckt_count 精确 ④(d)total_target_l_devices 精确 ⑤(e)container 名集合精确+某 container l36 计数精确 ⑥(f)leaf 名集合精确(核心层级齿:父级不在 leaf) ⑦(g)stdcell_usage 总数+top 单元名+top direct_count 精确 ⑧(h)stdcell top frequency_pct 容差+频率和≈100 ⑨(i)transistor_classification 含期望 L+总器件数精确+排除电阻 wrapper ⑩(j)特定 L 的 type 计数精确+占比和≈100 ⑪(k)anti-hardcode:A 特有 token 不在源码 ⑫(l)3-seed 确定性

### 3 negs
- neg1_empty: 空脚本 → (a)
- neg2_print_only: 硬编 A 的 oracle 值写到 out.json → (d)/(e)/(g)（B 值不同）
- neg3_core_removed: 解析正常但跳过 leaf 层级判定（全部 container 当 leaf）→ (f)

## 台账
- mjik0: claim → mark case (EDA-Eval-DesignFlow-NetlistStdcellAnalyzerProduce-001)
