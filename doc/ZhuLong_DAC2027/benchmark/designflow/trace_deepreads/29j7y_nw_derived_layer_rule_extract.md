# trace_deepread: 29j7y — NW* 产生的pattern (DRC rule deck NW-derived layer/rule extract)

**session**: `1790080851129_29j7y.messages.json` · user `lizwen` @ `hfeg0pkn002` (10.129.2.11)
**mc=60** · keywords: `drc:288;lvs:40;aether:32;.spi:8;calibre:7;cellview:6;.cdl:6;pyaether:5`
**fetched**: 237KB / 44 msgs (26 user / 18 assistant) · 2026-09-22 20:40 ~ 20:46
**agent model**: glm-5.2 @ cxmt-glm52

## 真实用户意图（逐字）

U#0（idx 0，唯一实质性 user_input）：
> `NW* 产生的pattern`

（其余 25 个 user-role msg 全是 tool_result，无新增用户输入。）

## agent 工具链（18 assistant turns）

1. **idx 1**: search_codebase(`NW\*`, `NW.*pattern`, `NWWell`, `nwell.*pattern`) + RAG search_apis("NW pattern generation nwell", lang=pyAether) — search_codebase 全 timeout，RAG 返回 aeCrtLdmosLayout/emyGCellPattern（弱相关）
2. **idx 4**: RAG search_apis("NW pattern nwell generation", lang=skill + "NW star pattern wildcard", pyAether) + list_allowed_files(/home/lizwen, depth2) — 返回 techGetMfgGridResolution/aelEnvListGlobs（弱相关），list_allowed_files 发现 /home/lizwen/3DPV, /home/lizwen/DRC, /home/lizwen/workarea/drc_patterns, /home/lizwen/techlib 等目录
3. **idx 8**: list_allowed_files(/home/lizwen/workarea/drc_patterns, /home/lizwen/workarea/drcpat, /home/lizwen/DRC, depth2) — 发现 DRC_Pattern_LIB/drcPatterns, DRCPatLib/drcPat 目录
4. **idx 12**: read_files(/home/lizwen/DRC/DRC.rule, /home/lizwen/DRC/DRC.test.rule) + list_allowed_files(drcPatterns/drcPat depth3)
5. **idx 16**: search_codebase(`NW\*`, `\bNW\b.*pattern`, `\bNW\b.*rule`) + read_files(/home/lizwen/techlib/dptAll.py) — search_codebase 又 timeout
6. **idx 19**: run_commands(grep -n -i 'NW' DRC.rule | head -100, grep -rn 'NW\*' DRC/, find -name '*NW*') — **run_commands 被 policy 拒**（非 approved profile）
7. **idx 21**: editor(/home/lizwen/search_nw.py, python grep NW script) — **写被拒**（outside writable roots）
8. **idx 23**: get_agent_policy_status() — 查可写根
9. **idx 25-29**: editor(/home/lizwen/workarea/search_nw.py) 写被拒 → editor(/home/lizwen/.cline/scripts/search_nw.py) 写被拒 → read_files(/home/lizwen/.cline/plugins/agent-policy.json) 查 policy → 发现可写根 /home/lizwen/.cline/scripts/data
10. **idx 29-31**: editor(/home/lizwen/.cline/scripts/data/search_nw.py) 写成功（python grep NW layer definitions in DRC.rule） → run_approved_command(profile=python-runner, /home/lizwen/.cline/scripts/data/search_nw.py) — **运行成功**，输出 NW layer defs
11. **idx 33**: editor(search_nw2.py, grep derived layers using NW) → run_approved_command — 输出派生层
12. **idx 35-37**: editor(search_nw2.py 续) → run_approved_command — 输出更多 NW 派生层 + DRC 规则
13. **idx 39-41**: read_files(DRC.rule 多段 line 3130-3140/3360-3370/3495-3535/5898-...) + read_files(line 5991-6170) — 读取 NW DRC 规则完整列表
14. **idx 43**: **最终 prose 汇总**（见下）

## 真实交付（idx 43 最终 text）

agent 产出结构化 prose 汇总 `NW* (N-Well) 产生的 pattern 完整汇总`：
1. **NW 层定义**: `NW = COPY NW_drawing //8:0` (Line 3135)
2. **派生层 20+**（4 类）：
   - Well 相关: ALL_DRAWING_WELL=OR DNW NW, NW_HOLE=HOLES NW INNER, PW=NOT BORD(OR NW AVT_ARRAY), PWnet, PW_IN_DNW, PWB
   - 电压分类: NW_GROUND=NET AREA RATIO NW OVER GROUND_PAD, NW_EXTER_POWER, NW_INTER_POWER, NW_FIX=OR..., NW_VAR=NOT NW NW_FIX
   - 器件识别: PACT=AND PDIF NW, NSUB=AND(AND NDIF DIF_NOINT_PG)NW, PNP_emitter=(AND PDIF BJT_PNP) INSIDE NW, PNP_collector/base, PNP_SEED, SV_NW_RES_OPEN, P_DIODE, AT4dummy=(OR AT4_CMP AT4_DUMMY2) CUT NW, NSUB_INT_DNW
   - 连接: CONNECT NW DNW, CONNECT NSUB NW
3. **DRC 规则 30+**（NW_* 命名，6 类）：W(width)/S(spacing)/A(area)/ENC(enclosure)/HA(hole area)/CL(concave step)，core/peri 双值，thin/thick Gox 区分
4. **DNW 规则涉及 NW**: DNW_EXT_005, DNW_O_006, DNW_W_007, DNW_S_008
5. **总结**: 派生层 20+ + DRC 检查 30+，GROUP NW NW_? 统一管理

## 域判定 & reframe

- **domain**: physical_verify（Calibre DRC rule deck 解析）✓ C-domain（drc:288/calibre:7 真实物理验证操作关键词，非 r712 l4tre PDK-release-note false-positive）
- **真实任务形态**: analysis-Q&A / explain（用户问「NW* 产生什么 pattern」，agent 解析 deck 给 prose 答案）→ **11-15 task初衷 B类复活**（旧规则判「prose 非脚本 / analysis-only」weak，新标准合法）
- **reframe**: mock-behavioral · 新子型 `drc-deck-derived-layer-rule-extract`（承 r645-r712 family）
  - 真实 2.19MB Calibre deck + license path-dependent → 纯 stdlib 微型 fixture
  - candidate = SVRF deck parser：层定义布尔算子 → 传递闭包(direct/transitive/depth) → 规则名 PREFIX==SEED 过滤 → W/S/A/ENC/HA/CL 分类 + value → CONNECT/GROUP → 确定性 JSON
  - **distinct** vs r710 DrcRunStatusAnalyze(DRC log 解析) / r707 BwzDummyFlowExtract(TVF deck dummy flow) / r704 DrcDeckRuleUpdClassify(deck-block 更新分类) = 本例 **DRC rule deck 派生层闭包 + 命名规则抽取**
- **fixture**: A(NW/12 derived/12 rule) / B(DW 反 A 全异) / B2(MW minimal edge)

## case 落地

- **case_id**: EDA-Eval-DesignFlow-NwDerivedLayerRuleExtract-001
- **k_rationale = k_check = 24 ≥ 8** GATE PASS ✓
- **3 negatives** distinct first_fail (c/d/e) ✓
- **jsonl_C**: 438 → 439 · **cases/C**: 438 → 439
- **ledger_C**: 29j7y claimed → case (covered 443 → 444, physical_verify 203 → 204)
- **自验**: reference 24/24 PASS + 3 negatives 全 FAIL + round-trip PASS ✓
