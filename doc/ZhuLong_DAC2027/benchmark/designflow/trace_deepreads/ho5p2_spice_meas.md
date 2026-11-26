# deepread: 1793869755608_ho5p2 (SPICE .measure 生成, analog_context)

- **trace**: 1793869755608_ho5p2 / jiangbaol / hfeg0pkn003(10.129.2.12) / mc=138 / analog_context
- **single-session**: 207 msgs, 7 user turns, 多轮真实 SPICE produce（duplicate-subckt 修复 / probe 修复 / .measure 追加 / slicer 尺寸 sweep）
- **dom note**: netlist:719; hspice:206; schematic:140
- **tool_use freq**: editor×N / run_approved_command×N / read_files×N / SandBox_run_code×N（FineSim/hspice 后仿流程）

## 真实意图
DDR5 DFE slicer 后仿：在已有 testbench `.sp` deck（`004_onlySlicer_delay_m2701.sp`）上追加一组长尾 `.measure tran` 语句，量化功耗 / 信号穿越时刻 / 定点电压，并把每项测量的含义整理成说明。会话中段还涉及 duplicate subckt 定义修复、.probe 修复、slicer 尺寸 sweep。

## user U-turns（7 条）
- U#0：起手给 FineSim bench + 要求跑 slicer 后仿（duplicate subckt 报错）。
- U#5：修复 duplicate subckt（rename `subckt XXX` → 唯一名）。
- U#11：.probe 修复（probe 信号名 / 格式）。
- U#33：**核心 .measure 追加需求** —— 3 条新测量：
  1. 实例 `XI7` 整体电源功耗，**采样窗口与 .sp 内已有 `Cur_slicer_*` 功耗测量一致**（`from='5n-32*UI' to='5n'`，`avg i(vcc!)`）；
  2. `t=1.53` 之后，找 `ldfedata` 第 1 个**下降沿**到达 `vvdd-0.36` 的时刻；
  3. `t=2.0` 时刻，测 `outn_stg1` 与 `outp_stg1` 的电压。
- U#39/U#44：slicer 尺寸 sweep（pmos/nmos width/finger 调参，重跑 sim 看 timing）。
- 终轮：acceptance / 收尾。

## assistant 路径
1. editor 修改 `.sp`：rename duplicate subckt、补 `.probe`、追加 `.measure tran` 块。
2. run_approved_command 跑 FineSim/hspice，读 `.mt0`/`.lis` 结果。
3. .measure 追加 facet（U#33）：在 deck 末尾粘贴
   - `.measure tran pwr_XI7 avg i(vcc!) from='5n-32*UI' to='5n'`
   - `.measure tran t_ldfe_first_fall when v(ldfedata)='vvdd-0.36' fall=1 td=1.53`
   - `.measure tran v_outn_stg1_at find v(outn_stg1) at=2.0`
   - `.measure tran v_outp_stg1_at find v(outp_stg1) at=2.0`
4. slicer sweep：调 width/finger → 重跑 → 读 measure 结果对比。

## A-faithful 判定：不可行
- 交付物是**对 live FineSim `.sp` deck 的原地编辑**，依赖 `/proj/...` 真实 sim 环境 + FineSim license，不可附加到离线 test。
- 无 user-accepted 离线产物（measure 结果是 sim 运行时产物，非便携输入）。

## B 档 synthesized（#339 合成 plan）
取 trace 可移植 facet = **measurement spec JSON → .measure 语句块 + 说明报告**（U#33 的 .measure 生成子任务，最干净的 portable produce）：
- **gen_spice_meas.py --spec <spec.json> --outdir <dir>**：读 measurement spec JSON，原样生成 `measures.sp`（`.measure tran ...` 块）+ `report.md`（name/type/expression 表格）。仅用 Python 标准库。
- **A**(spec_A.json): design=slicer_testbench, instance=XI7, pwr_signal=i(vcc!), window from='5n-32*UI' to='5n', 1 crossing(t_ldfe_first_fall/ldfedata/vvdd-0.36/fall/1/1.53), 2 at_voltages(outn_stg1@2.0, outp_stg1@2.0) —— **A 即 trace U#33 真实 spec 的忠实转录**。
- **hidden B**(spec_B.json): design=comparator_sa_testbench, instance=XSA, pwr_signal=i(vccd!), window from='10n-16*UI' to='10n', 1 crossing(t_data_first_rise/datain/vdd-0.30/rise/1/2.1), 2 at_voltages(outp_cmp@3.5, outn_cmp@3.5) —— 与 A 全不相交。
- **hidden B2**(spec_B2.json): design=bandgap_testbench, instance=XBG, pwr_signal=i(vbgd!), window from='20n-8*UI' to='20n', 1 crossing(t_vref_first_rise/vrefbg/1.2/rise/1/0.5), **1** at_voltage(v_vrefbg_at@5.0) —— at_voltages 数 1≠A/B 的 2，专门击败硬编 measure 条数。
- **反硬编码轴**: instance XI7/XSA/XBG 不同；pwr_signal i(vcc!)/i(vccd!)/i(vbgd!) 不同；窗口表达式不同；crossing signal/edge/value/td 全不同；at-voltage signal/time 全不同；**at-voltage COUNT A=2/B=2/B2=1** 不同（硬编常量条数者 c/f FAIL）。
- **check 16 条件 a-p**: a(zip 无泄漏+py_compile) b(B-run exit0+measures.sp+report.md 非空) c(measure 总数==1+n_cross+n_atvolt) d(功耗 measure 四字段 name/signal/from/to==B) e(crossing 顺序全字段==B) f(at_voltage 顺序全字段==B) g(measure 名唯一) h(crossing+atvolt 顺序==B) i(report 表行数≥总数+每名出现) j(report 含 design_B+instance_B+pwr_signal_B) k(反硬编码:源码无 A 字面量 XI7/ldfedata/vvdd-0.36/outn_stg1/slicer_testbench/5n-32*UI/i(vcc!)) l(A-run 产 A-spec 顺序全字段) m(跨输入 B2-run 产 B2-spec, atvolt 数 1≠2) n(确定性 3x sha256) o(每条 .measure 均 .measure tran 形式) p(头注释含 design_B+instance_B 且功耗 measure 为首条非注释行)。
- **negatives**: empty_shell(→b) / hardcode_a(→d/k, A 字面量进源码) / hardcode_b(→l, B 输出硬编 A-run 失败) / print_expected(→b, 只打印不写文件) / ref_core_deleted(→c, 只输出 header+power 丢 crossing/atvolt) / drop_atvolt(→c/f, 丢 at_voltage)。§4.9 三假 = empty_shell + print_expected + ref_core_deleted。
- **自验**: ref PASS 16/16；6 negatives 全 FAIL；§4.9 三假全 FAIL；4 distinct first_fail labels。
- **断言闸门** k_rationale=k_check=16 ✓。

## 真实 spec/拓扑要点（供 prompt 背景）
- DDR5 DFE slicer = Decision Feedback Equalizer 判决反馈均衡切片器（接收端数据恢复）
- FineSim/HSpice `.measure tran`：`avg`（窗口平均）/ `when v(sig)='val' fall/rise=n td=t`（穿越时刻）/ `find v(sig) at=t`（定点电压）
- 采样窗口 `from='5n-32*UI' to='5n'`：UI = Unit Interval（DDR5 数据周期）；32*UI 为若干 bit 周期
- `vvdd-0.36` = 跨越阈值表达式（vdd 减一个 Vth 量级），原样填入不做算术化简
- 已有功耗测量 `Cur_slicer_*` 用同一 from/to 窗口 —— 新 `pwr_XI7` 必须复用窗口（prompt 明确要求）

## 与存量 case 的关系
- **MeasStmtExtract-001**（#318）= .measure **抽取**（从 .sp 文本提取 measure 语句结构化）；
- 本 case SpiceMeasGen-001 = .measure **生成**（spec JSON → measure 语句块）。
- 二者**方向相反**（extract vs generate），不冲突。
