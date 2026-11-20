# 深读笔记 — 1789624027491_t45kv（PR job 启动方式选择 · CXMT idjoa/dejoa V0_APR）

- **trace**: `1789624027491_t45kv.messages.json`（zhigangw @ hfeg0pkn002, mc=53, 43 msgs, 412KB）
- **路径**: `/home/zhigangw/.cline/data/sessions/1789624027491_t45kv/1789624027491_t45kv.messages.json`
- **领域**: pg_layout（Innovus APR / Virtuoso AI-place / Place&Route 启动）→ shard C
- **工具分布**: list_allowed_files×多 · read_files×多 · search_codebase×2 · get_agent_policy_status×2 · (agent=lead)
- **关键词命中**: floorplan:208 · innovus:123 · pyaether:63 · netlist:54 · aether:50 · analog:41 · schematic:34 · cellview:29
- **用户意图轮**:
  - USER#1 (idx 0, mode=act): `how to start pr job` —— 提出需求（PR = Place & Route / APR 启动）。A 档不可行：意图过简，gold 是一段说明性回答而非工具产物 → B 档合成。
  - USER#2 (idx 38, mode=act): `do you search my own dir only for apr scripts?` —— 指出 agent 只在家目录找，miss 了 /proj/ 下的真实主 flow。属「指出根因/局限」轮，不作 A 档任务说明（按红线 #2），但其揭示的 policy-block 教学点构成 case 的核心判定。

## 真实流程（faithful）

```
USER "how to start pr job"
  → agent 探查 readable roots (/home/zhigangw/Desktop, /home/zhigangw)
  → 读 readme.idjoa / 模拟电路优化README / 时序分析README / cxmt_autoPR_AIplace_10_15_debug.il
  → 读 mywork/apr/innovus/{flooplan_init,run_finish,inn2vir_G4B,inn2vir}.tcl
  → 读 zwu_workload_test_*_run.sh / cxmt_autoPR_AIplace.il / zwu_dummy_function_startInnovus.il
  → agent 给出 3 种 PR 启动方式（AUTOPR SKILL GUI / Innovus tcl / workload shell）
USER "do you search my own dir only for apr scripts?"
  → agent 承认: Agent Policy Engine 限制 readable roots = /home/zhigangw/Desktop + /home/zhigangw
  → 真实主 APR flow 在 /proj/idjoa/V0/workdir/zhigangw/inn_apr/src/apr_tmp_flow (从 /shprojruns/lhioa/V0/ver/apr_flow/aprRun 拷贝), /proj//shprojruns//apps/ 全在 readable roots 之外 → 读不到
  → agent: 之前回答不完整, 家目录 mywork/apr/innovus/ 可能是旧拷贝/参考拷贝, 请用户贴主 flow 关键片段
```

## 三种 PR 启动方式（gold 知识）

1. **CXMT AutoPR AI-place SKILL GUI**（数字/stdcell block 首选）:
   - `load("/apps/imctf/.../AiPlaceIT/cxmt_autoPR_AIplace.il")` → `cxmt_autoPR_autoPlacingGUI()`
   - GUI: Target Cell / Action Type(floorplan|place|estimate|congestion) / Place Method(Flat|Hierarchy) / Place Algorithm(Min_Wires_Length|As Schematic) / stdcell libs / firstRow(R0|MX) / prBoundary
   - 直调 SKILL: `cxmt_autoPR_AIplace(cellInfo plugCell spacerCell stdLib stdCell firstRow actType ... )`
   - 后端: `python /apps/imctf/.../AiPlaceIT/place.py <date> <netlistDir> <instancesFile> <outDir> <user> '<prBoundaryPoints>' <lib> <cell> <actType> null <placeMethod> <placeStyle> null <switch_cell> null`
   - 访问限制: 仅 dejoa V0_APR 授权用户(含 zhigangw)
2. **Innovus APR tcl flow**（`/home/zhigangw/mywork/apr/innovus/`）:
   - `module load innovus/2139_ISR9_os7` 或 `bsub -Is -q tqueue innovus`
   - `source FF/init.tcl` → `flooplan_init.tcl` → `placeDesign` → `clockDesign` → `routeDesign` → `run_finish.tcl` → `inn2vir*`
   - inn2vir_G4B.tcl(G4B) / inn2vir.tcl(ICEM): Innovus→Virtuoso 导出(GDS/DEF/netlist/SPEF)
3. **Workload test shell**（`zwu_workload_test_2_2025Sep1110838_run.sh`）: 批量跑 workload 测试。

## 主 flow / policy block（核心教学点）

readme.idjoa 引用的真实路径（全部在 readable roots 之外 = /home/zhigangw/* 之外）:
| 路径 | 用途 |
|---|---|
| `/proj/idjoa/V0/workdir/zhigangw/inn_apr/src/apr_tmp_flow` | **主 APR flow 工作目录** |
| `/shprojruns/lhioa/V0/ver/apr_flow/aprRun` | 主 flow 的原始拷贝源 |
| `/proj/idjoa/V0/workdir/zhigangw/inn_apr/src` | APR 源脚本 |
| `/proj/idjoa/V0/workdir/zhigangw/dc_shell/` | DC 综合脚本 |
| `/proj/idjoa/V0/workdir/zhigangw/lpe/lpe/` | LPE/StarRC 提取 |
| `/apps/pdc_ai/eda/` | AI Place 引擎 + 导出 |
| `/apps/imctf/cad/init/settings_cdns/skill/le/AiPlaceIT/` | 官方 CXMT AutoPR SKILL |

Agent Policy Engine: `readable_roots=/home/zhigangw/Desktop + /home/zhigangw`, `writable_roots` 同。**主 flow 被 policy 挡住** → agent 应优先抛此事实, 而非用家目录脚本假装是答案。

## 合成（B 档 L1-boundary）

- **case**: `EDA-Eval-DesignFlow-PRStartMethodSelect-001`（pg_layout, synthesized, L1-boundary）
- **交付**: `pr_start_selector.py`（单文件 Python, CLI `<bundle.json>`/`--help`/无参 exit1, 读工作区探查 bundle JSON, 按 7 类优先级分类, 输出 VERDICT/ROOT_CAUSE/RECOMMENDED_ACTION/CONFIDENCE, exit 0 定论/2 AMBIGUOUS+INCONCLUSIVE/1 坏参）
- **bundle schema**: `readable_roots` / `referenced_project_paths` / `found_scripts[{path,type,tool}]` / `virtuoso_available` / `innovus_available` / `design_stage` / `tech` / `project` / `user` / `host`
- **7 verdicts 优先级**: ①MAIN_FLOW_POLICY_BLOCKED(referenced 含 apr_tmp_flow|apr_flow|inn_apr|aprRun 且不在 readable_roots 下 → request_access/high/exit0, **优先级最高**, 即便家目录有可用脚本也先抛) ②AUTOPR_SKILL_GUI(cxmt_autoPR_AIplace skill + virtuoso_available==true → load_skill_gui/high) ③INNOVUS_TCL_FLOW(innovus tcl + innovus_available==true → run_innovus_tcl/high) ④WORKLOAD_TEST_SHELL(workload_test shell → run_workload_sh/medium) ⑤AMBIGUOUS_MULTIPLE(≥2 方式脚本都在但 *_available 都缺失 → ask_user/low/exit2) ⑥NO_PR_ENTRY_FOUND(found_scripts 空 + 无 blocked 引用 → broaden_search/medium) ⑦INCONCLUSIVE(found_scripts 非空但无识别的 PR tool, 或单一方式脚本但 *_available==false → provide_details/low/exit2)
- **可用性拣选**: ≥1 方式「可用」时按 AUTOPR>INNOVUS>WORKLOAD 取一种; 仅当 ≥2 脚本都在但都缺可用性信号才 AMBIGUOUS
- **资产 A** = inputs/prompt.md(场景+7 类根因+优先级+CLI/输出/退出码契约)+task_brief.md+bundle_A.json(zhigangw, readable_roots=/home/zhigangw/Desktop+/home/zhigangw, referenced 含 /proj/idjoa/.../apr_tmp_flow + /shprojruns/.../aprRun, found_scripts 含 cxmt_autoPR skill×2 + innovus tcl×4 + workload shell×2, virtuoso/innovus_available=true → **MAIN_FLOW_POLICY_BLOCKED**)
- **隐藏 B** = 10 个嵌入 check.py 的 bundle(B1-B10, 结构≠A, 用户/路径/项目均不同: linwei/zhangs/wangl/chenj/zhouy/tianl/sunw/pengz/gaom; 覆盖 MAIN_FLOW_POLICY_BLOCKED/AUTOPR/INNOVUS/WORKLOAD/AMBIGUOUS/NO_PR_ENTRY/INCONCLUSIVE/坏bundle/优先级边界(blocked+home autopr 仍 BLOCKED)/边界(引用路径在 readable_root 内不 block+autopr)), 不进 SUT 沙盒
- **16 条断言**①-⑯(k=16, a-p): ①(a)zip+py_compile ②(b)--help exit0+提bundle/无参exit1+stderr ③(c)B1 MAIN_FLOW_POLICY_BLOCKED+request_access+ROOT_CAUSE含被block路径+exit0 ④(d)B2 AUTOPR_SKILL_GUI+ROOT_CAUSE含AI auto-place/cxmt_autoPR+load_skill_gui+high ⑤(e)B3 INNOVUS_TCL_FLOW+run_innovus_tcl+ROOT_CAUSE含Innovus且含floorplan ⑥(f)B4 WORKLOAD_TEST_SHELL+run_workload_sh+ROOT_CAUSE含workload ⑦(g)B5 AMBIGUOUS_MULTIPLE exit2+ask_user+low ⑧(h)B6 NO_PR_ENTRY_FOUND+broaden_search+exit0+medium ⑨(i)B7 INCONCLUSIVE exit2+low+provide_details ⑩(j)B1-B7 4字段齐全+VERDICT/ACTION属固定枚举 ⑪(k)跨输入守卫B1输出含linwei/abc且不含A的idjoa/zhigangw ⑫(l)确定性B2两次stdout一致 ⑬(m)坏bundle B8缺readable_roots exit1+stderr ⑭(n)A≠B A输出含idjoa；B2/B3不含idjoa且不含zhigangw ⑮(o)边界B9(blocked+home autopr)→MAIN_FLOW_POLICY_BLOCKED；B10(引用路径在readable_root内+autopr)→AUTOPR_SKILL_GUI ⑯(p)随机3条B×3种子verdict+exit稳定
- **自验**: ref PASS 16/16(local CHECK PASS) + negative_selftest NEG_RC=0(5 fake: fake_empty→a[语法错]/fake_always_autopr→c/fake_no_autopr_branch→d/fake_no_innovus_branch→e/fake_hardcode_a_paths→k 各击穿不同条件全 FAIL@distinct labels a,c,d,e,k) + §4.9 三假提交全 FAIL(空壳→b/只print期望→b/参考解删核心[policy-block分支]→c); test 字段 md5==磁盘 check.py 一致(4bce26adfa9f5a2afbd264c054ffa064, 15624B). k_rationale=k_check=16>=8 GATE PASS. pg_layout 域+1(18).
