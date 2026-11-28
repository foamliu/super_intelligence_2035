# Deepread: q6c1s — vsim_aether SDF 生成失败诊断

- session: 1795524485471_q6c1s
- user: sijialv @ hfeg0pkn004 (drvqa QA 环境)
- mc: 180, domain: schematic_netlist (netlist:3156;verilog:1968;schematic:1031;cmos:902;aether:253;pt_shell)
- trace: 688KB / 82 msgs (46 user / 36 asst), 10 list_allowed_files + 11 read_files + 10 editor + 9 run_approved_command
- FRESH (sijialv 仅 gwa9k 在 A 台账 mc6 digital, 本 session 全新), 已 claim D 台账

## 用户真实意图

sijialv 在 drvqa QA 环境调试：同一命令 `./bin/vsim_aether -m -n --sdf --merge &`（多阶段流水线：Aether 网表导出 emy2verilog → 合并 netlist → PrimeTime pt_shell 跑 sdf.tcl 的 write_sdf → 产 `pt_dir/WOWTOP_1C2A.sdf.gz`），为什么 **wangyoukang/172830 出了 SDF** 而 **lhtian 两个目录(164511 / 165950) 没出**。用户要求对比目录（vsim_aether / 环境变量 / cwd / config）找根因。后段用户澄清 165950 现存的 SDF 是手动 `bsub pt_shell -f sdf.tcl` 重跑的，非原 vsim 产物 → 诊断转向「原 vsim 运行为何没出 SDF」。

## 三个目录实测对比（assistant 收集的证据链）

| 检查项 | ① wangyoukang 172830 (成功) | ② lhtian 164511 (失败) | ③ lhtian 165950 (原 vsim 失败, 后手动补) |
|---|---|---|---|
| 顶层 emy.log (Aether 主导出) | 7745 行 Finished 0 errors | **1216 字节 NETLIST ERROR** | 7738 行 Finished 0 errors |
| 顶层 netlist (35MB 合并网表) | ✅ | ❌ 缺失 | ✅ |
| 顶层 netlist.mapping | ✅ | ❌ 缺失 | ✅ |
| pt_dir/pt.log | 93MB "Thank you for using pt_shell!" | **0 字节** | 93MB (后被手动跑覆盖) |
| pt_dir/pt_shell_command.log | ✅ 47MB | ❌ 缺失 | ✅ 47MB |
| pt_dir/WOWTOP_1C2A.sdf.gz | ✅ 115MB | ❌ 缺失 | ✅ 116MB (手动补) |
| pt_dir/sdfgen.log/transition_v.log/capacitance_v.log | ✅ | ❌ 全缺 | ✅ (手动补) |
| pt_dir/netlist_pt (PT 输入) | ✅ 29MB | ✅ 29MB (子导出反成功) | ✅ 29MB |
| 顶层 pt.log (CMD-015 sdf.tcl not found) | ❌ 无 | ❌ 无 | ✅ 1961B (手动/非 vsim, 干扰项) |

## 根因（多分支）

1. **② 164511 失败在 Aether 网表导出**：顶层 emy.log 1216 字节直接报
   `NETLIST ERROR: Netlist isn't produced due to errors reported before`
   未绑定引脚 `fnCompWrbypass` / `fnCompWrbypassrc`（`drvqa_cmos_core/CCRTop24_Com/symbol`，实例 `I_CCRTop24_Com_4Sec_1` in `m512Meg/schematic`）。
   导出中止 → 无顶层 netlist → PrimeTime 阶段根本没启动（pt.log 空、无 pt_shell_command.log）→ 无 SDF。
   注意 pt_dir/emy.log（netlist_pt 那次子导出）反而 100% 0 errors，说明 PT 输入本身没问题，问题在它上游的主导出。

2. **③ 165950 原 vsim 运行失败**：用户澄清现存 SDF 是手动 `bsub -I -q cvps pt_shell -f sdf.tcl` 补的。
   - vsim_aether Perl 脚本（line 497-629）SDF 段逻辑：line 558 `chdir $ptrundir`(pt_dir) → line 566 `if(-s "netlist")` 闸门（pt_dir netlist 导出非空才继续）→ line 603-605 `$sdfcmd="pt_shell -f sdf.tcl > pt.log"; bsub -I -J PTJOB -q $queue_name $sdfcmd` 在 pt_dir 内跑。
   - 所以 vsim 的 pt.log 永远落 pt_dir，**顶层 pt.log 是手动/非 vsim 调用留的干扰项**（CMD-015 "could not open script file sdf.tcl" = 顶层没 sdf.tcl）。
   - vsim_aether 脚本两用户 md5 相同（447f...）；libsdb 最终共享同一套 .db（char/harveyl/tt_db_0828/db_0911，26 项 basic.db 16596992B multidomain.gz 一致）；config/sdf.tcl 1538B 相同；form_sdf.rc/emy_sdf.env/si_sdf.env/form.rc/cds.lib/si.env 全相同。
   - config 差异：verilog.rc* (lhtian 多 brknetM0A/M1A/M2A/M3A/M4A/M6 short-cell 列表)、lib.defs (lhtian 1915B 多两个 work lib)、emy.env/tbconfig 指向不同 cell（但当前值 V0_Nov24 非 11-23 运行时值，仅旁证）。
   - 剩余可能 runtime 因素（非配置内容）：(a) line 566 `if(-s "netlist")` 闸门 — pt_dir netlist 导出空 → "PT netlist Failed!" 跳过 SDF；(b) bsub/queue/env — `$queue_name` 来自 tbconfig/外围 env，队列/环境差异致 pt_shell 未实际执行。

## 关键诊断技能（判分要点）

1. **目录清单对比**：按 file presence/size 判阶段产物是否齐全（netlist/netlist.mapping/pt.log/pt_shell_command.log/sdf.gz/sdfgen.log）。
2. **emy.log 解析**：检测 NETLIST ERROR + 未绑定 pin（pin 名/实例/cell 层次）vs Finished 0 errors。
3. **pt.log 状态**：0 字节 = PT 没跑；"Thank you for using pt_shell!" = 跑完；CMD-015 "could not open sdf.tcl" = 错误 cwd 启动（非 vsim 产物）。
4. **区分 vsim 产物 vs 手动补跑**：顶层 pt.log(CMD-015) 是干扰项；vsim 的 pt.log 永远在 pt_dir；手动 bsub 会覆盖 pt_dir/pt.log。需结合「文件 DATE 是否对应该次运行时间」+「顶层 vs pt_dir 位置」判 manual_override。
5. **vsim_aether 脚本流理解**：chdir pt_dir → `-s netlist` 闸门 → bsub pt_shell -f sdf.tcl。失败可在 export / pt_netlist_gate / pt_launch / sdf_write 任一阶段。
6. **配置/输入一致性判定**：driver md5 / libsdb / sdf.tcl 一致 → 排除配置内容，指向 runtime/env。

## case 合成 plan (task_id=VsimSdfFailDiagnoseProduce-001, LIVE-NA judge[L0,L1])

**synthesized-reframe**：把「真跑 vsim_aether + 真读 .75 上 GB 级目录」（强依赖真实文件系统/LSF/PrimeTime 二进制）reframe 为 spec-JSON 驱动纯 Python「vsim_aether SDF-failure 运行目录比较器 + 阶段诊断器」`diagnose_vsim_sdf.py(spec)->report.json`。无真实 EDA 二进制依赖（vsim_aether/pt_shell/emy2verilog 不在 eval 沙盒）。

**spec schema**：`{runs:[{name,user,manifest:{file:{present,size}},top_emy_log:{size,status,netlist_error,unbound_pins:[{pin,inst,cell}]},pt_dir_pt_log:{size,status,tail},top_pt_log:{size,status,cmd_error},config:{vsim_md5,libsdb_shared,sdf_tcl_identical,verilog_rc_diff,lib_defs_diff},sdf_present_manual_override:bool}],compare_summary:{driver_identical,libsdb_shared,sdf_tcl_identical}}`

**reference `diagnose_vsim_sdf.py`**：spec 驱动通用实现：
- `_classify_run(run)`：按 emy.log(netlist_error→failed_export) / pt_dir_pt_log(0B→failed_pt; empty+no netlist→failed_pt_netlist_gate; CMD-015 top→manual_override) / sdf 缺失 → failed_sdf_write / 全齐→success。返回 outcome + failing_stage + root_cause + evidence[]。
- `_cross_compare(runs)`：driver/libsdb/sdf_tcl 一致性判定 → 排除配置内容，标 runtime_suspect。
- `report.json`：{runs:[{name,outcome,failing_stage,root_cause,evidence}],compare_summary,verdict}

**check.py ~16 conds a-p** (k_check=k_rationale=16, 独立 gold 分支复算 classify_run 走不同代码路径 for/if + cross_compare + report 解析 + anti-hardcode tokenize 剥注释/字符串/docstring 源码扫描无 A-only token + 确定性 md5 + hidden-B 跨输入守卫)：
- a zip 含 diagnose_vsim_sdf.py ②b py_compile ③c A 运行 valid ④d A runs 数 ⑤e A 每 run outcome gold 匹配 ⑥f A failing_stage 匹配 ⑦g A 164511 root_cause 含未绑定 pin 名 ⑧h A 164511 evidence 含 NETLIST ERROR ⑨i A 165950 manual_override 识别 ⑩j A 165950 top_pt_log 标干扰项 ⑪k A compare_summary driver_identical=true ⑫l A libsdb_shared=true ⑬m A verdict 正确 ⑭n B 运行 outcome 全对(不同 failure mode) ⑮o anti-hardcode 源码无 A-only token ⑯p 确定性 3-run md5 一致。

**A (visible) spec_A.json**：3 runs 镜像真实 trace（wangyoukang-172830 success / lhtian-164511 failed_export unbound pins fnCompWrbypass / lhtian-165950 manual_override+original_failed_pt_netlist_gate）。真名 token。

**hidden B spec_B.json**：不同 3 runs 不同 failure mode（userA-success / userB-failed_pt_netlist_gate 空 netlist 跳 SDF / userC-failed_sdf_write write_sdf error / userD-manual_override），不同 cell/pin/日期/用户名，token-structurally 不相交 anti-hardcode。

**negatives 4 distinct**：empty→c / print_only→d / core_deleted→e / hardcode_a→n（全 FAIL distinct first-fails）。

**§4.9 trio** {empty,print_only,core_deleted} 3-distinct。ref PASS 16/16。test sha 3-way sync。LIVE-NA judge_layers=[L0,L1]。

**自验**：SKIP_RUN=1 eval/run_one.sh VsimSdfFailDiagnoseProduce-001 --shard D 框架接受；ref check.py PASS 16/16；negative_selftest 4-distinct FAIL。

下轮 r1666 按 plan 合成 VsimSdfFailDiagnoseProduce-001。
