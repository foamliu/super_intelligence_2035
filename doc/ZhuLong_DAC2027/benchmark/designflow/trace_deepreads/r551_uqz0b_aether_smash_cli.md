# r551 deep-read: uqz0b (jcgu@hfeg0plg81, mc=145) — Aether Smash CLI Porting

**sid**: 1794474504276_uqz0b · **user**: jcgu · **host**: hfeg0plg81 (10.129.8.132) · **mc**: 145
**keywords**: lvs:316;aether:173;lib.defs:133;.gds:114;netlist:101;drc:71;.cdl:69;virtuoso:53
**msgs**: 349 · **size**: 1.18MB · **domain**: layout_aether (Aether smash/porting)

## User intent evolution (13 user turns)

- **USER#0** (msg 16): "调整一下GUI布局，将step1后面的文本框取消..." = modify-existing GUI (flow_gui_demo.py). Not the produce-task.
- **USER#1** (msg 26): **★ produce-task author-new-script** — "接下来step2...原始脚本是在Aether界面上执行的，脚本路径/proj/train/AI_drcqa/workdir/jcgu/porting_test/configfile/Aether_Porting_Smash_20260826.py，运行后会出一个GUI界面...请解析一下这个脚本，然后重写可以在不启动Aether的情况下直接执行，必要的输入可以在本GUI界面的文本框里输入" → rewrite Aether smash script to standalone CLI. **A档合格** (提需求未给根因/方案).
- USER#2-4: params.json format spec — "根据GUI上面input files自动生成json文件，top_lib对应{Lib},top_cell对应{Cell},top_view对应{View},modify_dirs对应/proj/{Product}/{Version}/libs,stop_libs对应\"TECHLIB,basic,{product}_MAT\",do_delete默认false,log_file默认存在当前目录下"
- USER#5-10: debug iterations — pyAether not found, bundled python path, boost lib, OA lib issues (6 rounds of RuntimeError: pyAether is not importable)
- USER#11 (msg 287): "换个方法，先将...Aether_Porting_Smash_20260826.py这个脚本重构一下，我直接在terminal里用pythone **.py 参数这样的命令来执行测试" → refactor to CLI (Aether_Porting_Smash_cli.py)
- USER#12 (msg 311): "在terminal里运行脚本测试没问题，下面对这个脚本命令进行封装，首先cd到/proj/{Product}/{Version}/workdir/{Username}文件夹下，然后执行pythone {脚本绝对路径} --top_lib {Lib} --top_cell {Cell} ..." → GUI integration (wrap CLI into flow_gui_demo.py)
- USER#13 (msg 333): "使用pythone命令，不要用python3" (final fix)

## Assistant tool chain

- **editor ×40+**: flow_gui_demo.py (GUI, ~10 edits), aether_smash_step2.py (standalone smash module, 6 edits), run_step2_smash.sh (shell launcher, 8 edits), Aether_Porting_Smash_cli.py (CLI refactor, 6 edits), _envcheck×7 (env probing), _validate_step2.py, _pyfind/_pycheck/_findlib/_ldcheck/_findboost/_findoa (debug probes), _clean×9 (cleanup)
- **run_commands ×multiple**: ls/probe Aether install, test python paths, run smash script

## Key deliverables (final state)

### 1. aether_smash_step2.py (16310 chars, standalone smash module)
- `require_pyae()`: guards `import pyAether`; raises RuntimeError with clear message if not importable
- **Pure helpers** (no pyAether, unit-testable): STRETCH_INST_INFO (Nicap_Ring stretch CDF), stretch detection, modify-dir path validation
- `run_smash(params)`: main smash — reads params dict (top_lib/top_cell/top_view/modify_dirs/stop_libs/do_delete/log_file), uses pyAether dbOpenCV/dbCheckIsPCell/emyObjectIsAGR/dbSmashInst2/dbSaveCV to smash vias/AGR/pcells under top cell
- params.json schema: {top_lib, top_cell, top_view, modify_dirs, stop_libs, do_delete, log_file}

### 2. run_step2_smash.sh (2448 chars, shell launcher)
- sources ~/setup.bash for AETHER_ROOT
- finds Aether bundled python: $AETHER_ROOT/tools/aether/platform/linux26-x86_64/python/3.9/bin/python (3 candidates)
- sets PYTHONPATH=$AETHER_ROOT/tools/pyaether/3.9/linux26-x86_64/lib
- runs `"$PY" "$SMAASH_PY" "$PARAMS_JSON"`

### 3. Aether_Porting_Smash_cli.py (2537+ chars, CLI refactor)
- argparse: --top_lib, --top_cell, --top_view, --modify_dirs, --stop_libs, --delete, --log
- maps CLI args to original form fields
- init_logger(log_file), emy_error/emy_warn/emy_info
- stop_libs set always includes TECHLIB

### 4. params.json generation (from USER#4 template)
- top_lib={Lib}, top_cell={Cell}, top_view={View}
- modify_dirs=/proj/{Product}/{Version}/libs
- stop_libs="TECHLIB,basic,{Product}_MAT"
- do_delete=false (default)
- log_file=current_dir/Smash.log

## Case design: AetherSmashCliPort-001 (B档 synthesized mock-behavioral)

**Mock approach**: Replace live Aether/pyAether smash with a Python fixture that preserves the core CLI porting algorithm:
1. Parse original Aether GUI script (mock with form-field definitions + smash stub)
2. Generate standalone smash module (require_pyae guard + run_smash + pure helpers)
3. Generate CLI wrapper (argparse mapping form→CLI args)
4. Generate shell launcher (find bundled python + PYTHONPATH)
5. Generate params.json from input spec template

**Visible input (A)**: original_smash_script.py (mock GUI script) + input_spec.json (Lib/Cell/View/Product/Version/Username)
**Hidden input (B)**: different input_spec.json (different Lib/Cell/Product)
**Deliverable**: smash_cli.py + gen_params.py + run_smash.sh + manifest.json in submit.zip
**15 conditions (a-o)**: structure 3 (a-c: zip+py_compile×2) + smash_cli structure 3 (d: require_pyae guard / e: argparse 6 args / f: run_smash params keys) + shell 2 (g: AETHER_ROOT+bundled python / h: PYTHONPATH pyAether) + params gen 5 (i: all 7 fields / j: top_lib==B Lib / k: stop_libs TECHLIB+{Product}_MAT / l: modify_dirs template / m: B2 different) + determinism 1 (n: re-run same) + anti-hardcode 1 (o: B≠B2)
