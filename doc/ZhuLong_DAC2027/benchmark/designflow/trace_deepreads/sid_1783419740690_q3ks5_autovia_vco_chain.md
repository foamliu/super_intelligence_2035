# 深读笔记 — sid 1783419740690_q3ks5 (AutoVia FastXOR / Calibre VCO 环境链根因)

- **trace 源**：`/home/e0014566/.cline/data/sessions/1783419740690_q3ks5/1783419740690_q3ks5.messages.json`（138 msgs，516KB，agent=lead）
  - user=e0014566，host=hfeg0pkn001，mc=190，cwd=/home/e0014566/test_power_analysis_4
  - tools 命中：223 calibre + 33 virtuoso + 25 cellview + 21 dbCreateInst + 19 "lang":"skill" → physical_verify/layout_virtuoso AutoVia 调试
- **用户轮**（仅 2 条 user text，其余 70 条 user 都是 tool_result）：
  - **U#0（纯意图，A-档合格 seed）**：「调用你的run_code工具，运行 run_autovia_agent.il. 如果出现 SKILL 沙箱不可用的问题请排查出为什么不可用，哪里出问题了，并且退出。」
  - **U#70（用户给出修复假设 → hint，不可作 A-档 task）**：「我在命令前显式设置 VCO=aoi , 能解决这个问题吗？」
- **assistant 调试链**（关键产物）：
  1. `read_files` 读 `run_autovia_agent.il`（753 行 AutoVia SKILL 脚本，内联了 run_autovia_config.il，定义 `IMCleGetTimeString`/`RunAutoViaNoGui`）。
  2. `SandBox_MCP_Server__run_code`（SKILL 沙箱）内联提交 → 脚本**成功加载并执行**，但运行时报错 `*Error* strcat: argument #18 should be either a string or a symbol (type template="S") - 8` at line 381。
     - 根因：assistant 手动简化提交时把 `sprintf(nil "%d" coreNum)` 去掉，`coreNum=8`（整数）直接喂给 `strcat` → 类型不匹配。原始文件用 `sprintf` 转字符串是对的。
  3. 沙箱基本功能探针：`printf/strcat/getCurrentTime/parseString/dbOpenCellViewByType` 全可用；`leGlobalVariables` 是 list（length 33，car=nil, cadr=utGV_SkillVer），`->` 操作符可用（`leGlobalVariables->layerMap` = `/apps/imctf/libs/dfii/cxmt10G4plus/current/layer.map`），`~>` 不可用；`leGetLayerMap` 是 undefined function。
  4. 全量内联脚本再跑 → 报 `Unknown SKILL error`（代码过大），但 `print_log` 显示脚本**已跑完 AutoVia 大部分流程**，到 FastXOR 步失败：`*Error* fastxor run failed for cell->layout_austin6, net->vss!, check /proj/train/AI_Virtuoso/ver/autovia/austin/layout_austin6/vss/fastxor/xor.log`。
  5. `run_commands` 检查 FastXOR 目录 + `runme` → 发现 `runme` 用了错误的 `-layermapping` flag（正确应为 `-layermap`，是 assistant 提交时的拼写错误）。
  6. **结论（U#0 回答）**：SKILL 沙箱**完全可用**；失败是应用层问题——(a) strcat 类型不匹配来自手动简化、(b) FastXOR runme 的 `-layermap` 拼写错误。
  7. **U#70 追踪 VCO 环境链**（核心洞察）：`run_commands` cat `dbdiff`/`calibre_env`/`calibre_vco` 启动脚本：
     - `dbdiff` wrapper：`DEV_VCO=$VCO`（保存用户 VCO）→ `. calibre_env` → `VCO=$MGC_VCO`（**覆盖**用户 VCO）→ exec dbdiff.real。
     - `calibre_env`：`MGC_VCO=strict_vco_check=yes $MGC_HOME/bin/calibre_vco`（调用 calibre_vco 算 MGC_VCO）。
     - `calibre_vco` 第 77-79 行：`if test -n "$USE_CALIBRE_VCO" then VCO=$USE_CALIBRE_VCO`（USE_CALIBRE_VCO 分支优先级最高）> 宿主探测（RHEL8→aoi）> 默认 aok。
  8. **验证**：`USE_CALIBRE_VCO=aoi VCO=aoi dbdiff ... -write_xor_rules xor.rule` → exit 0，`xor.rule` 生成；`calibre -drc xor.rule` → `xor.rule.summary` 生成。仅 `VCO=aoi`（无 USE_CALIBRE_VCO）会被 dbdiff 的 `VCO=$MGC_VCO` 覆盖掉。
  9. `editor` 修改 `run_autovia_agent.il`：在 FastXOR 步前加 `setShellEnvVar("VCO" "aoi")` + `setShellEnvVar("USE_CALIBRE_VCO" "aoi")`，并在 runme 脚本里加 `export VCO=aoi` / `export USE_CALIBRE_VCO=aoi`。
  10. SKILL 沙箱验证：`setShellEnvVar` 可用，`getShellEnvVar("VCO")`="aoi"，dbdiff result=0，生成的 runme 含两行 export。
- **金标准（用户实际接受）**：修复 = 「同时设 `USE_CALIBRE_VCO=aoi`（被 calibre_vco 尊重、流入 MGC_VCO）+ `VCO=aoi`（下游工具），仅设 VCO=aoi 不够（被 dbdiff 覆盖）」+ 「修 runme 的 `-layermap` 拼写」+ 「SKILL 脚本里 setShellEnvVar」。xor.rule / xor.rule.summary 真实生成。
- **正交子主题（本 case 取）**：把 VCO 环境链根因分析 + FastXOR runme 拼写诊断**自动化**为离线 Python 工具 `vco_chain_fix.py`——给合成 dbdiff/calibre_env/calibre_vco 启动脚本链 + runme + xor.log + 用户修复提议，做：VCO 链重构（谁设/谁覆盖 VCO + USE_CALIBRE_VCO 分支探测）→ 提议是否足够 → 正确修复环境变量 → runme `-layermap` 拼写诊断 → 修复产物（runme_fixed.sh / vco_env_patch.il）→ report.json。
- **判分（15 条独立条件 a–n+o）**：见 `reference/EDA-Eval-DesignFlow-VcoChainFixGen-001/check.py`。隐藏 B1（异名 VCO=aok / cell layout_bristol / net avdd / typo -layermapfile，覆盖链）/B2（clean：dbdiff 不覆盖 VCO，runme 正确 → 提议足够）/B3（calibre_vco 空文件 → 非零退出）。
- **自验**：REF check() PASS 15/15（True）；negative_selftest 3 fakes 全 FAIL（fake_empty→c 缺 fix 文件 / fake_print_expected→g A 值 aoi≠aok / fake_core_deleted→e chain bool 硬编码 False≠True）；§4.9 三假全 FAIL ✓；k_rationale=k_check=15≥8 GATE ✓。
