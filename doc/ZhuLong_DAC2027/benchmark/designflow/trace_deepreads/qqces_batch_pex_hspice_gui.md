# qqces — batch PEX + Hspice GUI 修改 (e0039786 @ hfeg0pkn005, mc112)

trace: `/home/e0039786/.cline/data/sessions/1795074095632_qqces/1795074095632_qqces.messages.json` (113 msgs / 493KB)
scan: `ssh_eda_search_20261119_172105/summary.tsv` row: `10.129.x  hfeg0pkn005  e0039786  1795074095632_qqces.messages.json  441  waveview:1231;drc:617;synopsys:482;...` → B-shard spice_kw filter (hspice:238 in kw; but real domain from trace = PEX+Hspice batch flow, spice_sim/characterization adjacent)
ledger: claimed r894, fresh, NEW-user (e0039786 prior=0 in ledger_B)

## 用户真实意图（5 轮 user turn 原话）

1. **T0**: 「修改 `/home/e0039786/Desktop/DUT_lib/loop/pec_gui.py`，新增一个批量任务的功能，勾选后：可以对一批 GDS 进行抽网表和 Hspice 仿真；Browse GDS 和 Browse SP 可以选择多个 GDS 与 SP 文件，新增一个排序框，可以对选择的 GDS 和 SP 进行排序，gds 抽网表的顺序将按照数字从小到大进行，GDS 抽出的网表和排序数字相同 SP 文件进行配对，一起放入指定的路径下，等所有数字的 dspf 网表与 sp 文件都存入指定路径后，再调用指定路径下的 run 程序，批量提交 Hspice 仿真任务。」
2. **T46**: 报错 `NameError: name 'fr2' is not defined`（assistant 之前把局部 `fr2` 改成 `self.fr2` 破坏了后续 `fr2.pack()`）。
3. **T52**: 「给这个界面加一个滑动块，使这个页面能够滑动（内容多，没滑动块有些内容被阻挡）。」
4. **T67**: 「我发现程序执行批量任务在 copy dspf 网表和 sp 文件时，不仅会拷贝到 CAPSIM DIR 路径中的 DBC folder 中，还会另外 copy 到 Batch output dir 路径下，你检查一下原因，不要让它 copy 两次。」
5. **T96**: 「修改之后有报错，进行批量任务的时候它会报错，不再把网表和 sp 文件复制到指定路径，你检查一下原因。」（根因：`pex_sim.sh` 用 `set -u`，`NO_PLACE` 跳过 S3 后 `SP_BASE` 未赋值，S5 log 行引用 `$SP_BASE` 触发 unbound variable 退出非 0 → worker 中止。）

## assistant 工具链路（关键产物）

- 读 `pec_gui.py` + `pex_sim.sh` + `fix_inc.py`/`make_sp.py`/`comment_subckt.py` 摸清 Glory PEX 抽网表 + Hspice 流。
- 加 batch checkbox + batch frame（output dir + run program + Browse GDS multi `askopenfilenames` + Browse SP multi + sort listbox 带排序数字 + Up/Down/Remove + Run Batch）+ `_batch_worker`/`_toggle_batch`/`_batch_browse_gds`/`_batch_browse_sp`/`_batch_sort`/`_batch_remove_sel` 方法。
- `_batch_worker`：按 sort number 配对 GDS↔SP，对每个 GDS 调 `pex_sim.sh` 抽 dspf（`NO_PLACE=1 NO_HSPICE=1`，只抽不放置），worker 自己把 (dspf, sp) 放到 batch output dir，全部放完再调 run program 批量提交 Hspice。
- 修 `fr2` NameError：恢复局部 `fr2` + `self.fr2=fr2`。
- 加 scrollbar：Canvas + vertical Scrollbar + inner `scroll_frame`，重父化所有 frame；`_on_canvas_resize`/`_on_scroll_frame`/鼠标 wheel binding（`<MouseWheel>`/`<Button-4>`/`<Button-5>`）。
- 修 double-copy：`pex_sim.sh` 加 `NO_PLACE` flag，`=1` 时跳过 S3（copy dspf→`SIM_SUB` + `fix_inc.py` 写 sp），worker 拥有全部放置权。
- 修 `set -u` unbound `SP_BASE`：跳过 S3 后 `SP_BASE` 默认 `GDS_BASE`，S5 log 安全。
- 自验：`py_compile` + `bash -n` + headless `_batch_worker` 逻辑测试（stub 外部工具，验证配对/放置/run 调用/`NO_PLACE=1` 传递）。

## portability-reframe 决策（A 档不可便携 → 参数化生成器）

真实环境依赖 Glory PEX 抽网表工具 + 真实 PDK + Hspice + `/home/e0039786/Desktop/DUT_lib/loop/` 路径，不可便携入 SUT 沙盒。
reframe：造参数化生成器 `batch_pex_hspice_gui_gen.py`，读 spec.json → 产出 `<module_name>.py`（tkinter.ttk GUI + 模块级纯函数 `batch_worker_logic(gds_items, sp_items, output_dir, run_program, extract_cmd, env_no_place, env_no_hspice, log_func)`，可 headless 调用）+ `<shell_name>.sh`（`set -u` + `NO_PLACE` 跳放置 guard + `SP_BASE` 默认 guard + S5 log 安全）。
spec 参数化点：module/shell 名、batch checkbox/frame/output dir/run program 标签、各方法名、sort 升降序、extract_cmd 名、NO_PLACE/NO_HSPICE env 名、SP_BASE 默认源变量、scrollbar/mousewheel、log_fail_prefix、header banner。
hidden B = 结构性反向（不同 module/shell/方法名、sort 降序、不同 env 名、不同 run program auto-prefix、不同 banner）；hidden B2 = anti-stub（第三变体，方法名/run-program 又不同）。
判分：B+B2 真跑生成器 → py_compile + bash -n + 结构串逐一核对 + import 模块 headless 调 `batch_worker_logic` 验配对/放置/run 调用/`NO_PLACE=1` 传递/无 double-copy + anti-stub B2≠B + 反硬编码 A + 确定性 3-run sha256。

## 形态归类
script-build portability-reframe 第三十六实证（r847-r893 series 续）；GUI-modify + shell-integration + bug-fix 三合一 reframe；B 域 spice_sim/characterization（PEX 抽网表 + Hspice 批量提交）。
