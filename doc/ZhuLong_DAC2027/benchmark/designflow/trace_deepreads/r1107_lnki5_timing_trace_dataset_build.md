# trace_deepread: r1107 lnki5 (harrywu@hfeg0plg54, mc36, spice_sim)

**session**: 1794810817741_lnki5 (146 msgs, harrywu@hfeg0plg54)
**scan**: ssh_eda_search_20261123_064315, keywords analog:183;netlist:47;hspice:20;assembler:9;synopsys:8

## 用户意图 (U#0)
> 技术报告书已完成（报告文件：/ai_sandbox/dscqa/V0/agentdir/harrywu/simulation/AI_Timing_Analysis/Sample0/TRC-CRG-001_technical_report.md）。根据技术报告书生成可供用户使用的可视化平台工具，生成后自主进行测试debug。

TRC-CRG-001 = DDR6 sense-enable chain 反向时序追踪算法（trace_rigorous.py）。

## assistant 工具链
1. 读技术报告 + trace_rigorous.py（reverse timing trace: cell_kind 拓扑分类, extract_closure parse_spice, trace_cone compute_out_ports/is_supply, FSDB meas batch）
2. probe 环境: Python 3.7.1, flask/jinja2 可用, closure_merged.sp 88MB, 13 个 .tbl, _fetchwork/grab.mt0
3. 编写 TimingTraceViz/ 工具:
   - **build_dataset.py** ← 本 case 抽取对象：把多份磁盘数据聚合成 dataset.json
   - trcviz.py: SVG chain 渲染 + 波形渲染
   - server.py: Flask web 服务
   - run_tool.py / tests_tool.py: CLI + 自检
4. build_dataset.py 经历 editor 损坏→修复循环（regex 被编辑器吞字符→拆 _bd_part1/1b/2/3 分块写→_assemble.py 拼装）
5. 最终 build 成功: dataset.json 20 chain hops / 8 anchors / 2 waves(101pts)

## build_dataset.py 逻辑（reference 来源，从 trace editor new_text 重建）
- **parse_val(s)**: regex `([-+]?[\d.]+(?:[eE][-+]?\d+)?)\s*([mun]?)$` → SI 基本单位（秒/伏），支持 m/u/n 前缀
- **parse_mt0(path)**: regex `(\w+)_(INIT|R1|F1|R2|F2)\s*=\s*(\S+)`, "error" 行跳过(lowercase), float() guard, INIT 保留原值, R1/F1/R2/F2 ×1e9 (秒→ns)
- **parse_tbl(path)**: header `v(sig)` 提取 sig, 数据行 parse_val(t)→ns, 点数≥3 保留
- **build()**: 读 trace_result.json(overview) + chain_spec(REPORT_CHAIN+ANCHORS, trace 中硬编码) + mt0 + tbl(glob 第一个 crg_fscr_bsub_*/crg.tbl) → 组装 chain(idx + hop, 无 edge_ns 的从 mt0 r1 回填+meas=True)
- **main()**: CLI `<sample_dir> [out.json]`, 打印 chain/anchors/waves 计数

## reframe（本 case）
- trace 中 REPORT_CHAIN/ANCHORS 是硬编码（来自技术报告）。本 case 改为从 **chain_spec.json** 输入读取（测试 JSON 解析+组装, 非硬编码）。
- 核心齿: parse_mt0（regex + error 跳过 + 秒→ns + float guard）、parse_tbl（v(sig) 表头 + 单位换算）、chain 回填（无 edge_ns 的 hop 从 mt0 回填 + meas 标记）、overview 传播、anti-hardcode
- L1 纯 Python, domain=spice_sim（SPICE/FSDB 时序表征数据聚合）

## A vs hidden B（五重 anti-hardcode）
- **A**: TRC-CRG-001 DDR6 sense-enable chain, 20 hops, 8 anchors, SS/0.92V/-10C, fscript backend, grab.mt0 秒值, crg.tbl 2 sigs/23pts
- **B**: TRC-WL-002 WL-driver pulse chain, 11 hops（6 个无 edge_ns 需回填 vs A 0 个）, 6 anchors, FF/1.00V/85C, finesim backend, mt0 含 ERROR 大写+error 小写+n/a 非法值, crg.tbl 2 sigs/20pts

## check.py 9 条 (a-i)
a(zip+compile) b(B exit0+JSON) c(overview 6 字段传播) d(anchors_mt0 8 sig+error skip+秒→ns+INIT+float guard) e(chain 11 跳+idx+首末+6 回填 meas+edge_ns) f(anchors 6 匹配 spec) g(waves 2 sig+点数+ns 时间范围) h(anti-hardcode B 在/A 缺) i(3-seed sha256)

## 自验
- REF 9/9 PASS ✓
- 3 negs (empty/print_only/core_removed) 全 FAIL ✓
  - print_only 击中 c/d/e/f/g/h (6 齿)
  - core_removed 击中 d(无×1e9)/e(无回填) (2 齿)
- 3-seed sha256 一致 ✓
