# r1111 deepread — vyxnz (chuanqiz@hfeg0pnd001, mc75, characterization)

## Trace source
- user: chuanqiz
- host: hfeg0pnd001
- session_file: 1795003637713_vyxnz.messages.json
- match_count: 75 (analog:378;netlist:198;transistor:29;cmos:16;pex:15;hspice:10;verilog:8;synopsys:6)
- session_msgs: 50

## User intent (real task summary)
chuanqiz 在 SiliconSmart (SiS V-2023.12-SP5) 特征化运行树
`/rundata/dejoa/V0/simdir/char/sfeng/tt_25_0p9_compress/sisregular/` 下工作。
三连问：
1. 「理解所有 instance 文件与 configure.tcl，告诉我如何编写」
2. 「解析 analogIP/control/CustomDlyNcCtrlIP.inst 每行的含义」
3. 「add_pin Out pwrgt_type -output — pin type 是 pwrgt_type 是如何确定的？」
4. 「add_pin In — pin type 是如何确定的？」

核心真实意图 = **给定 DSPF RC 网表 + configure.tcl pintype 定义 + .inst add_pin 列表，
判定每个 pin 的 pintype 应该是什么，并给出网表证据（驱动管/接收管 + 源轨）**。

## 关键产物（assistant 构造的脚本与逻辑）
assistant 写 `/home/chuanqiz/scan_out_net.py`：
1. 解析 DSPF `.spf_RC`：找 `*|NET <name>` 块，块内 `*|I (<inst>:<TERM> <inst> <TERM> ...)` 行
   给出每个实例端子连到哪条 net。
2. **输出 pin 判定**：在 pin 的 NET 块里找 `:DRN` 端子 = 驱动管；查该管的 `:SRC` 在哪条 net。
   - PMOS 源所在 net = logic_high 参考轨
   - NMOS 源所在 net = logic_low 参考轨
3. **输入 pin 判定**：在 pin 的 NET 块里找 `:GATE` 端子 = 接收管；挑代表级（直接采样反相器），
   查其 `:SRC`。
4. 对照 `configure.tcl` 的 `pintype <name> -> <parent> { set logic_high_name <rail>; set logic_low_name <rail> }`：
   - high=vcc, low=vss → default
   - high=vcc, low=vssz → gndgt_type
   - high=vccz, low=vss → pwrgt_type
   - 加 `slow_` 前缀 = slew 范围修饰（50ps~50ns），非电压域
5. 输出结论 + 证据。

## 实测证据（trace msg 42/48）
CustomDlyNcCtrlIP cell（电源/地门控延迟链，gated 域 vccz/vssz）：
- pin `Out` (output): 驱动级 XI36.XIinv_0
  - MMP0:SRC → vccz, MMN0:SRC → vss → pwrgt_type
- pin `OutN` (output): 前驱 XI10.XI1
  - MMP1:SRC → vcc, MMN2:SRC → vssz → gndgt_type
- pin `In` (input): 接收级 XI13.XIinv_0
  - MMP0:SRC → vcc, MMN0:SRC → vssz → gndgt_type (slow_ 前缀因延迟链慢信号)

## configure.tcl pintype 定义（trace msg 49 还原）
```tcl
pintype default { set logic_high_name vcc; set logic_low_name vss }
pintype gndgt_type -> default { set logic_low_name vssz }
pintype pwrgt_type -> default { set logic_high_name vccz }
pintype slow_gndgt_type -> gndgt_type {
    set smallest_slew 50e-12
    set largest_slew  50e-9
}
pintype slow_pwrgt_type -> pwrgt_type {
    set smallest_slew 50e-12
    set largest_slew  50e-9
}
```

## Reframe（合成 case 的 spec）
**case = EDA-Eval-DesignFlow-SisPintypeResolveProduce-001**
- 输入：DSPF RC 网表片段（`*|NET`/`*|I`/`*|P` 行）+ configure.tcl（pintype 定义）+ pins.json（待判定 pin + direction）
- 输出：JSON，每 pin 给 {pin, direction, pintype, logic_high_rail, logic_low_rail, evidence:{driver_or_receiver_inst, pmos_src_net, nmos_src_net}}
- L1 纯 Python 解析（无 EDA 工具依赖），spec 驱动
- A = CustomDlyNcCtrlIP 真实结构采样（In/Out/OutN 三 pin，vcc/vss/vccz/vssz 域）
- hidden B = 另一 cell 结构：不同 pin 名、不同 rail 组合（含 default 全常规域 + 双 gated 域混合）、不同驱动/接收实例名、不同 net 块布局

## check.py 闸门设计（≥8 独立条件）
1. zip+py_compile+size
2. B exit0+非空 JSON
3. 顶层键 ⊇ {pins, n_pins, summary}
4. n_pins == B 期望数
5. 每 pin 字段齐 {pin,direction,pintype,logic_high_rail,logic_low_rail,evidence}
6. 每 pin pintype 与 oracle 一致（核心齿：解析逻辑对）
7. 每 pin logic_high_rail/logic_low_rail 与 oracle 一致
8. evidence.driver_or_receiver_inst 非空且与 oracle 一致（核心齿：真解析非硬编）
9. evidence.pmos_src_net / nmos_src_net 与 oracle 一致
10. default 域 pin (high=vcc/low=vss) 必须命中 `default`（反 always-gated 硬编）
11. pwrgt_type 域 pin (high=vccz/low=vss) 必须命中（反 always-default）
12. anti-hardcode：B pin 名/rail 名在场，A pin 名/rail 名缺席
13. 3-seed sha256 一致

## 3 negs
- neg_empty: 空脚本 → a/b
- neg_print_only: 打印 A 的 pintype 串无 JSON → b/c/d
- neg_core_removed: 真解析 B 但 pintype 永远返 default（跳过 rail→pintype 映射）→ 6/10/11
