# 深读笔记 · abico · SRAM schematic 全 port 功能讲解

- **session**: `1793860510641_abico` (子目录 `1793860510641_abico/` 下)
- **user/host**: e0030760 @ hfeg0pkn004 (10.129.2.13)
- **mc**: 114 (1105 scan) / pool B-kw 19 · keywords: rtl:220;schematic:154;virtuoso:151;netlist:90;aether:65;pyaether:52;cellview:35;hspice:20
- **trace**: 77 msgs / 244KB / agent=lead / 2 substantive user turns
- **pool 旧判**: parked "L1 explain-schematic-port-function; no produce deliverable; spice ratio 6%" (r? 11-09) → r618 reaudit 可造 (explain/介绍 Q&A)

## 用户原话
- U[0] (msg#0, 43c): `this schematic all port function,` （最初未指明哪个 schematic）
- U[7] (msg#7, 83c): `lacaa_sram_TV0/als_sramtc_tv0_shortloop_fs_soc_lpe/schematic` （给出 library:cell:view）

意图 = 列出该 SRAM schematic 的**全部 port 并讲解每个 port 的功能**（方向/位宽/功能分组）。

## 助手工具链
1. list_allowed_files / search_codebase 探 Desktop → 找 schematic 相关文件
2. 用户补 cell 路径后，search_codebase 找 netlist/verilog → 未找到（cell 在 OA 库里）
3. 读 eda_agent skill SKILL.md / case studies → 想用 Virtuoso SKILL 读 schematic
4. run_code (skill / pyAether) → **两个 sandbox 都 connection refused**（EDA bridge 没起）
5. 转 filesystem 探索：explore_lacaa.sh / open_sram.sh / prep_lacaa.sh → 定位 `/proj/lacaa/V0/`
6. editor 写 explore_lacaa_tv0.py → run_approved_command (python-runner) 多轮浅层 listdir（深 walk 超时 SIGKILL）
7. 读 lib.defs → `lacaa_sram_TV0` → `/proj/lacaa/TV0_FS_shortloop/libs/lacaa_sram_TV0`（OA 库）；DBRChk CSV 确认 top schematic `als_sramtc_tv0_shortloop_fs_soc`
8. 定位 cell 目录 `als_sramtc_tv0_shortloop_fs_soc_lpe/schematic/sch.oa`（99KB OpenAccess 二进制）
9. editor 写 explore2.py：读 sch.oa 二进制 → `re.findall` 抽 ASCII 串 → 得 **symbol 端口名**（VDDA/VSS/OutD/RDEN/WRL_ODD/WRL_EVEN/WRH_ODD/WRH_EVEN/WREnB/WREn/VSSWR/VCC/VDD/WL/BL/BLB + _T/_B/_A/_M 变体 + PRCH + PIN0..PIN32）
10. editor 改 explore2.py：`re.findall(rb'Pin "([^"]+)": floating ([a-zA-Z]+)', data)` → 得 **LPE pin-direction 记录 29 条**（msg#71）：

```
WL_T<127:0>      -> output        OUTD_T<127:0>    -> input
RDEn_T           -> output        WRH_EVEN_T       -> output
WREnB_T          -> output        WREn_T           -> output
WRL_ODD_T        -> output        WRL_EVEN_T       -> output
WRH_ODD_T        -> output        VDD_T            -> inputOutput
VCC_T            -> inputOutput   VDDA_T           -> inputOutput
VSS_T            -> inputOutput   VSSWR_T          -> inputOutput
WRL_EVEN_B       -> output        WREn_B           -> output
WREnB_B          -> output        WRH_EVEN_B       -> output
WRH_ODD_B        -> output        WRL_ODD_B        -> output
WL_B<127:0>      -> output        RDEn_B           -> output
VSSWR_B          -> inputOutput   VSS_B            -> inputOutput
VDDA_B           -> inputOutput   VDD_B            -> inputOutput
VCC_B            -> inputOutput   OUTD_B<127:0>    -> input
PRCH             -> inputOutput
count: 29
```

11. trace 在 msg#76 截断（agent 还在 explore2.py 想找 netlist 验方向），**未输出最终 port-function 报告**——但 port 数据已抽全。

## 关键事实
- cell = `lacaa_sram_TV0/als_sramtc_tv0_shortloop_fs_soc_lpe/schematic`，OA 库 `/proj/lacaa/TV0_FS_shortloop/libs/lacaa_sram_TV0`
- 顶层阵列 `ALS_Array_W128xB32_CH252`（128 WL × 32 BL，CH252）+ `ALS_Inst_W128xB128_CH252`
- 29 个 LPE pin：14 个 _T (top) + 14 个 _B (bottom) + 1 个 PRCH (global)
  - data: OUTD_T/OUTD_B (128-bit input, 输出数据回读), BL/BLB (symbol)
  - wordline: WL_T/WL_B (128-bit output)
  - write control: WREn/WREnB, WRH_EVEN/WRH_ODD, WRL_EVEN/WRL_ODD (_T/_B)
  - read control: RDEn (_T/_B)
  - power: VDD/VCC/VDDA (_T/_B, inputOutput)
  - ground: VSS/VSSWR (_T/_B, inputOutput)
  - precharge: PRCH (global, inputOutput)
- 方向语义：output = 阵列驱动（WL/WR/RD 控制 + WL 字线），input = 上游驱动（OUTD 数据输入），inputOutput = 电源/地（共享）

## 合成方案
**EDA-Eval-DesignFlow-SramPortExplainQA-001**（spice_sim schematic-port explain Q&A → 产 `sram_port_analyzer.py` 解析 port 抽取 → 结构化 JSON 报告，A 档 trace-faithful + 真实 sch.oa 抽取数据 asset + hidden B cross-input guard）：
- A = port_extraction.txt（verbatim msg#67 symbol 名 + msg#71 LPE 29 条 pin-direction）+ requirements.json + scenario.txt + task_brief.md
- hidden B = 不同 SRAM macro（lacaa_sram_TV1/als_sramtc_tv1_main_fs_hp，256 WL/64 DQ，命名 WL_TOP/WL_BOT/DQ_TOP/DQ_BOT/SAEN/PCH/CSEL/VDDIO/VSSIO，21 pins）port_extraction_B.txt
- 任务 = 写 sram_port_analyzer.py(workdir, out_dir) 读 port_extraction.txt 产 port_explain_report.json（14 顶层键：cell_name/library/port_count/ports/function_groups/side_groups/width_summary/power_ports/ground_ports/data_ports/wordline_ports/control_ports/direction_counts/summary）
- check.py 在 hidden B 上跑候选 analyzer，oracle 独立计算 B 的 port/direction/width/function_group/side，断言一致 + A-leak guard + B-grounding + 确定性 + 退化提交 FAIL
