# Trace Deepread: nabcd — Prompt Rule inh_ Prefix Fix Q&A

## Session
- session_file: 1793267105856_nabcd (e0039602@hfeg0pkn003=10.129.2.12, mc=64, 43 msgs, agent=lead)
- date: 2026-11-17 (trace from Nov 11)

## User Intent (verbatim U#1)
"请你阅读一下这个项目，这个项目目前有时候会犯一个很低级的错误，就是你看这里面内部cell用的power引脚名称和实际定义的不一样，请你修改ruleprompt约束一下这种情况，你先在规则里约束一下，然后由于我推测可能是后续正则查找拼接进prompt的示例使用了inh_vss这种名字，但是示例和自己转换撰写的定义不一样，请你在prompt当中告诉模型你需要模仿他的写法，变量名请不要随意混用"

附 example: `celldefine module d1yg2Ls2_gutc ( out, vcc, vbn, vbp, vss, in ); ...invhiz_base #(strength1, strength0) I0 (.A(in), .Y(net3), .En(inh_vcc), .EnN(inh_vss), .vcc_(vcc), .vss_(vss), .vbulkn_(vbn), .vbulkp_(vbp));`

## Project Context
- Project: `/home/e0039602/Documents/verilog_lib_trans_v1.4` — Verilog library conversion tool using LLM prompts
- Bug: LLM copies few-shot example variable names (inh_vcc/inh_vss/inh_vbn from simlib_drcoa_digital.sv) into module conversions where actual ports are vcc/vss/vbn/vbp (no inh_ prefix)
- Files modified: `src/rules_prompt.py` (RULES + build_prompt), `src/rules_prompt02.py` (RULES + build_prompt)

## Gold Standard (assistant msg#42)
4 modifications:
1. rules_prompt.py RULES line 63-71: New hard constraint — power/ground/substrate pin network names must come from module's actual declared ports, forbid fabricating or copying inh_ prefix from examples
2. rules_prompt02.py RULES line 56-64: Same constraint
3. rules_prompt.py build_prompt line 779-786: New output instruction — imitate example structure/style but don't mix variable names, network names must match module's original text
4. rules_prompt02.py build_prompt line 401-408: Same instruction

Verification: py_compile OK, content checks (新增约束/严禁捏造inh_/变量名不要随意混用/模仿示例写法/不许混入inh_/按本module原文核对) all OK, len(RULES)=30334/15941, ALL-CHECKS-PASSED.

## Case Design
- Case ID: EDA-Eval-DesignFlow-PromptRuleInhPrefixFixQA-001
- Domain: schematic_netlist (code-grounded prompt-rule-fix Q&A, D域新子型)
- A档 verbatim U#1
- Asset A: rules_excerpt_A.txt (reconstructed RULES section ~40 lines, shows gap — rules mention inh_ prefix but no constraint against copying), question_A.txt (verbatim user text with module example), task_brief.md
- Hidden B: rules_excerpt_B.txt (identifier-renamed: inh_→pwr_, vcc→vdd, vss→gnd, vbn→vnw, vbp→vpw, vssz→gndz, En/EnN→EN/ENB, strength1/strength0→drive1/drive0, d1yg2Ls2_gutc→d2yg2Ls2_gutc; same gap structure, zero A-identifier overlap)
- candidate_ref.py: Generic analyzer — reads rules excerpt, extracts prefix pattern, module ports, conflicting names, proposes rule text + prompt instruction, outputs 13-key JSON
- check.py: 12 assertions a-l (zip/compile/keys/prefix_pattern/issue/conflicting_names/rule_text/prompt_instruction/anti-hardcode/determinism)
- Self-verify: 12/12 PASS + 3 neg FAIL (NEG_RC=0) + §4.9 三退化全FAIL

## Asset Accessibility
- Original project on 10.129.2.12 at /home/e0039602/Documents/verilog_lib_trans_v1.4/
- RULES section reconstructed from trace editor diffs (msg#15/#16 show original lines removed, new lines added)
- Synth-deck approach: asset built from trace content, not from live project files
