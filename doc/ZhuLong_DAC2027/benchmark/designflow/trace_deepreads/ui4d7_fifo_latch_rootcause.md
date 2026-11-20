# trace_deepread · ui4d7 · curryxu @ hfeg0plg99 · mc83 spice_sim

- session_file: `1792544257107_ui4d7.messages.json` (in subdir `1792544257107_ui4d7/`)
- 106 msgs / 1.0 MB / 7 substantive user turns / 51 assistant turns
- 旧判: parked "peek全 diagnostic/consultation(netlist 为何保持高电平),非produce-task,reject" (2026-11-10 r435)
- r618 reaudit: 可造 (debug-Q&A → 根因诊断报告)
- host trace 取法: .75 open_session → `ssh hfeg0plg99` → `scp .../1792544257107_ui4d7/1792544257107_ui4d7.messages.json ./`

## 用户意图（逐 turn 原话）

1. (msg0) "请帮我分析这个电路为什么在RDFI<0>信号拉高之后，net53无法保持高电平，理论上net53应该保持高电平不掉电。仿真激励：...sim_FIFOx1.sp 仿真网表：...netlist"
2. (msg27) "好的，我按照了你的建议更改，之后还是会发现在RDFI<0>信号拉高之后，net53无法保持高电平..."
3. (msg51) "刚才是我搞错了，现在我把输入改成0了，但net53在RDFi<0>来之后仍然无法保持高电平..."
4. (msg59) "RDFi<0>的输入波形在这里.../input，在大约608ns-611ns之间拉低了，所以你重新分析下"
5. (msg87) "OK，现在vccz也定义完成了，但是OUT输出还是有点问题，理论上最后一个inv没导通，OUT不应该根据net53的变化而变化，而且out的初态也有点问题..."
6. (msg95) "麻烦帮忙看下为什么Data节点我在定义了0.9的初态之后，后续会掉电"
7. (msg96) "目前该电路的Data输出有些问题...RdFi<0>的信号源是.../input，RdFO<0>的信号源是.../input1"

→ 真实意图：**对 DDR4 FIFO 输出锁存器 (latrPF01DOutFIFOx1_m2701) 仿真电路做多轮根因诊断**，解释 net53 / OUT / Data / DataN 四个节点的异常行为并给修复建议。零脚本产物，纯分析。

## 电路拓扑（助手从真实 netlist 还原）

顶层 `sim_FIFOx1`（netlist 第82-88行）：
```
XI_latr  net06 RdFi<0> net53 Rst  ... latrPF01DOutFIFOx1_m2701   ← 锁存器(QN=net53)
XI_invFx1_2 ByteSelx net013 ... invFx1                            ← ByteSelx→反相→net013
XI_invFx1_0 RdFO<0>   net08  ... invFx1                           ← RdFO<0>→反相→net08
V0 net06 vss! DC=0 PWL 0 900e-3 900e-9 900e-3                    ← D=0.9V 固定
V27 Rst vss! DC=0 PWL 0 900e-3 100e-9 900e-3 100.06e-9 0         ← Rst 100ns 释放
XI13 net53 net08 RdFO<0> Data ... invenTx1_sub                    ← net53→三态缓冲→Data
XI2  Data  net013 ByteSelx DataN ... invenTx1_sub                 ← Data→三态缓冲→DataN
```
子电路：`latrPF01DOutFIFOx1_m2701` = `fbrPFx2_sub_Fifo`(RS 锁存) + `invhizTx1_Fifo`(三态输入) + `invFx1_sub_Fifo`(反馈/Fin 反相) ×2

激励文件：
- `input`  → `Vrdif<0> rdfi<0> 0 PWL(...)`  定义 RdFi<0>（608-610.36ns 低脉冲，~0.85V 高）
- `input1` → `VByteselx Byteselx 0 PWL(...)` 定义 ByteSelx（~0.85V 恒高）
- pwr.sp / option_finesim.sp / switch.sp 定义电源与选项

## 助手给出的根因（最终诊断 msg105）

| # | 问题 | 根因 | 严重度 |
|---|------|------|--------|
| 1 | **RdFO<0> 未定义** | netlist 用 RdFO<0>（XI_invFx1_0 + XI13 的 EnN）但 input/input1 无 V 源 → 节点浮空 → XI13 使能不确定 → Data 掉电 | 🔴 致命 |
| 2 | **D=0.9V 固定** | invhizTx1 写 QN=NOT(D)=NOT(0.9V)=0 → net53 始终 0，无法保持高 | 🔴 功能错误 |
| 3 | **.ic V(Data)=0** | sim_FIFOx1.sp 第23行强制 Data=0V 与 XI13 驱动 NOT(net53)=0.9V 冲突 → 初始收敛问题 | 🟡 次要 |
| 4 | **DataN 浮空** | XI2 始终 Hi-Z（ByteSelx 恒高→net013=0→XI2 disable）→ 仅 C_DataN=2fF 保持电荷 | 🟡 需确认 |
| 5 | **OUT 跟随 net53**（msg87） | invenTx2_sub 中 XNM0/XPM0 G=net53 D=OUT，即使关断 **Miller 栅-漏交叠电容 Cgd** 把 ΔV(net53) 耦合到 OUT；FinFET 260/340nm Cgd 不可忽略 | 🟡 物理机制 |

### 关键机制解释
- **RS 锁存自锁**：fbrPFx2 A=Fin 反相后路径 + R=Rst 控制下拉/上拉，QN 经反馈反相器 invFx1_sub_Fifo 自锁
- **三态缓冲使能**：invenTx1_sub En=net08 / EnN=RdFO<0>；En=1 & EnN=0 → 使能输出；任一不确定 → Hi-Z 或异常驱动
- **Miller 电容耦合**：ΔV_OUT ≈ [Cgd_XNM0+Cgd_XPM0]/[Cgd_total+C_OUT_total] × ΔV_net53，关断态 MOS 仍有栅-漏交叠电容

### 修复建议
1. 定义 RdFO<0> 信号源（input1 加 `Vrdfo<0> rdfo<0> 0 PWL(0 0 1e-7 0 1.0006e-7 900e-3 9e-7 900e-3)`）
2. D 与 Fin 同步（D 在 Fin 低脉冲期间=0V，使 QN=NOT(0)=0.9V 高）
3. .ic 与驱动方向匹配
4. Data Hi-Z 期加弱保持器防漏电

## 造题决策

- **形态**: debug-Q&A → 根因诊断报告（spice_sim L1 离线 netlist/stimulus 解析器）
- **A 档不可行**: 真实 netlist 在 `/proj/m2701/V0_DDR4/` 内网私有工程目录，SUT 沙盒无 /proj/m2701 访问；且真实激励文件 50000+ 行 PWL 含项目工艺参数 → 用 B 档 synthesized 复刻拓扑
- **B 档合成**: 复用真实子电路名 (latrPF01DOutFIFOx1_m2701 / fbrPFx2_sub_Fifo / invhizTx1_Fifo / invenTx1_sub / invenTx2_sub / invFx1)，节点名/未定义信号/D 极性/.ic 目标在 hidden B 中替换为不同取值（cross-input guard）
- **判分**: check() 跑候选脚本解析 netlist+stimulus → 产 root_cause_diag JSON，验 5 类根因识别 + 机制 + 修复建议 + cross-input guard + 3-seed 确定性（k≥13）
