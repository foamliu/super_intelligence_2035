# deepread — 1793675505011_qxaiv (junwangt / hfeg0plg07) · DRC switch-syntax-check sweep 优化

**轮**: r402 (2026-11-11 22:2x) · **结局**: parked（预算受限，深读完成未合成 case；DEBT+1）
**match_count**: 169 · **keywords**: drc:312;pdk:146;lvs:17;calibre:16;innovus:8;techfile:1
**domain**: physical_verify · **user prior**: junwangt 0 prior across all 4 shards（本 shard C 首条，fresh against A/B/D）
**trace size**: 1.1MB · 321 msgs (167 user / 154 assistant) · agent=lead
**tool_use**: 151 calls (read_files:43, editor:65, run_approved_command:31, list_allowed_files:8, run_commands:1, search_codebase:1, get_agent_policy_status:2)
**editor 形态**: `path`+`new_text`(write) / `path`+`old_text`+`new_text`(edit)；command 字段 None/absent

## 任务（USER#1, 14 条指令归纳）
优化 Perl DRC runset switch-syntax-check 脚本 `switch_syntax_check_LDDBG4B.pl`：
1. 遍历 LOGIC(Back/Face/NO) × BUFFER(YES/NO) × DRAM(1/2/4/6/8) 全组合（3×2×5=30 combo）
2. 每组合：重写 runset 中对应 switch 值 → 跑 `rules_syntax_checker $runset > tmp.log`
3. 仅当 `logic ne NO && buffer ne NO` 时检查 `output =~ /^error/im` 报错
4. 优化目标：并行化 + 日志文件输出 + 固定宽度列对齐 + 实时进度 + 全 YN switch 入结果行 + 不留 runset_dump

## 原始脚本（msg #2, 67 行, serial）
- 嵌套 foreach LOGIC×BUFFER×DRAM
- 每组合 `open(FH,'+<',$runset)` + `seek` 原地改 switch 行 + `close`
- `system("rules_syntax_checker $runset > tmp.log")` 串行
- 条件报错 `if ($logic ne "NO" && $buffer ne "NO") { if ($out =~ /^error/im) {...} }`
- 无并行 / 无日志文件 / 无列对齐 / 留 runset_dump 目录

## 7 次 editor 演化（最终 = `switch_syntax_check_LDDB2.0_optimized.pl`）
| msg | 类型 | 关键变换 |
|---|---|---|
| #243 | write | 初始 optimized 版：Parallel::ForkManager 引入，`--jobs 48` 默认 + override；runset 读取一次缓存，per-combo 内存编辑 + temp file；结果 append `./syntax_check_results.log`（非 stdout）；固定宽度 `%-14s %-18s %-18s %-18s` |
| #275 | edit | 移除 runset_dump 目录创建/清理段（改为 temp file 流，不留目录） |
| #277 | edit | 加 sanity-check：`which rules_syntax_checker` 在 PATH 否则 die |
| #279 | edit | 加实时进度条 `\r` + 完成百分比 |
| #283 | edit | NC_CHECK + 11 YN switch (LBM2_CHECK DxTSV_COPY BFBM2_CHECK D1BM2_CHECK D3BM2_CHECK D5BM2_CHECK D7BM2_CHECK DxTM_FOLLOW_M5 DxM1_FOLLOW_M1 BUFFER_CP_CHECK) bit-packed yn_bits 追加结果行 |
| #307 | edit | 列宽微调（容纳 NC_CHECK 长 flag 名） |
| #311 | edit | 最终打磨：注释 + 默认 jobs 文档 |

## 最终脚本特征（供未来 case 合成参考）
- `use Parallel::ForkManager; my $pm = Parallel::ForkManager->new($jobs)` （$jobs 默认 48，`--jobs N` override）
- runset 模板读一次进 `$runset_tpl` scalar；每 combo `my $r = $runset_tpl; $r =~ s/^LOGIC\s+.*/LOGIC $logic/m; ...` in-mem 编辑 → 写 temp file → `system("rules_syntax_checker $tmp > $combo.log")`
- 结果行格式 `printf $logfh "%-14s %-18s %-18s %-18s %s\n", $logic, $buffer, $dram, $status, $yn_bits`
- `./syntax_check_results.log` append-only（非 stdout）
- 实时 `\r` 进度条 `[12/30] 40%`
- 11 YN switch bit-packed 进 `yn_bits` 字符串
- 错误检测条件保留：`logic ne "NO" && buffer ne "NO" && $out =~ /^error/im`
- sanity-check `rules_syntax_checker` 在 PATH
- 不留 runset_dump 目录

## B 档合成判定（为何 parked 未合成）
真实流依赖 live `rules_syntax_checker`（产品 DRC deck 检查器，.75 沙盒无此工具）+ 真实 runset（产品 switch 值，敏感）。合成需：
- visible A = runset_template（合成 switch 占位）+ 原始 67 行慢脚本 + `rules_syntax_checker` stub（deterministic error/OK）
- hidden B = runset_B（不同 switch 值）+ stub_B（不同 error pattern）→ cross-input guard
- reference = 重建 optimized 脚本（从 7 次 editor patch 反演完整文件）
- check.py k≈14 a-n：zip 1 .pl / `perl -c` syntax / `--jobs` argparse / `Parallel::ForkManager` 源码 grep / 跑 B exit0 + 写 log / log 含 30 combo / 固定宽度列正则 / NC_CHECK + 11 YN 全现 / 错误检测条件（stub_B error combo 正确标记）/ 无 runset_dump 残留 / sanity-check / cross-input guard 跑 A 结果≠B
- 风险：Parallel::ForkManager 在 SUT 沙盒/检查环境未必装 → reference 须 `eval{require}`+serial fallback；SUT 提交若硬 require 会在缺模块环境 crash（case 环境敏感）
- ≥2 negatives + negative_selftest + §4.9 三假 + 自验全跑一遍

**park 原因**：r402 40min 硬预算下，从 1.1MB trace 反演完整 optimized 脚本（7 次顺序 patch 应用）+ 设计 check.py ≥8 断言 + 2 stub + negatives + §4.9 三假 + 自验全跑，预估 ≥38min，预算不足致未合成。深读完成，分析入档，**留待未来预算充裕轮合成 DrcSwitchSweepOpt-001**。

## claim/ledger
- `trace_ledger.py --shard C claim --session 1793675505011_qxaiv --user junwangt --host hfeg0plg07 --match 169 --domain physical_verify`（r402 22:40）
- r402 收尾 `mark --status parked`（深读完成，预算受限 park）

## 复用价值
- check.py 模式 = **源码/AST grep + 行为 smoke test（stub 外部命令）**，适合所有「外部 EDA 命令驱动的 Perl/Python 脚本优化」trace（DRC deck sweep / LVS runset batch / Calibre deck gen）
- runset_template + switch-combo 遍历模式可复用于其它 switch-sweep / corner-sweep 优化 case
- 7 次 editor patch 反演法 = 通用 trace→gold 重建技术（适用任何 editor-heavy 代码优化 trace）
