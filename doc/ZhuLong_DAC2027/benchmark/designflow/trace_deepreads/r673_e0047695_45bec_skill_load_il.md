# trace_deepread — r673 · 45bec · SkillLoadIlFaultTolerant

## trace provenance
- session: `1793167618126_45bec.messages.json`
- user: `e0047695` @ `hfeg0plg49` (10.129.8.86), also mirrored on hfeg0plg10/hfeg0plg76/hfeg0pkn005 etc (NFS shared home)
- match_count: 31 (keywords: virtuoso:182;cadence:74;aether:51;adexl:14;spectre:13;schematic:10;pyaether:9;techfile:1)
- 26 msgs / 7 user turns / 8 tool_use (1 editor write, 1 RAG api_details, 1 read_files)
- accessed via `ssh 10.129.8.86` → `/home/e0047695/.cline/data/sessions/1793167618126_45bec/...` (note: `.cline` not `.claude`; scan summary path-substring says `.claude` but actual dir is `.cline`)

## user turns (verbatim)
- U#0: 我的virtuoso 启动时是自动加载项目组的各种环境变量文件，我无法编辑和控制，什么办法可以开启事自动应用我自己的设置文件
- U#6: cdsinit cdsenv 能启动后直接source吗？
- U#11: *Error* eval: undefined function - ab / *Error* load: error while loading file - "/home/e0047695/.cdsenv" at line 1 ，ab\tautoHideEmptyTabs\tboolean\tt  (cdsenv 是 4 列配置格式, 不能用 load())
- **U#16 (核心 produce-task)**: 写个ciw能执行的函数脚本，来load我的il文件按（aaa.il）
- U#24 (follow-up, 不进 prompt): 写个最简单的skill函数 定义一个函数为35H 然后函数内容为语句A 和 B

## gold (MSG 19 editor write → myLoadIl.il)
```scheme
procedure( myLoadIl( fileName = "aaa.il" )
    let( ( candidates path )
        when( isFile( fileName )
            candidates = list( fileName )
        )
        when( !isFile( fileName )
            candidates = list(
                strcat( "./" fileName )
                strcat( getenv( "HOME" ) "/" fileName )
            )
        )
        foreach( path candidates
            when( isFile( path )
                printf( ">>> 正在加载: %s\n" path )
                loadi( path )
                printf( ">>> 加载完成: %s\n" path )
                return( t )
            )
        )
        printf( ">>> 未找到文件: %s\n" fileName )
        nil
    )
)
```
- 算法: isFile(fileName) → candidates=[fileName]; else → ["./"+fileName, getenv("HOME")+"/"+fileName]; foreach 第一个存在的 → loadi (容错逐行) + return t; 都没有 → nil
- loadi 而非 load: 文件里某行报错时打印错误并继续, 不中断整个文件

## reframe (B-dang mock-behavioral, judge 跑 Python 不跑 SKILL)
- SKILL myLoadIl.il → 纯 stdlib `my_load_il.py`
- 函数 `my_load_il(file_name="aaa.il", namespace=None, verbose=True)`
- isFile → os.path.isfile; getenv("HOME") → os.path.expanduser("~"); loadi 容错 → 逐行 exec + try/except continue; t/nil → True/False
- namespace dict 参数让判分可核验 exec 进去的变量 (SKILL 无此需求, Python reframe 新增以给 check 牙)
- 新子型 `skill-load-il-fault-tolerant`, r645-r671 mock-behavioral reframe 家族 SKILL→Python 首例 (distinct vs r671=batch-gds-cdl-cli / r670=ascii-sanitizer / r667=routing-track-finder)

## case 产物
- assets/.../prompt.md (用户原话 U#16 + 背景 + 函数契约 8 条) + task_brief.md + aaa_A.il (示例: greeting/counter=5/final=10, 2 出错行)
- hidden/: aaa_B.il (name/total=50/tag=51, 出错行 4/6) + aaa_B2.il (退化 v=1) + aaa_priority.il (k 测试 marker=777) + aaa_comments.il (仅注释)
- reference/: check.py (16 条件 a-p) + gold_ref.py + 4 negatives (first_fail b/c/f/d, 4 distinct) + negative_selftest.py
- 自验: gold 16/16 PASS ✓; 4 negatives ALL FAIL ✓; §4.9 三假(empty/print/core)全 FAIL ✓; k_rationale=k_check=16 GATE PASS ✓; test sha fa5fb91e (==disk)
- jsonl_C 417→418; ledger 45bec claimed→case ✓
