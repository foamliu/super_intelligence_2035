# Deepread: b2l64 — netlist fault injection produce-task (D 域命中)

- **session**: 1793952138224_b2l64 (t0003117 @ hfeg0pkn003 / 10.129.2.10)
- **scan**: ssh_eda_search_20261113_131349, mc=473, keywords `netlist:4326;transistor:649;schematic:383;hspice:243;virtuoso:140;cellview:117;.def:49;dbopencellviewbytype:11`
- **size**: messages.json 1,636,378 bytes, 292 msgs, NTURNS(user_text)=119
- **ledger**: claimed r618 (shard D, domain schematic_netlist), **未 mark case**（合成留 r619，DEBT:1）
- **r618 状态**: deepread-only 轮（首次，允许；r619 必须先交付本 case）

## 用户意图（trace-faithful）

- **U0**：「帮我把刚抽好的网表运行故障注入程序」
  - 前置：网表已由另一抽网表 skill 抽好（`lwdrx8_2d5T`），故障注入程序 = `skills_v0.2/netlist_extract/fault_inject_V3.py`（FaultInjector 类，4 种故障类型）
- **U23**：「1」→ 选 Open（开路）故障
- **U25**：「断开wl」→ 对 `Wl` net 注入 Open
- **U33**：「我记得手动使用故障注入程序时，开路是可以选择插入的电阻大小的…为什么你直接帮我断开了」→ 确认 Open 可自定义电阻，默认 1e9 Ω
- **U35**：「那能不能把短路可以选择一个很小的电阻吗」→ Short 可选小电阻
- **U43+**：转向「把抽网表 skill + 故障注入做成一个 skill」（SKILL 集成 + 栈溢出调试）—— **此段 infeasible（需 live Virtuoso load()），不进 case**

## 金标准（U0–U30 真实产物）

助理解析 `lwdrx8_2d5T` 网表：
- **20 个晶体管**（13 NMOS + 7 PMOS）
- **25 个 nets**
- 电路 = Wordline Driver 阵列，驱动 8 条字线 `Wl<0>`~`Wl<7>`

注入 Open 故障到 `Wl` net（3 个连接）：
- `MMN13.drain` → NMOS 漏极
- `MMN8.source` → NMOS 源极
- `MMP10.drain` → PMOS 漏极

生成故障网表插入大电阻：
```
R_open_Wl_3__1 Wl Wl_open 1000000000.0
```
（1e9 Ω，等效开路，串入而非完全断开）

FaultInjector 4 种故障类型（来自 fault_inject_V3.py）：
| 类型 | 说明 | 参数 |
|---|---|---|
| Open | 断开某 net 的特定连接，串大电阻（默认 1e9 Ω，可自定义） | net + 连接选择 + resistance |
| Short | 短接两 net，R≈0.001 Ω（可自定义小电阻） | net1 + net2 + resistance |
| Vth Shift | 修改器件 Vth | 器件 + delta |
| Leakage | 加漏电阻 | net + resistance |

## 合成计划（r619 交付）

**case_id**: `EDA-Eval-DesignFlow-NetlistFaultInj-001`（domain schematic_netlist，L1/L2）

**设计**：SUT 产出通用 `fault_inject.py`（SPICE subckt 解析 + 故障注入 + 写故障网表 + report.json）。check.py 在 hidden B 上 subprocess 跑 SUT 脚本，断言输出结构。

- **Asset A (visible)**: `wl_driver.netlist`（合成 lwdrx8_2d5T Wordline Driver，~20 MOS / 25 nets）+ prompt（trace-faithful U0/U23/U25 原话）+ task_brief（≤3 行：交付 fault_inject.py 到 outputs/submit.zip）
- **Hidden B**: `sense_amp.netlist`（不同电路，disjoint）+ Short 故障（net_a↔net_b，R=0.001）+ hidden_manifest.json
- **check.py ≥8 条** (a–n)：
  - a zip 含 fault_inject.py
  - b py_compile fault_inject.py
  - c 无泄漏（不含 reference/check 字样）
  - d CLI --help / --type 支持 open|short|vth|leakage
  - e subprocess 在 B 上跑 `fault_inject.py sense_amp.netlist --type short --net1 <a> --net2 <b> --resistance 0.001 -o out.sp --report out.json`，exit 0
  - f out.sp 含 `R_short_*` 电阻，值=0.001
  - g out.sp 短接的 2 net == B 指定 pair
  - h out.sp 晶体管数 == B 原网表（注入不改器件数）
  - i out.json 含字段 fault_type/target/resistance/connections/original_hash
  - j subckt 名保留
  - k 隐藏 B 交叉：换一个 B' netlist（cross-input），跑 open 故障，电阻 1e9，验证 R_open 存在 + 值
  - l report connections 列表 == 被断开的连接
  - m 随机化：3 seed 随机抽 net 子集，注入结果一致
  - n 只改 target net，其他 net 不变
- **negatives (≥2)**: empty_shell / print_only / hardcode_a（含 A 的预计算输出，过 visible 但败于隐藏 B 交叉 k）→ negative_selftest 全 FAIL
- **test_rationale**: `14 条断言：① zip含fault_inject.py ② py_compile通过 ③ 无reference泄漏 ④ CLI支持4种故障类型 ⑤ B上subprocess退出0 ⑥ out.sp含R_short电阻 ⑦ 短接电阻值=0.001 ⑧ 短接net对==B指定 ⑨ 晶体管数不变 ⑩ report字段齐全 ⑪ subckt名保留 ⑫ 隐藏B'交叉R_open+值1e9 ⑬ connections列表匹配 ⑭ 随机seed一致性`（k_rationale=k_check=14≥8 ✓）

**自验**：ref fault_inject.py 跑 check PASS 14/14 + 3 neg ALL FAIL + §4.9 三假全 FAIL，落 D.jsonl + mark case。

## 域归属判定

- netlist:4326 主导 + 故障注入对 SPICE 网表操作 → **schematic_netlist**（D 域）✓
- 非 waveform（无 waveview/fsdb），非纯 analog（故障注入是网表结构变换）
- r614 发现「mc 排序对 waveform 域误导（qx7gd mc108=开fsdb）」⇒ 本例 b2l64 mc473 netlist:4326 是 **真用户任务复杂度**（netlist 关键词反映真实解析工作量），与 r614 对照 ⇒ **mc 作 ranking signal 域相关**：waveform 域被 assistant 工具 verbosity 撑高，netlist 域反映用户任务

## 命中率更新

D 域累计：r608 1/20 + r610 0/6 + r612 0/14 + r614 0/24 + r617 0/4 + r618 1/4 = **2/72≈2.8%**（上修 r614 的 1/64≈1.6%）
