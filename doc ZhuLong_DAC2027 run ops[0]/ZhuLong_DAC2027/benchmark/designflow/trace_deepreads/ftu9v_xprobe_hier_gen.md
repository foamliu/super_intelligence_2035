# Deep-read: ftu9v — CrossProbe 层级 CSV 生成（xiwang @ hfeg0pkn002）

**session**: 1794018796078_ftu9v.messages.json  
**user/host**: xiwang / hfeg0pkn002 (10.129.2.11)  
**match_count**: 497 (schematic:154 netlist:340 hspice:3)  
**size**: 477552 bytes, 129 msgs, 模型 GLM-5.2  
**domain**: schematic_netlist  
**grade**: B synthesized (资产私有不可直用 → 合成 fullmap_A/B)  
**level**: L1 (离线 Python 层级遍历+CSV 生成,无 EDA 工具)  
**case_id**: EDA-Eval-DesignFlow-XProbeHierGen-001  
**k 条断言**: 15 (a-o), check.py 15 独立条件, GATE PASS

## 真实 trace 流水

会话由 FindCir4CrossProbe_wx skill 触发（i=0 是 skill_instructions 块，非自然 user turn）。agent 全程 4 个自然 user turn（i=92/94/113/117）：

1. **i=0-91（skill 执行阶段）**：agent 在 pyAether 沙箱内写 `collector.py` 做实例级 BFS：从 `ddgoa_top/WOWTOP` 递归扫描全 schematic 层级，按真实 OA 实例句柄逐层记录 `父cell → {子cell: [instname|lib]}` 到 `fullmap.json`（分块增量合并，最终闭包 8985 cell、265 个直接例化 ptn_lvio 的父 cell）。再写 `builder.py` 做实例级遍历（按 ptn_lvio 祖先剪枝 + 总线逐位展开 + X 前缀），输出 CrossProbe 10 列 CSV（141725 行 ptn_lvio 器件实例）。全量格式校验 + pyAether 逐段回放抽样验证 0 坏行。

2. **U1 (i=92)**: "all approve during this task" — 批准，agent 确认交付。

3. **U2 (i=94)**: "根据找到的这些信息，帮忙依据你的理解，总结一下ptn_lvio都用在哪些模块的电路" — agent 用 fullmap.json 统计 265 父 cell 按 6 库分类，按功能归纳 9 大模块（DQ 收发/WCK 时钟/稳压参考/总线驱动/位线控制/环振电源门控/BTI 老化/LVIO 标准单元/延时相位）。

4. **U3 (i=113)**: "根据找到的这些信息，帮忙依据你的理解，总结一下ptn_lv都用在哪些模块的电路" — agent 发现 ptn_lv 是 ptn_lvio 的同名兄弟器件（394 父 cell），参数化 builder 的 seed（`sys.argv[3]`），重跑生成 185619 行 CSV，同样按 6 库 394 父 cell 归纳模块（电平转换/行列译码/WCK/DQ 收发/标准单元）。

5. **U4 (i=117)**: "上面ptn_lvio所产生的文件中，hierarchy path（hierPath列）不需要器件本身的instance。举例说明：/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_Array1GBK1.XI_m1G_TOP.XI_VblhXdecTopE.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<0> 换成 /XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_Array1GBK1.XI_m1G_TOP.XI_VblhXdecTopE.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2。帮忙按照这个，重新生成这个文件" — agent 改 builder 加 `MODE = sys.argv[4]`（leaf/parent），parent 模式：hierPath 截止父电路实例，instName/libName/cellName 同步改父电路，同一父实例多器件去重。重跑得 49524 行（从 141725 leaf 行去重）。

## 关键产物

- `collector.py`：pyAether BFS 层级采集 → fullmap.json
- `builder.py`：实例级遍历 + 总线展开 + X 前缀 + leaf/parent 双模式 CSV 输出
- `DDGOA_V0_ptn_lvio_records.csv`：leaf 141725 行 / parent 49524 行
- `DDGOA_V0_ptn_lv_records.csv`：leaf 185619 行
- 总线展开：`MP0<3:0>` → `MP0<0>..MP0<3>`（4 位），`MP0<1:0>` → 2 位

## 资产可达性

- `/proj/ddgoa/V0/libs/*` 与 `/ai_sandbox/ddgoa/V0/agentdir/xiwang/` 经 NFS 可读但属 xiwang 私有（fullmap.json/builder.py 实物不可直接复用为公开资产）
- → B-grade synthesized：合成 fullmap_A.json（同结构迷你层级）+ fullmap_B.json（不同 root/seed/结构反硬编码）

## 合成设计

**fullmap_A**（visible）：root=`ddgoa_top|WOWTOP`, seed=`ptn_lvio`
- 双分支：LP5TOP（用 seed）+ LP5TOP_ArrayDie（不用 seed，测剪枝）
- 6 直接父 cell：VblhDigDrvCmpIP / VblhXdecTopE / VblhXdecDrv / DqTxP2sM6 / VintComp / VintAmp
- VblhDigDrvIPTop 二次例化（via Array8G_E + Array1GBK1）→ VblhDigDrvCmpIP 出现在 2 条路径（测多路径）
- 总线：MP0<3:0>(4) / MP0<1:0>(2) / MP1(1) / XMP5(1) / XMP2(1) / XMP3(1) / XMP4(1)
- leaf=18, parent=7

**fullmap_B**（hidden）：root=`ddgoa_cmos_top|CHIP_TOP`, seed=`ptn_lv`
- 双分支：CoreTop（用 seed）+ IoTop（用 seed，WckOsc/DqBuf）
- 12 直接父 cell，更深嵌套（WckOscCore 16 位总线 MP0<15:0>）
- leaf=51, parent=13
- 每维度反硬编码：root 名 / seed 名 / cell 名 / 库名 / 总线宽度 / 层级深度全不同

## 候选脚本（xprobe_hier_gen.py）

CLI: `--fullmap <json> --seed <cell> --mode <leaf|parent> --out <csv>`
逻辑：
1. 加载 fullmap.json
2. 自动找根（不被任何 cell 例化的 cell）
3. 构建目标器件的祖先闭包（直接含 seed 的 cell + 传递含祖先的 cell）
4. 从根 DFS，按祖先闭包剪枝
5. leaf 模式：每个器件实例（总线逐位展开）一行，hierPath 含器件段，cellName=器件名
6. parent 模式：每个父电路实例一行（同父多器件去重），hierPath 截止父电路，cellName=父电路名
7. 每段实例名加 X 前缀，输出 10 列 CSV

## 判分（check.py, 15 条 a-o）

a zip 合法+含 .py / b py_compile / c leaf B subprocess exit 0 / d 表头 10 列 / e leaf B 行数=51（反硬编码）/ f hierPath 格式（/ 开头+每段 X）/ g instName==末段 / h cellName==seed+lib==TECHLIB / i 总线展开 ≥8 位 / j parent B subprocess exit 0 / k parent 行数<leaf 且=13 / l parent 末段为电路（XI_）非器件（XMP）/ m parent instName==末段 / n parent cellName≠seed / o 反硬编码（A leaf=18≠51）+3-seed 确定性

## 自验

- ref PASS 15/15（leaf_B=51, parent_B=13）
- §4.9 三假：fake_empty→e / fake_print_only→e / fake_core_deleted→e 全 FAIL
- 4 neg：neg_hardcode_a→e / neg_drop_parent→n / neg_print_only→e / neg_empty→e 全 FAIL
- negative_selftest ALL_FAIL=True
- 3-seed 确定性（B leaf 3 次 md5 一致，含在 check o）
- byte-sync sha 3737ccd9 size 8169
- D.jsonl 234→235
