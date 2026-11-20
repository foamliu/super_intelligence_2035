# Deep-read: 1794570767776_u4uxo (stephens@hfeg0plg58/10.129.8.103, mc=58)

## Trace metadata
- session: 1794570767776_u4uxo
- user: stephens, host: hfeg0plg58 (10.129.8.103)
- match_count: 58, keywords: schematic:185;cmos:185;netlist:19;pyaether:5;hspice:1
- 164 msgs / 82 user / 82 assistant, tools: editor:37, run_approved_command:20, read_files:16, list_allowed_files:2, SandBox_MCP_Server__run_code:2

## Real task (trace-faithful)
stephens 在 FineSim Monte Carlo 仿真后需要提取电压裕量统计:
1. **u msg 0**: "读取这个路径下的.csv文件 /rundata/ddgoa/V0/simdir/finesim/workdir/stephens/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0_stephens_schematic_ALPS/output_compare_final_mc2p2sigma"
2. **u msg 3**: "并配合上级目录里control_mc_spf_t04.sp的testbench，给出每个corner数据统计"
3. **u msg 45**: "直接读csv文件里的avg std min max行，给出VMHL VMLH VMHL_LV VMLH_LV"
4. **u msg 73**: "汇总在一张表里，只要包含avg min max就行"
5. **u msg 74**: "可读性强一点"

## Data formats

### VM_RST0.mt0.csv (FineSim MC output)
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=1
.TITLE '*********************************'
       mc_index,        vmlh_lv,        vmhl_lv,           vmlh,           vmhl,         temper,         alter#
     1.0000e+00,     1.5559e-01,     1.2652e-01,     1.4312e-01,     1.2655e-01,     2.5000e+01,     1.0000e+00
     2.0000e+00,     1.6012e-01, ...
...
avg     1.5698e-01,     1.2705e-01,     1.4347e-01,     1.2586e-01,     2.5000e+01,     1.0000e+00,
std     9.0945e-03,     8.6206e-03, ...
min     1.3179e-01, ...
max     1.8281e-01, ...
```
- Columns: mc_index, vmlh_lv, vmhl_lv, vmlh, vmhl, temper, alter#
- 18 alter groups, 300 MC samples each
- After each group: avg/std/min/max summary rows (first field = stat name, trailing comma)

### control_mc_spf_t04.sp (SPICE testbench)
- .param pvcc, .alter sections defining 18 PVT corners
- Each alter: corner (TT/SS/FF/SF/FS), temp (-40/25/130°C), pvcc, PW, tCCDs

### 18 corners (alter# 1-18)
1: TT,25C,0.68V | 2: TT,25C,0.80V | 3: SS,-40C,0.82V | 4: SS,-40C,0.90V
5: SS,130C,0.74V | 6: SS,130C,0.865V | 7: FF,-40C,0.70V | 8: FF,-40C,0.805V
9: FF,130C,0.605V | 10: FF,130C,0.735V | 11: SF,-40C,0.82V | 12: SF,-40C,0.90V
13: SF,130C,0.74V | 14: SF,130C,0.865V | 15: FS,-40C,0.82V | 16: FS,-40C,0.90V
17: FS,130C,0.74V | 18: FS,130C,0.865V

## Signals
- VMLH_LV / VMHL_LV: Voltage Margin Low-to-High / High-to-Low (low-voltage mode)
- VMLH / VMHL: Voltage Margin Low-to-High / High-to-Low (normal mode)
- Values in Volts in CSV, output in mV (×1000)

## Assistant's solution evolution
1. analyze_mc_data.py → mc_analysis.py: compute stats from raw data rows (mean/std/min/max per alter)
2. extract_summary.py: read pre-computed avg/std/min/max rows directly from CSV
3. print_table.py (final): correct column mapping (parts[1]=vmlh_lv, [2]=vmhl_lv, [3]=vmlh, [4]=vmhl), output formatted table in mV
- Bug fixed: early version mapped temper to VMHL column (25000.00mV), corrected in final version

## Final output (msg 162)
```
FineSim Monte Carlo Summary (mV) - AVG / MIN / MAX per Corner
 No. Corner               Stat  |    VMLH_LV    VMHL_LV       VMLH       VMHL
   1 TT  25C 0.68V        AVG   |     156.98     127.05     143.47     125.86
   1 TT  25C 0.68V        MIN   |     131.79      99.25     117.05     101.65
   1 TT  25C 0.68V        MAX   |     182.81     150.14     168.05     149.23
   ...
```

## Case synthesis plan
- Domain: characterization, Level: L2 (portable)
- A: 6 corners × 50 MC samples, synthesized CSV + testbench
- Hidden B: 6 different corners × 40 samples, different values (cross-input guard)
- Task: parse CSV avg/min/max rows + map alter# to corners from testbench → summary CSV (mV)
- k≥8 assertions incl. cross-input guard
