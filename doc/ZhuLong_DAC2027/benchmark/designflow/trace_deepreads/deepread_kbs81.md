# 深读笔记 — kbs81 (e02141@hfeg0pkn001, mc=96, eda_other)

- **session**: `/home/e02141/.cline/data/sessions/1790128216866_kbs81/1790128216866_kbs81.messages.json` (141 msgs, 717850 B)
- **kw**: 18 pyAether · 8 virtuoso · 8 netlist · 8 hspice · 8 "lang": "pyAether" · 5 spectre · 5 calibre
- **用户轮** (真实 `<user_input>` 逐字):
  - U@0: `帮我配置 swb-python-api` — 环境配置任务（另一任务，不入本 case）
  - U@60: `帮我创建一个名为try0923的新 SWB 项目，路径是 /home/e02141/devops/，添加 sprocess、sdevice 和 svisual 三个工具，sprocess 上添加参数 Lg（扫描 0.15、0.25、0.35）和 NWell（扫描 1e17、5e17），然后保存。` — **纯提需求（创建 SWB 项目+加工具+加扫描参数+保存），未给根因/修复 → A档任务说明**
  - U@96: `bash collect_env_info.sh > env_info.txt 2>&1` — 运行收集脚本（另一任务，不入本 case）
- **assistant 工具链** (针对 U@60):
  - RAG_MCP_Server__search_apis × 多次（查 swbpy2 Deck/Gtree/AddTool/AddParam API）
  - read_files `~/.cline/skills/swb-python-api/skill.json`、`~/devops/example/gtooldb.tcl`/`gtree.dat`/`gvars.dat`（参考已有项目结构）
  - read_files `~/devops/PlanarNMOS_Example/gtooldb.tcl`/`gtree.dat`/`gvars.dat`/`gscens.dat`
  - editor 写 `/home/e02141/.cline/scripts/data/create_try0923.py`（swbpy2 Python 脚本）
  - editor 写 `/home/e02141/.cline/scripts/data/run_create_try0923.sh`（一键 shell）
  - SandBox_MCP_Server__run_code × 多次（pyAether/skill sandbox 均 Connection refused / 30s 超时，不可用）
  - run_approved_command（profile hello_world，UID 不匹配，不可用）
- **金标准** = `create_try0923.py`（assistant 产出，工具真实产物，人工复核 API 调用序列正确）。sandbox 不可用故未实跑，用户未反馈结果；金标准取脚本本身（与 r233 D2pHandoffDirGen / r232 ViewCopyInstCount 同模式：代码生成类 case，gold = 产物脚本）。
- **gold 脚本关键 API 调用序列**:
  1. `from swbpy2 import *` / `from swbpy2.gtree import Deck, Gtree` / `from swbpy2.tool import Standards`
  2. `deck = Deck('/home/e02141/devops/try0923/')`
  3. `tree = deck.getGtree()`
  4. `tree.AddTool("sprocess","sprocess")` / `tree.AddTool("sdevice","sdevice")` / `tree.AddTool("svisual","svisual")`
  5. `tree.AddParam("sprocess","Lg",["0.15","0.25","0.35"])` / `tree.AddParam("sprocess","NWell",["1e17","5e17"])`
  6. `deck.save()`
  7. `deck.getPath()` / `tree.AllToolNodes()` / `tree.AllParamNames()`（introspection）
  8. `deck.finalize()`
  9. `__main__` 守卫：`try: from swbpy2 import Deck; except ImportError: 提示用 gpythonsh 运行; sys.exit(1)`
- **A档 faithful 合成**:
  - 任务说明 = U@60 逐字原文（不脱敏、不改写、不补全）
  - 接口固定：`mode:design_flow` + `entry_point=outputs/submit.zip` + `test=check(deliverable, workdir)`
  - task_brief.md 只写交付接口与文件位置（≤3 行：交付 create_swbb_project.py 进 submit.zip，配置驱动读 config.json，用 swbpy2 API 创建+保存）
  - 资产：prompt.txt(U@60) + task_brief.md + swbpy2_api_ref.txt(swbpy2 API 签名，供 SUT 参考) + config_A.json(try0923 配置)
  - 金标准忠实重建为配置驱动版 `create_swbb_project_ref.py`（从 config.json 读 project_path/tools/params，调 swbpy2 API）— 不是抄 gold 而是泛化 gold 的 API 调用模式
  - 判分只对事实（API 调用序列+参数值），不对措辞
- **隐藏 B**: 2 tools (sprocess/sdevice, svisual 移除) + params Tox(4值)/Nch(3值) on sprocess + project_path 在 /tmp（结构对立，反硬编码 A 的 try0923/svisual/NWell/5e17）
- **隐藏 B2**: 4 tools (含 sdevice3d) + params Lg(5值) on sprocess + Vds(3值) on sdevice + project_path distinct（随机化，跨输入一致性）
- **判分机制**: check.py 嵌入 swbpy2 stub 包写入临时目录，SUT 脚本以 cwd=临时目录 + PYTHONPATH=临时目录 子进程执行，stub 把所有 API 调用记录到 JSONL 文件，check 读回比对（静态 a-d + B 子进程 e-l + B2 子进程 m-n，14 条独立条件）
- **覆盖域**: eda_other（TCAD/Sentaurus Workbench 工具脚本自动化）
- **结论**: A档 faithful 合成交付 EDA-Eval-DesignFlow-SwbProjectCreate-001（eda_other L1-static+subprocess 14 conds a-n）
