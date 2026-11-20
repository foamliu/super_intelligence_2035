# Deepread: 1793265549716_ykb7a (e0039602 @ hfeg0pkn002, mc76, digital)

## 会话
- session: 1793265549716_ykb7a.messages.json (目录格式, 471KB, 40 msgs)
- agent: lead (zhulong)
- 单轮 produce-task (1 user turn, U#0)

## 用户意图 (U#0 原文要点)
项目 `verilog_lib_trans_v1.4.1` 有时会犯低级错误：内部 cell 用的 power 引脚名称和实际定义不一样。
- 示例 module `d1yg2Ls2_gutc` 只声明 `out/vcc/vbn/vbp/vss/in`
- 但实例 `invhiz_base I0 (.En(inh_vcc), .EnN(inh_vss), ...)` 用了 `inh_vcc`/`inh_vss` —— module 里没声明
- 用户推测：后续正则查找拼接进 prompt 的参考示例用了 `inh_vss` 这种名字，但示例和自己转换撰写的定义不一样
- 要求：① 在规则里约束一下 ② 在 prompt 当中告诉模型"你需要模仿他的写法，变量名请不要随意混用"

## Agent 工具链
1. list_allowed_files / get_agent_policy_status — 探索项目
2. read_files README.md + config.yaml
3. read_files rules_prompt.py + rules_prompt02.py + search_codebase (inh_vcc|power|模仿)
4. read_files rules_prompt.py (34-420) + simlib_ref_db.py + simlib_lookup.py
5. **诊断根因** (msg 14): module 只声明 in/out/vcc/vbn/vbp/vss，但实例连 `.En(inh_vcc)/.EnN(inh_vss)` —— 这些 `inh_*` 名字来自 `simlib_ref_db.reference_snippet()` 正则按 module 名在 golden 库 `simlib_drcoa_digital.sv` 匹配出的参考示例。模型把参考示例的变量名误当当前 module 真实网络 → 编译失败
6. editor ×5: 改 3 文件
   - `rules_prompt.py` 规则【1】前加"[网络名必须属于当前 module —— 禁止借用/混用参考示例或其它 module 的变量名]"
   - `rules_prompt02.py` 同样约束
   - `simlib_ref_db.py` reference_snippet 头部改"只模仿写法，严禁混用变量名"
   - 两文件 output-requirement 节加强化 bullet
7. 写 `_verify_edits.py` (py_compile 3 文件 + 检查新文案出现在拼接 snippet) → run_approved_command PASS
8. 清理临时脚本 (_verify_edits.py / _cleanup.py)

## A-faithful 判定
用户给症状(power pin 名不一致) + 根因假设(参考示例用了 inh_vss) + 要求(规则约束+prompt 警告)，**未给具体规则文案/修改位置** → A-faithful 合格。

## Deliverable
修改后的 `rules_prompt.py` / `rules_prompt02.py` / `simlib_ref_db.py` (私有 /home/e0039602/Documents/verilog_lib_trans_v1.4.1/) → 沙盒不可达 → INFEASIBLE → **B档合成**。

## 合成方向
确定性核心 = Verilog power-pin/未定义网络一致性静态检查器：
- 解析 module 声明名 (端口 + wire/trireg/reg + parameter)
- 剥离注释 (// 行 + /* */ 块)
- 提取实例 `TYPE [#(params)] NAME (.Port(net), ...)`，跳过参数覆盖 #(...)
- 标识符边界匹配找出 .Port(expr) 里未声明的网络 (inh_vcc ≠ vcc，禁子串)
- 处理拼接 {a,b}、字符串字面量、注释陷阱
- 输出 JSON 一致性报告 + rule_suggestion

## 新 case
EDA-Eval-DesignFlow-VerilogPowerPinConsist-001 (digital L1-B, k=17, archetype=verilog-power-pin-naming-consistency-checker)
A=module_A.v (d1yg2Ls2_gutc, I0/I1 buggy inh_vcc/inh_vss); B=hidden module_B.v (aux_pwrchk_d8, P0 pwren + F2 q2/rstn, 不同信号名/实例/陷阱)
