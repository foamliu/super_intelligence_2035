# deepread — sid 1794461397387_7ehdd (chengwen @ hfeg0pkn003 / 10.129.2.12, mc=37)

**session**: 1794461397387_7ehdd, user=chengwen, host=hfeg0pkn003, ip=10.129.2.12
**keywords**: analog:1041;netlist:97;drc:96;cmos:51;lvs:33;schematic:9;hspice:6;aether:3
**size**: messages.json 411KB / 46 msgs
**domain**: schematic_netlist (D)

## 用户意图（逐字）
- U0/U4: 「`/proj/drcpa/V0/workdir/chengwen/simulation/drcpa_top_DDR5TOP_config_pwrup_trans_ALPS/netlist.presim` 这是netlist，帮我整理一下用到vdleq的cell name和hierarchy」

(提出需求轮 — 用户只说目标，未给根因/修复 ⇒ 合格 A-档任务说明来源)

## 助手工具链 / 产物
1. `analyze_vdleq.py` (v1) → 跑通：376361 行 / 6929 subckt / 173 touching vdleq，但顶层判断不准（库 cell 未被实例化）
2. `analyze_vdleq_v2.py` → 报告 vdleq_report.txt(3044 行), roots 11 个(含 switch_close 等)，hierarchy 155 路径
3. `analyze_vdleq_v3.py` → 修正 ①端口续行(`+`)把 vdleq 端口误判为 body ②实例行末尾参数(如 `m=4`)致 master 误判。修正后：173 touching(143 both / 29 body-only / 1 port-only), 265 hierarchy 路径, roots=PERI0/Array6G_T 等
4. `verify_vdleq_top.py` → 复核顶层端口：Array6G_T/PERI0 端口 inh_vdleq 连顶层 net `vdleq!`

## 金标准（trace 末尾用户接受的结果，U45 整理）
| 项目 | 数值 |
|---|---|
| netlist 总行数 | 376,361 |
| subckt 总数 | 6,929 |
| 接触 vdleq 的 cell | 173 (143 both + 29 body-only + 1 port-only) |
| port-only cell | R_RasBnkLogic (端口 cm1_ro_IsoViso2VdleqEn = 控制信号，未内部使用) |
| hierarchy 路径 | 265 |
| 顶层 root | PERI0, Array6G_T |
| 顶层电源网络名 | vdleq! |

## 合成计划（本轮 r620 落库）
- **case_id**: EDA-Eval-DesignFlow-VdleqCellHierExtract-001
- **domain**: schematic_netlist (D), L1 离线 Python 网表解析 (真跑候选 subprocess)
- **SUT 产**: `vdleq_analyze.py` (CLI: `python3 vdleq_analyze.py <netlist>`, 报告打印 stdout) + `vdleq_report.txt`
- **asset A (visible)**: `netlist_A.sp` — 6 subckt / 5 touching(1 port-only R_RasBnkLogic / 1 body-only AG_TSEnCtrl / 3 both) / 6 hierarchy 路径 / roots PERI0,Array6G_T / top net vdleq!
- **hidden B (check target)**: `netlist_B.sp` — 10 subckt / 7 touching(0/3/4) / 8 路径 / root PERI0
- **hidden C (cross-input guard)**: `netlist_C.sp` — 4 subckt / 3 touching(0/0/3) / 3 路径 / root PERI1
- **check.py**: 16 cond (a)-(p), 内嵌 oracle 自算 golden 比对候选报告；B 数值/集合 8 cond + C 跨输入 guard + A 反硬编码 guard + zip/compile/leak 3 cond
- **negatives**: 5 个(empty_shell→b / print_only→o / hardcode_a→e / core_deleted→j / no_classify→h), 全 FAIL, 5 distinct labels
- **自验**: ref PASS 16/16 + 5 neg ALL FAIL NEG_RC=0 + §4.9 三假(empty/print/core)全 FAIL
- **k_rationale = k_check = 16 ≥ 8 ✓**

## 判分难度
L1 静态网表解析 + subprocess 真跑候选。难在：①vdleq 接触分类(port/body/both)语义 ②hierarchy 路径计数(共享子电路多路径) ③跨输入泛化(反硬编码)。判分器内嵌 oracle，对事实(计数/集合)断言，不对措辞。
