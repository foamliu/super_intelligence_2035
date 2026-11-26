# Deepread: 1790566107917_f1rqc — TCL→SKILL 代码转换器 (hbpeng)

> Revived from parked (r556 候选池重审, old weak filter "too-large-dev-task" retired).
> 新标准: produce-task 合法, B档 = 固化核心转换能力为自包含脚本 (不复制整个多文件包).

## trace 元信息
- session: `1790566107917_f1rqc` · user: `hbpeng` · host: `10.129.2.14` (hfeg0pkn004) · mc=147
- file: 2.82MB / 685 msgs · agent `cline lead` (glm-5.2) · 2026-09-28
- keywords (summary.tsv): calibre:4451;pdk:2168;... (calibre=PDK QA context, not the task itself)
- domain: **eda_other** (SKILL = Cadence Virtuoso scripting language; TCL→SKILL transpiler = EDA tool automation)

## 用户真实意图 (USER#0 verbatim)
> `请自己设计方案，实现tcl代码转skill代码。要求如下：`
> `1.tcl代码解析需要成熟方案，考虑后续扩展问题`
> `2.代码转化请提供基本方案和案例，考虑后续扩展问题`

= **produce-task**: 构建 TCL→SKILL 代码转换器。需求明确:
1. 成熟的 TCL 解析方案 (lexer+parser→AST, 可扩展)
2. 基本转换方案 + 案例 (examples), 可扩展

## assistant 真实探索与产出
1. 发现已有 `/home/hbpeng/tcl2skill/` 项目 (lexer.py/ast.py/parser.py/translator.py/skill_visitor.py)
2. 分析现状: 两个并行翻译器 (visitor 模式 vs translator), 结构混乱, 缺测试/文档/插件
3. 产出 (200+ editor edits):
   - `DESIGN.md` 设计文档
   - `plugin.py` 插件注册机制 (可扩展)
   - `expr_engine.py` TCL expr 表达式引擎
   - `config.py` / `utils.py`
   - 重构 `skill_visitor.py` (AST visitor → SKILL code gen)
   - `tests/` (test_lexer/test_parser/test_skill_visitor/test_plugin)
   - `examples/` (simple_vars.tcl/control_flow.tcl/procedures.tcl/lists.tcl/file_io.tcl)
   - `README.md`
4. 后续优化: switch 语句/regsub/append 行为/Empyrean sys_* 函数透传/复杂 expr

## 核心 TCL→SKILL 转换映射 (从 trace 提取)
| TCL | SKILL |
|---|---|
| `set var val` | `setq(var val)` 或 `var = val` |
| `expr $a + $b` | `a + b` (SKILL infix) |
| `if {cond} {body}` | `if(cond body)` |
| `while {cond} {body}` | `while(cond body)` |
| `for {init} {cond} {step} {body}` | `for(init cond step body)` |
| `foreach v $list {body}` | `foreach(v list body)` |
| `proc name {args} {body}` | `procedure(name (args) body)` |
| `list a b c` | `list(a b c)` |
| `lindex $L $i` | `nth(i L)` |
| `llength $L` | `length(L)` |
| `puts $msg` | `println(msg)` |
| `return $v` | `return(v)` |
| `# comment` | `; comment` |
| `switch $v {...}` | `case(v ...)` |
| `append v s` | `v = strcat(v s)` |

## B档设计 (本轮交付)
- **case_id**: `EDA-Eval-DesignFlow-Tcl2SkillTranspile-001`
- **deliverable**: 自包含 Python `tcl2skill_transpile.py` — 读 TCL 源文件 → 解析 (lexer+parser→AST) → visitor 生成 SKILL 代码 + 转换报告 JSON
- **不依赖**: 私有 PDK Tcl callbacks, /home/hbpeng 项目 (合成自包含 TCL 输入)
- **asset A** (SUT 可见): `sample_A.tcl` (变量/expr/if/while/foreach/proc/list/注释)
- **hidden B** (check 只跑 B): `sample_B.tcl` (不同结构: switch/for/nested proc/lindex/llength/append/return, 不同变量名/数值)
- **check()**: 在独立 tmpdir 解 zip → subprocess 跑 transpiler on B → 解析 SKILL 输出 + JSON 报告 → ≥12 断言
- **negative**: naive_passthrough (原样输出 TCL) / print_expected (打印期望 SKILL 串) / empty_shell / core_deleted (删 visitor)

## A档不可行理由
session 685 msgs, 产物是 200+ editor edits 的多文件包, 依赖 hbpeng 私有 tcl2skill 项目 + PDK Tcl callbacks; 无法作为自包含 A档 zip 交付。B档固化为聚焦转换器脚本。
