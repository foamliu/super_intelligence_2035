# Trace deepread — 6ipfr (phoebeli @ hfeg0plg96, mc91, spice_sim)

**session**: `1794361050224_6ipfr.messages.json` (44 msgs, 473KB)
**trace 在子目录**: `/home/phoebeli/.cline/data/sessions/1794361050224_6ipfr/1794361050224_6ipfr.messages.json`
（非根 .messages.json，host 端 find 校验：1794361050224_6ipfr/ 子目录下）
**scan**: 11/16 07:26 扫描 mc=91 (ledger 旧快照 mc18 已 stale)；keywords netlist:370/analog:94/pex:68/cmos:66/aether:30/hspice:25；tools 279 netlist/20 schematic/18 hspice/2 spectre
**agent**: lead (zhulong, Aether/Cadence/PrimeSim-Finesim 工具链)

## 用户真实意图（3 类相互关联的问题）

1. **msg0 (user)**: 「如何在 block 网表里定义一个 pwl 电压源」 — how-to：block（子电路/模块级）网表里定义 PWL 电压源。
2. **msg2 (user)**: 贴 4 条错误求解决：
   ```
   ERROR! no reference ckt vh for xi_setiddampoip_111(netlist:67170) of vintrefampcoreip
   ERROR! no reference ckt vh for xisetiddampo(netlist:427654) of vcsldigdrvcmphsyip
   ERROR! no reference ckt vh for xi_setiddampoip_92(netlist:423044) of vblhstbylpowerampotaip
   ERROR! no reference ckt vh for xi_setiddampoip_92(netlist:422179) of vcsldldostbyampotaip
   ERROR! exit due to previous fatal errors
   报错了，该怎么解决
   ```
   **msg4 (user)**: 给仿真目录路径 `/rundata/ddgoa/V0/simdir/finesim/ddgoaF/MatrixRun_Netlist_IDD_20260824_Vcap_DLDO_function/.../forcevintcore` 求解决方案。
3. **msg42 (user)**: 给两行网表求 vh 合理处理：
   ```
   XI_SetIDDAmpOIP_71 net021 Out inh_vcc SetIDDAmpOIP vh vout=pvblh
   vcc vh inh_vss PWL(0s {pvint1} 1.46us {pvint1} 1.66us {pvint2} 2.4us {pvint2} 2.6us {pvint3}) power=0
   如何合理的对 block 网表的 vh
   ```

## assistant 工具链与产出

- **msg5 list_allowed_files** → 仿真目录（bsub.log/compare.rep_20261020/... 允许读）
- **msg7-msg39 read_files / run_approved_command** → 探 si.inp(~1364 行) + netlist.presim(~183MB) + bsub.log；尝试写 find_missing_subckts.py（editor 被拒：profile shell-runner 需 filePath / Desktop 空无可写脚本）
- **msg41 (assistant)**: 综合分析根因 + 4 缺失 cell + 解决方案
- **msg43 (assistant)**: 分析 msg42 两行网表，指出 vh 在 X 元素 subcircuit 名之后被 Finesim 当 view name

## 关键诊断（msg3/msg41/msg43 verbatim 要点）

**4 条错误本质**：PrimeSim/Finesim 层次展开 X 元素时找不到子电路定义。报错行号(67170/427654/423044/422179)指 netlist.presim（~183MB）中的行号，非 si.inp。

**4 缺失 cell**（均为模拟 IP 块）：
| cell | 引用位置 | 功能推测 |
|---|---|---|
| vintrefampcoreip | netlist:67170 | Vint 参考电压放大器核心 IP |
| vcsldigdrvcmphsyip | netlist:427654 | Vcsl 数字驱动比较器迟滞 IP |
| vblhstbylpowerampotaip | netlist:423044 | Vblh 待机低功耗放大器 OTA IP |
| vcsldldostbyampotaip | netlist:422179 | Vcsl DLDO 待机放大器 OTA IP |

**关键歧义（msg43 核心）**：X 元素语法 `X<inst> <节点1> <节点2> ... <subckt_name> [view_name] [params]` 中，当 `vh` 出现在 subcircuit 名**之后**、参数**之前**时，Finesim 把 vh **优先解析为 view name（view hierarchical / 参考电路视图）**，而非节点名，于是去该 cell 的 vh view 查找，找不到即报「no reference ckt vh」。在用户给的展示行 `XI_SetIDDAmpOIP_71 net021 Out inh_vcc SetIDDAmpOIP vh vout=pvblh` 中 vh 是第 4 个连接节点（SetIDDAmpOIP 的第 4 端口）；而报错行里 vh 紧贴 subcircuit 名之后被当 view name。

**解决方案（3 选）**：
- 方案 A（推荐最快）：把这 4 个 cell 加进 `.option finesim_ignore`（仿真已 ignore 大量同类模拟 IP：VcslStbyAmpIP/VblhGRefAmpVdd1M5IP/RefAmpComCore115VIP 等，这 4 个漏配）
- 方案 B：X 元素用 `PARAMS:` 或 `$` 分隔，明确区分节点名与 view 名
- 方案 C：检查 ADE Switch View List / cell 有无 schematic/symbol view / 是否需 ahdl_include

**PWL 电压源写法（msg1）**：基本 `V<name> <+节点> <->节点> PWL(<t1> <v1> <t2> <v2> ...)`；在 `.SUBCKT` 内接端口或内部节点；末尾加 `R` 重复；`PWL FILE="stimulus.dat"` 从文件读；`TD=2ns` 延迟；时间单调递增，默认秒/伏，可加 ns/ps/us 后缀。

## 合成决策

- **form**: debug-Q&A + how-to → 产出生成式「FineSim block 网表 vh 诊断与处理指南」JSON（14 键）
- **layer**: L1（离线 Python 生成器解析 doc/ 产结构化 JSON，不跑 EDA 工具）
- **case_id**: EDA-Eval-DesignFlow-FinesimVhDiagGuide-001
- **A 档 trace-faithful**：error_log.txt 用 msg2 verbatim 4 条错误；netlist_snippet.txt 用 msg42 verbatim 两行网表；sim_context.txt 用 msg4 仿真路径 + 仿真器 finesim；scenario.txt 用 3 类问题 + 助手诊断要点
- **hidden B cross-input**：合成 yfchen @ hfeg0plg88 / DDR VDD1P2 reference / 3 条错误(不同 cell: vdd1p2refampcoreip/vcorebiasgenotaip/vdd1p2ldostbyotaip, 不同实例/行号) / 不同 netlist snippet(VrefAmpOIP + PWL vrefsrc) / 同 finesim 仿真器
- **判分牙**：16 断言 — error_count/errors/missing_cells/simulator 全部 cross-input（check.py 独立解析 B 的 error_log+sim_context 对账，硬编码 A 必 FAIL）；root_cause/vh_role/pwl_syntax/fix_options 验关键知识点覆盖；A-leak 守卫 13 token；确定性 3 rerun
- **自验**: ref 16/16 PASS + 4 negs(空壳→d / print-only→c / hardcode-A→e cross-input / deleted-core→k)全 FAIL · k_rationale==k_check==16 ✓
