# Deepread — 1793669959152_3123n (CML 带宽扩展公式手册 Q&A)

> ⛔ **CROSS-SHARD DUP — 不可造 D case**（r943 发现）：
> ledger 互斥拒绝：本 session 已在 **shard B** 台账 status=case，
> case_id=`EDA-Eval-DesignFlow-CmlBwExtensionHandbook-001` (2026-11-17)。
> B 的 "CmlBwExtensionHandbook" = 与本笔记 msg[318]/msg[319] **同一任务**（CML 带宽扩展手册）。
> ⇒ D 不得造此 case。本笔记仅作「B 已覆盖、勿重复」的存证，**r944 不要再用 3123n**。
> 真正可造的 revival 候选见 MEMORY_D r943 段「下轮 r944」清单。

- **session**: 1793669959152_3123n
- **user**: lvyy  · **host**: hfeg0pkn005 (home 也可在 pkn002/ahpc505 访问；sessions 在 `~/.cline/data/sessions/1793669959152_3123n/` **子目录**，非 flat)
- **mc**: 576 · **domain**: analog_context (D-pure: netlist:2079;hspice:1436;schematic:657;analog…)
- **size**: 3,254,222 B / 447 msgs (>2MB → 本轮 deepread-only，synth deferred)
- **trace_source**: real, lvyy 真实在做 LP6/DDR4 CML 接收器电路调参 + 公式推导问答
- **旧 ledger 判定**: parked「CML circuit sizing Q&A (why sweeping mp5 size changes current; what W/L range for 100uA); analysis+tuning not produce-task」
- **11-15 reaudit**: Q&A/explain/analysis 全部恢复为可造 → 本候选 revival 合法

## 选定 A-faithful 用户轮 = msg[318]（verbatim，未给根因/修复 ✓）

> 写出以下相关公式: CML电路加上NCE电路的公式；源退化CTLE；gate-bias OTA，求增益带宽和传输函数等各种分析，包括零极点。还有其他什么可以用来提高带宽的方式也列出来。

（提出需求式 Q&A：要公式推导手册，用户未给根因或修复方案 → A 档合规）

## GOLD = msg[319]（assistant 完整结构化公式手册，~7.4KB）

标题：**《CML 带宽扩展与均衡技术：完整公式手册（结合本电路实测参数）》**
基准参数：gm=1.15mS、R=2.9k、ro_in≈7k、ro_tail≈10k、C_L=26fF、I_side=100µA、实测 A₀=2.34(7.41dB)、f₃dB=3.0GHz。

**六节结构**：
- 〇. 基线 CML 缓冲器传输函数（半电路推导，A_dm(s)、A₀、主极点、GBW、A_cm、CMRR 表）
- 一. 源退化 CTLE（R_s∥C_s）：Z_s(s)、完整二阶传输函数、零极点表（A₀/ω_z/ω_p,deg/ω_p,out/Boost=1+gm·R_s）、本电路设计公式（R_s=425Ω, C_s=250fF）、headroom 校验
- 二. NCE 负电容增强：C_eff=C_c(1−A_v) 推导、A_v 三档表、本电路 C_c 公式、稳定性判据（ω_sf>3×BW）
- 三. Gate-bias OTA（有源电感/负阻）：Z_out(s) 零极点形式、ω_z/ω_p/R_eff、稳定性判据 gm_L·A₀·R_eff<1
- 四. 其他带宽扩展技术：4.1 并联峰化 Shunt Peaking (m=L/(R²C_L), BW×1.72) / 4.2 T-coil (×2.83) / 4.3 NIC 负阻抗 / 4.4 前馈 Feedforward / 4.5 分布式放大器
- 五. 本电路推荐组合（性价比排序表，① 源退化 CTLE…）

**真实标识 token**（A-only，反硬编码用，word-boundary）：
CML / NCE / CTLE / gate-bias OTA / 源退化 / 负电容 / shunt peaking / T-coil / NIC / feedforward / 分布式放大器 / V6f / cml_tran.sp / net8 / CMLBias / mp5 / mp6 / mp2 / ω_p,deg / Boost / R_s / C_s / C_eff / C_c / A_v / Gm,ota / R_o,ota / GBW / CMRR / 半电路 / 虚地 / headroom / 1.15mS / 2.9k / 26fF / 100µA / 7.41dB / 3.0GHz / 425Ω / 250fF / 1.5GHz / 146nH / 36nH

## 拟造任务形态（r943 deferred → r944 synth）

**case_id 候选**: CmlBandwidthFormulaExplainQA-001
**domain**: analog_context
**reframe**: manual-grounded howto/explain Q&A→produce（承 r928-r941 范式，formula-compendium 子维度首例）
**A 资产**: `cml_bandwidth_formula_explain_A.md` — 基于 GOLD msg[319] 合成的结构化 markdown 公式手册（保留 6 节框架 + 真实参数表 + LaTeX 公式块 + 设计公式 code block）
**question_A.txt**: verbatim msg[318]
**B hidden 平行场景**（token 不相交，结构同构）: `lc_vco_tuning_formula_explain_B.md` — 合成 **LC-VCO / PLL charge-pump / CDR 带宽与噪声公式手册**（同 6 节结构：基线 LC-VCO 相位噪声传输 / 尾电流滤波 CP / KVCO 线性化 / 有源电感变容 / 其他降噪技术 / 推荐组合）。B-only token：LC-VCO / PLL / CDR / charge-pump / KVCO / phase noise / ISF / PN / tail filter / varactor / 李森 / 环路带宽 / 锁相 / 抖动 / φ_n / K_cp / K_vco / N（分频比）/ I_cp / f_ref / 1.6GHz / 12MHz / 0.8nV/√Hz …
**candidate parser**: 复用 `circuit_module_explain_parser.py` verbatim（通用 markdown 手册解析器，8 键 JSON{project_name,module_name,framework_diagram,submodules,jedec_context,evidence_files,design_highlights,limitations}+report.txt）—— 注意：formula-compendium 手册的 "submodules" 对应各技术节（CTLE/NCE/Gate-bias-OTA/Shunt-Peaking…），"framework_diagram" 对应 ASCII 框架/传输函数图。需验证 parser 对公式块（$$…$$）与表格的解析兼容性；若不兼容则 r944 适配 parser（新增 formula_expressions 字段）。
**check.py 12 断言 a-l**（承 r937/r939 模板）: a zip+py / b py_compile / c A JSON 8 键 / d B JSON 8 键 / e B module_name 含 LC-VCO/VCO 非 CML / f B submodules≥5+期望 B-only 名{LC-VCO,PLL,CDR,ChargePump,KVCO,Varactor,ISF,TailFilter}⊆blob / g B framework_diagram≥500字+≥3 box-drawing / h B jedec_context≥2 训练 kw{phase noise,PLL,CDR,锁相,抖动,VCO,KVCO} / i B design_highlights≥2 / j report 含≥2 模块/框架 kw / k 反硬编码 B stdout 0 个 A-only token word-boundary / l 3-seed md5 一致
**隐藏 B 反硬编码要点**: A-only 通用词（带宽/增益/零点/极点/传输函数）因 LC-VCO 也涉及属合法重叠须排除；以电路名+变量名（CML/NCE/CTLE/C_eff/R_s vs LC-VCO/PLL/KVCO/ISF/I_cp）做 word-boundary 区分。

## next-round 执行清单（r944 第一件事）
1. ssh .75→hfeg0pkn005 已验证可读（路径 `~/.cline/data/sessions/1793669959152_3123n/1793669959152_3123n.messages.json`）—— 本轮已 scp 到 workdir，GOLD msg[319] 已落本笔记
2. 合成 A 手册（基于本笔记 GOLD 全文）+ B 手册（LC-VCO/PLL/CDR 平行）+ parser（验证/适配公式块）+ check.py 12 断言
3. 自验 12/12 PASS + 3 neg 全 FAIL + §4.9 三退化 + 3-seed
4. 落 EDA-Eval-DesignFlow_D.jsonl，ledger mark 3123n --status case --force（revival-from-parked）
5. l1_subgrade=L1-realrun-python 续标第 21 case；asset_fidelity=synthesized-reframe D 域第 13 例；manual-grounded howto/explain D 域第 11 例；formula-compendium 子维度 D 域首例

## 其他可造用户轮（同 session 2nd-case-same-session 候选，备选）
- msg[0] 「为什么扫输入管mp5的尺寸会导致电流差这么多」（含文件路径，需附 cml_tran.sp 资产 → 较重）
- msg[320] 「为什么要用电流镜的方式给差分电路给电流，不能直接在CMLBias处给恒定电压？」（纯概念 Q&A，重复 4x = 用户不耐烦；GOLD msg[323]+ 跑 PVT 角实证）
- msg[372] PVT 跑仿真任务（真跑 produce-task，但需 finesim 网表资产 → L2 重）
