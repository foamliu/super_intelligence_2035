# Deepread: 1795400302725_xlnvg (e0039602@hfhds201, mc=10)

## Session
- user: e0039602
- host: hfhds201 (10.129.32.75)
- session_file: 1795400302725_xlnvg.messages.json
- match_count: 10
- keywords: verilog:291;netlist:148;drc:32;waveview:7
- domain: digital (A-pure, verilog dominant 97%)

## User intent (原话)
> 请你给我解释一下这个项目下的代码，这是在做什么，执行代码的入口和命令是什么

## Trace flow
1. [0] USER: 解释项目代码、用途、入口和命令
2. [1] ASST: get_agent_policy_status → list_allowed_files /home/e0039602 (depth=2)
3. [3] ASST: list_allowed_files /home/e0039602/Documents (depth=2) + list_allowed_files verilog_lib_trans_v2.3.4 (depth=1)
4. [5] ASST: 发现多个候选项目，ask_question 让用户确认
5. [8] ASST: 列出候选项目：verilog_lib_trans_v2.3.4（最新版，README+run.py+run.sh+config.yaml+src/）、历史版本、finesim-fsdb-reader、fm_run 等

## Real project (verilog_lib_trans_v2.3.4)
- **用途**: Netlist cell-converter agent — 用大模型(glm-5.0)把 stdcell 网表里 simlib 缺失的 cell 转成 SystemVerilog simulation model，再用 xrun(ncvlog) 编译校准
- **入口**: run.py (803 行)，通过 run.sh 包装调用
- **命令**: `python run.py --offline` / `--prompt-only` / 默认线上
- **配置**: config.yaml (agent/paths/ref/xrun 四段)
- **src/ 模块**: netlist_parser, agent_client, xrun_check, rules_prompt, output_validator, parallel_worker, logic_check, expr_check, port_check, simlib_ref_db, report_writer, rules_engine, rules_fix, logging_util, prompt_monitor, llm_parser, offline_mapping, update_timingarc (22 个)
- **转换流程**: load_config → extract_missing(parse netlist+simlib) → build_prompt(rules_prompt+ref) → agent_convert(threadpool LLM) → xrun_check(compile+repair) → output_report

## Case design (B档 synthesized)
- **task_id**: EDA-Eval-DesignFlow-VlibTransToolAnalyzeProduce-001
- **A档不可行原因**: 真实工程树在 .75 /home/e0039602/Documents/ 下，SUT 沙箱不可达；且真实项目有 22 个模块 803 行 run.py，体积过大不适合做附件
- **B档合成**: 按 trace-faithful 结构合成 project_A（6 模块简化版，保留 run.py+run.sh+config.yaml+README+src/ 完整结构）+ hidden project_B（不同工具名/模块名/配置键/流程前缀）
- **判分**: 通用 analyze_tool.py 脚本在 hidden B 上跑，14 条独立断言（entry_point/shell_wrapper/cli_args/pipeline_stages/modules/config_file/config_top_keys/validation_gate + anti-hardcode A + determinism）
- **A/B 判别 token 零相交**: A={run.py,run.sh,config.yaml,stage_,netlist_parser,agent_client,xrun_check,rules_prompt,output_validator,agent,paths,ref,xrun} / B={main.py,start.sh,settings.yaml,step_,gate_parser,llm_api,ncsim_check,prompt_builder,result_checker,llm,io,templates,ncsim}

## 判分契约合规
- check() 返回 `return True` / `return False`（严格契约合规）
