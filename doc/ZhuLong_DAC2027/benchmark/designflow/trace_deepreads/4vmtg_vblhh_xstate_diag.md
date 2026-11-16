# Deepread — 4vmtg: vblhh X态根因诊断 (netlist-grounded debug Q&A)

**Session**: `1789984306992_4vmtg` | **User**: bin1y | **Host**: hfeg0pkn002 (10.129.2.11)
**mc**: 8574 (total), 199 (per-host 11/09 snapshot) | **Domain**: schematic_netlist
**Agent**: lead | **NMSG**: 109 (40 assistant) | **User_input turns**: 1 (clean single-intent)
**旧判定**: parked "netlist/LVS/HCELL analysis+debug Q&A ... not a single-turn produce-task"
**11-15 revival**: ✅ 复活 — 真实用户意图=debug Q&A「为什么 vblhh 一直 X 态」，单轮闭环可造，gold=结构化根因诊断（事实断言，可 falsify）

---

## 1. 用户原话（A档 verbatim，唯一 propose-need 轮）

**U#5 (msg#5)**:
> `/proj/drgqx/V0/simdir/verilog/bin1y/verilog.ddr5.drgqx.1101_dbr/debug_tt1106/netlist 分析一下这个网表文件，为什么vblhh的电压一直为x态`

= "analyze this netlist file, why is vblhh's voltage always in X state"

模式：netlist-grounded signal-X-state root-cause diagnosis Q&A（信号悬空诊断）。
旧规则判 "analysis not produce" → 11-15 令复活为合法 debug-Q&A 子型（D 域第 7 子型，承 r785 LvsPrfLogicDiag pattern）。

## 2. 金标准（assistant 最终诊断，msg 末轮，2762 字符）

**根本原因**: `vblhh` 一直为 X 不是 netlist 内部逻辑错误，而是 **`+define+LocalPower` + `+define+MOVE` 配置下，电源 pin `inh_vblhh` 两头都没有驱动** → 悬空成 X。

**证据链（3 条，全部结构化、可程序化检测）**:

### 证据 1 — xun.log 激活的 defines
`checkin_0.x16_9200/xun.log` 第 47-48 行:
```
+define+MOVE
+define+LocalPower
```
→ 本次 debug 同时激活了 `MOVE` 和 `LocalPower` 两个宏。

### 证据 2 — top.sv: inh_vblhh 的 TB 侧连接只在 `ifndef LocalPower` 分支
`top.sv`（芯片例化 `WOWTOP Chip (...)`）第 119-141 行:
```verilog
`ifndef LocalPower
//added by biny
.inh_vblhh    (Share_pin_if.VDD),
.inh_vblhbk   (Share_pin_if.VDD),//local power
.inh_vblen    (Share_pin_if.VSS),
.inh_vdleq    (Share_pin_if.VDD),
.inh_vblhm    (Share_pin_if.VDD),
`endif
.inh_vdll     (Share_pin_if.VDD),
...
.inh_vblh     (Share_pin_if.VDD),   // ← vblh（单 h）无条件接 VDD
.inh_vap2     (Share_pin_if.VDD),
...
```

| 引脚 | 连接条件 | 本例结果（LocalPower=1）|
|---|---|---|
| `.inh_vblh`（单 h） | 无条件接 VDD | ✅ 有 VDD |
| `.inh_vblhh`（双 h） | 只在 `!LocalPower` 时接 VDD | ❌ **悬空** |
| `.inh_vblhbk` / `.inh_vblen` / `.inh_vdleq` / `.inh_vblhm` | 只在 `!LocalPower` | ❌ 悬空 |

→ 解释了为什么**只有 vblhh 是 X**（而非所有电源都 X）：电源被刻意分成「外部供电」(无条件) 和「本地供电」(只在 !LocalPower) 两组，vblhh 属于后者。

### 证据 3 — netlist: LocalPower 的内部驱动（Ary32G 阵列）被移除
`LocalPower` 语义 = 这些电源不靠 TB 强制，靠 chip 内部电压发生器自己产生（对应模拟阵列 `Ary32G` 里的 AG_* 电压产生电路）。

但本次是 `MOVE` 模式:
- `top.sv` 第 9-19 行在 `MOVE` 定义下**不 include 阵列网表**:
  ```verilog
  `include "netlist"
  `ifndef MOVE
      `ifndef NOARRAY
          `include "array_netlist.v"     // MOVE 时被跳过
          `include "wow_hybrid_connect.v"
  ```
- `WOWTOP` 网表本体里，`Ary32G Iatop` 阵列例化整段被注释掉（netlist 第 733243-733706 行，用 `/* ... */` 包起来），改用 `alias` 把 DQ pad 直连绕过阵列（第 733707-733724 行）。

→ 内部电压发生器（Ary32G AG_*）缺席 + TB 侧 `ifndef LocalPower` 不接 → `inh_vblhh` 两头无驱动 → `vblhh = X`。

## 3. 资产可达性

- 原 netlist `/proj/drgqx/V0/simdir/verilog/bin1y/verilog.ddr5.drgqx.1101_dbr/debug_tt1106/netlist` 跨用户权限未知（bin1y 同组，可能可达，但 netlist 733724 行巨大）。
- top.sv / xun.log 同目录。
- **造题策略 (synth_deck 模式, 承 r785)**: 不需要全量 netlist，只需 3 段结构化节选重建 asset A:
  1. `defines_A.txt` — xun.log 的 +define 行（MOVE, LocalPower）
  2. `top_sv_A.excerpt` — WOWTOP Chip 例化的电源 pin 连接块（含 `ifndef LocalPower` 条件 + 无条件 .inh_vblh 对照）
  3. `netlist_status_A.txt` — Ary32G Iatop 注释状态（present/commented）+ alias 旁路状态 + array_netlist.v include 条件
- 全部可从 trace read_files tool_results + gold answer 引用的行号重建（gold 已逐字引用 top.sv 119-141 / xun.log 47-48 / netlist 733243-733724）。

## 4. 拟造任务形态（套 #254 v2 code-grounded debug-diagnosis，承 r785）

**Case ID (拟)**: EDA-Eval-DesignFlow-VblhhXStateDiagQA-001
**Domain**: schematic_netlist | **Mode**: design_flow | **A档**: verbatim U#5
**candidate.py CLI**: `python3 candidate.py <asset_dir>`
- 读 defines 文件 → active_defines[]
- 读 top.sv 节选 → 解析 `.pin (net)` 行，识别 `ifndef/endif` 条件块，分类 power_pin_connections[{pin, net, condition}]
- 读 netlist_status → array_instance_status (present/commented/aliased)
- 综合诊断: floating_pins[] = pins whose condition excludes them under active_defines AND internal driver absent
- 输出 JSON: {active_defines, power_pin_connections, array_instance_status, floating_pins, root_cause_signal, diagnosis_summary, cited_identifiers}

**hidden B (结构相反变体)**: 不同的 power pin 名（如 `inh_vdwl` 双写 `inh_vdwll`）、不同的 defines 组合（如 `NOARRAY` 替代 `MOVE`）、array present 但 AG_* driver 缺失、root_cause_signal=vdwll。与 A 零标识符重叠。

**check.py 12 断言 a-l (拟)**:
- ① zip 含 candidate.py ② py_compile ③ 必需顶层键 ④ active_defines 含 B 的两个 define ⑤ power_pin_connections 非空 ⑥ floating_pins 含 B 的 root_cause pin ⑦ 该 pin 的 condition 为 `ifndef <B_define>` ⑧ array_instance_status=commented/absent ⑨ root_cause_signal==B 的信号名 ⑩ diagnosis 指出"两头无驱动/悬空" ⑪ anti-hardcode 不泄 A 标识符(vblhh/inh_vblhh/inh_vblh/LocalPower/MOVE/Ary32G/Share_pin_if/WOWTOP) ⑫ 3-run md5 确定性

**negative samples (拟, ≥4)**: empty_zip / print_only / core_deleted(无 floating_pins 检测) / hardcode_a(硬编 A 的 vblhh) / naive_array_present(误报 array 存在)

## 5. 风险与可行性

- ✅ gold 是结构化事实断言（哪条 pin 在哪个 ifdef、array 是否注释、哪些 define 激活），全部可程序化检测，非散文。
- ✅ 单用户轮、单意图、闭环诊断 → 符合 design_flow 单轮契约。
- ⚠️ 多文件节选（defines + top.sv + netlist_status）→ candidate.py 需解析 3 类输入，比 r785 的单文件 1prf.py+lvs.rep 略复杂，但模式相同。
- ⚠️ hidden B 需精心构造相反结构（array present 但 driver 缺失 / 不同 ifdef 条件），确保 check 有牙且 candidate 不能 canned。
- **结论**: 可造，质量高（mc=8574，真实 DRAM netlist debug，gold 诊断精确）。本轮因时间预算（r796 已用 ~24min 探索 eo84n 跨 shard 碰撞 + godra spef-workflow 排查 + 4vmtg 深读）未合成，DEBT:1 → r797 第一件事合成。

## 6. 本轮探索链（r796 revival 候选排查记录）

1. **eo84n** (xdwang@hfeg0pkn005, mc=413, "count inverters in schematic") — 完整深读 + 21 实例清单 + gold=3 inverters (I92/I7/I9 invLVx1)。**跨 shard 碰撞**: C 已用同 session 造 `EDA-Eval-DesignFlow-NetlistSchBuilder-001`（U#4/U#5/U#6 建图任务），trace_source session_file 相同 → 按 4-shard 去重纪律放弃，不造竞争 case。
2. **godra** (williang@hfeg0pkn002, mc=76) — parked 旧注 "find RCPC cells" 误导；实际 U#0="跑 spef check"，是 skill-driven workflow（spef-check pipeline + log 分析），非干净单轮 falsifiable Q&A → 放弃。
3. **i6kg9** (t0002607@hfeg0plg98, mc=288, "circuit-reading Q&A 512X8M4B2 spec verify") — 11/16 快照未含此 session，ssh 10.129.8.230 未找到 session 文件 → 素材不可达，放弃。
4. **4vmtg** (bin1y@hfeg0pkn002, mc=8574) — ✅ 选定，本 deepread。

## 7. ledger 状态

- 4vmtg 在 D 台账为 parked（line 675），claim 被 refused（parked 不可 re-claim）。
- r797 合成落库后用 `mark --session 1789984306992_4vmtg --status case --case-id EDA-Eval-DesignFlow-VblhhXStateDiagQA-001` 结算（覆盖率分子）。
