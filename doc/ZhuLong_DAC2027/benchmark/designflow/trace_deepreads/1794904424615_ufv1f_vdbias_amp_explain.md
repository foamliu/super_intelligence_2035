# Deepread: 1794904424615_ufv1f — AG_VdbiasStdAmpv1 电路工作原理解释

## trace_source
- **session**: 1794904424615_ufv1f.messages.json
- **user**: e0017841 (jason7.jiang, TD/CTD/DTCO)
- **host**: hfeg0plg56 / 10.129.35.75 (NFS-shared home, 也出现在 hfeg0plg53/10.129.35.69)
- **match_count**: 47 (cellview:141; analog:83; cmos:75; schematic:62; pyaether:42; verilog:21; aether:15; dbget:9)
- **model**: glm-5.3-flash
- **cwd**: /ai_sandbox/drgqx/V0/agentdir/e0017841
- **scene**: aether assistant (engine=aether)
- **started**: 2026-11-17T08:33:44Z
- **规模**: 30 msgs / 503KB / inputTokens 449846 / outputTokens 53584
- **domain**: schematic_netlist + analog_context（D-pure）

## 用户真实意图（3 轮提问）
1. msg[0]: 「你能看到我目前打开的这个电路吗？AG_VdbiasStdAmpv1」— 确认 agent 能读当前打开的 Aether 原理图
2. msg[20]: 「为什么停了」— 催促 agent 给出结论
3. msg[22]: 「好 帮我详细解释这个电路的工作原理，是如何实现输出Vdbias!全局偏置电压的」— **核心任务**：解释 AG_VdbiasStdAmpv1 如何产生全局 Vdbias 偏置电压

**任务形态 = analysis-Q&A（电路原理解释）**，合法真实意图（2026-11-15 令：analysis-Q&A 不是 weak）。

## agent 工具链（assistant 行为）
- `list_allowed_files` → 列工作区 26 个文件（ampv1_full.txt / ampv1_params.txt / deep_top.txt / deep_std.txt / extract_*.py / gen_vdbias_pdf.py / Vdbias_Signal_Chain_Analysis.pdf 等，均为前序会话的提取产物）
- `RAG_MCP_Server__search_apis` / `get_api_details` → 查 `mdeGetCurrentLibCellView` / `aeGetTopLevelCellView` / `aeGetWndCellViewId` / `emyDesign` 类
- `run_approved_command` shell-runner → 跑 get-username.sh 得 `e0017841`
- `SandBox_MCP_Server__run_code` pyAether → `aeGetWndCellViewId()` / `aeGetCurDesign()` / `mdeGetCurrentLibCellView()` → 确认当前打开 `drgqx_cmos_analog / AG_VdbiasStdAmpv1 / schematic`
- `SandBox_MCP_Server__run_code` pyAether → 读 `emyDesign` 属性 `instCount=87 / netCount=80 / termCount=9` + 遍历 `instances` / `terminals` / `nets`（**这是关键产物**）
- `read_files` → 读 ampv1_full.txt / ampv1_params.txt / deep_top.txt / deep_std.txt / switch_probe.txt / ampv1_cdf_main.txt / net_check.txt / std_check.txt / gen_vdbias_pdf.py（**注意：这些 tool_result 在 trace 里返回空串——文件内容未回传到 trace，但 msg[18] 的 pyAether print_log 已含完整拓扑**）
- 最终输出：markdown 详解 AG_VdbiasStdAmpv1 工作原理（DDR5 全局 Vdbias 偏置链末级伺服放大器）

## 电路关键事实（从 msg[18] print_log 提取，真实拓扑）
- **Design**: drgqx_cmos_analog / AG_VdbiasStdAmpv1 / schematic
- **Counts**: inst=87, net=80, term=9
- **9 个端口（terminals）**: Fbin, VdbiasOut, EnV, EnVF, Fbout, BiasV<1:0>, VdbiasRef, BiasN, cc
- **87 个实例（name @ master）**:
  - PMOS: MP0<15:0>, MP1<3:0>, MP6<59:0>, MP7<39:0>, MP8<3:0>, MP9<7:0>, MP10<7:0>, MP11<7:0>, MP12<7:0>, MP13<7:0>, MP14<3:0>, MP15<7:0>, MP16<7:0> @ TECHLIB/ptk_lv/symbol; MP2,MP3,MP4,MP5 @ TECHLIB/ptk/symbol
  - NMOS: MN0<3:0>, MN1<3:0>, MN5<7:0>, MN6<7:0>, MN7<7:0>, MN8<7:0> @ TECHLIB/ntk_lv/symbol; MN2,MN3,MN4,MN9,MN10,MN11 @ TECHLIB/ntk/symbol
  - 子电路: I_AG_NmirUnit_182/183/184/185/187<1:0>, I_AG_NmirUnit_IPD_0/1/2<1:0> @ drgqx_cmos_analog/AG_NmirUnit/symbol（8 个 NmirUnit 实例）; I_AG_SetIDDAmpOopen_IPD @ AG_SetIDDAmpOopen; I_AG_SetIDDAmpIn_IPD @ AG_SetIDDAmpIn
  - 开关: I_switch_0/3/4/42/81/144/161/162/167/168, I16<1:0>, I17<1:0> @ TECHLIB/switch/symbol（12 个 switch）
  - 电源/地: I_vdd1_159, I4, I25, I26 @ vdd1; I_vss_135/140/141/142/143/170, I2,I3,I5,I6,I8,I9,I21 @ vss
  - 端口符号: PIN0,PIN1,PIN2,PIN4,PIN5,PIN6,PIN8,PIN10,PIN48 @ basic/in|io|opin
  - 其他: IprobeI_resld/IprobeI_PL/IprobeI_BT/IprobeI_extld/IprobeI_srcld/IprobeI_PR @ probeI; I0,I1 @ MarkHOV; I_noteSymbol_40 @ noteSymbol; I_noConn_166 @ noConn
- **80 个网络**（含位宽标注 <*N>）: 含 VdbiasOut, VdbiasRef, Pmirror, Neg, Pos, Pgate, ntail, mirrorl, preout, Pr_L, Pr_R, EnV, EnVF, Fbin, Fbout, BiasN, BiasV<1:0>, cc, vdd1!, vss! 等
- **完整 dump 已提取** → `designflow/trace_deepreads/_seed_ufv1f_ampv1_schematic_dump.txt`（4388B / 183 行）

## 系统定位（agent 最终解释）
AG_VdbiasStdAmpv1 是 DDR5 全局 Vdbias 偏置产生链的**末级"功率级"伺服放大器**：
```
AG_VdbiasGenCore → Idbias → AG_VdbiasTrs(I-V 4档) → VdbiasRef → AG_VdbiasStdAmpv1(本电路) → VdbiasOut = 全局 vdbias!
(电流域 trim)          (产生基准电压)                (强驱动闭环稳压)        (= 顶层 AmpOut)
```
GenCore 产生精确但无驱动能力的基准，本电路把 VdbiasRef 伺服放大为强驱动 VdbiasOut。

## 造题设计（revival · 下轮合成）
**case_id 候选**: `VdbiasAmpExplainProduce-001`（schematic_netlist, L1, k≥8）

**任务形态**: 给定一个 Aether 原理图 dump 文件（`Design` 行 + `Counts` 行 + `-- Instances --` 列表 + `-- Terminals --` 列表 + `-- Nets --` 列表，格式同 pyAether `emyDesign` 遍历输出），写一个 Python 脚本 `analyze_schematic.py` 解析 dump 并产出结构化 JSON 分析报告。

**A（SUT 可见）**: AG_VdbiasStdAmpv1 dump（87 inst / 80 net / 9 term，已提取到 _seed 文件）
**B（hidden）**: 另一电路 dump（不同 inst/net/term 计数、不同端口名、不同子电路），结构不同非换文件名。B 的构造方式：从 A dump 派生但实质性修改（删/增实例、改端口名、改子电路前缀），或找另一个真实 session 的 dump。

**deliverable**: `outputs/submit.zip` 含 `analyze_schematic.py` + A 的分析报告 `analysis_A.json`

**check()（≥8 独立断言，只跑 B）**:
1. submit.zip 解压含 analyze_schematic.py + analysis_A.json
2. 在独立临时目录跑 `python3 analyze_schematic.py <B_dump_path>` 产出 analysis_B.json 且为合法 JSON
3. analysis_B.json.instCount == B 真实 instance 数（check 独立解析 B dump 计算）
4. analysis_B.json.netCount == B 真实 net 数
5. analysis_B.json.termCount == B 真实 terminal 数
6. analysis_B.json.portList（sorted）== B 真实 terminal 列表（sorted）
7. analysis_B.json.subBlocks 正确识别 B 中 master cell 前缀（如 AG_NmirUnit / AG_SetIDDAmpIn / switch / ptk_lv / ntk_lv 分组计数）
8. analysis_B.json.busWidths 正确解析 `<N:0>` 位宽标注（如 MP6<59:0> → 60）
9. analysis_A.json（submit 内）的 instCount/netCount/termCount == A 真实值（87/80/9，防 agent 写一个 B 能跑但 A 报垃圾的脚本）
10. analysis_B.json.biasFlag 正确判断 B 是否为偏置电路（启发式：terminals 含 Vdbias 类 + 有 switch + 有 NmirUnit）

**3 负样本（全 FAIL）**:
- `fake_print_only.py`: 只 print A 的期望 JSON → 在 B 上跑出 A 的数字，断言 3/4/5/6 失败
- `hardcode_a.py`: 硬编码 A 答案 → 同上，B 断言失败
- `core_deleted.py`: 解析逻辑删空只返空 dict → 断言 2/3/4/5/6/7/8/10 失败

**test_rationale（k=10 条断言）**:
`10 条断言：① zip 含 analyze_schematic.py+analysis_A.json ② analyze_schematic.py 在 B dump 上跑出合法 JSON ③ instCount==B真实 ④ netCount==B真实 ⑤ termCount==B真实 ⑥ portList==B真实terminals(sorted) ⑦ subBlocks 正确分组 B 的 master 前缀 ⑧ busWidths 正确解析 <N:0> ⑨ analysis_A 的 inst/net/termCount==87/80/9（防 A 报垃圾）⑩ biasFlag 正确判断 B 是否偏置电路`

**质量闸门**: L1 离线 Python（读附件写脚本，不依赖沙盒工具），符合"用户意图=解释电路，交付=结构化分析报告（脚本产出）"的真实映射；hidden B 防背题；3 假全 FAIL；k=10≥8。

**复活阻塞**: 本轮预算不足以完成 check.py + reference + 3 负样本 + selftest + 自验。下轮直接从本 deepread 起步：A dump 已在 `_seed_ufv1f_ampv1_schematic_dump.txt`，构造 B（派生修改）+ 写 check.py + reference analyze_schematic.py + 3 负样本 + negative_selftest.py + 自验 + 追加 D.jsonl。

## parked 原因
预算（40min）不足完成合成+自验；不凑 weak case。A dump 已落盘，下轮可立即合成。
