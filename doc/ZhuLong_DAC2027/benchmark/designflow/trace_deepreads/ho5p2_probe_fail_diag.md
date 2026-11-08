# ho5p2 — SPICE .sp probe fail 诊断 (jiangbaol @ hfeg0pkn004)

## trace
- session: 1793869755608_ho5p2 (jiangbaol, hfeg0pkn004, 207 msgs, 1.0MB, file-based, mtime Nov 5)
- 11-05 重扫令 hfeg0pkn004 cron 盲区 263 unscouted，spice>=10 unprosected 21 条，ho5p2(sp=97 hspice, jiangbaol) peek → CLEAN

## 选轮 (A-faithful)
- U#0: duplicated subckt definition 报错（= 97ksq 同题，不入 prompt）
- U#2: 如何设置 option 让 hspice 波形每层级含所有 net 信号（知识问答，不入 prompt）
- **U#7 逐字（任务说明轮，提出需求，无根因/修复 → A-档选轮 ✓）**:
  `/proj/m2701/V0_DDR4/simdir/finesim/workdir/jiangbaol/simulation/001_slicer/Slicer_testbench/004_onlySlicer_delay_m2701.sp`
  `帮我检查下这个.sp为什么无法probe slicer_out以及slicer1st_out，并改正`
- U#33 后续追加 measure 语句（不入 prompt）

## 金标准 (assistant A#32)
两个根因：
1. **slicer_out (line 216) — 大小写错误**: .sp 写 `LDFEdataEr`/`LDFEdataErN`（小写 d），网表真实 net 名 `LDFEDataEr`/`LDFEDataErN`（大写 D）。大小写敏感 → 引用不存在的 net → probe 不到。
2. **slicer1st_out (line 215) — 内部节点未保存**: 层级路径 `XI7.XI_DqIbSAHFM6IP.outp_stg1/outn_stg1` 正确，但 `.option probe=1` + `.probe TRAN V(*) i(*) isub(*) except="*:*"` 的 `except="*:*"` 排除所有子电路内部节点 → 内部节点电压 probe 取不到值。

附带大小写 bug：
- line 222: `DQSampN` → `DqSampN`
- line 255/260: `LDFEdataEr`/`LDFEdataErN` → `LDFEDataEr`/`LDFEDataErN`

修复：
1. 改大小写: `LDFEdataEr` → `LDFEDataEr`, `LDFEdataErN` → `LDFEDataErN`
2. 补显式 `.probe TRAN v(XI7.XI_DqIbSAHFM6IP.outp_stg1) v(XI7.XI_DqIbSAHFM6IP.outn_stg1)` 或去掉 `except="*:*"`

## .sp 关键 probe 行 (msg#27 tool_result)
```
212| .probe Cur_slicer1st = 'i(XI7.XI_DqIbSAHFM6IP.xmp2.main)'
213| .probe Cur_slicer2nd = 'i(XI7.XI_DqIbSAHFM6IP.xmn3.main)'
214| .probe Cur_slicer_latch = 'isub(XI7.XI_DqIbSAHFM6IP.inh_vcc)'
215| .probe slicer1st_out = 'v(XI7.XI_DqIbSAHFM6IP.outp_stg1) - v(XI7.XI_DqIbSAHFM6IP.outn_stg1)'
216| .probe slicer_out = 'v(LDFEdataEr) - v(LDFEdataErN)'
222| .probe DQSIN='v(XI7.XI_DqIbSAHFM6IP.DQSampN)-VVDD/2'
253| .probe out_stg1_cm = '(v(XI7.XI_DqIbSAHFM6IP.outp_stg1) + v(XI7.XI_DqIbSAHFM6IP.outn_stg1)) / 2'
255| .probe ldfe_cm = '(v(LDFEdataEr) + v(LDFEdataErN)) / 2'
258| .probe out_stg1_dm = 'v(XI7.XI_DqIbSAHFM6IP.outp_stg1) - v(XI7.XI_DqIbSAHFM6IP.outn_stg1)'
260| .probe ldfe_dm = 'v(LDFEdataEr) - v(LDFEdataErN)'
```

## 网表关键结构 (msg#32 diagnosis)
- 顶层: `XI7 ... LDFEDataEr LDFEDataErN ... DqIb_2stg_DfeM6V2IP_DT` (netlist line 336)
- 电容: `C9 LDFEDataEr vss! ...` / `C10 LDFEDataErN vss! ...`
- 子电路 `doubletail_nmoslatch` 有 `outp_stg1`/`outn_stg1` (line 206/207/298-302)
- 实例层级: XI7 → XI_DqIbSAHFM6IP (实例化 doubletail_nmoslatch, line 326)

## 合成计划
- case: EDA-Eval-DesignFlow-ProbeFailDiag-001 (spice_sim A-faithful L1)
- A = A_slicer_sp.sp (faithful 重建 probe block + .option probe=1 + except="*:*") + A_netlist (faithful 重建 doubletail_nmoslatch + XI7 顶层)
- hidden B = B_slicer_sp.sp (结构不同: strongarm_latch, CLKbuf/CLKbufN 大小写 bug) + B_netlist
- reference = diag_probe_fail_ref.py <sp> <netlist> -o out.json (解析 .probe 提取 net 名, 交叉比对 netlist, 找大小写不匹配 + except="*:*" 内部节点排除)
- check.py 15 断言 (a-o): 含交叉输入守卫(k:A 上 LDFEdataEr→LDFEDataEr)+A-only 泄漏闸门(l:B 输出不含 LDFEdataEr)+核心技能迁移
