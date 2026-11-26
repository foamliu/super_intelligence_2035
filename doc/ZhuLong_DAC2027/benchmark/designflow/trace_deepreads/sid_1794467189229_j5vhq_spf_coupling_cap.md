# deepread: j5vhq — SPF 寄生耦合电容提取（single-signal）

- session: 1794467189229_j5vhq · user gallopc@10.129.2.14 · mc16 · domain schematic_netlist
- kw: cmos:513;schematic:426;netlist:177;synopsys:5;waveview:2;calibre:2
- trace: 470KB / 132 msgs / 8 user turns · ssh 10.129.2.14 OK
- claim r625 (shard D)

## 用户意图（逐字原文，仅掩码路径中无私密 key）
- U0: 移动到这个路径操作 /proj/.../anly_spf_xdec/
- U42: 帮我执行这个脚本，找到 OcEnGNGap0 这个信号和其他信号的寄生电容
- U51: 修改为大于2fF的就显示，改了脚本再运行一下
- U61: 帮我生成一下这个信号 OcNcsGGap0
- U69: test_OcNcsGGap0_cap 是我提取出来 spf 中这两个信号到耦合电容，帮我加出来一个总电容，然后比较一下，脚本算的对不对
- U80: 帮我把最小电容值设置成一个可以输入的参数，默认10fF，使用terminal命令可以控制，然后给我生成一个terminal命令格式
- U100: 生成一个新的脚本，这个脚本也是执行类似的操作，但是统计到是所有信号和所有信号之间的寄生电容，按大小排序，默认值是20
- U112: 帮我生成

→ clean produce-task, spec-by-iteration（阈值过滤 + CLI 参数化 + 单信号耦合电容提取）。
U0 是路径定位（非需求），U42/U51/U80 是核心 spec；U100 all-pairs 是扩展版本。

## 助手工具链
list_allowed_files → read_files XDecGap.spf → editor 写 inspect_spf.sh/sample_spf*.sh → run_approved_command grep 抽样 `^C ` `^R ` `^L ` 行学 DSPF 语法 → editor 写 extract_spf_cap.py → run python-runner 验证 vsszloc/OcEnGNGap0/OcNcsGGap0 → 多轮 editor 改 --min_ff default(20→2→10) → read test_OcNcsGGap0_cap.txt 复核 → sum_test_caps.py 独立求和比对（REPORTED_FF=64.955）→ 写 extract_allpairs_cap.py（SQLite 聚合全信号对）→ nohup 跑全文件 → check_allpairs.sh 轮询。

## 真实 DSPF 格式（StarRC，从脚本 docstring + 抽样确认）
- 耦合电容行: `C<serial> <node1> <node2> <value_Farad>`，node 可带 `:pin` 后缀
  - 例: `C7584_1 XI_XDec_0.vsszloc:93 GrPreHvUSec0:13 2.96288e-20`
- 自地容声明: `*|NET <net> <value_pf>PF`
- 地节点集合: {0, gnd, ground}
- 脚本 CAP_RE = `^C\S+\s+(\S+)\s+(\S+)\s+([-+.\dEe]+)`；NET_RE = `^\*\|NET\s+(\S+)\s+([-+.\dEe]+)PF`

## 真实算法（extract_spf_cap.py 130 行，纯 stdlib）
1. CLI: `extract_spf_cap.py <spf> <target> [--min_ff 10] [-o OUT]`
2. min_val = min_ff * 1e-15 (fF→F)
3. is_target(net): net == target OR net.endswith('.'+target)  ← 层次匹配
4. net_of(node): strip `:pin` 后缀
5. 遍历每行：
   - CAP 行：n1,n2 → ne1,ne2 = net_of；t1,t2 = is_target
     - 都 target → skip（同 net 自容）
     - 都非 target → skip
     - 一方 target：other = 非方；if other in GROUNDS → gnd += val；else peers[other] += val, peer_cnt[other] += 1
   - NET 行：if is_target(net_of(name)) → self_ground = val_pf * 1e-15
6. items = [(net,c) for peers if c > min_val] sorted by -c（严格 >）
7. 输出：
   - `# Target signal : <target>`
   - `# Matched net alias(es) : <sorted aliases>`
   - `# Cap unit : fF`
   - `# Only totals > <min> fF shown`
   - `#partner_signal  cap_fF  n_coupl`
   - rows `%-20s %14.4f %12d`
   - if gnd > min_val: `<GROUND(0)>  <gnd_fF>  -`
   - if self_ground > min_val: `<GROUND(decl)>  <self_fF>  -`
   - `# Total entries > <min> fF : <len(items)>`
8. console summary 打印 total/aliases/ground/self

all-pairs 版本（extract_allpairs_cap.py）：SQLite 聚合每对信号 net_of 后 (a,b) sorted ≤，跳 ground，sort desc，--top N。本 case 聚焦 single-signal 版本（更聚焦、可验证）。

## 合成计划（case_id: EDA-Eval-DesignFlow-SpfCouplingCapExtract-001）
- SUT 产通用 `spf_coupling_cap.py`（纯 stdlib CLI `<spf> <target> [--min_ff V] [-o OUT]`）
- A=sample_A.spf（target OcEnGNGap0，含层次别名 XI_XDec_0.OcEnGNGap0、:pin、ground 0/gnd 累加、self 18PF、both-target skip、阈值边界）
- hidden B=sample_B.spf（target OcNcsGGap0，不同 nets，ground 0/gnd/ground 三累加=45fF，self 5fF 过滤，别名 XI_TOP.OcNcsGGap0）
- hidden C=sample_C.spf（target DrvClk0，跨输入反硬编码，ground+self 都 >10）
- check.py 16 cond a-p（zip/py_compile/通用无硬编码A/B exit0+非空/B partner set/B cap值/B n_coupl/B 排序降序/B GROUND(0)=45/B 无GROUND(decl)/B aliases/B Total=3/C partner OutBuf0=45 n=2/C GROUND(0)=50+GROUND(decl)=12/反硬编码A B输出不含OcEnGNGap0/自定义阈值--min_ff 30 只剩1）
- 内嵌独立 oracle（parse DSPF 自算 expected）非文本相似
- 4 neg: empty_shell→b / print_only(硬编码B)→m / hardcode_a(只认OcEnGNGap0)→e / core_removed(无ground累加)→i，全 FAIL
- §4.9 三假 (empty/print/core_removed) 全 FAIL，ref PASS 16/16
- k_rationale = k_check = 16 ≥ 8 ✓
