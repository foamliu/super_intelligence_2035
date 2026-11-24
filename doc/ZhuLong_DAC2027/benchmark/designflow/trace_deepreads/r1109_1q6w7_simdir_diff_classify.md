# r1109 deepread: 1q6w7 (max7c @ hfeg0pkn005 = 10.129.2.14)

- session: `1795438607101_1q6w7.messages.json` (406KB / 55 msgs)
- scan: mc=18, keywords `verilog:521;netlist:16` (97% A-pure digital/verification)
- eda_flow: open_session(peek-A-r1109) → ssh 10.129.2.14 cat messages.json → close(cleaned)

## 用户真实意图（trace 原文）

**U#0** (act mode):
> 比对 /proj/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.Nov23/ 和 .../Nov17/ 下的一级目录
> 把 Nov23 有但 Nov17 没有的文件复制到 .../Nov17/

**U#22** (act mode):
> .../Nov17/ 下的 run_async_flow.sh 有问题啊，要等前一个回归跑完才到下一个，我只需要提交命令就行，不用等前一个跑完就能提交下一个，只需要两个命令直接加个 3s 的延时就行

**U#25** (act mode):
> .../Nov17/ 下的 run_async_flow.sh 按 /rundata/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.Nov17/run_regression_all_config_tt 的格式修改

## 助手工具链 (Task 1 = 目录 diff + copy)

1. `list_allowed_files(depth=1)` 列 Nov23 与 Nov17 一级条目（含 hidden）
2. `editor` 写 `diff_simdirs.py`（dry-run：分类 file/dir/symlink，symlink 解析 target + absolute/relative + inside/outside src，计算 total bytes to copy）
3. `run_approved_command(python-runner)` 跑 dry-run → 报告 27 项缺失（7 dir + 18 symlink + 2 file），symlink 全绝对路径指向 src 外部，实际数据 6.85MB（libs 6.4MB 主）
4. `editor` 写 `copy_missing.py`（symlink 复制链接本身不跟踪；目录递归；文件保留属性；复制后验证）
5. `run_approved_command` 跑 copy → 成功
6. `list_allowed_files` 独立验证 Nov17 已含所有新条目

## 关键产物结构

- **diff_simdirs.py**: parse `list_allowed_files` JSON 输出 → classify entries → symlink target analysis → total bytes → JSON + 文本报告
- **copy_missing.py**: shutil.copy2 / shutil.copytree / os.symlink（不跟踪 target）→ post-copy verify

## 域判

digital / verification（LPDDR5 verilog simdir + 回归脚本；纯 A-pure，无 layout/spice 关键词）

## 造题方向

选 **Task 1 (目录 diff + classify)** 造题：交付 `diff_simdirs.py` 通用目录差异分类器。
- 输入：两个 `ls -la` 风格的目录列表文本文件
- 输出：JSON 报告（missing/extra/common + 类型分类 + symlink target 分析 + total bytes）
- B 档 synthesized：真实 /proj/ddjoc 工程树沙箱不可达 → 按 trace-faithful 结构合成 A/B 列表
- hidden-B：完全不同的 DDR4 PHY simdir 列表，A/B 判别 token 零相交（missing/extra 条目名全不同）

## anti-hardcode 判别 token

- A 判别 token: lpddr5_interface.sv, lpddr5_model.v, lpddr5_tasks.sv, lpddr5_test.sv, assertion, coverage, coverage_ai, libs, patterns, proj_common_files, proj_monitor, libs_old, lpddr5_test.sv.bak, Pattern_tasks.v, report_1123, top.sv.bak, /proj/ddjoc/V0/workdir/max7c/sos_manage_lpddr5/
- B 判别 token: ddr4_train.sv, ddr4_model.v, ddr4_interface.sv, ddr4_tasks.sv, timing_table, dft_lib, train_coverage, assertion_bind, wave_probe.tcl, ddr4_phy_top.sv, patterns_b, monitor_b, libs_v1, ddr4_phy_top.sv.bak, netlist_v2, regression_old, probe_v2.tcl, report_1005, top_v2.sv.bak, /rundata/ddr4/workdir/shanliny/
- 零相交 ✓
