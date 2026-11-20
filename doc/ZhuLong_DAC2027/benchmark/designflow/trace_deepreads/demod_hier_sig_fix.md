# trace_deepread: demod (1792573684287_demod) — hier_sig.py fix

- **trace**: wenzhuod @ hfeg0plg36 (10.129.32.46), mc=109, 145 msgs (81 user / 64 assistant)
- **path-bug revival**: r971 确认子目录路径 `~/.cline/data/sessions/1792573684287_demod/1792573684287_demod.messages.json` 可读 (710KB)
- **domain**: schematic_netlist (netlist:537/verilog:171/drc:121)
- **user turns**:
  - **U#0 (A-faithful seed, verbatim)**: 「/rundata/.../hier_sig.py 先了解此脚本的内容，要求是 输入是一个fullchip 网表 ， 一个cellname ， 和一个cell内部一个信号名 ， 把这个cell的所有例化cell 的 hierarchy 都抓出来 ，并且补上信号名 ，输出一个list。现在碰到的问题是 python hier_sig.py V0_DDR5TOP_2026Oct14.160646.local IO_ZqTop DRZQPRB 比如，但是抓不到这根信号的连接关系」
  - U#101: 「优化了下，可以看出优化了哪些部分吗」(用户自己优化了脚本，agent 做 diff 验证 671→571 行功能等价)
  - U#124: 「可以自动approve吗」(meta：问 cline policy 审批能否自动)
- **assistant 工作链** (64 tool_use):
  1. read_files hier_sig.py 全文 (470 行)
  2. 写 diag_hier_sig.py 诊断网表 (30.5MB / 4501 module)：IO_ZqTop 全网表仅 1 例化 (LBDQ.I_IO_ZqTop)，DRZQPRB 是其 51 端口之一 (output[5:0])
  3. diag2/diag3/diag4 追连接链：IO_ZqTop.DRZQPRB → LBDQ.DRZQPDB (接 2 ZQ pad) → BCenterDQ.DRZQPDBi (接 4 模块) → 内部 wire 停
  4. **定位两个真实 bug**：
     - **Bug1 (用户抱怨「抓不到连接关系」)**: `--resolve`/`_resolve_signal` 只返回一个裸网络名 (追到内部 wire DRZQPDBi 就停)，不报每层 fanout
     - **Bug2 (静默丢例化)**: `_parse_instances` 参数正则 `#\s*\(([^)]*)\)` 遇嵌套括号参数 (如 `ntk_hv #(.mostype("rnmos"))`) 整条语句匹配失败被丢弃 → 全网表 2056 个 ntk_hv/ptk_lv 例化被漏
  5. 重写 6 part (_hier_p1..p6) + build_hier_sig.py 拼接 (23512 字节)：平衡括号扫描 _parse_instances + 新 _resolve_chain/_net_fanout (逐层 net+kind+fanout)
  6. test_hier_sig.py (迷你网表全路径覆盖) + test_hier_sig_real.py (真实网表回归)：dlyg 回归 15075 行逐字节一致 + 精确找回 2056 丢例化
  7. deploy_hier_sig.py 备份+替换 /rundata 原件；rerun_user_cmd.py 重跑用户命令重新生成输出
- **GOLD 交付**: 修复版 hier_sig.py 部署回 /rundata/.../netlist/hier_sig.py (原件备份 .orig)
- **合成 case**: EDA-Eval-DesignFlow-HierSigFixProduce-001 (analog→schematic_netlist, A-faithful U#0 verbatim, synthesized-reframe asset)
  - A = buggy hier_sig.py (含两个真实 bug 的代表版) + netlist_A.v (mini, IO_ZqTop/DRZQPRB 主题)
  - 隐藏 B = netlist_B.v (TOPB/MIDB/LBDQB/ZqCoreB/ntk_hvb 不同名, 同 bug 类)
  - deliverable = 修复后的 hier_sig.py; check.py 12 断言 a-l (nested-paren 修复 ntk_hvb count==3 + --resolve chain≥2 跳+fanout + 反硬编码 + 3-seed)
- **与既有 case 关系**: D 域 netlist-parsing script-fix L2 produce 首例; path-bug revival 第 4 例 case; 与 SchPinAddProduce-001 同 schematic_netlist produce 域但不同范式 (fix-buggy-script vs produce-from-scratch)
