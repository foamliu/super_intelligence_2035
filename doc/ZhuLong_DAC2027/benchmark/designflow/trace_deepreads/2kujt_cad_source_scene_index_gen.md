# deepread — 1794877997747_2kujt (steveny @ hfeg0pnd001, mc=243)

- **session**: /home/steveny/.cline/data/sessions/1794877997747_2kujt/1794877997747_2kujt.messages.json (152 msgs, 1017KB)
- **host**: hfeg0pnd001 (ssh from .75 OK)
- **keywords**: pyaether:1370;aether:364;virtuoso:204;netlist:94;cellview:88;verilog:65;drc:63;schematic:55
- **domain**: layout_aether (pyaether dominant)

## 用户真实意图

steveny 维护 eda_agent 技能仓库（/home/steveny/context-infrastructure/rules/skills/eda_agent/），该技能让 AI agent 在 CAD 工具里找工具/方案。问题：仓库维护了多份「静态 CAD 工具索引/目录」文件（如 pyaether/01_foundation/02_cad_framework_analysis.md 16729B、03_cad_tools_index.md 78KB layout index 等），复制了活 CAD 源码内容，导致 (1) 上下文 15k+ 行膨胀，(2) 静态索引路径随源码演进过期 → agent「找工具找不到」。

用户两轮指令：
- msg#0: "review eda_agent skill 是否符合持续学习的技能，我想让它在 cad tools 里面找工具到时候找不到，感觉上下文的组织有问题"
- msg#20: "注意 source of truth 只维护一份，降低未来修改成本"
- msg#77: "search apis 和 cad 源码没关系，只是一个 api rag 知识库，是不成体系的。cad 源码是针对不同场景的解决方案，是相对成体系的。另外，cad 源码靠 grep 找效率太低了，需要一个索引的"

## agent 工具链与关键产物

1. **eda_skill_linecounts.py** (msg#15-18): 量化上下文重量（行数扫描），基线 15,497 行。
2. **eda_skill_delete_catalogs.py** (msg#21-25): 删除 86KB layout index + 78KB utility index + 8 个静态 catalog（复制活 CAD 源码的第二份）。
3. **eda_skill_scan_deadlinks.py** (msg#40-43): 扫描 skill 树中引用已删文件名的死链（### file / L行号: [text](deleted.md) 格式）。
4. 重写 3 个 SKILL.md 路由文件 + 5 个 00_INDEX.md/README.md，把「找工具」从静态列表改为活检索流程。
5. **gen_cad_tools_index.py** (msg#92-121): 核心 deliverable —— CAD 源码场景索引生成器（唯一维护入口）：
   - `scan_tree(root, func_re, suffix)`: os.walk 跳过 `.`/`.SOS`/`__pycache__`，按子目录分组，PY_FUNC_RE=`^\s*def\s+(\w+)\s*\(` / SKILL_FUNC_RE=`^\s*procedure\s*\(\s*(\w+)\s*\(`，funcs[:8]
   - `check_curated_refs(aether, cdns)`: 校验 10 个 known_refs (base, rel) 是否 `os.path.isfile`，缺失加入 missing
   - `--write` 写 cad_tools_raw.md；默认报告模式
   - 真实扫描：465 PyAether + 615 SKILL files；8 curated refs 过期（le/IMClePinReplaceWithLabel.py、le/leViaPlusMinus.il、le/leAutoVia.il→实际 le/IMCleAutoVia.il、le/leMarkNet.il、ut/utHilight.il 等）
6. **eda_skill_locate_tools.py** (msg#112-115): 在真实源码里定位 8 个过期引用的正确路径（证明旧 catalog 路径 stale）。
7. 修复后：dead-link scan 0 hits，context 15,497→10,762 行。

## 关键判断（reframe）

gen_cad_tools_index.py 的核心扫描+校验逻辑是干净纯 Python 子问题（无需 /apps/imctf 访问，标准库即可），固化成可判分模块 cad_index_gen.py：输入 mock CAD 源码树（pyaether/.py + skill/.il + known_refs.json）→ 输出 report.json（platforms/by_subdir/funcs/total_files/total_funcs/stale_refs/valid_refs）。

子型 `cad_source_scene_index_gen` 首例。与 steveny 既有 C case（无）正交；与同 shard 的 SkillEditManifestVerify（adaml，SKILL.md 编辑校验）正交（彼校验文档编辑，此扫描源码+校验引用存在性）。

## 合成 (B 档 mock reframe)

- A=sample_a/cad_src: pyaether/ le(2 .py + 1 .il 跳过)/se(1)/ut(1) + skill/ le(2)/ut(1)/se(1) = 8 files, 12 funcs; known_refs 8 条, 3 stale (le/IMClePinReplaceWithLabel.py, le/leMarkNet.il, ut/utHilight.il)
- B=hidden/cad_src: pyaether/ le(1)/db(1)/hi(1) + skill/ le(2)/ut(1) = 6 files, 10 funcs; known_refs 7 条, 3 stale (le/IMClePinReplaceWithLabel.py, le/leViaPlusMinus.il, ut/utHilight.il)
- A/B 在 total_files(8 vs 6)、total_funcs(12 vs 10)、子目录({le,se,ut} vs {le,db,hi}+{le,ut})、stale rels、文件名全异 → 反硬编

## case

EDA-Eval-DesignFlow-CadSourceSceneIndexGen-001 (cad_source_scene_index_gen, k=16, layout_aether)
