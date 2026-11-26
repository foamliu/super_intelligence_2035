# 深读笔记 — 3qe6x (waveform, WaveCompare 顶层封装 CLI)

## trace 元信息
- session: `1790733563737_3qe6x.messages.json`
- user: e0039602 @ hfeg0plg102 (10.129.8.136)
- mc=45, 157 msgs, keywords: waveview:134;netlist:66;synopsys:46;hspice:8
- 扫描源: candidates_mc30.tsv (Nov 4 快照), fresh (不在 4-shard 台账)

## 项目背景 (A#11)
- 项目名: **AutoDebug (AutoDebugWithPassRef_V3)** — DRAM 芯片 SPICE 级仿真失败的自动化根因定位工具
- 痛点: 网表 99.5MB/58万行/8378 子电路/十几层嵌套；失败信号(如 `dq0<0>`)源头可能在上游七八层
- 原理: 同一电路同一激励在两个 PVT corner 下仿真结果不同 → 沿驱动关系向上游遍历, **第一个波形出现差异的节点 = 故障源 (SOURCE)**
- 三层架构: NetlistTrace(结构层) / **WaveCompare(测量层, src/divergence/)** / 编排层(v3_debug_b0.py)

## WaveCompare 核心设计 (A#21)
- **比对的是"边沿序列"不是逐点电压**: pass/fail 两 corner 的 VDD/摆幅/slew 天生不同, 逐点减法无意义 → 抽象成边沿序列(每个上升/下降沿带时刻/方向/幅度)再对比
- **算法优先 LLM 只救灰区**: 321 net 里 321 个算法判, LLM 判 0
- T0→T4 五级流水线, 入口 `compare_net()` (src/divergence/__init__.py), 每个 net 输出 `DivergenceReport`
- **四种判决**: `EQUIVALENT`(等价) / `DIFFERENT`(发散) / `GRAY`(灰区) / `NO_DATA`(无波形)
- T0.a 两段式提取(extraction.py): 粗扫(±100ns, 1ns 步长枚举翻转) → 估全局时移 Δ_global → 精窗 → 精提(10ps)

## 用户意图 (produce 轮, 干净)
- **U#22**: 「如果我想单独调用一下compare代码对比两段波形，请你告诉我应该如何对比，或者你写个代码，让我可以通过给信号的路径和名称，还有时间范围，直接对比两段代码」
- **U#28**: 「请你尽可能调用这个项目当中的波形对比代码，然后封装一个顶层让我可以直接调用」
- = clean produce: 把 WaveCompare 流水线封装成「给信号路径+名称+时间范围 → 直接对比两段波形」的顶层 CLI

## 真实交付物 (assistant 产)
- 文件: `/home/e0039602/Documents/ZGCtestAutodebugV3/tools/compare_signal.py` (303 行)
- 顶层函数:
```python
def compare_waveforms(signal, t0_ns=834.5, t1_ns=838.5,
                      fail_tbl=None, pass_tbl=None,          # 方式①: 已提取 .tbl 缓存
                      fail_fsdb=None, pass_fsdb=None,        # 方式②: 从 FSDB 现场提取
                      fail_wave=None, pass_wave=None,        # 方式③: 内存波形
                      demo=False,                            # 方式④: 内置合成波形
                      vdd_pass=1.15, vdd_fail=0.88,
                      coarse_step_ns=0.05, fine_step_ns=0.01,
                      max_pair_gap_ns=2.0, no_llm=True, **extra_ctx):
    # → (rep, summary)
```
- 信号名归一化 `_split_signal`:
  - `v(a.b.c)` → bare_net=`a.b.c`, vkey=`v(a.b.c)`
  - `a.b.c` → bare_net=`a.b.c`, vkey=`v(a.b.c)`
  - `dq0<0>` / 残缺 `v(a.b.c` 也兼容
  - bare_net 供 fscript/FSDB 侧, vkey 供 .tbl/内存适配器做索引
- .tbl 列名格式: `v(...)` keys (R#79 注释「.tbl 缓存的列名是 v(...)」)
- CLI: `compare_signal.py --signal '...' --t0 834 --t1 838 --fail-fsdb ... --pass-fsdb ... [--demo] [--bsub]`

## 真实调用实例 (U#97/U#109/U#121)
```
python3.10 tools/compare_signal.py \
  --signal 'xi_channel.xi_chansc0.xi_dqsc0.xi_dqpadm6_0.xi_dqio.xi_dqouttop.pumain<2>' \
  --t0 834 --t1 838 \
  --fail-fsdb 'simdata/finesim.PerBnk_ActWrPreActRd_4b4g_B0_tck0.313nsRL68WL32TS_12800_RDQSENtENc.x12.SS0.88v-40c.X12.tmp.voltage_s/raw/finesim.fsdb' \
  --pass-fsdb 'simdata/finesim.PerBnk_ActWrPreActRd_4b4g_B0_tck0.313nsRL68WL32TS_12800_RDQSENtENc.x12.FF1.15v130c.X12.tmp.voltage_s/raw/finesim.fsdb'
```
- 真实信号: `xi_channel.xi_chansc0.xi_dqsc0.xi_dqpadm6_0.xi_dqio.xi_dqouttop.pumain<2>` (DRAM DDR5 层次路径, 总线位 `<2>`)
- corners: FF1.15v130c (pass, vdd_pass=1.15) vs SS0.88v-40c (fail, vdd_fail=0.88)
- 时间窗: 834-838 ns
- 后续: U#126「让每次报错包的具体一点」(改 adapters.py 错误信息), U#143「加 bsub 提交到服务器跑」(加 --bsub flag)

## A-faithful 判定
- U#22/U#28 是干净 produce 意图 + user-accepted 产物存在 → A-faithful 候选
- **但不可行**: gold (compare_signal.py) 依赖项目 `src/divergence/` 模块(不可移植) + 真实 fsdb 2GB(不可附加) + live FineSim/fscript(L2 不可移植)
- → **B 档 synthesized**: 重述为 produce(spec → 波形对比 CLI + 报告生成器), L1 离线(解析简单 .tbl 文本波形快照, 无需 EDA 工具)

## 合成 plan (wave_cmp.py)
- CLI: `wave_cmp.py --pass-tbl <file> --fail-tbl <file> --signal <path> --t0 <ns> --t1 <ns> --vdd-pass <V> --vdd-fail <V> --outdir <dir>`
- .tbl 格式: 文本, 头部 `# signal: v(...)`, 列 `time_ns, v(net)` (模拟真实 .tbl 的 v(...) key)
- `_split_signal`: `v(a.b.c)`/`a.b.c`/`a.b<2>` → (bare_net, vkey)
- 边沿提取: 在 [t0,t1] 窗内, 上升沿(跨 0.5*vdd 上行) + 下降沿(跨 0.5*vdd 下行)
- 对比: 边沿序列按时刻匹配(容差 max_pair_gap), 数量/时刻差异 → verdict
  - 无数据 → NO_DATA; 边沿完全匹配 → EQUIVALENT; 差异超阈值 → DIFFERENT; 灰区 → GRAY
- 输出: verdict.json{signal,bare_net,vkey,t0,t1,vdd_pass,vdd_fail,n_edges_pass,n_edges_fail,verdict,n_diff_edges,max_shift_ns} + edges.json{pass_edges,fail_edges} + report.md

## 反硬编码五轴
- A=DDR5 `xi_channel...pumain<2>`, FF/SS, 834-838ns, vdd 1.15/0.88, 8 边沿
- hidden B=LPDDR4 `phy_top.xi_phyx16.xi_dqbyte0.dq<7>`, TT/FF, 1200-1204ns, vdd 1.2/1.1, 不同边沿数/时刻
- hidden B2=SERDES `serdes_top.xi_rxlane0.rx<0>`, 常量波形(无边沿) → NO_DATA 守卫
- design/前缀/信号名/时间窗/vdd/边沿全不同 → 硬编 A 者 B/B2 全 FAIL

## check.py 16 条件 a-p
a(防泄漏+py_compile) b(B-run exit0+3文件) c(verdict.json 顶层键) d(_split_signal 归一化 v()剥离+bare/vkey) e(verdict∈{EQUIVALENT,DIFFERENT,GRAY,NO_DATA}) f(时间窗过滤: 所有边沿∈[t0,t1]) g(边沿提取: n_edges_pass==B pass .tbl 实际) h(n_edges_fail==B fail .tbl 实际) i(DIFFERENT 判决: B 设计为 DIFFERENT) j(report.md 含 signal+verdict+t0/t1+边沿数) k(edges.json 含 pass_edges+fail_edges 列表(t_ns,direction)) l(max_shift_ns 计算: 匹配边沿最大时差) m(vdd 归一化: 0.5*vdd 阈值自适应 B 的 vdd) n(反硬编码: 源码无 A 标记 pumain/xi_channel/834/FF1.15/SS0.88; A-run 产 A 信号; B-run 产 B 信号≠A) o(B2 守卫: 常量波形→NO_DATA+n_edges==0) p(确定性 3x sha256)
