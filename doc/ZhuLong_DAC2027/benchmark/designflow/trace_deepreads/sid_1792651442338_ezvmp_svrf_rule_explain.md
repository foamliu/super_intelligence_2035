# 深读笔记 — sid 1792651442338_ezvmp (laryu @ hfeg0plg76, mc=49, 137 msgs)

**shard C · domain physical_verify · case EDA-Eval-DesignFlow-SvrfRuleExplain-001 (r159)**

## trace 元信息
- user: laryu (新用户，本 shard 首次)
- host: hfeg0plg76 (10.129.x)
- session: /home/laryu/.cline/data/sessions/1792651442338_ezvmp/1792651442338_ezvmp.messages.json (747KB, 137 msgs)
- tools 命中: 619 calibre（SVRF DRC 规则）+ 少量 netlist/schematic/hspice
- match_count: 49（mc>=30 池）

## A-档 seed（用户原话逐字，U#1 idx=0 ts=1792651442338）
```
NL_S_008_10 {
    @ Min - Space of NLDD to P_DIF, except P+_Guarding  [value: ^_NL_S_008_10_]
    EXT  NL1  (PDIF NOT PSUB) <  _NL_S_008_10_  ABUT<90 SINGULAR OVERLAP INSIDE ALSO REGION
    EXT  NL2  (PDIF NOT PSUB) <  _NL_S_008_10_  ABUT<90 SINGULAR OVERLAP INSIDE ALSO REGION
    EXT  NL3  (PDIF NOT PSUB) <  _NL_S_008_10_  ABUT<90 SINGULAR OVERLAP INSIDE ALSO REGION
    EXT  NL4  (PDIF NOT PSUB) <  _NL_S_008_10_  ABUT<90 SINGULAR OVERLAP INSIDE ALSO REGION
}这个是SVRF，帮我每句话解释一下
```
- **纯意图**：用户粘贴一段真实 SVRF DRC 规则块（NL_S_008_10，4 条 EXT 子句），要求"逐句解释"。
- **A-档合格**：用户只表达目标（解释），未指出根因/未给修复方案。✓
- 后续轮（U#2+）漂移到 vim/gvim 配置（.vimrc / signcolumn / colorcolumn），与本 case 主题无关，**不进 prompt**。

## assistant 工具链（仅 SVRF 解释部分，idx 1）
- 无工具调用，直接产出文本解释（A[1]）。
- 解释质量高，结构化：规则名 → @ 注释 → 逐 EXT 子句拆解（关键字/层1/层2布尔表达式/阈值变量/修饰符 ABUT<90 SINGULAR OVERLAP INSIDE ALSO REGION）→ 总结 → 工艺背景（BCD/LDMOS）。

## 金标准（trace 末尾用户实际接受的结果）
- 用户接受 A[1] 的逐句解释（U#2 直接转去问 vim，未对 SVRF 解释提出异议 ⇒ 默认接受）。
- 本 case 不复刻散文解释（散文不可断言），**重构为结构化 JSON 解释**：解析任意 SVRF 规则块 → 输出每条检查子句的结构化字段（keyword/layer1/layer2_expr/layer2_layers/layer2_bool_ops/operator/threshold_var/modifiers/raw）+ 规则名 + 注释 + summary。
- 断言只对**事实**（解析出的字段值），不对措辞。

## case 设计
- **mode**: design_flow · **entry_point**: outputs/submit.zip（单文件 svrf_rule_explain.py）
- **A（SUT 可见）**: prompt.md（U#1 原文）+ rule_A.svrf（NL_S_008_10 块原文）+ task_brief.md（≤3 行接口）
- **隐藏 B（不进 SUT 沙箱，check 只跑 B）**: rule_B.svrf = **结构不同**的 SVRF 规则（1 块 M2_ENC_014，3 条子句 ENC/EXT/INT，不同层/修饰符/阈值变量），强制 SUT 写**通用解析器**而非硬编码 A 答案
- **CLI**: `svrf_rule_explain.py <input.svrf> [--out PATH]` / `--help`/`-h` exit0 / 无参 exit2+stderr
- **输出 JSON schema**: `{"rules":[{"name","comment","checks":[{"raw","keyword","layer1","layer2_expr","layer2_layers","layer2_bool_ops","operator","threshold_var","modifiers"}],"summary"}]}`
- **判分 15 条独立条件 (a)–(o)**：见 reference/check.py 顶部 docstring
- **负样本**: naive_hardcode_a（硬编码 A 答案→B 规则名错）/ naive_hardcode_b（硬编码 B→跨输入守卫 A 规则名错）/ fake_empty（空 rules）/ fake_print_expected（只打印不写文件）/ fake_core_deleted（删 modifier 解析）
- **§4.9 三假提交**: (a)空壳 zip (b)只 print A 期望串 (c)ref 删核心（modifier+layer2_expr 解析）→ 全 FAIL
- **难度**: L1-boundary（离线 Python 解析 SVRF 文本→结构化 JSON），属 §5 ≤30% L1 配额内的 physical_verify 补牙

## 泄漏隔离
- SUT 沙箱只放 prompt.md + rule_A.svrf + task_brief.md（A 输入）。
- check.py / reference/ / hidden/（rule_B.svrf）绝不进 SUT workdir；判分在独立临时目录跑。
