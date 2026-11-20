# r885 deepread — pzo6g (verilog_lib_trans_skill packaging produce-task)

## trace source
- session: `1793953438523_pzo6g`
- user: e0039602 @ hfeg0pkn003 (10.129.2.12)
- mc: 269 (reaudit旧scan口径; 11-21 scan mc=2 verilog:2 — keyword口径变化, 文件实存854KB)
- domain: **verification** (A-shard) — netlist→SV 转换 + skill 打包, 数字流程
- ALIVE: YES (subdir-path: `/home/e0039602/.cline/data/sessions/1793953438523_pzo6g/1793953438523_pzo6g.messages.json`, 854738 B, 155 msgs)
- 旧判: 2026-11-10 parked "context-coupled-verilog-lib-trans-skill-packaging" (旧 weak 标准)
- r885 重判: **MAKEABLE** (11-15 新标准: produce-task 合法; 交付件可跑 → check 有牙 §4.2)

## 用户真实意图 (USER#4, msg5, 唯一实质 user turn)
> "现在请你将这个功能做成一个，就是使用这些prompt，参考对应的sv文件，生成新的，并存入resultmap当中，不用路由三次了，每个生成一遍，由调用skill的agent自行完成查验，然后做完之后也可以再用tb_family子skill再查改一次，最后要能实现生成结果一样，一个resultmap，还有运行完extract_converted_sv.py得到的最终SV文件，将这些包装成一个skill放在该目录下的verilog_lib_trans_skill1/里，然后我可单独把这个skill移走，只要给定网表和log就可调用自行执行的skill"

意图 = 把现有 `verilog_lib_trans_skill` 工程（网表→SV 转换：用 prompt 参考 .sv 生成新 SV，存入 result_map；extract_converted_sv.py 提取最终 SV；tb_family 子 skill 查改）打包成一个**可移走的自包含 skill** (`verilog_lib_trans_skill1/`)：给定网表+log 即可自执行。交付 = skill1/ 目录。

## trace assistant 工具链 (msg6-153)
- 读现有工程: README.md (CLEANPROJECT 干净自包含网表转换工程), run.py (730+行: extract_missing/resolve/write_module/parallel), extract_converted_sv.py (从 result_map 提取转换结果按原序写 SV), src/rules_prompt.py (ruleprompt3 完整 model 转换版), src/port_check.py (端口一致性校验门禁), src/offline_mapping.py (离线演示数据固化), src/parallel_worker.py, tb_family/ (子 skill 查改), docs/adjustment_netlist_to_sv.md
- 建 verilog_lib_trans_skill1/: run_skill.py (15804B edit 超限分多次写), SKILL.md, run_skill.sh, config.yaml, extract_converted_sv.py (复制), test/test_netlist.v, src/, docs/, outputs/
- 测试: _run_offline.py → "offline+extract exit 0 / result_map 转换块数量: 1 / 网表模块数量: 1 / 已替换/写入的转换模块数: 1"; _run_prompt.py → "prompt-only exit 0 / LEN 20569 / [rules] src.rules_prompt"; _run_online_stub.py → exit 0; _check.py → SYNTAX-OK
- 验证可移走: _validate_move.py → "moved to /tmp/skill_move_test_5jjvv52w/verilog_lib_trans_skill1 / exit 0 / result_map..." (relocatable 确认)
- 清理: _rm_*.py 系列删除临时脚本, final top files = ['SKILL.md', 'config.yaml', 'docs', 'extract_converted_sv.py', ...]
- 最终 syntax: run_skill.py SYNTAX-OK, src.netlist_parser IMPORT-OK, src.simlib_lookup IMPORT-OK

## 合成方案 (B档 synthesized, DEBT 下轮)
- **case_id**: EDA-Eval-DesignFlow-VlogLibTransSkillPkgProduce-001 (待定)
- **fixture A** (自包含, faithful compact 重构自 trace tool_results):
  - `verilog_lib_trans_skill/` 工程精简版: run.py (核心: extract_missing/write_module/parallel 路由, 去掉三次路由改单次), extract_converted_sv.py (result_map→SV 提取), src/rules_prompt.py (model 转换 prompt), src/port_check.py (端口校验), src/offline_mapping.py (离线映射), src/parallel_worker.py, test_netlist.v (示例网表), docs/adjustment_netlist_to_sv.md, tb_family/ (子 skill 查改), README.md
  - task_brief.md (用户原话 + 工程结构说明 + 交付要求: skill1/ 可移走)
- **hidden B** (判分, 结构不同, judge-only 不进 SUT):
  - 另一 netlist_B.v (不同 module 名/端口/cell) + log_B, 期望 result_map_B + extracted_SV_B 结构
  - base64 内联 check.py, SUT 不可见
- **check.py** (≥8 独立断言, §4.2 真跑候选):
  1. submit.zip 解出 verilog_lib_trans_skill1/ 目录结构齐全 (SKILL.md/run_skill.py/run_skill.sh/config.yaml/extract_converted_sv.py/src/test/)
  2. SKILL.md 含 skill 描述 + 调用方式 (给定 netlist+log 自执行)
  3. run_skill.py 语法 OK (py_compile)
  4. **真跑**: run_skill.py --netlist <hidden B netlist> --log <B log> --offline → exit 0
  5. 真跑产出 result_map_B.txt 结构正确 (# Netlist cell conversion report + 按 module 组织 + cell 转换块)
  6. 真跑产出 extracted SV (extract_converted_sv.py on result_map_B) → SV 文件含 hidden B module, cell 转换后内容
  7. 可移走性: skill1/ 无绝对路径依赖 (grep /home/e0039602 应为 0, 或仅出现在可配置参数)
  8. run_skill.sh 调用 run_skill.py (wrapper 正确)
  9. config.yaml 含必要配置 (rules 模块/netlist 路径参数)
  10. anti-leak: 不泄漏 hidden B 独有标识符
  11. anti-degenerate: 空壳/只 print 期望/删核心 (extract_converted_sv 逻辑) 三假全 FAIL
  12. 确定性重跑稳定
  - k_check = k_rationale ≥ 8
- **negative**: empty stub / generic_print / core_del (删 extract_converted_sv.py 核心逻辑) → 全 FAIL
- **自验**: ref 解 (按 trace agent 的 skill1 结构合成) 跑 check.py PASS; 3 neg FAIL; §4.9 (a)空zip (b)print-expected (c)core-deleted 全 FAIL

## 为何本轮只深读不合成
- trace 854KB/155msg, fixture A 需 faithful compact 重构整个 verilog_lib_trans_skill 工程 (run.py 730+行 + src/ 多模块 + tb_family/ + docs/) — 体量大, 合成需专门一轮
- §3 允许 "单条 trace 过大时本轮只深读, 心跳记 DEBT: 1 deepread 未合成, 下一轮交付"
- 本轮 40min 预算已用于选料(11-21 scan A-pure 枯竭再确认)+deepread, 合成超预算; 不降质赶工 (§4 闸门不放松)

## 下轮优先
合成 EDA-Eval-DesignFlow-VlogLibTransSkillPkgProduce-001 (本 deepread 已就绪, fixture A 计划已列), 兑现 DEBT。
