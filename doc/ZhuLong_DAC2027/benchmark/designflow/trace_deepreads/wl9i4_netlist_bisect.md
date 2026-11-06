# 深读笔记 — wl9i4 / xingx / hfeg0pkn003 / mc404 / schematic_netlist

## trace 元数据
- session_file: `1792042618272_wl9i4.messages.json` (dir-based: `/home/xingx/.cline/data/sessions/1792042618272_wl9i4/1792042618272_wl9i4.messages.json`, 1.7MB)
- user/host/ip: xingx / hfeg0pkn003 / 10.129.2.12 (also on hfeg0pkn002/10.129.2.11, same NFS home)
- match_count: 404 (netlist:1277, hspice:11, schematic:8, synthesis:7, virtuoso:5, calibre:5, pyAether:4, innovus:4)
- n_msgs: 752, user turns: 25, tool_uses: 356 (run_approved_command:266, editor:69, read_files:13)

## 用户意图（逐轮原文，produce 轮）
- U#0/U#2: `pwd` → `cd /proj/ddgoa/V0/simdir/verilog/xingx/`
- U#7: `执行make compile_net -n` (dry-run)
- U#45/U#51/U#66: 跑 make compile_net，等待并报告是否编译成功
- U#100/U#114/U#124: module load ds/xcelium/24.03.005 → `make compile_net nc=off`
- **U#300** (核心需求): "this compile time is too long. I need you to give me a schedual to find out if there is a way to shorten the compile time cost"
- **U#306**: "the earilier version netlist, the total time cost of compile/elabotion is about 25 minutes. so the first thing i need you check is the netlist. but the netlist is huge. do you have the plan to analyze it?"
- **U#344** (交付约束): "1. created a new directory /proj/ddgoa/V0/simdir/verilog/xingx/net_test 2. all your jobs will be done in it, you can copy the netlist and libs into this directory. 3. don't change other files. 4. you can use your command to replace the 'make compile_net nc=off' 5. the changes you made to any copied files, please give me a log to show me the difference line and why you change it."
- **U#416** (方法论): "i think you can do binary sort on the nestlist, by annotating the netlist into different pieces and parallel do compile/elaboration jobs. and then you can find which part of the code affected the time cost most."
- **U#495** (关键澄清): "the Array16GTop is also the part we should verify. Only the schematic marked with special view like verilog view, we can use a model to replace the schematic. So maybe it is time for you to do binary annoating the code to find out which code spend the most time."

## assistant 工具链（produce facet）
1. **parse_children.py** (sha256 59b8343c) — 解析 Verilog netlist，找指定 module 的 direct child instances。输出格式：
   ```
   LP5TOP spans lines 939145..945078
   direct instances under LP5TOP: 4
   HShortHSInPkg                                I_HShortHSInPkg_272
   QShortQSInPkg                                I_QShortQSInPkg_273
   Channel                                      I_Channel
   Array16GTop                                  I_Array16GTop
   ```
   实现：定位 `module <mod>` ... `endmodule` 行范围，正则 `^\s*([A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*\(` 提取实例（跳过 input/output/wire/reg 等声明）。
2. **mkrun.sh** — 创建 run dir（filelist.f + libs/netlist 符号链接）。
3. **run_cmp.sh** — 用 LSF bsub 提交 xrun elaboration：`bsub -q vbatch_lp -I "xrun +access+rwc +sv +xm64bit ... -top <Module> -f filelist.f -c (tag=<tag>)"`
4. **qcheck.sh** — bjobs 查状态 + tail xrun.log，提取 elaboration stats（Initial blocks / Cont. assignments / Pseudo assignments / Timing checks / Process Clocks）。
5. **log_expN.sh** — 把每轮 bisection 结果追加到 CHANGELOG.txt。

## 真实二分搜索结果（热点定位）
```
WOWTOP  (whole chip) ............................................ ~69 min
├─ I_A_Top      (Ary16G,   top-level 16G array) .................. ~3 min
├─ I_C_Top      (LP5TOP,  controller/logic) ..................... ~62 min
│   ├─ I_Channel (Channel) ...................................... ~4 min  (init 1.08M, pseudo 0.57M)
│   └─ I_Array16GTop (Array16GTop) .............................. ~59 min  ★ (init 2.70M, pseudo 7.34M)
└─ SealRing (2x) ............................................... negligible
```
热点 = **Array16GTop**（~59/62 min of LP5TOP, ~86% of total ~69-min, driven by ~7.34M pseudo-assignments）。

Array16GTop 再分：Array8G_W / Array8G_E / SpineTop（trace 在 round-3 监控中截断，未给出最终数）。

## A-faithful 判定
- ❌ 不可移植：live xrun + LSF bsub + 49MB netlist（/proj/ddgoa/...）+ 真实 elaboration 时间驱动自适应二分。
- ✅ B-grade synthesized：取可移植 facet = **netlist compile-time bottleneck 二分定位器**（读 netlist + per-module xrun stats → 产出 parse_children.py + bisect_plan.json + hotspot_report.md + run_plan.sh）。check 验结构（树/表/命令/热点）不验真跑 xrun。L1 离线可验。

## 合成 plan（NetlistBisectLocalize-001, schematic_netlist, B, L1, 16 条件 a-p）
- **gen tool**: `netlist_bisect.py --spec <spec.json> --outdir <out>`
- **spec.json 结构**: {netlist_path, top, xrun_flags:[...], lsf_queue, module_stats:{<mod>:{elapsed_min, initial_blocks, pseudo_assigns}}}
- **产出 4 文件**:
  1. `parse_children.py` — 独立子工具（与真实 trace 同名同格式），`python3 parse_children.py <netlist> <module>` 打印 children
  2. `bisect_plan.json` — 完整二分树（root=top，递归 children 来自 netlist 解析；每个节点带 stats）
  3. `hotspot_report.md` — 树图（缩进）+ stats 表（module/elapsed/initial_blocks/pseudo_assigns）+ 显式 dominant block
  4. `run_plan.sh` — 每个非叶 module 的 children 各一条 xrun+bsub 命令
- **A**: netlist_A.v (WOWTOP→Ary16G/LP5TOP→Channel/Array16GTop→Array8G_W/Array8G_E/SpineTop), spec_A.json (stats 忠实转录真实数: WOWTOP 69/3.8M/7.9M, LP5TOP 62, Array16GTop 59/2.70M/7.34M, Channel 4/1.08M/0.57M, Ary16G 3, ...)
- **hidden B**: netlist_B.v (CHIPTOP→CoreTop/PhyTop/AnalogTop/SealRing, CoreTop→CtrlUnit/CacheTop/DtuTop, PhyTop→PcsTop/PmaTop, CacheTop→TagArray/DataArray×4), spec_B.json (top=CHIPTOP, dominant=CoreTop 80min, 不同的 xrun_flags/lsf_queue)
- **hidden B2**: spec_B2.json (同 netlist_B 但 top=CoreTop，dominant=CacheTop，第3套 stats/flags/queue) — 击败硬编 top/dominant/flags/queue
- **反硬编码轴**: top 名(A/B/B2 = WOWTOP/CHIPTOP/CoreTop 全不同)、module 名全不相交、dominant block 不同、xrun_flags 不同、lsf_queue 不同 → 硬编 A 字面量 → 多 cond FAIL

## check 16 条件 a-p 清单
①submit.zip 顶层含 netlist_bisect.py 且无 check/reference/negative/.jsonl/.tsv/spec_B 泄漏且 py_compile 通过
②B-run exit0 且 4 文件(parse_children.py/bisect_plan.json/hotspot_report.md/run_plan.sh)均非空
③emitted parse_children.py 在 hidden B netlist 上正确提取指定 module 的 direct children（module+instance pairs，与正解一致）
④parse_children.py 输出格式含 "spans lines" + "direct instances under X: N" + "<Mod> <Inst>" 行
⑤bisect_plan.json 有效 JSON，root == spec_B top
⑥bisect_plan.json 每个非叶节点的 children 列表与 netlist_B 解析的 direct children 一致（按名集合）
⑦bisect_plan.json 是 valid tree（所有 child 引用要么是叶、要么是 plan 内节点；无悬空引用）
⑧bisect_plan.json 覆盖 spec_B module_stats 中所有 module（每个有 stats 的 module 都在树里）
⑨run_plan.sh 含 xrun 命令且每个非叶 module 的每个 child 有一条 `-top <Child>` 行
⑩run_plan.sh 含 bsub 提交到 spec_B lsf_queue
⑪hotspot_report.md 含二分树图（缩进/box 形式，含每个 module 名）
⑫hotspot_report.md 含 stats 表（列含 module/elapsed/initial_blocks/pseudo_assigns）且 ≥1 行 per non-trivial module
⑬hotspot_report.md 显式标识 dominant block（含 "dominant" 字样 + 该 module 名）
⑭dominant block == argmax(elapsed_min) 来自 spec_B module_stats（不是硬编 Array16GTop/WOWTOP）
⑮确定性：3 次 B-run bisect_plan.json sha256 一致
⑯反硬编码：源码无 A 字面量(WOWTOP/LP5TOP/Array16GTop/Channel/vbatch_lp)；A-run 产 A-correct plan(root==WOWTOP)

## 自验清单
- ref PASS 16/16
- 6 negatives 全 FAIL（empty_shell/print_expected/ref_core_deleted/hardcode_a/hardcode_b/drop_runplan）
- §4.9 三假（empty_shell/print_expected/ref_core_deleted）全 FAIL
- k_rationale == k_check == 16 ✓
