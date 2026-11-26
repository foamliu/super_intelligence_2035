# trace_deepread: 1793763926139_g7b4c — CML 输入管尺寸扫描电流差异根因

- session: `1793763926139_g7b4c` · user `lvyy` · host `10.129.2.14` (hfeg0pkn005) · mc=482
- agent: `lead` · 411 msgs (219 user / 192 assistant) · tools: editor×106, read_files×34, run_approved_command×35, list_allowed_files×8
- keywords: netlist:1680, hspice:1383, schematic:584, synopsys:262, transistor:143, mosfet:69, analog
- domain: schematic_netlist (analog_context)

## 电路
CML(Current Mode Logic) 差分对，DDR4 用。核心网表 `netlist_1102give`（5 PMOS 顶层实例）：
- **XPM6** CMLBias CMLBias vdd2d! → 二极管连接镜像参考（gate==drain=CMLBias），w=2.4µ/L=120n/multi=1
- **XPM5** CkTo CKT net8 → 输入差分对 +（drain=CkTo 输出, gate=CKT 输入, source=net8），w=2.1µ/L=50n
- **XPM4** CkCo CKC net8 → 输入差分对 −（drain=CkCo, gate=CKC, source=net8），w=2.1µ/L=50n
- **XPM3** net8 CMLBias vdd2d! → 尾电流镜像 1（drain=net8, gate=CMLBias, source=vdd2d!），w=2.85µ/L=120n
- **XPM2** net8 CMLBias vdd2d! → 尾电流镜像 2（同 XPM3）
- **R1/R2** CkCo/CkTo → vss! 2.9k（负载电阻）
- **I6** CMLBias vss! DC=100µA（偏置电流源）
- mirror_ratio = (2.85×1)/(2.4×1) = 1.1875；expected_tail = 100µA×1.1875 = 118.75µA

## 关键用户轮（提出需求/表达目标，A 档候选）
1. **[0] M0**：「我搭了一个电路，电路路径在激励文件…cml_tran.sp 中，为什么扫输入管 mp5 的尺寸会导致电流差这么多」← **分析-Q&A**，选为本 case 任务说明
2. [23]「你能直接帮我调电路吗」
3. [172]「CML 指标：电流镜 100µA/输入共模 75-225mV/摆幅 100-280mV/输出共模 290mV/DC 增益 7dB/带宽 3G，给设计思路并调好电路」← 造题 + 调电路
4. [242]「直接改好方案 A 的激励文件并跑全套验证」
5. [318]「写公式：CML+NCE/源退化 CTLE/gate-bias OTA 增益带宽传输函数零极点…」← 公式 Q&A
6. [372/395/408]「以 netlist_1102give 跑 PVT(0.875/0.96/0.79 × -40/25/130 × tt/ss/ff × CM 75/225mV)，tran+ac，6.4E9Hz 差分输入，给 100M/4G/4.4G 增益、-3dB 带宽、电流 min/max」← PVT produce-task（session 末尾 editor 持续报错未交付）

## 金标准（M0 的根因）
hspice OP（TT/0.875V/25C, winput=2.1µ/linput=50n）：
- XPM6：**Saturation**，Id=-100µA（二极管参考）
- **XPM5：Linear**，Id=-166.5µA ← 输入对 + 在线性区
- **XPM4：Subth**，Id=-5.3µA ← 输入对 − 在亚阈值
- XPM3/XPM2：Saturation，Id=-85.9µA（尾镜像）

⇒ **根因**：输入差分对 XPM5/XPM4 不在饱和区（一在线性、一在亚阈值）。扫 W/L 会让输入管在 linear↔saturation↔subth 之间迁移；非饱和区电流强依赖 Vds(=net8)，尾电流镜像（XPM3/XPM2 镜像 XPM6）无法维持固定尾电流 ⇒ 支路电流剧烈发散。这正是用户「电流差这么多」的物理来源。

## 资产可达性
- 原 `/rundata/m2701/.../netlist_1102give` 与 `/proj/m2701/.../cml_tran.sp` 跨用户（e0031982 vs lvyy/m2701w）**Permission denied**。
- 从 trace `read_files` tool_result（msg [397]）恢复 netlist_1102give 器件行（lines 18-25），简化保留 w/l/multi/4 端点（drop as/ad/ps/pd/sa/sb/sxact 等寄生参数，不影响拓扑分析）。
- OP 报告数据从 trace tool_result（含 region/Id/Vgs/Vds/Vth/Vdsat/Beta/Gm/Gds + node voltages）合成 op_report_A.txt。

## 造题决策（A 档 trace-faithful analysis-Q&A）
- 任务说明 = M0 用户逐字原文（仅 mask 无，路径保留原值）。
- 交付物 = `cml_current_analyzer.py`（解网表顶层实例→分类 diode_ref/input_pair/tail_mirror→算 mirror_ratio/expected_tail→解 OP report region→非饱和器件与 input_pair/tail 求交定 dominant_mechanism）+ `cml_current_report.json`。
- hidden B = cml_rx 单元 / FF/0.96V/-40C，结构相反：尾镜像 XM3/XM4(multi=2) 在 Linear、输入对饱和 → dominant_mechanism=tail_mirror_out_of_saturation（≠A），mirror_ratio=3.0（≠A 1.1875），IBIAS=80µA（≠A 100µA）。
- check() 12 断言 a-l：②n_mos ③n_R/n_I ④diode_ref ⑤input_pair ⑥tail_mirror ⑦mirror_ratio ⑧expected_tail ⑨I6 ⑩op_regions+mechanism(A) ⑪anti-hardcode B 机制/ratio/I6 全 ≠A ⑫3-run 确定性。
- 自验：ref 12/12 PASS + 4 neg FAIL distinct labels + §4.9 三退化(empty/print_only/deleted_core)全 FAIL + test==disk byte-sync + k_rationale=k_check=12≥8 GATE PASS。
