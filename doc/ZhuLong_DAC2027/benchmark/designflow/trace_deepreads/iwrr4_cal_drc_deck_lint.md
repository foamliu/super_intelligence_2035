# Deepread: iwrr4 — calibre DRC UT-check deck 学习/调试 (physical_verify)

**trace_source**: user=xydou, host=hfeg0plg69, session_file=1795245585227_iwrr4.messages.json, match_count=483, msgs=519
**keywords**: calibre:1460;drc:1009;.gds:182;pyaether:178;cellview:146;aether:127;dbshape:68;dbget:55
**tools**: editor:115, run_approved_command:76, read_files:20, run_code:12, search_apis:9, get_api_details:7
**domain**: physical_verify (calibre DRC deck authoring/debugging)

## 真实用户意图

- U@0: "你好"
- U@2: "/apps/imctf/utrunset/cxmtG4C/LP/calibreDRC_UTCheck.rule 你学习一下这一套UT检查的脚本，要学会自己会写会调试，我一会让你写几个检查脚本"

用户让 agent **学习 calibreDRC_UTCheck.rule 这套 UT 检查规则 deck 的写法**，之后让 agent **自己写/调试几个 DRC 检查脚本**。属于 physical_verify 域的 DRC deck 编写/调试意图。

## 会话关键产物（assistant 调试轨迹）

agent 学习了 calibreDRC_UTCheck.rule 的 SVRF 格式后，自己构造了一个独立 deck（"我的规则 + calibre.layer + test.gds"）来派生一个 "mid" 层并跑 DRC。调试中遇到的真实问题：
1. **派生层 "mid" 全空** —— 原因是测试脚本把 `LAYOUT DEPTH ALL` 也过滤掉了，层次被限制 → 改用独立 deck。
2. **结果形态异常**（整个版图 bbox、0.187 小方块、PCH 环 bbox 都成了 "mid"）—— 当前构造在层次版图上行为不符预期 → dump mid 区域看实际形状。
3. **精度不匹配** —— 用户的 test.gds 是 0.1nm 网格，deck 的 PRECISION 需修正后重跑。

派生层操作用到：geomAnd/geomOr/geomNot/geomSize、INTERACT/AND/OR/NOT/INSIDE/OUTSIDE/TOUCH/EDGE/EXPAND EDGE...BY/CUT/WITH TEXT/CONNECT。

## 参考规则格式（calibreDRC_UTCheck.rule 真实片段）

```
LAYOUT PATH "XX.gds"
LAYOUT PRIMARY "XX"
LAYOUT SYSTEM GDSII
RESOLUTION 1
PRECISION 10000
UNIT LENGTH U
DRC RESULTS DATABASE "drc.rdb"  ASCII
DRC SUMMARY REPORT   "drc.sum" HIER
DRC MAXIMUM RESULTS ALL
DRC KEEP EMPTY YES
LAYOUT DEPTH ALL
DRC CELL NAME YES CELL SPACE XFORM ALL
FLAG ACUTE YES / FLAG OFFGRID YES / FLAG SKEW YES
#DEFINE SL_CHECK
#DEFINE CHECK_FLOATING_METAL
VARIABLE PWRGND_PIN "?!"
VARIABLE Stdcell "Dly*" "SCmos*" ...
VARIABLE GRID 0.0001
// derived layers:
PG_INT_MOS = (OR PG_drawing PG_PCH PG_NCH) INTERACT DIFF
pplug = (PDnet NOT INTERACT GATE) AND PWnet
sd = (NDnet OR PDnet) INTERACT GATE
PTR = INTERACT PACT PG_PCH
expand_region = EXPAND EDGE (OR EDGE AT4_x_p AT4_x_n) OUTSIDE BY 0.05
AT4_x_p_wi_PC = AT4_PCH TOUCH OUTSIDE EDGE (expand_region INTERACT PC_drawing)
M1_sig_pin_p = M1_any_pin_p NOT M1_pg_pin_p
CONNECT M1_sig_pin_p M1_s
// DRC CHECK blocks:
CHECK_PIN_m { ... }
```

## 拟造 case 设计（档 B produce-tool · mock L0/L1）

**case_id**: EDA-Eval-DesignFlow-CalDrcDeckLint-001
**judge_layers**: ["L0","L1"]（纯 Python 解析 SVRF 文本，无需 EDA 工具）
**真实溯源**: metadata.trace_source{user:xydou, host:hfeg0plg69, session_file:1795245585227_iwrr4, match_count:483, real_task_summary:"学习 calibreDRC UT-check SVRF deck 格式并编写/调试 DRC 检查脚本；调试中遇到派生层 mid 全空(LAYOUT DEPTH 过滤)、形态异常、PRECISION 网格不匹配(0.1nm)"}

### reframe
write `caldeck_lint.py` CLI 读 calibre SVRF DRC deck 文本 → 解析 → 校验派生层拓扑 + DRC 规则正确性 → 输出 lint.json。

### 候选需执行的校验（每条独立可 FAIL）
1. 解析 deck 分段：header(LAYOUT PATH/PRIMARY/SYSTEM, RESOLUTION/PRECISION)、VARIABLE 定义、#DEFINE 开关、派生层赋值(name = expr)、DRC CHECK 块
2. 派生层依赖图：检测未定义层引用（派生层引用了未定义且非 primary/gds 的层名）
3. 检测派生层循环依赖（A→B→A）
4. 校验操作 arity：AND/OR ≥2 操作数, NOT 1, INTERACT 2, INSIDE/OUTSIDE 2, EXPAND EDGE...BY 1 region+1 distance, CUT 2, TOUCH 2, WITH TEXT text+var+layer
5. PRECISION/RESISION 一致性：正整数, PRECISION>RESOLUTION
6. DRC CHECK 块引用的层均已定义
7. #ifdef guard 使用的开关须在 SWITCH DEFINITION 声明
8. 表达式中的 VARIABLE 引用须已声明

### 输出格式
```json
{"deck":"...","errors":[{"type":"undefined_layer|circular_dep|bad_arity|precision|undef_check_layer|undef_switch|undef_variable","line":N,"message":"...","severity":"error|warn"}],"summary":{"total_errors":N,"by_type":{...}}}
```

### A / B
- A(visible deck_A.svrf): DDGOA 风格，含 5 个故意错误（1 undefined ref, 1 circular dep, 1 wrong-arity, 1 undeclared variable, 1 undeclared switch），不同层名/位置
- B(hidden deck_B.svrf): 不同 deck，不同错误模式（不同层名 M3/HLP/AT4 风格 + 不同错误位置/类型组合）

### check.py 计划（≥12 cond）
①候选文件存在 ②Python 编译 ③argparse CLI ④hidden B 可读 ⑤候选跑 B exit0+输出 ⑥lint.json 结构{deck,errors,summary} ⑦errors 总数==期望 ⑧每个期望错误 type 出现 ⑨错误 line 落在合理范围 ⑩无虚假错误(by_type 只含期望 type) ⑪summary.total_errors==len(errors) ⑫summary.by_type 计数正确 ⑬3 跑确定性 md5 ⑭A!=B 防硬编(error type 集合不同) ⑮precision 错误被检出 ⑯circular_dep 错误被检出

### 负样本
- empty: 写 {} → 各 cond FAIL
- print: 只 print 期望 JSON 串不解析 → A!=B / line 范围 cond FAIL
- core: 删循环检测逻辑 → circular_dep cond FAIL
- hardcode: 硬编 B 的错误列表 → A 跑出错 cond FAIL

## 状态
- **本轮**: deepread 完成 + case 设计定稿，未合成（时间预算 40min 用尽于选料+深读）
- **ETA**: 下一轮 (r1226) 直接按本设计合成（assets/hidden/reference/negative/check.py + 自验），预计 1 轮交付
- ledger: iwrr4 已 claim (physical_verify)
