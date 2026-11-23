# Deepread: 87doj — ddgoa testmode Puds pattern generation (analog_context)

## Trace source
- session: `1794990961329_87doj.messages.json`
- user: nevinrao @ hfeg0pkn004 (10.129.2.13)
- mc=25, keywords: analog:553;cmos:65;pex:17;verilog:11;lvs:4;pyaether:2
- size: 577KB, 54 msgs
- ledger: shard D, claimed r1225

## Real user intent (msg 0, verbatim core)
> 需要验证的是 cm1_io_Spd1600PudsDis，该 testmode 的功能是在 default 且小于 1600Mbps 下，更改 modereg 里 Puds 值，默认为 011 (80 ohm)，这个 testmode 会 disable 掉用 cm 替换 modereg 值的功能。cm=0 且 frequency 小于 1600Mbps 下，更改 modereg 里 Puds 值，默认为 011 (80 ohm)。电路里作用的地方是 MR3。cm=1 的情况下就没有这个功能了。我需要检查在 cm=0/1 情况下，不同 frequency，看 MR3 的 puds 是否改变。相关 pattern 在 /proj/ddgoa/V0/simdir/verilog/qi3wang/verilog.lpddr5.ddgoa.net1015_debug/patterns/proj_function/cmds_testmode/，参考一下给我完整 pattern。

= 用户要求**生成一个完整的 testmode pattern**（Verilog/.v 格式）来验证 cm1_io_Spd1600PudsDis：在 cm=0 & freq<1600Mbps 时改变 MR3 Puds 值（默认 011=80ohm），disable cm-replace-modereg；cm=1 时无此功能。需覆盖 cm=0/1 × 不同 frequency 组合，检查 MR3 Puds 是否改变。

## Agent behavior (research-only, 未交付)
agent 全程 read_files 研究参考 pattern，**未 write_to_file 任何产出**。读取的参考文件（均在 .75 上 /proj/ddgoa/V0/workdir/qi3wang/sos_manage_lpddr5/lpddr5/ddgoa/patterns/proj_function/cmds_testmode/）：
- `TM_parameters.v` — testmode 参数定义（含 MR3/Puds bit 定义，读 line 50-150 与 2130-2150）
- `TM_inc.v` / `tm_common/tm_common.v` / `tm_config/tm_config.v` / `tm_common/TM_exit.v` — testmode 公共框架/包含文件
- `allCMAdr_MAandOP.csv` — MR 命令 MA/OP 表（读 line 583-590 与 2120-2130），含 MR3 write 命令编码
- `cmds_other/TM_Puds.v` — **现有 Puds testmode pattern（关键模板）**
- `cmds_other/TM_other_inc.v` / `cmds_other/TM_DqShift.v` / `cmds_other/TM_EDvfscDis.v` / `cmds_dqshift/TM_DqShift.v` — 其他 testmode pattern 参考（频率/speed 切换 + MR 读取结构）

session 在 agent 仍读 TM_parameters.v 时结束，未生成最终 pattern。

## 可离线判分内核（case 设计草案 · DEBT 下轮合成）
**内核 = 解析 testmode 规格 + MR3 Puds bit 定义 + 现有 TM_Puds.v pattern 结构 → 生成新 testmode .v pattern**

判分对象：生成的 pattern .v 文件（结构化解析，非文本相似）。规格确定性：
- cm=0 & freq<1600Mbps → MR3 Puds 可改（默认 011）；disable cm-replace-modereg
- cm=1 → 无功能（Puds 不改）
- 需覆盖 cm{0,1} × freq{<1600, ≥1600} 组合，检查 MR3 Puds

**A/B 结构性不相交设计（草案）**：
- A：testmode = cm1_io_Spd1600PudsDis，target MR=MR3，Puds default=011(80ohm)，freq 阈值 1600Mbps，cm 维度 {0,1}
- B1：testmode = cm1_io_SpdXXXXPodsDis（不同 MR，如 MR17；Pods default=101；freq 阈值 3200Mbps；cm 维度 {0,1}）
- B2：testmode = 不同 Puds default + 不同 freq 阈值 + cm=1 仍无功能但 freq 边界不同
- token/位宽/MA/OP/阈值全不同 → 结构性不相交

**k_check ≥ 12 草案**（待下轮读 TM_Puds.v + allCMAdr_MAandOP.csv 细化）：
① zip 含 .v pattern 文件 ② B1 exit0 + 非空 ③ pattern 含 testmode 名定义 ④ 含 MR write 命令（MA=target MR） ⑤ cm=0&freq<阈值 分支改 Puds ⑥ cm=1 分支不改 Puds ⑦ Puds default 值正确 ⑧ freq 阈值判断正确 ⑨ 含 freq 切换命令 ⑩ 含 MR 读取/校验命令 ⑪ 三次 md5 一致 ⑫ 反硬编码（无 A-only token）

**§4.9 三假**：empty_shell→①/②；print_only→③/④；core_deleted→⑤/⑥/⑦；hardcode_a→③（A testmode 名≠B）。

## 下轮合成 TODO
1. 读 .75 上 `cmds_other/TM_Puds.v` 全文 + `allCMAdr_MAandOP.csv` MR3 段 + `TM_parameters.v` Puds 定义段，确定 pattern .v 的精确语法（module/include/命令格式）
2. 据此定稿 A/B + k_check 清单 + reference 解
3. 合成 EDA-Eval-DesignFlow-TestmodePudsPatternGen-001（L1 analog_context k≥12）

## 判定
- 真实意图 ✓（produce：生成完整 testmode pattern）
- D 域归属 ✓（analog_context 主导：analog:553，ddgoa testmode/MR/Puds 电路语境）
- 与 r1220-r1224 内核不相交 ✓（本例 = ddgoa testmode pattern 生成 + MR Puds 规格驱动；前例为 SPICE 解析/Verilog 静态例化树/clock 传播/寄存器溯源/总线常量布线，全不相交）
- 本轮只深读，DEBT: 1 deepread 87doj 待合成（spec-driven produce case，参考文件已定位在 .75）
