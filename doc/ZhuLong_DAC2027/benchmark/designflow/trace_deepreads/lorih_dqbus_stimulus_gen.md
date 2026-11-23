# trace_deepread: lorih — DQByte D<15:0> 网表层次解析 + inc_stimulus.sp 激励生成

- session: `1794913542002_lorih` (dir `1794913542002_lorih/`)
- user: reedchen  host: hfeg0pkn002 (10.129.2.11)  mc=88 (scan 20261123_064315)
- domain: schematic_netlist（D 域）· keywords: netlist:334;cmos:318;schematic:209;analog:11;aether:7
- 88 msgs (39 user / 49 assistant), 1.78MB messages.json
- agent: lead (带 ask-eda / list_allowed_files / read_files / editor / run_approved_command)

## 文件路径修正（重要 · 供后续轮次复用）
- cline session 存储为**目录**：`/home/<user>/.cline/data/sessions/<slug>/<slug>.messages.json`（不是直接的 `.messages.json` 文件）。
- r1198 fresh_D_pure 池里所有候选此前用旧路径 `sessions/<slug>.messages.json` 全判 MISSING 是**路径 bug**，非文件清理。修正后 12/12 候选文件均在。
- 本轮已确认 lorih 文件存在（scp 到 .75:/tmp/lorih.json，1.78MB）。

## 2 个 user turn（真实意图流）

1. (U0@0) 用户 reedchen 有 SPICE 网表 `/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_top_ChannelLeft_sim/netlist`，想先编写一套 Dbus 激励。给出示例 VDbus2_5 / VDbus2_6 ... PAT('pvcc' 0 5ns 70p 70p 'tCCD' b001010...111 RB=1 R=-1) 格式，要求按此 PAT 模板为 DbusEvRd 信号生成激励写入 inc_stimulus.sp。agent 读网表 + editor 写 inc_stimulus.sp + run_approved_command 校验。
2. (U1@56) **核心 produce 任务**：「找到 DQbyte 模块里，链接所有 DDbusDrv0-7_rev0 模块的 D<15:0> 的所有 net 的真实 path，比如 XI_DQByteLo.net305<0-15>，然后继续在 inc_stimulus.sp 给这些信号给予 pvcc 的初始值激励」。

## agent 交付（最终 assistant 文本 + tool 链）

agent 用 editor 写解析脚本 + run_approved_command 跑网表 grep/awk，定位：
- top 实例 `XI_DQByteLo`（DQByte subckt 的 top-level instance，可直接寻址）
- DQByte 内 8 个 `DqDbusDrv_{0..7}_rev0` subckt 实例：XI224/XI212/XI213/XI214/XI219/XI220/XI221/XI222
- 每个驱动器的 `D<15:0>` 输入端口连到 DQByte-scope net：`net305/net310/net317/net324/net336/net343/net350/net357<0..15>`
- 真实 path 表（8×16=128）：

| driver | instance | D<15:0> real path |
|---|---|---|
| 0 | XI224 | XI_DQByteLo.net305<0..15> |
| 1 | XI212 | XI_DQByteLo.net310<0..15> |
| 2 | XI213 | XI_DQByteLo.net317<0..15> |
| 3 | XI214 | XI_DQByteLo.net324<0..15> |
| 4 | XI219 | XI_DQByteLo.net336<0..15> |
| 5 | XI220 | XI_DQByteLo.net343<0..15> |
| 6 | XI221 | XI_DQByteLo.net350<0..15> |
| 7 | XI222 | XI_DQByteLo.net357<0..15> |

- 在 inc_stimulus.sp 追加 128 行（8 drivers × 16 bits），每行把 write-data 输入绑到 pvcc：
  `Vdqdrv{0-7}_{0-15}		XI_DQByteLo.net{XXX}<{bit}>		0 dc=pvcc`
- 最终 inc_stimulus.sp 287 行。验证：每个 net path 都对得上 DqDbusDrv_* subckt 端口顺序（bit order: netXXX<15>→D<15> … netXXX<0>→D<0>）。

## 可离线判分内核抽取（下一轮合成 case 用）

**kernel = SPICE 网表层次解析 + 端口-net 解析 + 激励生成**

输入：SPICE 网表（含 subckt 层次：top → DQByte 实例 XI_DQByteLo → 8 × DqDbusDrv_*_rev0 subckt 实例，每个有 D<15:0> 输入端口连到 DQByte-scope bus net netXXX<0..15>）+ 目标（DQByte 模块里 DDbusDrv0-7_rev0 的 D<15:0> 真实 path + pvcc 初始激励）。

处理：
1. 解析 `.SUBCKT` 端口表（含 bus 端口 D<15:0>）；
2. 解析实例化语句 `X<inst> ... <master_subckt>`，建立 inst→master + 端口连接（实例化参数表 .PORT(SIG) 顺序对 subckt 端口表）；
3. 对目标 subckt 类型 `DqDbusDrv_*_rev0`（glob `*Drv*rev0` 或精确名）在目标父实例 `XI_DQByteLo` 下枚举全部子实例；
4. 取每个子实例的 `D<15:0>` 端口连接到的父作用域 net 名（bus net netXXX<0..15>），拼层次 path `XI_DQByteLo.netXXX<{bit}>`；
5. 生成激励：`Vdqdrv{drv}_{bit}\t\t<hier_path>\t\t0 dc=pvcc`，共 8×16=128 行。

输出：inc_stimulus.sp 片段（128 行 V 语句）+ path 表 JSON。

**与已有 case 不相交**：r1208 AsyncRiskResetWaiveGen 是门级网表引脚-信号解析+复位过滤+waive 生成；r1210 SchemDesInvProduce 是 SPICE subckt 网表→设计清单（inst/net/terminal/bus 展开）；本 case 是**网表层次 path 解析 + 总线 bit 展开 + dc 激励生成**，kernel（path 拼接 + bus bit 展开成 128 条 V 语句）与两者结构性不同。

**hidden B 设计**：B 用不同 top 实例名/不同 DqDbusDrv master 名/不同 net 编号/不同 bus 位宽（如 D<7:0>，4 个驱动器 → 32 行），与 A 在名称/规模/位宽上全不相交，anti-hardcode-A 断言 B 输出 path 与 A 全不相交。

**k_check 草案（≥8）**：① zip 含 .py ② B exit0 ③ 生成 .sp ④ B 驱动器数==Bgt（反 A=8）⑤ B 总 bit 行数==drv×width（反 A=128）⑥ B 每行 V 语句格式（Vname <path> 0 dc=pvcc）⑦ B path 集合匹配 Bgt（层次名+bit）⑧ B path 父实例==B 的 DQByte 实例名（反 A=XI_DQByteLo）⑨ B bus bit 范围正确展开（B width 反 A=16）⑩ 确定性 3 次 md5 一致 ⑪ anti-hardcode-A B path/net 名与 A 全不相交 ⑫ B path 中 net 编号集合匹配 Bgt（反硬编码 A 的 305/310/...）。

## 状态
- **本轮只深读，case 合成留下一轮**（DEBT）。理由：本轮时间预算消耗在候选筛选——r1198 fresh_D_pure 池因路径 bug 全判 stale，重定位 + 多轮 scp/peek 后确认 tuh6e(w0hwk)/onepv 仿真流依赖、unz6r 与 r1208 ezpe5 重复、xr13e 单问 Q&A，最终 lorih 命中。lorih 88msgs/1.78MB 不算超大，但剩余预算不足以走完 assets/reference/hidden/negative/self-verify 全流程；按 §3 质量闸门「未过闸门的 case 一律标 incomplete 不入库」，宁留 DEBT 不出半成品。
- 下一轮直接用本笔记合成 `EDA-Eval-DesignFlow-DqBusStimulusGen-001`（L1 schematic_netlist，目标 k≥12）。
