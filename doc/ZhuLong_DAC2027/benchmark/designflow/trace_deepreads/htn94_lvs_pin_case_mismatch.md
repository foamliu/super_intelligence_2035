# htn94 — felixw LVS "all cells CORRECT but overall INCORRECT" pin case mismatch diagnosis

- **session**: 1794381444433_htn94, user felixw @ hfeg0plg09 (10.129.35.73), mc=152
- **domain**: physical_verify (LVS debug)
- **size**: 70 msgs / 36 user_input / ~rich multi-turn investigation
- **claim**: r871, physical_verify

## User intent (U#0 verbatim)
> 帮我分析一个lvs case，run lvs的路径 /proj/ddgot/V0_Lay_20260723/ver/lvs/felixw/DqPadIM6_NewDfe_newrule ，report /proj/ddgot/V0_Lay_20260723/ver/lvs/felixw/DqPadIM6_NewDfe_newrule/lvs.rep 中显示INCORRCT ，但是底层的cell和top cell都是correct的，没找到报错在哪

(单轮干净意图：定位 "overall INCORRECT 但所有 cell CORRECT" 的根因。后续 35 user turns 围绕同一 debug 展开深挖，本 case 取 U#0 干净意图。)

## Gold investigation chain (assistant)
1. list_allowed_files run 目录 → read_files lvs.rep 1-200
2. 发现 **OVERALL COMPARISON RESULTS → INCORRECT** (line 32 ASCII art), **Error: Components with non-identical signal pins** (line 37)
3. **CELL SUMMARY** (line 42-74): 所有 cell 含 top `DqPadIM6_NewDfe` 全部 CORRECT —— "cell 全对但 overall 错" 的经典现象
4. 分页读 lvs.rep → **line 564-576 `COMPONENT TYPES WITH NON-IDENTICAL SIGNAL PINS`**:
   - `Layout Component Type:  rnmg_3t (3 pins): (p n) bulk`
   - `Layout Extra Pins:      bulk`
   - `Source Component Type:  rnmg_3t (3 pins): (p n) BULK`
   - `Source Extra Pins:      BULK`
5. **line 134 `LAYOUT CASE YES`** —— pin 名大小写敏感
6. 读 layout 网表 `DqPadIM6_NewDfe.sp` line 157: `.SUBCKT rnmg_3t plus minus bulk` (小写 bulk)
7. 读 source PDK `source.added` line 550: `.SUBCKT rnmg_3t PLUS MINUS BULK` (大写 BULK)
8. **根因确认**: rnmg_3t 电阻第 3 pin (bulk body) 在 layout 网表小写、source PDK 大写；`LAYOUT CASE YES` 使 pin 名大小写敏感 → "non-identical signal pins" → overall INCORRECT（即使每个 cell 内部 CORRECT，因为这是 component-type 级别的 pin 定义差异，影响所有用到 rnmg_3t 的 cell 的比对）
9. rule deck `calibreLPE.rule` line 4102-4103 `DEVICE rnmg_3t ... psub(bulk)` (小写) + DMACRO RES_REDUCE line 4087 缺 BULK 映射 → 修复点
10. 额外发现: rule deck include V0P5 PDK 而 source CDL include V0P1 source.added —— 两个 PDK 版本混用
11. 实例化位置: source CDL `IO_IbResEsd_new` (line 671) 例化 4 个 rnmg_3t (XR0-XR3, line 673-676), 第 3 pin → vss!

## Reframe (档 B, fixture-driven)
真实 gold = 诊断报告 (读 lvs.rep + 网表 → 定位 non-identical signal pins 差异 + 识别 pin 大小写 mismatch 根因 + 找实例化位置)。reframe 为 **fixture 驱动 LVS non-identical-signal-pins 差异定位器**:
- 候选交付 `lvs_pin_mismatch_diag.py <lvs_rep> <layout_sp> <source_cdl> [-o out.json]`
- 解析 lvs.rep: overall_status (INCORRECT/CORRECT), LAYOUT CASE 参数, "COMPONENT TYPES WITH NON-IDENTICAL SIGNAL PINS" 段 → device + matched pins + extra pins (layout/source)
- 解析 layout_sp: `.SUBCKT <device>` pins + 行号
- 解析 source_cdl: `.SUBCKT <device>` pins + 行号; 找 `<device>` 的实例化 (X* 行) → instance_cell + 行号 + count
- 大小写敏感比对 extra pins → case_mismatch 分类
- 输出结构化 JSON 诊断

## Fixtures
- **A (可见, 入 SUT 沙箱)**: 基于 htn94 真实数据精简 — rnmg_3t, layout `plus minus bulk` vs source `PLUS MINUS BULK`, instance IO_IbResEsd_new (XR0-XR3 → vss!), LAYOUT CASE YES, OVERALL INCORRECT
- **B (隐藏, 嵌 check.py)**: 不同 device `rnesd_3t`, layout `in out sub` vs source `IN OUT SUB`, instance PadResDly (XR5-XR7 → gnd!), 不同行号 — A/B 标识符全异 → 硬编 A fail B, 硬编 B fail A

## 判分牙型
exact-field-match (LVS 诊断输出本质唯一: 事实字段都是确定的). 16 teeth (a-p): zip/compile, stdlib-only, CLI exit0+out.json, valid JSON+keys, overall_status==INCORRECT, layout_case==YES, device==rnesd_3t, layout_subckt_pins, source_subckt_pins, mismatched_pins (case_mismatch pair), layout_subckt_line, source_subckt_line, instance_cell+count, anti-hardcode A guard, 3-seed determinism, anti-cheat B-literal scan.

## 意图审计
keep —— felixw 真实意图 (定位 "overall INCORRECT 但 cells CORRECT" 的 LVS 报错根因) 完整保留, reframe 是 grounding (真实 49k 行 runlvs.log + 项目 PDK 路径不可沙盒 → 小合成 fixture + 结构化 JSON 诊断输出, 离线化) 非加难; U#0 用户原话逐字入 prompt; pin case mismatch + LAYOUT CASE YES + extra-pin 语义全部直出 trace gold 调查链; 2026-11-15 reaudit 后 debug-Q&A/analysis 类合法第 N 例.
