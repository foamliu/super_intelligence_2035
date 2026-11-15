# 深读笔记 · gsmj2 · TSPC_RVT 网表功能分析

- **session**: 1791980431476_gsmj2 (子目录 1791980431476_gsmj2/ 下)
- **user/host**: adaml @ hfeg0pkn002 (10.129.2.11)
- **mc**: 58 · keywords: netlist:160 hspice:132 schematic:109 pdk:41 transistor:31 aether:18 cadence:10 pyaether:9
- **trace**: 53 msgs / 476KB / 1 substantive user turn
- **pool 旧判**: parked "reject analysis 网表功能分析报告" (r435) → r618 reaudit 可造 (analysis Q&A)

## 用户原话
`/proj/m2701/V0_DDR4/workdir/adaml/simulation/TSPC_RVT/hspiceD/schematic/netlist/netlist 读取这个电路网表，给出这个电路的功能分析和原理报告。`

## 助手工具链
1. read_files netlist (37 行, 2 switch subckt + 20 MOS) → 中段截断
2. read_files netlist 24-37 行补读 → 完整网表
3. list_allowed_files 仿真目录 → 只有 schematic netlist + psf(空)
4. read_files input.ckt/.stimulusFile/netlistHeader/amap/*.port/designInfo/.designVariables → .stimulusFile 空, psf 空 ⇒ 单元级原理图网表, 无测试激励
5. read_files amap/hlmc22ull_prvt_ckt_hspiceD.inst + nrvt_ckt .inst + TSPC_RVT.inst/.net → 确认管脚顺序 n1=D n2=G n3=S n4=B
6. editor 写 tspc_switch_sim.py (开关级行为仿真器) → run_approved_command 跑 → 索引 bug → editor 修 → 再跑
7. 5 场景: S1(D=!Q 反馈)=二分频 / S2(D=0)=Q 保持 0 / S3(D=1)=Q 置 1 / S4(RST 复位 17ps 内 Q=0) / S5(CK=3.3GHz 仍二分频)
8. editor 写 TSPC_RVT_report.md 报告 → 最终 msg#52 输出完整报告

## 关键产物 (均在用户 /home/adaml/tspc_sim/ 下, /proj 内网 SUT 沙盒不可达)
- tspc_switch_sim.py: 开关级行为仿真器 (验证功能推导)
- TSPC_RVT_report.md: 功能分析与原理报告

## 一句话结论 (助手)
TSPC_RVT = 20 管、真单相时钟(TSPC)正沿触发 D 触发器, 带异步高有效复位 RST。CK 上升沿采样 D(Q=D); D 接 !Q 反馈时构成二分频器(÷2), 50% 占空比。

## 网表结构事实 (从 trace 工具结果提取, 用于造题 A 档 fixture)
- 库 adaml / 单元 TSPC_RVT / view schematic / hspiceD / 生成 2026-10-14 20:18:53
- 工艺 HLMC 22nm ULL, PDK 子电路 prvt_ckt(P-RVT)/nrvt_ckt(N-RVT), L=30nm
- 管脚顺序 (amap .inst): n1=D(漏) n2=G(栅) n3=S(源) n4=B(衬底)
- 顶层端口: CK / D / RST / Q
- 20 MOS: XPM0-PM11 (10 PMOS prvt_ckt, 缺 PM2/PM7) + XNM0-NM11 (10 NMOS nrvt_ckt, 缺 NM2/NM7)
- 2 个 .subckt 定义: switch_close (R=0.001), switch_open (空) — 均未被顶层实例化 (Cadence 工件)
- 内部节点: net037/net016/net018/net14/net8/net4/net013/net7/net11 (9 个)
- 电源: vcc! / vss! (.GLOBAL)
- .stimulusFile 空, psf 空, .designVariables 空 ⇒ 无测试激励, 单元级原理图

## 造题决策
- **A 档不可行**: 真实 netlist 在 /proj/m2701/V0_DDR4/... 内网工程目录, SUT 沙盒无 /proj 权限不可达 → B 档 synthesized
- **A fixture**: 真实 TSPC_RVT 网表(37 行原文) + ports.txt(CK/D/RST/Q) + cell_meta.txt + amap_pinorder.txt + sim_context.txt
- **Hidden B**: 结构不同的 CMOS 单元 (NAND2 ND2HVT, 4 管, 组合逻辑, 端口 A/B/Y) → cross-input guard (B 的 counts/ports/nets/class 全异于 A) + A-leak guard (B 输出不得含 TSPC_RVT/adaml/net016/switch_close 等 A 专属 token)
- **交付**: tspc_netlist_analyze.py(workdir, out_dir) → 解析 doc/ → 产 tspc_netlist_analyze.json (21 顶层键的结构化分析报告)
- **判分牙**: check.py 独立解析隐藏B fixtures 计算 ground truth (无硬编码 B 值), 18 条独立断言; 硬编码 A 的 stub 在 B 上 FAIL (cell_name/counts/ports/class/A-leak 多重失败)
- **域/层**: spice_sim / L1 (离线 python 解析)
- **case_id**: EDA-Eval-DesignFlow-TspcNetlistAnalyze-001
