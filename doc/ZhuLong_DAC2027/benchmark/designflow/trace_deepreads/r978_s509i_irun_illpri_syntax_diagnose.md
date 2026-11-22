# r978 deepread — s509i (e03101@hfeg0plg103, mc61, verilog:267 A-pure verification)

## Trace
- scp from hfeg0plg103: `1794894600066_s509i.messages.json` 305KB / 98 msgs
- agent = "lead" (subagent), U#1 = big context summary (LPDDR6 tb_1008 AVC/CSV/CK Sync/fsmr=2)
- 6 clean user turns (mostly tool_results from parent); real tasks in U#1 context + agent self-driven investigation

## Session主线
LPDDR6 testbench (lpddr6_tb_1008 / lpddr6_tb_1119) debugging:
1. verilogrun generation mechanism (vsim Perl wrapper现场生成)
2. X6 AVC run configuration (X6/DEFF互斥, top.sv:9-15 ifdef X6→undef DEFF+define SEFF)
3. vsim parameter→irun mapping (makefile→GetOptions→verilogrun)
4. DEFF dynamic switching (Normal⇄DEFF via MRW, handle_deff_mode_entry)
5. t_val = round(period/2) relationship (avc2csv第一列→pevave t_val)
6. **pevave_tasks.sv:300 syntax error diagnosis** (← 本case提炼点)

## 本case提炼 (msg 87-97)
用户意图: scan irun.log找错误 + 诊断编译失败根因

trace gold:
- scan_irun_log.py扫描14449行irun.log → 3个*E错误全指向pevave_tasks.sv:300:
  - L580: `ncvlog: *E,ILLPRI (pevave_tasks.sv,300|88): illegal expression primary`
  - L582: `ncvlog: *E,EXPSMC (pevave_tasks.sv,300|88): expecting a semicolon`
  - L588: `ncvlog: *E,CSISYX (pevave_tasks.sv,300|136): case item syntax error`
  - L14446: `irun: *E,VLGERR: ... Exiting with code (status 1)`
- 源文件pevave_tasks.sv L300: `PDRIVER.CK_t <=#3*t_val) getpetablevalue(...)` 
  - bug: `#3*t_val)` → 少`(`多`)`, 应为 `#(3*t_val)`
  - L298/299/301/302全正确 `#(3*t_val)`, 唯独L300手误
- fix: `<=#3*t_val)` → `<=#(3*t_val)`

## Case设计
- 通用diagnose_compile_error.py: irun_log + src_file → JSON
- 解析ncvlog *E行(error_code/file/line/col), 读源文件行, 分类syntax error, 生成fix
- 分类: hash_delay_missing_paren (`#<N>` not followed by `(` + unbalanced `)`)
- A=pevave_tasks.sv:300 (visible), B=wavegen_tasks.sv:456 (hidden, 同bug类型不同file/line/col/values)
