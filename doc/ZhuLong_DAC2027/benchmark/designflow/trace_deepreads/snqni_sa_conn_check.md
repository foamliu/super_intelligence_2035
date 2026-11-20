# trace_deepread — snqni (SA cell netlist connection-check Q&A)

- session: `1793934795764_snqni`
- user: cong3li @ hfeg0pkn004 = 10.129.2.13
- mc: 21, domain: analog_context
- trace size: 16 msgs / 78711 B
- pool entry: `pool_reaudit_D.tsv` "可造(需源确认)" — 旧判 weak/Q&A not-produce
- ledger: parked r608 (2026-11-13 "circuit-conn-check Q&A (FBCC straping) not produce-task")
  → revived r793 (2026-11-15 mandate revives analysis/Q&A candidates)
- delivered case: **EDA-Eval-DesignFlow-SAConnCheckQA-001** (D.jsonl 454→455)

## U#0 (verbatim, trace msg#1)
> 这是一个bl length976,wl length1024的section级别的testbench，这个电路使用了FBCC架构和straping,帮我检查一下这个电路的连接有没有问题

## Gold (assistant msg#15, the long final answer)

### 关键事实
1. **用户描述的 section 级 FBCC testbench (BL=976, WL=1024, strapping) 在工作区不存在**。agent 用
   `list_allowed_files` + `search_codebase` 排查整个 `agentdir`，关键词 `FBCC`/`strap`/`976`/`1024`
   全部未命中。
2. 工作区 `/ai_sandbox/drexp/V0/agentdir/cong3li` 实际只有 **一个 SA (sense amplifier) cell** 的
   相关文件：
   - `sa_netlist.sp` — DRAM latch-type bitline sense amplifier cell 的 authoritative SPICE 网表
     (pins: BLT BLC SAP SAN CSB DLT DLC; 6 MOSFET)
   - `build_sa_schematic.py` — pyAether 原理图构建脚本
   - `check_syntax.py` / `find_agent.py` / `find_bridge.py` — 工具脚本
3. agent 如实报告文件不存在，然后对手头唯一的 `sa_netlist.sp` 做连接检查。

### sa_netlist.sp 连接检查结论 (gold)
4 端 MOS 语法 `M nd ng ns nb model`，逐行核对：

| 器件 | 语句 | D | G | S | B | 判定 |
|---|---|---|---|---|---|---|
| MP1 | `MP1 BLT BLC SAP SAP pch` | BLT | BLC | SAP | SAP | ✓ |
| MP2 | `MP2 BLC BLT SAP SAP pch` | BLC | BLT | SAP | SAP | ✓ PMOS 交叉耦合正确 |
| MN1 | `MN1 BLT BLC SAN SAN nch` | BLT | BLC | SAN | SAN | ✓ |
| MN2 | `MN2 BLC BLT SAN SAN nch` | BLC | BLT | SAN | SAN | ✓ NMOS 交叉耦合正确 |
| MN3 | `MN3 DLT CSB BLT BLT nch` | DLT | CSB | BLT | BLT | ✓ 列选通 DLT↔BLT |
| MN4 | `MN4 DLC CSB BLC BLC nch` | DLC | CSB | BLC | BLC | ✓ 列选通 DLC↔BLC |

- `.SUBCKT SA BLT BLC SAP SAN CSB DLT DLC` 与文件头注释 pin 顺序一致 ✓
- 交叉耦合：MP1 栅接 BLC、MP2 栅接 BLT；MN1 栅接 BLC、MN2 栅接 BLT —— "对侧栅、同侧漏"，锁存型 SA 正确接法 ✓
- 列选 MN3/MN4 双向 DLT/DLC 接 BLT/BLC，栅由低有效 CSB 控制 ✓
- **设计提示（非接线错误）**：MN1/MN2 的 bulk 直接打 SAN（接开关管源极/开关电源轨），
  PMOS 侧 SAP 与 NMOS 侧 SAN 都是"浮动主体接开关轨"。高灵敏度 SA 里通常允许（三阱内 body 跟源），
  但应评估 body 电压随开关浮动对噪声裕量的影响。

### build_sa_schematic.py 原理图连线 (潜在问题)
- SAP 没有真正连到 PMOS 锁存源极（rail 只画到 SAP pin 即止，MP1/MP2 源极悬空）。
- 交叉耦合走线在 y=8.9 / y=2.9 同一横线往返，疑似把差分位线 BLT/BLC 物理短到同一 net。
- 需结合 PDK 实际 pin 位置在 Aether 里实地跑一遍才能定论。

## case 构造决策

trace 的真实资产是 **sa_netlist.sp**（DRAM SA cell），不是用户描述的 FBCC section testbench。
这个 mismatch 是 trace 的真实形态，予以保留：asset A = sa_netlist.sp（gold = 连接自洽正确）。

hidden B = identifier-renamed 变体 + 1 处蓄意连接缺陷：
- 重命名：SA→SAMP, BLT→BLP, BLC→BLN, SAP→VPSE, SAN→VNSE, CSB→CSL, DLT→DOP, DLC→DON,
  MP→PFET, MN→NFET, pch→pmos_m, nch→nmos_m（零标识符与 A 重叠，W/L/M 几何参数保留）
- 植入缺陷：PFET2 = `PFET2 BLN BLN VPSE VPSE pmos_m`（栅自连漏极 BLN，破坏 PMOS 交叉耦合；
  A 的 MP2 = `MP2 BLC BLT SAP SAP` 正确交叉耦合）
- candidate.py 须检测为 self_tied_gate@PFET2

## candidate.py 设计
通用 SPICE 网表连接检查器（无硬编码标识符）：
- `find_netlist` — glob *.sp/*.cir/*.spi + fallback 扫 .SUBCKT
- `parse_netlist` — 解析 .SUBCKT 头 + MOSFET 例化行（按 model 名或 M-前缀判定 MOSFET，
  兼容 A 的 MP1/MN1 标准 SPICE 与 B 的 PFET1/NFET1 非标准命名）
- `detect_issues` — 对共享源极的 PMOS/NMOS 对检查交叉耦合：栅==自漏 → self_tied_gate；
  栅!=对侧漏 → cross_couple_mismatch
- `extract_cited_identifiers` — 从 question + subckt 名/pin + device 名/net 收集标识符
- 输出 5 顶层键 JSON

## check.py 13 断言 (a-m)
a zip含candidate.py / b py_compile / c 5必需键+合法JSON /
d subckts含SAMP / e num_devices==6 / f PMOS==2&NMOS==4 /
g connection_issues非空 / h 缺陷定位PFET2 /
i cited_identifiers含≥3个B引脚 / j assessment不声称无问题 /
k anti-hardcode(16个A-only forbidden token零泄漏) /
l B-grounding(含≥1个B-only token) / m 3-run md5一致

## 自验
- ref PASS (13/13)
- 5 negatives 全 FAIL，distinct labels: empty_zip→a / print_only→c / core_deleted→d /
  hardcode_a→k / naive_no_bug→g
- §4.9 三退化 (empty-zip/print-only/core-deleted) 全 FAIL ✓
- candidate on A → A-grounded (16/16 A-tokens, 0 B-leak, subckt=SA, 0 issues)
- candidate on B → B-grounded (16/16 B-tokens, 0 A-leak, subckt=SAMP, 1 issue@PFET2)
- A≠B → 非 canned ✓
- 3-run deterministic ✓
- k_rationale == k_check == 13 ≥ 8 GATE PASS ✓

## 覆盖率
D shard case 440→441
