# 深读笔记 — 19y5l FineSim .PROBE 电流语法诊断 + x-probe 改写

## trace 元信息
- session: `1793012967002_19y5l`（thqu @ hfeg0plg99, mc=78, 127 msgs, 512KB）
- tools 关键词: hspice/finesim/spice/simulator（spice_sim domain）
- agent: lead (cline)

## 真实流（逐轮用户意图）
- U0: 问 `/rundata/.../ncsim.shm` 是什么文件 → 纯解释（NC-Sim 数字仿真数据库目录），非 spice 交付
- U2: 「sp文件如何probe出每一个节点的电流」→ **A 档选轮候选**：干净「提出需求」，未给根因/修复。agent 走 AskEDA RAG 给文字解释（`.PROBE IALL`/`.PROBE I(M1)`/`.PROBE IALL(M1)`），**无 runnable artifact**
- U10: 「.probe v(*) i(v*) isub(*.inh_*) / .probe i(*) 这个为什么只probe出了输入激励的电流」→ 报告观察（不是给根因/修复），问「为什么」
- U14: 「.probe isub(*.inh_*) 我这样写怎么一个电流都没又啊」→ 报告观察
- U18: 「.inc '...NET_v2_3' 网表是这个，我想要 I_R_NegVssIdd2N_645 和 I_R_NegVssIdd3N_645 这两个的输入输出电流」→ **干净意图**：要两个子电路实例的端口电流
- U58: 「.../Result_IDD/NET_v2_3/ 看一下log文件」→ 让 agent 读 sim log
- U75: 「你帮我修改一下」→ 让 agent 改 test.sp
- U103: 「读一下最新的结果和log文件」→ 读改后重跑结果
- U109: 「在wv里边还是只能看到电压他」→ 报告 WaveView 只见电压（最后一条用户轮，无显式接受）

## 关键技术点（trap 三连）
1. **`.probe i(*)` 只探测独立源电流**（V/I 开头的 voltage/current source），不探测器件电流。`*` 通配符在 `i(*)` 中只匹配独立源名。要测器件电流用 `.PROBE IALL(M1)` 或逐个 `.PROBE I(M1)`。
2. **`.probe isub(*.inh_*)` 无输出**：`isub()` 不支持通配符 `*`，参数必须是明确的子电路端口路径 `isub(xtop.xbank.xinh_env.vdd)`。且 `isub` = sub**circuit** port current（非 substrate 衬底电流，常见误解）。
3. **`.PROBE I(实例名.端口名)` 在 FineSim 中失败**：FineSim 把 `I(name)` 当**器件**电流，端口不是器件 → `WARNING! can't find device 'xi_r_negvssidd2n_645.negvncsgn' for .probe`。正确写法是 **FineSim x-probe**：`.probe tran x(实例名.端口名)`，或等价 `ISUB(实例名.端口名)`。

## agent 实际交付
- 经 read_files / search_codebase / list_allowed_files / run_approved_command 读 NET_v2_3 网表 + test.sp + test.log
- 定位 test.sp 第 56-70 行用了 14 个 `.PROBE I(XI_R_NegVssIdd2N_645.<port>)` / `.PROBE I(XI_R_NegVssIdd3N_645.<port>)`，FineSim log 第 144-153 行全部 `can't find device` 警告
- 用 editor 在 `/home/thqu/fix_probe.py` 写一个 Python 替换脚本，run_approved_command 跑它把 test.sp 的 `.PROBE I(...)` 改成 `.probe tran x(...)`
- 重跑 FineSim：`# probed signals : 102 (# x(): 14)`，0 警告，Successfully Completed
- U109 报告 WaveView 看不到电流 → agent 给 WaveView 信号搜索建议（`x(...)` 命名规则）
- **无显式用户接受**（U109 是抱怨，agent 给建议后无后续用户轮）

## A 档判定
- U2 是最干净的「提出需求」轮，但 agent 仅 RAG 文字解释，无 runnable artifact，trace 末尾用户未显式接受
- → **A 档不可用**（无金标准产物形态 + 无用户接受）→ **B 档 synthesized**：保留「FineSim `.PROBE I(subckt.port)` → x-probe 改写 + 重跑验证」子技能，金标准由 .75 标定

## distinct vs 已有 B spice_sim case
- gvm3g=ModelScopeFix（.model scope 误用）·hk622=NoRefCktFix（缺 .refckt）·uky6c=DcConvFix（DC 不收敛 dcalg/nodeset）·cllpy/b86q7=Vcc2scActDeckGen（deck 生成器）·fwgyy=FineSimWorkflowRunner（自主工作流）·5kcuw=StimLoopComplianceFix（.for/.while stimulus 合规）·q9r9s=TbAuditFix（undefined .param/empty probe/redundant Vsrc）·hgfso/CmdEdgeMeasGen（.measure deck 生成）
- **本条=FineSim `.PROBE I(subckt.port)` → x-probe 静态改写 + 重跑双验（original warnings / rewritten # x():）**，shard B 首个「current-probe 语法诊断 + x-probe 改写器」case，distinct ✓
- 注意 vs q9r9s TbAuditFix：q9r9s 的「empty `.probe v()`」是空选择子语法错；本条是「`.probe I(subckt.port)` 语义错（端口非器件）」，trap 完全不同（q9r9s 改 `.probe v(*)`，本条改 `.probe tran x(...)`）

## 便携化（.75 可行性已验证）
- trace 走 foundry PDK（cxmt）+ LPDDR5 IO 子电路，不可便携 .75
- reframe：level-1 Shichman-Hodges MOS + 自定义 subckt（显式端口）+ FineSim V-2023.12-1 -spice
- **.75 实测（V-2023.12-1, /proj/train/AI workdir）**：
  - broken（`.PROBE I(xdut.in/out/vcc)`）→ `WARNING! can't find device 'xdut.in' for .probe (tb_broken.sp:8)` ×3，`# probed signals : 8`（0 x()），Successfully Completed（警告非致命）
  - fixed（`.probe tran x(xdut.in/out/vcc)`）→ 0 警告，`# probed signals : 11 (# x(): 3)`，Successfully Completed
  - 确定性：重跑 byte-identical（FineSim 无随机）
- 关键判定信号：log 中 `# probed signals : N (# x(): M)` 行；`can't find device '<arg>' for .probe` 警告行

## case 设计 EDA-Eval-DesignFlow-ProbeSyntaxFix-001（spice_sim, B档 synthesized, L2 真跑 FineSim -spice, k=15 计划）
- 子技能：检测 `.PROBE I(<dotted.subcircuit.port>)`（FineSim 把 I() 当器件电流，端口非器件 → can't find device）→ 改写为 `.probe tran x(<dotted>)`（x-probe 子电路端口电流）；同时诊断 `.probe i(*)`（只独立源）+ `.probe isub(*.wildcard)`（不支持通配符）报告但不自动改；保留 `.PROBE I(<device>)`（无 `.`，真器件电流）不改
- A（可见）：subckt `inv_a`（4 端口 in_a/out_a/vcc_a/vss_a）实例 `xinv_a`，broken `.PROBE I(xinv_a.in_a/out_a/vcc_a)` + 真 `.PROBE I(xmn_a)`（保留）+ 诊断 `.probe i(*)` + `.probe isub(*.inh_*)`
- B（hidden）：subckt `nand2_b`（5 端口 a_b/b_b/y_b/pwr_b/gnd_b）实例 `xu_b`，broken `.PROBE I(xu_b.a_b/b_b/y_b/pwr_b)` + 真 `.PROBE I(xmp_b)`（保留）+ 诊断 `.probe i(*)` + `.probe isub(*.vbb_*)`；不同端口数/名/实例名/器件名 → 防 hardcode
- 候选 probe_syntax_fix_ref.py（CLI <testbench.sp> <spec.json> <out_dir>：正则检测 `.probe i(<dotted.arg>)` → 改写 `.probe tran x(<dotted>)`；检测 `.probe i(*)` / `.probe isub(*.wildcard)` → diagnostics；保留无 `.` 的 `I(device)` → subprocess finesim -spice 原始 + 改写 → parse log `# probed signals : N (# x(): M)` + `can't find device` warning count → probe_fix_report.json + testbench_rewritten.sp + sim_log/{original,rewritten}.log）
- check.py 15 条 a-o：(a)zip+tool (b)py_compile (c)B FineSim 真跑签名+completed (d)B 报告 broken_probes 非空≥预期 (e)B rewritten 有 `.probe tran x(...)` 且无 dotted `.probe I(x` 残留 (f)B rewritten log `# x():` 匹配 GT (g)B original log `can't find device` 警告数≥预期 (h)B rewritten 0 警告 (i)B 真 `.probe I(<device>)` 保留未改（反 over-rewrite）(j)B 诊断 i(*)/isub(*) 检出报告 (k)report schema 完整 (l)跨输入守卫 rerun A：A rewritten 有 A-token(xinv_a/in_a) + A `# x():` 匹配 A GT (m)judge 独立重跑 B rewritten→completed+# x(): 匹配 (n)确定性重跑 B rewritten_n_xprobe 一致 (o)B rewritten 无 A-token 泄漏（反 hardcode_a）
- 6 neg：naive_empty/naive_print_expected/naive_no_rerun/naive_over_rewrite（把所有 I() 都改包括真器件）/naive_hardcode_a/naive_drop_diagnostics + §4.9 三假
- GT 标定：A → broken 3 warnings, rewritten `# x(): 3`, 保留 `I(xmn_a)`；B → broken 4 warnings, rewritten `# x(): 4`, 保留 `I(xmp_b)`（待 .75 实测确认）
