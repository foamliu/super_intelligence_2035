# Deepread — sid 1787821853675_z72bi (sophiaw / hfeg0plg09 / mc=167 / 182 msgs / 1.28MB)

**域**：layout_aether (pyAether — SPICE 仿真编排 skill 编写)
**用户**：sophiaw (E0030524, sophia.wei@cxmt.com, PDC/APIP/Design-AI) — **新用户**（shard C 首次覆盖）
**agent**：cline (lead)

## 用户意图演进（genuine user turns，逐字原文）

- **msg0 (HANDOFF/seed)**：`/skill-creator 帮我生成一个可以自动跑finesim,presim,nanospice测试仿真的skill` —— **A-档合格 seed**：提出目标（生成自动跑 FineSim/PreSim/NanoSpice 测试仿真的 skill），未给根因/未给修复方案。⇒ A-档 seed。
- msg49：`/home/sophiaw/.cline/skills/spice-sim-runner 路径下的SKILL.md我用gvim打开是乱码的` —— 报告 gvim 乱码（现象，非根因）。
- msg63：`现在重新用 gvim 打开 /home/sophiaw/.cline/skills/spice-sim-runner/SKILL.md` —— 重开。
- msg67：`请调用这个仿真运行的skill，创建一个简单的网表和testbench` —— 调用 skill 造 netlist+testbench（依赖 msg0 的 skill 已存在）。
- msg138：`沙箱为什么不能运行` —— 问沙箱不可运行（现象）。
- msg152：`在路径下有一个ansim的软件包，请你分析一下` —— 分析 ansim 包（第二任务，与本 case 无关）。
- msg165：`anasim` —— 拼字纠正（anasim，非 ansim）。

## assistant 工具链（关键）

- **msg0-37**（skill 生成）：`find /home/sophiaw -name INDEX.md -path skills`、`RAG_MCP_Server__search_apis`（seGuiRunSimulation/anpGetSimHspiceDInfo/cbGetSimHspiceDInfo/anpGetSimSpectreInfo/seGuiShowNetlist/aeExportNetlistCDLShow/cdfGetSimInfos 等 19 次语义检索）、`RAG_MCP_Server__get_api_details`（4 次）、`mkdir -p .../spice-sim-runner`、`cat > SKILL.md << 'SKILLEOF'`（写出完整 skill）、`cat > INDEX.md`（更新索引）。
- msg49-64（乱码修复）：`vim --version`、备份 `~/.vimrc`、`printf 'set encoding=utf-8...'`、`vim -es` 验证、`nohup gvim SKILL.md`。
- msg67-133（demo 仿真）：`mkdir spice_sim_demo`、`cat > inverter.sp`（CMOS inverter subckt）、`cat > run_sim.sh`、`cat > README.md`、`cat > run_pyaether.py`、`finesim tb_inverter.sp`（LD_PRELOAD/LD_LIBRARY_PATH 修复、`.measure dc vol find v(out) at=1200→120→when v(in)=1.2V` 三轮迭代）。
- msg138-147（沙箱诊断）：查 `ip_port.json`、`chmod o+x .cline/data`（权限修复）。
- msg152-172（anasim 分析）：`find / -iname anasim`、定位 `/apps/imctf/cad/script/Frontend/AnasimPro/`（core/tabs/scripts/designer/project_adapter/benchmark）。

## gold（用户实际接受）

msg0 的产物 = `/home/sophiaw/.cline/skills/spice-sim-runner/SKILL.md`（用户 msg49 用 gvim 打开=接受查看；msg67 调用=接受使用）。SKILL.md 结构：
1. YAML frontmatter（name: spice-sim-runner / description: 自动运行 FineSim/PreSim/NanoSpice 测试仿真…）
2. 元数据（类型 Workflow / 适用场景 / 执行环境 pyAether / 创建日期 2026-08-27）
3. 目标（一句话：网表生成→仿真器配置→仿真运行→结果收集→结构化报告）
4. 验收标准 8 条（环境初始化/仿真目标就绪/仿真器配置/网表生成/仿真运行/结果保存/资源释放/报告输出）
5. 可用资源与边界：仿真器表（FineSim/PreSim/NanoSpice + Fast SPICE/SPICE + SPICE(hspiceD)）+ 核心 API 清单（环境与设计管理 emyInitAether/aeOpenDesign/aeGetCurDesign/aeCloseDesign；MDE Platform 仿真 MdePlatSession.open/createByDesign/getSetting/netlistAndRun/allResultNames/save/close/getLastError；MDE Platform 设置 MdePlatSetting.getTest/getCorner/addModelFileForCorners/addParameterForCorners/addGlobalParameter/copyCorner；MDE Platform 测试 MdePlatTestSetting.setTranAnalysis/enableTranAnalysis/addExpressionOutput/switchJobPolicy；MDE Platform Corner MdePlatCorner.addModelSection/addParameterValue/addTemperature/enable/disable；MDE Platform 结果 MdePlatResult.saveResultsToDir/savePlotSnapShot/reEvaluate/getName；传统 GUI seGuiRunSimulation/seGuiShowNetlist/seGuiCrtSimProbe/dmExportNetlist/cdfSetSimInfo；外部工具 aeRunCmdWithSocket/aeSetSubProcessEnv）+ 边界与限制
6. 方法论建议：仿真路径选择 + MDE Platform 依赖顺序 9 步 + 仿真器配置 3 方式 + 分析类型 + 异常处理
7. 输出规格：SPICE Simulation Report 模板（Design/Simulator/Path/[Environment][Setup][Simulation][Output][Cleanup]/Status/Errors）
8. 已知陷阱（初版待补充）

## 合成方案（B-档 L1-boundary，与存量正交）

`EDA-Eval-DesignFlow-SpiceSimSkillGen-001`：把 SKILL.md 的生成固化为 bundle-driven 渲染器 `spice_sim_skill_gen.py`。bundle 提供 skill_name/title/description/metadata/goal/simulators/acceptance_criteria/api_catalog[{category,apis[{api,sig,desc}]}]/dependency_order/report_template/pitfalls/boundary_notes；渲染器产出 SKILL.md（frontmatter+元数据+目标+验收标准+资源与边界(仿真器表+API 清单+边界)+方法论(依赖顺序)+输出规格(报告模板)+已知陷阱），stdout 报告 Skill/Out/Lines/Size/Sections/APIs/Simulators/Criteria。

**为什么 B-档**：A-档需 SUT 自己经 RAG search_apis 发现 pyAether API，但 SUT 沙盒只配 eda_flow MCP（无 RAG_MCP_Server），API 发现不可复现 → B-档把 API catalog 放进 bundle，SUT 只做结构化渲染。

**与存量正交**：r136 DigitalDesignFlowSampleGen（doc 渲染）/r143 SvrfFragMerge（片段合并）是 Markdown 渲染；本案是 **Cline Skill 文件（SKILL.md）生成**——frontmatter + 多级 API 表 + 依赖顺序 + 报告模板，断言对 skill 文件结构（frontmatter/元数据/验收标准/API 清单完整性/依赖顺序/报告模板/陷阱表），🚫 不对措辞。

资产 A=inputs/prompt.md+task_brief.md+bundle_A.json（spice-sim-runner，FineSim/PreSim/NanoSpice，真实 8 验收标准 + 完整 pyAether API catalog + 9 步依赖顺序 + SPICE Simulation Report 模板）。
hidden B=**3 个嵌入 check.py 的 bundle**：
- B1 干净 mixed-sim-runner（Spectre/HSPICE/ngspice，全结构，验全部 15 条结构断言）
- B2 跨输入守卫 adc-tb-sim-skill（Spectre/ngspice，验输出+stdout 不含 A 专属 token：spice-sim-runner/FineSim/PreSim/NanoSpice）
- B3 坏 bundle 缺 api_catalog（exit1+stderr+不写输出）

**15 条断言** ①-⑮ (k=15, a-o)：①(a)zip+py_compile ②(b)CLI(--help/-h exit0+usage 含 bundle；无参/坏 bundle exit1+stderr) ③(c)B1 exit0+写出 SKILL.md ④(d)B1 frontmatter name+description 匹配 bundle ⑤(e)B1 元数据 type/scope/env/created 全字段匹配 ⑥(f)B1 目标含 bundle.goal ⑦(g)B1 验收标准列出全部条目(计数+逐条归一化匹配) ⑧(h)B1 仿真器表含全部 simulators(name+netlist) ⑨(i)B1 核心 API 清单含全部类别下全部 API(api 名+desc 出现) ⑩(j)B1 方法论依赖顺序按序列出全部步骤 ⑪(k)B1 输出规格含报告模板关键标记(Design/Simulator/Path/Status) ⑫(l)B1 已知陷阱含全部 pitfalls(name) ⑬(m)跨输入守卫 B2 输出+stdout 不含 A 专属 token ⑭(n)确定性 B1 两跑 stdout+md5 一致 ⑮(o)坏 bundle B3 缺 api_catalog exit1+stderr+不写输出。

**失败模式（教学点）**：①硬编码 A 专属 skill_name/仿真器名跨 bundle 穿(B2 守卫击穿) ②漏 API 表/仿真器表 ③frontmatter 缺失 ④依赖顺序乱序/缺步 ⑤报告模板缺标记 ⑥坏 bundle 仍写文件 ⑦非确定性。

leakage 隔离：SUT 沙箱只含 assets(prompt/task_brief/bundle_A)，check.py/reference/jsonl/test 不进沙箱，hidden B 嵌 check.py。
