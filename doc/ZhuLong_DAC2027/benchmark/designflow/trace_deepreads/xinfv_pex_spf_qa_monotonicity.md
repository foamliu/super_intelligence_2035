# trace_deepread: xinfv (sierraw PEX SPF QA)

- session: 1795416975614_xinfv.messages.json
- user: sierraw @ hfeg0pkn001, mc=296, 191 msgs, schematic_netlist domain
- ledger: claimed r1230 -> case EDA-Eval-DesignFlow-PexSpfQaMonotonicityCheck-001

## 真实意图
用户 sierraw 在 `/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/lpe_trend/LPE` 有 SPF/DSPF 文件
(64 corner = {BASE,MB}x{ELVT,LVT,SVT,ULVT}x{cbest_ccbest,cworst_ccworst}x{m40c,0c,125c} + typical x {25c,85c},
DSPF 1.3 GloryEX RC)。要做 pex 极简 QA，建 QA 文件夹放代码+结果：
- 0. cell 数统计(每库每 VT)
- 1. 同温度跨 corner CAP 检查 cbest<typical<cworst (cell/net/cap 三层)
- 2. 不同 corner 跨温度 CAP 检查
- 3. 同 corner 跨温度 R 检查(温度升高 R 变大, cell/net 两层)

## assistant 行为
写 `qa_pex_min.py` (83255B/1633 行): 解析 DSPF(*|NET pF / C 元件 F / R 元件 ohm, 节点 base 去子节点后缀),
实现 4 项筛查: cell 一致性、cap 跨 corner 单调性(链式最近温度配对, cell/net/cap 三层口径)、
跨 corner 跨温度 cap、导线 R 温度系数(铜正温度系数, 跨 net 栅/阱电阻不计入)。
输出 qa_summary.md 中文报告 + results/*.csv 明细 + matplotlib 图表。
辅以 analyze_viol.py/diag_netn.py/diag_devcap.py 诊断脚本 + verify_migrate.py 迁移校验。

## reframe (可离线判分内核)
项目 SPF/项目文件受权限保护沙盒不可读 -> 抽取内核 = 从结构化 mini-DSPF 文件集
(按 `<lib>_<vt>_<corner>_<temp>.dspf` 命名)生成 PEX QA 报告: 解析 *|NET 总电容(pF)/C 元件(F)/R 元件(ohm),
跑 Check0(cell 名一致性)/Check1(cbest<typical<cworst 电容单调性)/Check3(同 corner 跨温度 R 正温度系数),
输出 qa_report.md + violations.csv + cell_count.csv。
与 r1208-r1229 内核全不相交(本例 SPF/DSPF 解析 + 跨 corner 电容单调性 + 电阻温度系数 QA,
前例 mt0 period1t / postsim TB wrapper / Verilog 例化树 / clock 传播 / 寄存器溯源 / 总线布线 / emyDesign dump 全不相交)。

## case 设计
- A (visible, assets/.../A/lpe_A): 20 个干净 mini-DSPF (BASE/MB x LVT/SVT x cbest/typical/cworst x 温度), 无违例 -> 期望 OVERALL=PASS
- B (hidden, assets/.../hidden/lpe_B): 20 个 mini-DSPF, 植入 3 类违例:
  - check0: BASE_LVT_cbest_m40c 的 *|ROOT_DESIGN = invBAD (其余 = invBaseLVT) -> cell 名不一致
  - check1: net out 的 cworst 总电容 0.75pF < cbest 1.20pF -> 违反 cbest<typical<cworst
  - check3: net mid 导线电阻 R(125c)=7.0ohm < R(m40c)=10.0ohm -> 温度升高 R 反而下降
- A/B 结构性不相交(A cell 全一致 invBaseLVT/invBaseSVT/invMbLVT/invMbSVT 且无违例; B 植入 invBAD + out 反向 + mid R 反向)
- k_check=15: zip 有效+含.py / py_compile / B 产报告 / B=FAIL / A=PASS(anti-hardcode 交叉) / check1 标 out / check3 标 mid / check0 标 invBAD / in 无误报(check1) / in 无误报(check3) / violations.csv 表头 / 3 次确定性 / 源码无 B 硬编码值 / 空输入优雅 / 无 __chk 残留

## §4.9 三假
- N1_empty (空桩): 无报告 -> ③FAIL
- N2_hardcode_a (硬编码 B 违例): A 上仍报 FAIL -> ⑤anti-hardcode FAIL
- N3_core_deleted (删核心只报 PASS): B 上报 PASS -> ④FAIL

## 自验
本地 python3.12: reference 15/15 PASS + 3 负样本全 FAIL + negative_selftest ALL OK + round-trip(从 case JSON 提取 test exec) PASS
