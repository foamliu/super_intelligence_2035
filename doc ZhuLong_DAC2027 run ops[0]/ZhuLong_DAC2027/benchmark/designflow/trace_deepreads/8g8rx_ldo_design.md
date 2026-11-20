# Deepread — 8g8rx (jessegao / hfeg0pkn005 / mc195) — LDO 设计

## trace 来源
- session: `1792201142166_8g8rx.messages.json` (1.55MB / 390 msgs / 207 user)
- user: jessegao, host: hfeg0pkn005 (10.129.32.75)
- match_count: 195 (schematic:259 / virtuoso:148 / netlist:118 / dbGet:117 / pyAether:68 / calibre:9 / spectre:5 / hspice:1)
- tools: cline (with agent-policy-engine plugin, python-runner / shell-runner profiles)

## 用户真实意图轮（10 个真实文本轮）
- **U#0**「帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB @0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度」← **A-faithful 提出需求轮**（干净，非根因/修复）
- U#59「声明一下，这里的psrr为负值」← 澄清 PSRR 符号约定
- U#100/101「帮我输出一份电路图及验证报告」← 要求交付报告
- U#115「完整文档已生成在 /home/jessegao/Spice_Agent/design/ldo_v1/circuit_diagram_and_verification_report.md 这个文件怎么打开」← 接受+how-to
- U#118「直接帮我把内容输出到终端」
- U#120「我如何看这个电路」+ U#121「2」
- U#128「我对...有三方面改进：1.管子L太长了l=1~2u；2.负载电容2n ESR3欧母；3.带载5mA drop30m」← **改进轮（新需求，非根因）→ Rev.B**
- U#158「帮我生成一个验证报告，pdf版本，包含电路图、仿真model与spec、仿真数据」← PDF 报告（agent 因无 pdflatex/pandoc 失败）

## agent 工具链与产物
- 工作目录 `/home/jessegao/Spice_Agent/design/ldo_v1/`（Spice_Agent V2 框架，9-CP 流程）
- 探索：list_files /home/jessegao/Spice_Agent/{knowledge/ip/pwr, pdk_rules} → 读 PDK 规则、bias_ref.md
- 设计：editor 创建 state.json / pre-design.md / spec.md / dut_ldo_v1.sp / 4 个 testbench（ac/loadreg/linereg/psrr）/ design-report.md
- 多次 editor 失败（old_text missing / multiple occurrences / input too large >6000 chars）
- 仿真：python-runner 多次失败（Traceback），未成功跑 spectre/hspice → 无真实仿真数据
- Rev.B（U#128 改进后）：rev_b.sh / gen_revb.py / fix_revb_final.sh 重写 dut_ldo_v1.sp（L=2u, Cout=2n, ESR=3, 5mA, Miller 移除改为输出极点主导）
- 报告：circuit_diagram_and_verification_report.md（20KB，ASCII 电路图 + 8 节）+ gen_pdf.py / pdf_report.py（PDF 生成失败：无 pdflatex/wkhtmltopdf/pandoc）

## gold（用户接受的真实产物 — Rev.B）
ssh cat 拿到最终态文件（e0031982 可读 jessegao home）：
- **dut_ldo_v1.sp**（34 行，Rev.B）— 干净的 PMOS LDO SPICE 网表：
  - `.SUBCKT ldo_v1 vdd vout gnd vref en`
  - EA：X1/X2 nMOS 差分对（ntn, w=5u l=2u）+ X3/X4 pMOS 电流镜负载（ptn）+ X5/X6 bias 镜像（ntn_m）+ Rbias 290k (vdd→vb_tail)
  - Xpass PMOS pass（ptn, w=5u l=0.3u nf=200, gate=ea_out, source=vdd, drain=vout）
  - 反馈分压：R1 100k (vout→vfb) + R2 1.1M (vfb→gnd)  ← **注：trace 原值 R2=1.1M 给出 Vout=0.57V ≠ 0.9V，agent 设计错误；reference 人工复核修正为 R2=136.8k 使 Vout=Vref*(1+R1/R2)=0.9V**
  - Cout 2n + Resr 3Ω（输出电容+ESR，U#128 改进）
  - `.ENDS ldo_v1`
- **spec.md**（Rev.B）— 8 行规格表（VIN 1.0/1.1/1.2, VOUT 0.85/0.9/0.95, ILOAD 5mA, IQ<10uA, DC_GAIN 40/45, PM 40/70, LD_REG 6mV/mA, VDROP 30mV）+ PSRR 声明（承认 L=2um 增益受限，PSRR@100kHz 约 -5~+10dB 不满足 -20dB）
- **circuit_diagram_and_verification_report.md**（20KB）— 7 节：电路原理图(ASCII)/器件清单/仿真验证方案/解析计算验证/指标达标矩阵/PVT 分析/文件清单

## 合成决策（A 档 trace-faithful）
- **任务说明 = U#0 原文逐字**（不脱敏，不补全）
- **交付接口**：gen_ldo.py 读 config.json → 生成 dut_ldo.sp + spec.md + report.md（参数化 LDO 生成器，使 check() 能在 hidden B 上重跑）
- **资产 A** = config.json（U#0 specs 结构化：vin=1.1/vout=0.9/vref=0.52/iq=10uA/psrr=-20/gain=40/pm=40/L=2u/Cout=2n/ESR=3/Iload=5mA/nf=200/R1=100k/R2=136.8k；PDK ntn/ntn_m/ptn）— interface asset，不添加 U#0 之外的信息
- **hidden B** = config_B.json（结构不同：vin=1.2/vout=1.0/vref=0.6/iq=20uA/psrr=-25/gain=50/pm=50/L=1u/Cout=5n/ESR=5/Iload=10mA/nf=400/R1=80k/R2=120k/design=ldo_b7）→ 跨输入护栏
- **reference** = gen_ldo.py（参数化生成器，拓扑取自 Rev.B：EA 差分对+电流镜+bias 镜像+PMOS pass+反馈分压+Cout/ESR；R2 由 vout/vref-1 比例正确导出）+ reference_submit.zip
- **check.py 18 条件 a-r**：a zip 含 gen_ldo.py / b py_compile / c 跑 B 退 0 出 3 文件 / d .SUBCKT 名=B design / e PMOS pass(vout+vdd+gate=ea_out) / f nMOS 差分对(vref+vfb) / g pMOS 镜像(≥3+ea_out/ea_inp) / h bias(≥2 ntn_m+Rbias→vdd) / i 反馈(R1 vout-vfb, R2 vfb-gnd) / j Cout+Resr=B 值 / k spec B vin&vout / l spec B iq&psrr / m spec B gain&pm / n report 电路+验证+≥3 标题 / o R1/R2≈vout/vref-1 / p 跨输入护栏(B 名在 A 值不在) / q 3 次确定性 / r 退化计数(≥6X ≥3R ≥1C)
- **自验**：ref PASS 18/18 · 4 negatives ALL-FAIL distinct{empty→c / print_fixed_A→d / core_deleted→e / naive_no_esr→j} · NEG_RC=0 · §4.9 三假(c/d/e) distinct ✓ · k_rationale=k_check=18 ✓
- **layer**：L1-boundary（离线 Python 生成 SPICE 网表文本，不跑仿真；真跑条件=check 跑候选脚本生成 B 网表后静态解析拓扑/规格）

## 去重检查
D.jsonl 87 行无 LDO/ldo case（grep -i ldo 无命中）→ 无重复。

## 备注
- trace 末尾 U#158 PDF 报告失败（无 PDF 工具），agent 未交付 PDF；用户最终接受的是 .md 报告（U#115 阶段）+ Rev.B 网表（U#128 阶段）。本 case 取 U#0 作任务说明，gold 取 Rev.B 网表+spec.md+report.md（用户接受的产物）。
- agent 设计错误（R2=1.1M 与 Vout=0.9V 不符）经人工复核修正为 R2=136.8k（断言对事实：反馈分压比必须给出 spec 的 Vout）。
