# Trace deepread: c4vkj (lorikx @ hfeg0pkn004 / 10.129.2.13)

- **session**: 1793933365155_c4vkj (directory, autofs), 73 msgs, 31 assistant turns
- **user**: lorikx (proven digital — r424 lilaj XsCheckReportDiag, r427 c6xow CrCheckAudit)
- **mc**: 82, keywords verilog:166;rtl:155;synopsys:33 — clean A-dominant digital
- **工具调用**: read_files×6, search_codebase×2, editor×19, run_approved_command×12, get_agent_policy_status×1

## User prompts (real, non-tool-result)
- **U#0** (act mode): 「@rtl/ppc_inject_fault.v 是同事针对fault inject function优化后的代码，在line704-958，请阅读后帮我融合到 @rtl/sp_2pram.v 代码中」= "merge colleague's optimized fault-inject code (lines 704-958) into sp_2pram.v" — **clean produce-task, no root cause given → A-faithful**
- U#3: 「继续」(continue)
- 后续 user turns 均为 tool_result (agent's read/edit/run outputs)

## Agent (deepseek-lead) 工作流
1. read_files ppc_inject_fault.v:680-1000 → 理解 fault_injection 块结构
2. search_codebase "FAULT_INJ" → 找 sim/Makefile 的 `+define+FAULT_INJ` 开关
3. search_codebase apply_fi/fi_xor_mask/fi_enable/inject_one/parse_and_inject in sp_2pram.v → 确认目标文件无既有 fault-inject 代码
4. **editor×19** 迭代合并到 sp_2pram.v:
   - 新建 **tmp_grep_fi.py** (grep fault-injection patterns: FAULT_INJ/apply_fi/fi_xor_mask|fi_and_mask|fi_or_mask|fi_enable|inject_one|inject_range|clear_fault|clear_all_faults|parse_and_inject/defects=/mem[)
   - 新建 **tmp_premerge_check.py** (defect_bit_pos refs, TB plusarg usage, sp vs ppc diff)
   - 替换 sp_2pram.v 旧 defect_bit_pos 简单故障注入 → 新 comprehensive fault_injection 块
   - 接线 fi_enable + `ifdef FAULT_INJ` 守卫 + fi_xor_mask/and/or_mask [DEPTH] 数组 + apply_fi 函数 + inject_one/inject_range/clear_fault/clear_all_faults/parse_and_inject tasks + +defects= plusarg 解析 + corner maps (c0-c5 bit, c0-c2 addr)
5. run_approved_command×12: 跑 tmp_grep_fi.py / tmp_premerge_check.py / 仿真验证

## fault_injection 块结构 (ppc_inject_fault.v 700-958, 完整提取)
- **masks**: fi_xor_mask[DEPTH]/fi_and_mask[DEPTH]/fi_or_mask[DEPTH] (reg [DATA_WIDTH-1:0])
- **control regs**: fi_enable (1-bit), fi_result ([DATA_WIDTH-1:0])
- **tasks**: inject_one(a,b,t) / inject_range(a,b,t) / clear_fault(a) / clear_all_faults / parse_and_inject(item)
- **function**: apply_fi(raw_data, addr) = ((raw & and_mask) | or_mask) ^ xor_mask (order: AND→OR→XOR)
- **defect types**: x=XOR(default) / s0=SAF0 / s1=SAF1 (t=0/1/2)
- **plusarg**: +defects="addr:bit:type,..." ($value$plusargs)
- **ifdef**: FAULT_INJ
- **bit corners**: c0→0, c1→1, c2→DW/2-1, c3→DW/2, c4→DW/2+1, c5→DW-1 (6 corners)
- **addr corners**: c0→0, c1→(DEPTH-1)/2, c2→DEPTH-1 (3 corners)
- **out-of-range guard**: a>=0 && a<DEPTH && b>=0 && b<DATA_WIDTH (inject_one silently ignores)
- **wildcard**: a<0 = all addrs (whole column), b<0 = all bits (whole row)

## 合成决策
- **A-faithful produce-task INFEASIBLE**: deliverable = merged sp_2pram.v (300+ 行编辑), check 设计"code-merge semantics hard to parameterize" (原 park 理由)
- **B 档合成**: agent 的 tmp_grep_fi.py helper 定义了 fault-inject 接口提取需求 → 合成 **fault_inj_extract.py** (Verilog 接口提取器, 11 字段 JSON)
- **TFC (trace-faithfulness coverage)**: 11 维度全部可追溯到 trace:
  1. ifdef ← tmp_grep_fi.py 搜 FAULT_INJ
  2. enable_reg ← agent 接线 fi_enable + ifdef 守卫
  3. masks (xor/and/or) ← tmp_grep_fi.py 搜 fi_xor_mask|fi_and_mask|fi_or_mask
  4. apply_function ← tmp_grep_fi.py 搜 apply_fi
  5. apply_order ← agent 替换 apply_fi = ((raw & and) | or) ^ xor
  6. tasks ← tmp_grep_fi.py 搜 inject_one|inject_range|clear_fault|clear_all_faults|parse_and_inject
  7. defect_types ← agent 接线 type field parsing (s0/s1/默认 x)
  8. default_type ← parse_and_inject else t=0 (default XOR)
  9. plusarg ← tmp_grep_fi.py 搜 defects= + agent $value$plusargs("defects=%s")
  10. bit_corners ← parse_and_inject bit-field case(ci) c0-c5
  11. addr_corners ← parse_and_inject addr-field case(ci) c0-c2
  → **TFC = 11/11 = 100%**

## hidden B 设计 (cross-input guard)
- ifdef: INJECT_FAULT (≠ FAULT_INJ)
- enable_reg: err_en (≠ fi_enable)
- masks: err_flip_mask/err_zero_mask/err_one_mask (≠ fi_xor/and/or_mask)
- apply_function: apply_err (≠ apply_fi)
- apply_order: [or, and, xor] (≠ [and, or, xor] — B 用 | first, & second, ^ last)
- tasks: inject_single/inject_wildcard/clear_addr/reset_all/parse_item (5, 全不同名)
- defect_types: flip=XOR/zero=SAF0/one=SAF1 (≠ x/s0/s1)
- default_type: flip (≠ x)
- plusarg: inject (≠ defects)
- bit_corners: 4 (c0→0, c1→DW/2, c2→DW/2+1, c3→DW-1) (≠ 6)
- addr_corners: 2 (c0→0, c1→DEPTH-1) (≠ 3)
- 参数名 DW (≠ DATA_WIDTH), AW (≠ ADDR_WIDTH)
→ 11/11 字段全不同, cross-input guard 极强

## park 重开理由
- 原 park (r~): "clean produce-task but code-merge semantics hard to parameterize for spec-driven-generator check; defer"
- 重开: park 是关于 check 设计难度 (one specific approach), 不是 trace 不合格
- reframe 为 interface extractor (非 merge auditor) 绕过 code-merge check 难度
- agent 的 tmp_grep_fi.py helper 已定义提取需求 → B 档合成有 trace 依据 (TFC 100%)
