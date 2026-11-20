# 深读 trace 记录：ukkn7（ERC_AI_CHECK pipeline · virtuoso→aether flow 改写）

> 即时令 IX §五 要求：本轮先深读 1 条真实 trace，理解完整对话流，下一轮提炼成 case。本文件为脱敏深读笔记。
> 原始 messages.json 1.6MB / 867 msgs / 447 user / 420 assistant / 340 run_commands / 436 tool_result，
> 已 scp 到 .75 workdir 解析后 close_session keep=false cleaned（不入库，不入 git）。
> 与并行 agent 的 m2vah（hfeg0pkn001 / rscalc-autovia-powerfill）深读**无交集**（不同用户/不同 session/不同主机/不同主题），避免冲突。

## trace 来源（脱敏）
- host: `hfeg0plg91`（10.129.8.223；同 session 亦出现在 hfeg0pkn003 / hfeg0plg15，NFS 共享 home）
- user_hash: `8adf72139dee`（sha1[:12] of real username）
- session_file: `1789370647360_ukkn7`（实际路径 `<ip>:/home/<USER>/.cline/data/sessions/1789370647360_ukkn7/1789370647360_ukkn7.messages.json`，1,616,161 字节）
- session_msgs: 867
- summary.tsv match_count: **1478**（全语料最高单会话命中）
- keywords: `aether:1496;virtuoso:1148;netlist:811;analog:195;cadence:167;cellview:67;lib.defs:54;schematic:48`
- tool_use 分布: run_commands 341 · editor 39 · read_files 33 · search_codebase 11 · RAG search 5 · list_allowed_files 3
- real_task_summary: ERC_AI_CHECK pipeline 跑通 + 子 section 过滤修复 + step3+ virtuoso→aether flow 改写

## 用户真实目标（11 条 user message 提炼）
用户手头有一个 **ERC（Electrical Rule Check）AI_CHECK pipeline**，工作目录 `/home/<USER>/work/ERC/`：
- 代码在 `ERC/codes/`（`run_all.sh` 编排 + `run_step0/1/2/3.sh` + Python `prepare_new_netlist.py`/`analyze_errors_v1.py`）
- 数据在 `ERC/drcpa/`（`ERC_Wesign.csv` 等）
- **核心需求**：基于 `run_all.sh` 对 `drcpa/` 数据跑完所有 follow，**只看 ERC 报错里的 2.1–2.8 section**
- **关键纠正 1**：`filter_erc_by_section` 当前只支持按主 section 号（如 "2"）过滤，不支持子 section（"2.1"）→ 需修复
- **关键纠正 2**：这是个 **aether 项目**，不是 virtuoso → step3+ 的验证 flow 现在只有 virtuoso `.il` 脚本，**需要改写一套 aether flow**
- **环境线索**：用户一般通过 `vir` 命令进入选择项目界面，选定项目和版本后通过 `aetherLE` 或 `aetherSE` 进入 aether
- **运维波折**：virtuoso 一直调不起来 → 用户判断是登陆节点问题 → 换登陆节点重试 → 最终明确"是 aether 项目不是 virtuoso"

## agent 工作过程（340 run_commands）
1. **探查**：读 `run_all.sh`（step0–4 定义）、`prepare_new_netlist.py`、`analyze_errors_v1.py`、`filter_erc_by_section`、ERC CSV section 分布
2. **诊断 section 过滤缺陷**：ERC CSV 含 2.x/3.x/5.x 多 section，`filter_erc_by_section` 只支持主号 "2"，不支持 "2.1"；用户只要 2.1–2.8
3. **改 Python**：编辑 `prepare_new_netlist.py` 让 `--erc-section` 支持子 section（踩 `\r\n` Windows 换行符坑 → 改逐行替换修复）
4. **数据就位**：把 `drcpa/` 数据软链接到 `codes/`（pipeline 要求同目录）；定位 python3 `/apps/local/python/Python-3.10.18/bin/python3`
5. **跑 step1**：`ERC_SECTION='2.1,...,2.8'` 跑 `prepare_new_netlist.py` 生成 netlist + project_config.json
6. **step3 verify 调试 virtuoso（长线受阻）**：尝试启动 virtuoso → `LD_LIBRARY_PATH`/`libstdc`/`CXXABI` 版本冲突（IC617 ISR23 / IC618 ISR11 / oa_v22.60.036），大量 `sleep 25 && tail step3_verify.log` 轮询
7. **用户纠偏**：用户指出"是 aether 项目，启动 aether 不是 virtuoso"+ 换登陆节点
8. **pivot 到 aether**：定位 aether `/apps/empyrean/tools/aether_new/tools/aether`；发现 wrapper 的 `tbcload1.7` 路径错（`$PANDA_HOME/../platform/$PLATFORM/lib/tbcload1.7` 实际在 `.../tools/platform/linux26-x86_64/lib/`）；写本地 `lib.defs` INCLUDE aether 的 lib.defs 但 skip `amsLib`；写 `test_aether.il`（`dbOpenCellViewByType("drcpa_top" "ddr5top" "schematic" nil "r")`）验证
9. **最终用户指令**：step3 及以后的 flow，现在代码只提供 virtuoso `.il`，项目是 aether 的，**需要改写一套 aether flow**

## 最终状态
trace 在"改写 aether flow"任务**进行中**结束（agent 正在调 aether 启动 / tbcload1.7 路径）。交付尚未完全闭环——这恰好是个**真实、hard、多步调试+改写**任务，天然有区分度。

## 关键文件/产物（路径含真实用户名，建 case 时脱敏）
- 工作目录：`/home/<USER>/work/ERC/`
- 编排：`codes/run_all.sh`（step0–4）、`codes/run_step0.sh`…`codes/run_step3.sh`
- Python：`codes/prepare_new_netlist.py`（含 `filter_erc_by_section` 子 section 缺陷 + `\r\n` 坑）、`codes/analyze_errors_v1.py`
- 数据：`drcpa/ERC_Wesign.csv`、`drcpa/vtable_real.csv`
- 配置：`codes/llm_config.json`、`codes/project_config.json`、`codes/lib.defs`
- virtuoso step3 脚本：`codes/*.il`（待改写为 aether）
- aether：`/apps/empyrean/tools/aether_new/tools/aether`，`vir` → `aetherLE`/`aetherSE`
- 运行产物：`codes/pipeline_logs/step*.log`、`codes/results/`、`codes/.pipeline_tmp/`

## 可提炼的 design_flow case 方向（下一轮）
**case 主题**：ERC pipeline 子 section 过滤修复 + step3+ virtuoso→aether flow 改写
- **prompt**（自然语言任务目标，反映真实场景）：给定 ERC_AI_CHECK pipeline（`run_all.sh` 编排 step0–3 + Python `prepare_new_netlist.py`/`analyze_errors_v1.py`）与 step3 的 virtuoso `.il` 验证脚本。任务：(1) 修复 `filter_erc_by_section` 使 `--erc-section` 支持子 section 过滤（如 `2.1,2.2,...,2.8`，当前只支持主号 "2"）；(2) 由于该项目是 **aether** 项目而非 virtuoso，将 step3+ 验证 flow 从 virtuoso `.il` 改写为 aether flow（经 `vir`→`aetherLE`/`aetherSE` 进入 aether，`dbOpenCellViewByType` 打开 `drcpa_top/ddr5top/schematic`）；(3) 跑 pipeline 只产出 ERC 2.1–2.8 section 的报错。交付： patched `prepare_new_netlist.py` + 改写后的 aether step3 flow 脚本 + ERC 2.1–2.8 报告，打包 `outputs/submit.zip`。约束：不破坏 step0–2 既有行为；aether flow 需正确处理 lib.defs（INCLUDE aether lib.defs，skip amsLib）与 tbcload1.7 路径。
- **attachments**（合成/脱敏，因真实 ERC_Wesign.csv/.il/run_all.sh 为私有）：合成的 `run_all.sh` + `prepare_new_netlist.py`（带子 section 缺陷 + `\r\n` 坑）+ virtuoso `step3.il` + 样本 `ERC_Wesign.csv`（含 2.x/3.x/5.x section）+ `lib.defs` + `llm_config.json`，入 `assets/<task_id>/`
- **entry_point**：`outputs/submit.zip`
- **test**（Python 双参 `check(deliverable, workdir)`）：解 zip → 断言：
  (a) `prepare_new_netlist.py` 含子 section 过滤逻辑（正则 `2\.[1-8]` 或等价，且主号 "2" 不再整段吞 2.x）；
  (b) aether step3 flow 脚本存在，含 aether 入口（`aetherLE`/`aetherSE`/`dbOpenCellViewByType`），**不含** virtuoso 直调（`virtuoso -nograph`/`cds.lib` virtuoso-only）；
  (c) ERC 报告只含 2.1–2.8 section（无 3.x/5.x）；
  (d) lib.defs 处理正确（INCLUDE aether lib.defs，skip amsLib）。
  参考 `docs/rtl_design_flow_case_design.md` §3.2/3.3 的脚本/报告交付件 test 写法。
- **test 语言**：Python（pyAether 本地自测，校验脚本/报告产物，不强求真跑 aether daemon——规避 aether host run_code 超时 block）
- **metadata.domain**：analog（ERC/aether schematic 校验）或新建 `verification` 子向
- **metadata.trace_source**：见本文顶部 trace 来源块
- **难度**：hard（多步调试 + 跨工具改写 + 真实环境坑：`\r\n`/tbcload1.7 路径/lib.defs）
- **资产缺口**：真实 ERC_Wesign.csv + .il + run_all.sh 是 e0031668 私有；建 case 时用等价合成资产（可照真实结构仿造：ERC CSV 用 `2.1_…/2.8_…/3.1_…/5.2_…` 行，prepare_new_netlist.py 嵌入真缺陷，step3.il 用 virtuoso SKILL 占位）。test 校验产物结构 + section 过滤 + aether 入口，可全本地 Python 跑。

## 备注
- 本 trace 的真实 aether 跑通依赖 aether daemon（agent 调 run_commands 340 次大半在调 virtuoso/aether 启动）；pi 被测若真跑会撞 aether host run_code 超时 block。**判分用产物校验（Python 本地）规避**：test 只校验 zip 内的 patched 脚本 / aether flow 脚本 / ERC 报告，不强求 pi 真跑 EDA。
- 即时令 IX §三.3：prompt 里可有真实文件名/工具名/指标（run_all.sh / aetherLE / dbOpenCellViewByType / drcpa_top/ddr5top / 2.1–2.8），但脱敏真实用户名/路径（<USER> 占位）。
- **下一轮**：照本节"可提炼的 design_flow case 方向"合成 assets + 写 prompt + 写 Python 双参 test + 入 `EDA-Eval-DesignFlow.jsonl`（追加，不建新文件）+ pi 调试。
