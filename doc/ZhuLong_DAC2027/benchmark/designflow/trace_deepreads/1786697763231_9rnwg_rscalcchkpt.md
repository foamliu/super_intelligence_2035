# trace_deepread: 1786697763231_9rnwg (e0014566 @ hfeg0pkn001, mc=178)

- **session**: `/home/e0014566/.cline/data/sessions/1786697763231_9rnwg/1786697763231_9rnwg.messages.json` (837KB, 174 msgs, 1 user turn)
- **domain**: pg_layout (Virtuoso rscalc power-network resistance prep)
- **tools**: 237 virtuoso + 72 cellview + 24 calibre + 8 skill + 5 dbGet + 4 pyAether
- **user intent (verbatim, A-档)**: 「我现在要用rscalc计算电阻，看看其powernet 上的RTEXT，没有的话，帮忙在合适的位置上打上。既然不能修改原本的layout, 请先原封不动拷贝一份这个layout, 然后分析，然后打上RTEXT。另外，请在配置文件rscalc.config 中增加 check points, 以计算这点的电阻。增加的量控制在50左右，分布要广泛典型。」
- **gold (assistant real output)**:
  - 分析 `auto_austin_case1/BCenterR` (bBox 12508.79,-749.76 → 18177.74,685.65; 1068 shapes; RTEXT=0 RNODE=0)
  - 3 power nets: vdd1!, vss!, vcc!; RDL pad positions: vdd1!@(16139.851,367.694), vss!@(15586.395,367.694), vcc!@(15309.665,367.694); vss!/vcc! 有第二簇 pad (~17500/17350)
  - `add_rtext_batch.il`: dbCopyCellView BCenterR→BCenterR_rsv4, dbCreateLabel 3 nets on RDL/RTEXT, dbSave, verify copy RTEXT=3 + original RTEXT=0
  - `rscalc.config`: cellName=BCenterR_rsv4, pwrNets="vdd1! vss! vcc!", checkPoints = 50 个 4 元组 `list("net" x y "RDL")`, 分布 x=15150–17600 / 4 y-levels(-548.644,-363.794,367.694,552.544)
  - **关键 bug 修复**: run_rscalc_nogui.il 原仅支持 3 元组 `(x y "layer")` → addtext.dat 解析报错 `Failed to convert position to decimal value ... token=RDL`；改为 4 元组 `("net" x y "layer")` + CXMTGetCheckLayerName 映射 → RSDB build 成功, .rvn 出结果
- **case 抽取**: 把「check-point 生成 + RTEXT 标注脚本生成」子任务重构为通用生成器 `gen_rscalc_chkpts.py`（读 layout_desc.json → 输出 generated/rscalc.config 的 checkPoints 行 + generated/add_rtext_batch.il），A=真实 layout 描述(BCenterR/bbox/3 nets/pads/y_levels/target=50), 隐藏 B=合成(TopCell/bbox 0-4000/3 异 nets VDD2!VSS!VCCO!/6 pads/3 layers RDL,M5,M3/target=60)→强制通用解析非硬编码
- **判分 10 条(a–j)**: ①zip+py_compile ②--help/no-arg exit ③B 跑写两文件 ④B checkPoints count 60±3 + 全 4 元组 ⑤B 全 nets 均衡 ⑥x8bin≥4 / y4bin≥3 / layers⊆B 且≥2 ⑦最近 pad 归网(5 抽样) ⑧il 含 dbCopyCellView/dbCreateLabel/RTEXT/dbSave/ORIG_VERIFY + B tokens, 不含 A 硬编码 ⑨跨输入守卫 A≠B + A il 用 BCenterR ⑩B 确定性字节一致
- **k=10/10 a–j; ref PASS 10/10 + 5 neg 全FAIL(空壳/only-print/core-deleted/hardcode-a/no-distrib) + §4.9 三假全FAIL ✓; check.py 自包含(A+B 内嵌, 10842B, sha 14df8e18); test==disk check.py roundtrip OK**
- **leakage 隔离**: check.py 内嵌 B, 不进 SUT workdir; SUT 只见 assets A + prompt + task_brief ✓
- **选料**: 仅 e0014566 sessions 在 .75 本地可读; layout-dominant 过滤(lay>0, net≤2×lay) → 64 候选; 选 9rnwg(单用户轮、clean build intent、pg_layout 域 undercovered 22 case)
