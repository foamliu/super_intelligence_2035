# Deepread: 1789454632664_t1xjg — SKILL(.il) → pyAether flow port (ERC step4a)

- **trace**: `1789454632664_t1xjg.messages.json` (341 msgs, 175 user / 166 assistant)
- **user/host**: e0031668 / hfeg0pkn003 (10.129.2.12)，mc=704
- **agent**: lead (cline)，tools: run_commands×113, read_files×12, editor×34, RAG_MCP_Server__search_apis×10
- **domain**: schematic_netlist (pyAether schematic 遍历 + 网名分类)

## 用户意图（3 条非空 user 轮）
1. (idx 0) 主任务：「ERC_AI_CHECK 代码在 ERC/codes 下，请基于 codes 下的 run_all.sh，对 ERC/drcpa/ 下的数据文件跑完所有 follow，只看 erc 报错里面的 2.1-2.8 的，目前流程卡在 step3，step3 及以后的 flow，现在的代码只提供了 virtuoso 环境的脚本.il，这个项目是 aether 的，需要你改写一套 aether flow」
2. (idx 297)「现在流程是什么状态了？」
3. (idx 309)「帮我再完整跑一遍，更新下日志」

## 真实工作流
- 原 ERC 流程 step3/step4a/step4b 用 Virtuoso SKILL(.il)：`verify_paths_batch.il` / `verify_virtuoso_paths.il` / `find_correct_path.il` / `get_cell_chains.il` / `run_path_verify.il`。项目实为 Empyrean Aether（pyAether），无 Virtuoso，流程卡 step3。
- agent 探索 `/apps/empyrean/tools/aether_new/tools/pyaether/`（example/labs/docs），确认 pyAether API：`emyInitDb` / `emyCdbaNS` / `emyScalarName` / `emyString` / `emyLib.find+getAccess` / `dbGetAllLibs·dbGetAllCells` / `dbOpenCVByType(lib,cell,view,"schematic",mode)` / `cv.getTopBlock()` / `block.getInsts()·getNets()·getTerms()` / `inst.getName·getCellName·getLibName(ns, emyString)`。
- 关键坑：`aether -nc` 跑 pyAether 脚本要 `PY_INIT_FILE=<script>`；**禁止 `QT_QPA_PLATFORM=offscreen`**（此构建无 offscreen 插件会 SEGV），需真实 X display。脚本结束必须 `os._exit(0)` 终止 aether。
- 产出 5 个 pyAether 脚本：`aether_db.py`（共享 DB helper）、`aether_verify_paths.py`、`aether_verify_virtuoso_paths.py`、`aether_find_correct_path.py`、`aether_get_cell_chains.py` + `run_aether_py.sh` 启动器；改 `run_verification_pipeline.py` / `run_all.sh` / `run_step3.sh` 把 .il 引用换成 .py。
- 另修：`run_all.sh` 裸 `python3` 解析到系统 3.7.1（缺 libpython3.7m.so.1.0），加 `PYTHON3=/apps/local/python/Python-3.10.18/bin/python3`。

## 用户接受的金标准（末轮 assistant 文本 + 产物）
- step3 Aether Verification Pipeline：Pass1 (aether_verify_paths.py) 235→216 OK / 18 FAIL_INST / 1 FAIL_NET (91.9%)；Pass2 (aether_verify_virtuoso_paths.py) 216/216 100%。
- 产物：`top_refined_verified.csv` (216 条)、`.pipeline_tmp/cell_chains.csv` (216 nets = 208 INTNET + 8 PORT)、`forceNet_spice.txt` / `forceNet_virtuoso.txt` (各 714 行 / 99 cells / 215 rows / 133 distinct nets)。
- 日志 `pipeline_logs/step3_verify.log` / `step4a_classify.log` / `step4b_forcenet.log` 全部刷新为 Aether 成功结果。

## 本 case 取的核心：step4a `get_cell_chains.il` → pyAether
- `.il` 语义：读 `virtuoso_run.conf` (TOP_LIB/TOP_CELL/VER_CSV) → 打开 top schematic → 对 VER_CSV 每行按 `Path` 的 `.` 分隔实例链逐级 `inst~>name` 精确匹配下降，拼 `cellChain`（每级 `inst~>cellName`），叶子 block 上对 `netName` 分类：terminals 先匹配→PORT，nets 匹配→INTNET，否则 bus 位 `da<8>` → bus range `DA<17:0>` 回退（rexMatchp + 区间比较）→PORT/INTNET，都没→NOT_FOUND。写 `cell_chains.csv` (num,Path,netName,netType,cellChain) + summary `Processed N nets`。
- `aether_db.py` 等价封装：`emyCdbaNS` + `dbOpenCVByType` + `block.getInsts/getNets/getTerms` + `inst.getName/getCellName/getLibName(emyString)` + 大小写不敏感 lib/cell 解析 + bus bit/range 正则回退 + `net_classify`。
- 大小写不敏感（Virtuoso cell 名与网表可能大小写不同）是真实陷阱。

## 判分设计（本 case）
- L1-static + stub-functional：check.py 注入一个 stub `pyAether`（背后是已知小原理图 A: schtest/top+inv+refpdk p18/n18，B: schtestB/top2+nand2），subprocess 真跑候选 `aether_get_cell_chains.py`，断言 cell_chains.csv 结构 + PORT/INTNET/NOT_FOUND/cellChain/多层下降/bus-range；隐藏 B 重跑反硬编码。
- 15 条独立断言 (a–o)；5 negatives 命中 5 个不同 label (h/j/k/l/o)；NEG_RC=0；ref PASS。
- 与 SubSecFilter-001(ukkn7) 互补：后者只做 CSV 子段 2.1–2.8 过滤；本 case 做 SKILL→pyAether 的 schematic 遍历 + 网名分类改写（真实 pyAether DB API）。
