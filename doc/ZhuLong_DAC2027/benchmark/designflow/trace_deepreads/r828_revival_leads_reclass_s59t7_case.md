# r828 — NOFILE-parked revival 第四矿脉深读：3 高 mc leads 全跨域 + s59t7 造题兑现

> 类型：造题 1 case（ZtypeWaveCompareProduce-001, verification, B档, k=12/12）+ 治理（3 revival leads 域重判）
> 日期：2026-11-20
> eda_flow session r828

## 一、r827 第四矿脉 3 高 mc A-revival leads 深读 → 全跨域

r827 code-fix `revive-nofile` 解锁第四矿脉，实测 3 条高 mc A 域 lead subdir-ALIVE。
本轮逐条 fetch + 读首用户意图 + 看 assistant 工具链，**三条全是 scan 关键词误判的跨域**：

| slug | user@host | mc | size | r827 判定 | r828 深读真实意图 | 真域 | 跨 shard 状态 |
|:--|:--|--:|--:|:--|:--|:--|:--|
| yicdk | hengbow@10.129.8.226 | 120 | 482KB | A lead | finesim/primesim fullchip SPICE 仿真流程分析 + custom pattern | **B spice_sim** | B 11-11 parked「trivial 1msg」= flat-path NOFILE 误读，应复活给 B |
| g8en5 | jinsongl@10.129.2.14 | 73 | 1.1MB | A lead | cck 电路连通性遍历 Tcl 函数 (cckSearchInst/cckExplore, tdv/IND/RES/CAP/mos) | **D schematic_netlist** | B 11-11 parked「raw SKILL log」= NOFILE 误读，应给 D |
| zg7xg | jinsongl@10.129.2.14 | 65 | 817KB | A lead | ERC marker (schMark/voltMark) 传播 + power rail (VHV/SUV/SVP) | **C physical_verify** | B parked「wrong-shard ERC」正确，应给 C |

**根因**：scan 关键词「verilog/dbget dominant」不可靠 —— verilog 出现在 spice sim vector 里，dbget 是通用 EDA 命令。mc（关键词命中数）与 session 丰富度/真实域均弱相关。**域判定必须读首用户意图 + assistant 工具链，不能靠 scan kw。**

**处置**：A 不造（守任务初衷不强用跨域凑 A）。A 台账 3 行 --force 更新 parked note（subdir-ALIVE + 真域 + defer to B/D/C）。未碰 B/C/D 台账。已在 discuss/A.md r828 通报 B/C/D 复活。

## 二、8 条低 mc5-7 A-recoverable 批量 subdir 探测 → 8/9 ALIVE

r827 dismissed 为「低 mc5-7 薄料」的剩余 9 条 A-recoverable，本轮批量 subdir 探测：

| slug | user@host | mc | subdir size | 判定 |
|:--|:--|--:|--:|:--|
| 9scu4 | e0045128@10.129.2.14 | 27 | 23724 | ALIVE (11-14 已判 trivial synthesis:3 pyAether only) |
| 1y66j | e0041392@10.129.2.12 | 6 | 232337 | ALIVE — workspace 平台配置 Q&A (weak) |
| **s59t7** | rongjiez@10.129.2.14 | 7 | **563204** | **ALIVE — 波形对比 Perl 脚本, verification 域, 造题！** |
| uhla7 | e0025730@10.129.8.86 | 5 | 64698 | ALIVE (待评) |
| dqi7d | liyingw@172.16.8.14 | 5 | 62615 | ALIVE (r803 rotation-NOFILE 是 flat-path 误判) |
| otgh9 | e0045488@10.129.2.13 | 5 | 135836 | ALIVE (同上) |
| r44l7 | vendor.cno.chjh07@10.129.2.11 | 5 | 355678 | ALIVE — Python web app (非 EDA, IT 工具) |
| 5fn4e | e0047722@10.129.8.125 | 5 | NOFILE | 真蒸发 |
| gucnl | e02141@10.129.2.14 | 6 | 63273 | ALIVE (待评) |

**8/9 subdir-ALIVE** —— 印证 r803「rotation-NOFILE」大多也是 flat-path 假阴性。
其中 s59t7 是 verification 域真料 → 本轮造题。

## 三、造题：ZtypeWaveCompareProduce-001（s59t7 兑现）

s59t7 (rongjiez@10.129.2.14, mc7, 563KB/35msgs/lead):
- UT#0: compare_wave.pl → compare_wave_new.pl 重构丢失全-Z exp 信号处理（chkTypeJumpFromFSDB 检测 fsdb 10ns 后跳转 + writeZtypeSigReport），要求加回（parallel_compare，不 shift 只检测 a2d 跳转，不考虑 seg_on）
- UT#2: filterSkipSigs dqs_t 全 Z/X 直接 error_exit 过激，改为「只要有一个好 dqs_t 就不报 error」
- 用户明确「建议和代码，不要直接改文件」

**§5 produce-task reframe**：依赖真实 FSDB 二进制 + fork 子进程的逻辑无法 headless 判分。reframe 为自包含 Perl 脚本 `ztype_compare.pl`，`.vec` 改文本格式（`<时间秒> <值>`），保留原始语义（10ns 阈值含等号、全-Z/X 判定、dqs_t 两遍过滤「存在好者则 skip 坏者」）。

- **资产 A**（可见）：sig_config_A (4 信号) + debug_dir_A/*.vec
- **隐藏 B**（不进 SUT）：sig_config_B + debug_dir_B (不同信号名 + 末行时间 8e-9/25e-9/空) + 3 场景 (dqst_allbad / dqst_mixed / boundary 10e-9)
- **check 12 条独立断言**（真跑 perl on B）：编译/exit/ztype Matched·Mismatched/Shift Time NA/空 vec 边界/普通 Compared/dqs_t 三场景/10e-9 阈值含等号/块结构完整
- **自验**：ref PASS 12/12 + 3 neg (empty/print_only/core_del 删 chkTypeJumpFromFSDB) 全 FAIL 命中不同断言组 (empty→③, print_only→③④, core_del→④⑪)
- A.jsonl 414→415. ledger mark s59t7→case.

## 四、纪律

- 🚫 未改题/图/check；🚫 未碰他 shard jsonl/MEMORY/台账（A 台账 --force 仅改 A 自己的 3 行 parked note）
- ✅ trace 溯源：s59t7 真实 trace, real_task_summary 含用户原话
- ✅ 隐藏 B 与 A 信号名/数/取值/场景全异
- ✅ k_check == k_rationale == 12 ≥ 8
- eda_flow session r828 待 close
