# r249 deepread — xqeql (kaixuanx) — Calibre LVS/ERC + PEX hcell 流

- **trace**: `1793707420467_xqeql` · user `kaixuanx` · host `hfeg0pkn002`(10.129.2.11) · mc=181 · 131 msgs / 550KB · agent=lead · **NEW user (0 prior cases)**
- **keywords**: lvs:1107 pex:269 calibre:269 netlist:169 hspice:115 .cdl:77 pdk:75 .spi:32
- **tools (real usage)**: calibre:161 netlist:149 hspice:103 schematic:23 (calibre LVS/PEX + sim 混合，physical_verify 为主)
- **domain**: physical_verify (Calibre LVS/ERC + PEX StarRC/calibreLPE)

## 用户意图（逐轮，mode=act）
- **U#0**：「LVS ERC报错 Rule File Pathname: /proj/m2701/V0_DDR4/ver/lvs/virproj/CTLE_active_ind/_calibreLVS.rule_ nwell without net to power CTLE_active_ind」— 报 LVS/ERC 错（nwell 无电源连接），**给出根因** → A档不合格（rule 2）
- **U#39**：「NMOS使用P-TAP GUARD RING，PMOS使用N-TAP」— 给修复方案（guard ring 指派）→ A档不合格
- **U#41**：「我这里抽寄生参数报错，hcell文件不存在，无法运行lvs」— PEX hcell 缺失报错 + 根因 → A档不合格
- **U#49/U#54**：贴 pvpro.main LPE 运行日志（corners.smc 25 corner）
- **U#55**：贴 LPE 提交日志「calibre -lvs -spice layout.spi -hier -turbo 1 -hcell .../hcells lpe_RCC.rule > cci_lvs.log」「Terminate LPE running due to CCI-LVS run failed」
- **U#101**：「spf 文件在 .../CTLE_active_ind.spf.TYP_98_RCC，需要修改仿真脚本 .../ctle_act_ind_post.sp，更改调用关系来跑后仿」— 提出需求（后仿），但 = simulation 域（非 shard C physical_layout）

## agent 真实产物（tool_use 序列）
1. **grep_erc_rule.py** (A#8, 1554B, 在 ~/Desktop) — grep/parse ERC rule from `_calibreLVS.rule_` + `.erc.summary`
2. **check_cdl.py** (A#30, 666B) — check CDL
3. **find_hcell.py / find_hcell2.py** (A#50→A#128, ~15 次迭代) — 早期版本做 hcell 生成（从 layout/source 层级派生 hcell 列表）；**最终版本被改写为 post-sim 验证脚本**（verify X1 call vs SPF .SUBCKT ports / supply source / leftover pre-layout netlist / env insert position）— hcell-gen 逻辑已被覆盖丢失
4. **ctle_act_ind_post.sp** (A#118, 4303B) — 后仿脚本（simulation 域）
5. **corners_0p8.env / tt_98_post_insert.env** — corner 文件（simulation 域）

## BLOCKER（本轮无法合成的根因）
- **`/rundata/m2701/V0_DDR4/ver/...` 与 `/proj/m2701/...` 资产对 e0031982 权限拒绝**（属 kaixuanx 项目）：hcells、cci_lvs.log、no_lay_cvps_hcell.rep、_calibreLVS.rule_.svrf、layout.spi、source.cdl 全部不可读 → 无法取真实输入资产
- agent 的 hcell-gen 脚本（find_hcell2.py 早期版本）被同路径 editor 覆盖为 post-sim verifier → hcell 生成逻辑丢失，只能从 trace 对话反推

## 可建 B档 子任务（下一轮合成，用 representative 资产重建）
1. **【首选】Calibre LVS hcell 生成器**（physical_verify, L2 候选）：输入 = layout 层级 cell 列表 + source 层级 cell 列表 + 部分已有 hcell + cci_lvs.log(missing-hcell 错误)；输出 = 完整 hcell 文件（layout/source cell 配对，含 LAYOUT COMPONENT / SOURCE COMPONENT 映射）。ground on U#41/U#55「hcell 不存在 → CCI-LVS failed」。DISTINCT from r240 WlAdjacentPairParse(.rep PAIR)。需重建代表性 layout/source 层级（从 trace 提到的 CTLE_active_ind 子模块名）。**真跑 L2 角度**：可用 eda_flow run_code 在 .75 上跑 calibre -lvs 验证生成的 hcell 让 CCI-LVS 通过 — 但需真实 LVS rule + 网表，重；倾向 L1（离线 hcell 配对生成器，断言输出结构）。
2. **【备选】Calibre ERC rule grep/parse**（physical_verify, L1）：grep_erc_rule.py 的逻辑 — 从 LVS rule 文件 grep ERC rule 段 + 解析 .erc.summary 报错。ground on U#0「nwell without net to power」。需重建代表性 _calibreLVS.rule_ + .erc.summary。
3. **【备选】CDL check**（physical_verify, L1）：check_cdl.py 逻辑。需重建代表性 CDL 输入。

## 下一轮（r250）计划
- **第一件事：清 DEBT:1** — 合成 xqeql 的 B档 case（首选 hcell 生成器，L1 representative 资产，k≥8 断言，§4.9 三假 + negative）。
- 若 hcell 逻辑从 trace 反推不足，退而用 grep_erc_rule 子任务（ERC rule parse + nwell-power 检测）。
- 资产重建依据：trace 中 agent read 的文件路径 + U 轮描述的输入格式 + grep_erc_rule.py/find_hcell2.py 最终版可读（在 ~/Desktop，可 SSH 取）。
