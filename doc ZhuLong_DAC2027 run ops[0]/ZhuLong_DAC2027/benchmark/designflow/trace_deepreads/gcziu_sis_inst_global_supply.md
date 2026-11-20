# trace_deepread — 1793585029552_gcziu (jhhu @ hfeg0pkn004) — SiliconSmart .inst 生成

## 来源
- session: 1793585029552_gcziu (jhhu, hfeg0pkn004, dir-based, 149 msgs, 1.1MB, mtime Nov 2)
- 11-05 重扫令 hfeg0pkn004 cron 盲区 263 unscouted peek 11 取第 10 个 gcziu(sp=50)
- domain: characterization (siliconsmart instance 配置)

## 对话流
- U#0: `/proj/drgqx/V0_20261028/workdir/jhhu/cvps/sisregular/drgqx_cmos_io/netlists/DL_DFFPD_sub2.spf_RC zhege cell`（看这个 cell）
- A#1-A#9: assistant run_commands/read_files 读 SPF，解析结构
  - A#9: `*|DSPF 1.3` / StarRC R-2020.09-SP5-4 / `.SUBCKT DL_DFFPD_sub2 IN1 IN2 IN3 OUT1 OUT2 RST`（line 23，7 信号端口）
  - DL_DFFPD = 带 PD 复位的 D 触发器，3 输入 IN1/IN2/IN3，2 输出 OUT1/OUT2，复位 RST
- U#10: `zenme xie ta de instance gei siliconsmart yong?`（怎么写它的 instance 给 siliconsmart 用？）← A-档选轮（提出需求，无根因/修复 ✓）
- A#11-A#23: assistant 继续读 SPF/control 目录，A#23 给出 4 种 SiliconSmart instance 写法（直接吃 SPF / db_define_cell / SPICE instance / 双网表模式）+ sequential cell template 建议
- U#24: 用户粘贴自己的 .inst 配置（power_meas_supplies {vdll vbulkp} / add_back_bias_supplies / set_netlist_file / add_pin 6 信号端口 / set_subckt_ports {7 端口} / add_function+add_latch / create_parameter cut_netlist）
- A#25-A#36: assistant 读 .inst/configure.tcl/sis.log/runtime，A#36 给出**金标准诊断**：
  - **根本问题**：SPF 第 23 行 `.SUBCKT DL_DFFPD_sub2 IN1 IN2 IN3 OUT1 OUT2 RST` — **vdll/vssdll/vbulkn 不在 .SUBCKT 端口列表**，它们只是 SPF 内部 `*|P (vdll O ...)` 标注的全局电源/地
  - 用户的 .inst 只 add_pin 信号端口 + set_subckt_ports 7 端口，**漏掉电源声明** → SiliconSmart 例化时电源浮空 → sis.log 121 sims 全失败（hspice exit 1）
  - **修复**：`add_global_net vdll -type power` / `add_global_net vssdll -type ground` / `add_global_net vbulkp -type power` / `add_global_net vbulkn -type ground`（把 *|P 标注但非 .SUBCKT 的电源声明为全局网）
  - 附：`cut_netlist` 非标准参数应删；RC 寄生网表太重建议另给纯净 CDL
- U#37+: 用户转问 DqsDividerGut cell 的 timing arc（另一任务，非本 case 范围）

## 金标准（用户接受的结果）
- A#36 的修正后 .inst：在用户配置基础上加 4 行 `add_global_net <supply> -type power/ground`
- 核心技能：识别 SPF 中 *|P 标注但不在 .SUBCKT 端口的电源/地，声明为 add_global_net

## 真实 SPF 结构（从 assistant read_files tool_result 提取）
- line 2: `*|DSPF 1.3` / `*|DESIGN DL_DFFPD_sub2` / StarRC R-2020.09-SP5-4
- line 23: `.SUBCKT DL_DFFPD_sub2 IN1 IN2 IN3 OUT1 OUT2 RST`（7 信号端口，无电源）
- line 25: `*|GROUND_NET 0`
- line 27-28: `*|NET vdll 0.00074035PF` + `*|P (vdll O 0 2.8250 1.7800)`（vdll 是 *|P 端口但非 .SUBCKT）
- line 230-231: `*|NET vssdll ...` + `*|P (vssdll O 0 2.8250 0.0000)`
- 同理 vbulkp / vbulkn（*|NET + *|P O，非 .SUBCKT）
- 内部 *|I 引用 XI91.XI0/XI4.XI0/XI5.XI0/XI6.XI0/XI8.XI0/XI10.XI0 等子模块的 BULK/SRC/GATE/DRAIN

## case 合成
- EDA-Eval-DesignFlow-SisInstGenSupplyGlobal-001 (characterization, A-faithful, L1, k=15)
- A = DL_DFFPD_sub2.spf_RC（faithful 重建 88 行：.SUBCKT 7 端口 + 4 电源 *|NET/*|P O + 6 信号 *|NET/*|P I/O + 内部 R/C）
- hidden B = Sa_dfe_top.spf_RC（结构不同 49 行：.SUBCKT CLK D Q QB 4 端口 + 电源 vdd/vss/vbbp/vbbn）
- reference = gen_sis_inst_ref.py（解析 .SUBCKT 信号端口 + *|P 非 .SUBCKT 电源，分类 power/ground/bulk，生成含 add_global_net 的 .inst）
- check.py 15 断言(a-o)：含交叉输入守卫(m:B 输出 CLK/D/Q/QB+vdd/vss)+A-only 泄漏闸门(n:B 输出不含 DL_DFFPD_sub2/IN1/vdll)
- 自验：ref PASS 15/15 + 4neg FAIL distinct(b/m/g/g) + NEG_RC=0 + §4.9 三假(空壳b/打印期望m/删核心g) FAIL + 断言闸门 15==15≥8 + jsonl test==disk sha ade46d9e
