# 深读笔记 · o1hsg · wl-adjacent-detect skill references 补全

- session: `1795092542726_o1hsg` · user `ziyuny` @ `hfeg0pnd001` (10.129.32.189) · mc=229
- domain: layout_aether (Calibre DRC SVRF deck + skill 文档；物理验证版图相邻 WL 检测)
- scan keywords: drc:1597 / calibre:569 / pdk:194 / .gds:194 / lvs:30 / aether:3
- NMSG=264 (USER=149 / ASST=115)，messages.json 1.9MB
- ledger: claimed r1534（synthesis DEBT 目标）

## 真实用户意图（一句话）

用户新建了 skill `/home/ziyuny/.cline/skills/wl-adjacent-detect`（Workflow 型：GDS + WL 命名正则 → Calibre DRC 找相邻 WL → parser 提取 → CSV 对表），但 `references/architecture.md` 与 `references/absolute-path.md` 两个理解层文档是 4 字节 "null" 占位空文件。用户让 assistant 读通 skill（SKILL.md + deck + debug 史 + 可执行资产），**起草补全这两个 reference 文档**。

## assistant 工具链（关键路径）

1. `list_allowed_files` skill 目录 → 结构：SKILL.md + references/{architecture.md(空), absolute-path.md(空), troubleshooting.md, wl_adjcent_llm.md} + scripts/{rep2csv.py, census_names.sh, wl_adjacent.drc, A_mblx744_e_wlo_WL.gds, rundrc.sh, parse_wl_pairs.py}
2. `read_files` SKILL.md + troubleshooting.md + 两脚本（census_names.sh / rep2csv.py）；两个空 reference 文件 read 返回 null
3. `editor` 写 check_ref_files.py → `run_approved_command` 确认两个 reference 文件确为 4 字节占位
4. `list_allowed_files` 外部资产目录 `/home/ziyuny/zl/wl_adjcent/`（deck/parser/rundrc.sh/12 个 .rep/CSV 产物）确认存在
5. `read_files` rundrc.sh（5 入参接口）+ deck `wl_adjacent.drc` 第 120-132 行 → 发现 SKILL.md 声称的「L132 VARIABLE wl_patterns 死代码」属实，全文核实 deck
6. 汇报理解 + 提问；用户选「我来起草补全这两个文件」
7. `skills skill-creator` 取 skill 文件写作纪律；`list_allowed_files`+`read_files` 收集三份素材：deck 全文、`wl_adjcent_llm.md`（19 轮 debug 史 / run19 分步表 / R5 命名教训 H_WLo1<510>）、`absolute-path-discipline` skill（通用规则 + Job 3063498 亲历案例）
8. `editor` 两步法（insert_line + 删尾部 "null" 残留）写入 architecture.md(4969→最终 10349B) + absolute-path.md(2569→最终 4684B)
9. 后续小修补（[52] 多次 editor 微调 architecture.md / SKILL.md）

## 关键产物（已 scp 到 .75 workdir 验证，r1534）

- **SKILL.md**：skill 主规格。输入契约（gds_path/--pattern/space_um 缺省 0.182/gds_primary/rundir/--parity）、运行目录规则、6 步流程（pattern 翻译→rundrc.sh 跑 Calibre→transcript 体检→parse_wl_pairs→rep2csv→CSV）、PDK 视角（NET 网络提取 + EXTERNAL OPPOSITE 对边间距 < 0.182 + DFM TEXT/PROPERTY/MERGE 属性附加 + NODAL MULTI 广播 + VSTRING 聚类 + 12 个 DFM RDB ASCII rule check）
- **deck `wl_adjacent.drc`**（scripts/ 下，run19 架构静态 deck）：步号↔行号见 architecture.md 速查表。关键 sed 锚点：L158-161 `NET <金属> "H_WL?<?>"`（step1 网络提取）、L209-211 `EXTERNAL < 0.182 OPPOSITE`（step6 对边间距）、L122-151 TVF member() 骨架 + L132 `VARIABLE wl_patterns` 死代码未接线、L408-515 step8 12× DFM RDB ASCII 输出 .rep
- **wl_adjcent_llm.md**（references/，15531B）：19 轮 debug 全史。run19 核心（NET AREA RATIO 选网）、R5 命名教训（最初假设 s23m2wle<55>，真实命名 H_WLo1<510> 家族）、run15-18 四条 union 死路（ORNET/LAYER SET/plain OR/STAMP 全死）、run8 ordinal 越界 23 万条
- **architecture.md**（最终 10349B）：理解层文档。run19 deck 步号↔行号速查表 + 术语对照 + 数据通路（网名属性流 12 条链 + 间距几何流）+ 关键设计决策的为什么（12 条 per-source 链不能合并、间距条带跑在无属性层、OPPOSITE metric 防密集连片等）
- **absolute-path.md**（最终 4684B）：路径纪律专篇。规则 + 两层原因（bsub CWD≠提交机 / sandbox CWD 不定）+ Job 3063498 亲历失败案例（相对路径 → calibre OPEN1 exit4 → 修复 cd $RUNDIR + 全绝对 → Job 3064887 DONE）+ 本 flow 逐参数落点清单 + 唯一豁免（deck 默认 LAYOUT PATH 相对）+ 排查手法
- **troubleshooting.md**（8464B，已存在非空，本轮不动）：排错层

## LIVE 分类（preliminary）

**LIVE-NA**。deliverable = 两个 markdown 理解层文档（architecture.md + absolute-path.md）。check 实质依赖的是候选**从 B 的源材料（deck + debug 史 + SKILL.md）正确抽取事实**写入文档，不是真实 EDA 工具产物。§2.1 桩体检 Q2=否：shape-correct-but-wrong（文档结构对但事实全错）骗不过 oracle 逐事实比对（B 的 space/pattern/run#/命名/Job#/行号/GDS 名逐项校验 + anti-hardcode tripwire 禁 A 专有 token）。judge_layers=[L0,L1]。

## 合成计划（DEBT，下轮 r1535 交付）

- **deliverable**：`submit.zip` 含 `references/architecture.md` + `references/absolute-path.md`
- **A（SUT 可见）**：真实 SKILL.md + deck + llm.md（ziyuny 真实参数：space 0.182 / pattern "H_WL?<?>" / run19 / 命名 H_WLo1<510> / 死代码 L132 / 12 rep / 4 pin 层 HSP/M3A/M2A/M1A / 3 金属 M1/M2/M3 / Job 3063498 / GDS A_mblx744_e_wlo_WL.gds）
- **B（hidden）**：变体源材料——deck 做系统性 sed 替换（space→0.150 / pattern→"WWL_*<*>" / 命名→WWL_b<330> / Job→4058821 / GDS→B_mblx998_n_wwl_WL.gds）+ 在死代码块前插若干注释行使 L132 漂移到 L145（制造行号差异，强化 anti-hardcode）+ llm.md 同步替换 run#/命名。结构（12 rep/3 金属/4 pin）保持一致以避免级联漂移失控；行号差异集中在死代码块后的局部漂移需重新 grep 确认
- **reference 解**：adapt 真实 architecture.md/absolute-path.md 到 B 参数（行号重 grep + scalar 替换）
- **check（≥10 独立断言）**：独立临时目录解 zip → 读两 md → ① architecture.md 存在 + absolute-path.md 存在 ② 含 B space 阈值 0.150 ③ 含 B pattern WWL_*<*> ④ 含 B 死代码行号 145 ⑤ 含 B run 号 run23 ⑥ 含 B 命名家族 WWL_b<330> ⑦ 含 12 rep / step8 输出结构 ⑧ 含 OPPOSITE 对边间距概念 ⑨ absolute-path.md 含 B Job 4058821 ⑩ 含 bsub CWD≠提交机 原因 ⑪ anti-hardcode tripwire：两 md 不得含 A 专有 token（0.182 / H_WLo1<510> / 3063498 / A_mblx744）
- **3 neg**：naive_empty（空 md→断言①②FAIL）/ naive_print_A（硬编码 A 文档→tripwire ⑪ FAIL + ②③④FAIL）/ neg_missing_file（只交一个 md→①FAIL）
- **自验**：ref 解跑 check 全 PASS；3 neg 全 FAIL；SKIP_RUN=1 eval/run_one.sh 框架部署 OK

## 风险

- B 变体 deck 行号漂移需在 .75 上实测 grep 确认（不可手算），下轮 r1535 先做
- doc 类 case 的「有牙」依赖 oracle 逐事实比对 + anti-hardcode tripwire，已设计到位；k≥10 满足 §4.3
- 源材料全部自包含（已 scp 验证可达），无需 .75 真跑 EDA ⇒ LIVE-NA 稳妥

## 本轮（r1534）选料结论

5 个 r1531 留待 full-deepread 的 C-pure fresh 候选全部 full-deepread 完毕：
- td5sc（wenhanz mc1 drc:5）：mc 过低，env-debugging 同 x3t64，弃（不 claim）
- w4hlp（jcgu mc231）：porting_flow GUI launcher 迭代，无数值化 deliverable，parked
- x8iwg（ziyuny mc229 lvs:1834）：LVS 分析报告 produce-task 但输入文件 /rundata/ddgoa 对 e0031982 perm-denied，assets 需从 trace 重建；session 夹杂 skill-rename 机制，parked（deferred）
- lzy92（shanliny mc229 pex:1331）：PEX batch debug 60+ throwaway 脚本，env-debugging dominant，parked
- **o1hsg（ziyuny mc229）**：skill references 补全，doc-authoring 合法意图，源材料全自包含可达，**选定 DEBT 合成**

⇒ 再次确认 r1495/r1531 结论：mc≥5-300 band C-domain physical_verify/layout fresh 池以交互式调试/迭代 session 为主，clean produce-task 稀缺；o1hsg 是本轮唯一可合成候选。
