# k7668 — verilog_lib_trans ff module replace · r572 deepread

- **session**: `1793779533537_k7668` · user `e0039602` @ `hfeg0pkn003` (10.129.2.12) · mc=307
- **size**: 1,225,916 B / 223 msgs / 14 user-text-turns / ~90 tool_uses
- **keywords**: verilog:1403; lvs:698; netlist:73; drc:41; rtl:7; systemverilog:3
- **path**: nested `/home/e0039602/.cline/data/sessions/1793779533537_k7668/1793779533537_k7668.messages.json`
- **old parked**: r295 "verilog_lib_trans_v2 tb fix, 3-turn evolved complex task needs xrun+actual files, too complex to parameterize" + r382 "context-coupled-verilog-lib-trans-tb-family-compare-modify"

## 用户轮（14 个，关键 8 个）
1. msg[0]: "你当前在哪个文件夹下"
2. msg[4]: "对比 tb_family 中 tb_xxx.sv 的区别，按参考修改这个目录下的 tb_xxx.sv"
3. msg[40]: "把 AIout1104_retrue.sv 里 ff 相关的用 tb 重新跑然后修改成正确的，用修改好的替换 AIout1104 里对应的模块"
4. msg[73]: "找到原始版本的 8 个 ff，用 skill 测试，修改到八个全部正确就拼进 AIout1104"
5. msg[103]: "跳过测试，直接把通过测试的八个拿进去换了"
6. msg[138]: "不用编译检查，告诉我这 8 个有没有格式正确的替换进去就行了"
7. msg[156]: "给你重新弄好了一份 AIout1104.sv，把 pass 的那 8 个 ff 格式正确地替换进去"
8. msg[172]: "把本次对话中产生的临时 py 脚本都删掉"

## agent 工具链（~90 calls）
- list_allowed_files: 浏览 verilog_lib_trans_v2/ 目录结构
- read_files: 读 tb_family/*.sv, AIout1104_retrue.sv, AIout1104.sv, result_map txt
- search_codebase: 查 RTL_SOURCE_FILES / module 定义
- editor (35+): 写大量 _*.py 脚本 (_diff_all_tbfamily, _analyze_aiout, _run_ff_xrun, _extract_ff_rmap, _replace_ff_ai1104, _probe_ai1104_ff, _verify_110401, _rm_8ff, _del_rm 等) + 直接编辑 tb_ffr.sv/tb_ffrq.sv
- run_approved_command: 跑 xrun 编译测试 ff module + 运行 _*.py 脚本
- ask_question: msg[26] 澄清

## 判定
**B档 produce-task 合法（新标准）**：
- 用户核心意图 = 按 module 名从修好的版本替换目标文件中的对应 module（msg[40]/[73]/[156]）
- r295 "too complex to parameterize" 是针对 A档（完整多轮 xrun 测试流程），B档提取核心 capability = **Verilog module replacement by name**，完全可参数化
- agent 交付 `_replace_ff_ai1104.py`：读 AIout1104_retrue.sv → 提取 ff module → 按 module 名替换进 AIout1104.sv → 写出
- check.py 可判分：module 名匹配 + 替换 + keep 不变 + 顺序 + 确定性

## B档合成
- **case_id**: EDA-Eval-DesignFlow-FfModReplace-001 (digital, L1-B, k=12)
- **A**: target_A.sv (10 modules: 6 ff-buggy + 4 keep) + replacements_A/ (6 corrected ff .sv)
- **B**: target_B.sv (10 modules: 5 replace + 5 keep, 完全不同 module 名/逻辑) + replacements_B/ (5 corrected .sv)
- **ref**: replace_modules_ref.py (regex module...endmodule 提取 + 按名替换 + 保持其余不变)
- **check.py**: 12 断言(①-⑫), 全独立可 FAIL
- **negatives**: 4/4 全 FAIL distinct (naive_empty→⑨ / print_expected→⑤ / core_deleted→⑩ / hardcoded_A→⑦)
- **§4.9 三假提交**: 全 FAIL distinct(⑨/⑤/⑩)
- k_rationale=12==k_check=12≥8 GATE PASS

## 关联
- e0039602 用户既有 case: DelayCellParamGen-001 (jt7be, r547)
- 本 case 是候选池重审复活首条 fresh-deepread 交付（r572）
- r295 旧 parked 理由 "too complex" 在新标准下不成立 — B档提取核心 capability 即可造
