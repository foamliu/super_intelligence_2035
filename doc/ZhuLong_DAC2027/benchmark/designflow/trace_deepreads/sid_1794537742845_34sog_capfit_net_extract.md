# Deepread — sid 1794537742845_34sog · capfit net extraction (shanliny)

- **trace**: shanliny @ 10.129.2.14 (hfeg0plg...), mc=37, keywords pex:166;netlist:134;.spi:19;calibre:3
- **session**: messages.json 1.58MB / 97 msgs / 2 user turns (U0 + U1 at msg[81])
- **domain**: schematic_netlist (SPF/RC netlist text transform + PEX cap fitting)
- **真实任务**: 用户有一个 RC 走线可视化工具 (rc_viz_tool2.py CLI + rc_viz_gui.py Tk GUI)，本轮提两个需求：
  1. **仅测R模式**：把等效电阻 R 的测量与 PNG/XLSX 输出彻底隔开，能只打印 R 值不生成任何文件。
  2. **新功能「电容拟合走线提取」**：把指定 `*|NET <name>` 分节完整提取成独立网表（不是裸复制 net），并在该 net 上每个晶体管的 栅(g)/漏(d)/源(s) 端子节点追加拟合结电容 `Cfit...`；三种端子类型分别指定电容值、可选择性加；支持按器件族屏蔽（连坐：`...MIMP0:g` 一并屏蔽 `...MIMP0@2:g`、`...MIMP0@3:g`，strip `@N` 实例后缀）。
  - U1 修正（msg[81]）：输出网表支持直接在用户输入的绝对路径下创建（自动建父目录）；电容行首字母必须用 `C`（`Cfit...`），用 `X` 开头会被仿真器当成器件实例。
- **助手产物**: 改 rc_viz_tool2.py（CLI 引擎）+ rc_viz_gui.py（GUI）；新增 `extract_net_with_cap()` + `parse_cap()` + `dev_family()` + `--extract-net/--extract-out/--cap-g/--cap-d/--cap-s/--shield/--r-only`。端到端用 uploads/test_share.netlist（686KB/10334 行真实 SPF）验证：net=XBKB.XBK_CNT.XXDEC0.SHARE, n_rc=78, n_dev_term=16, 新增 Cfit 行（s=1e-14, d=1e-12, g=5e-15），shield XINV_FCK[1].MIMP0:s 连坐排除 @2 与本体。
- **SPF 格式（关键）**:
  - `*|NET <name> <cap>PF` 分节头 → `*|S (node x y)` 段点 → `*|I (DEV:TERM DEV TERM TYPE FLAG X Y)` 器件端子连接 → `Cc<N> n1 n2 val` 耦合电容 → `Cg<N> n 0 val` 对地电容 → `R<N> n1 n2 val` 电阻 → `*|ENDNET` 或下一 `*|NET` 结束分节。
  - `*|I` 第 3 字段 = 端子名（g/d/s/t1/...）；只有 g/d/s 是晶体管结电容端子，t1/b 等不加。
- **合成计划（已落地）**:
  - case_id `EDA-Eval-DesignFlow-CapfitNetExtract-001`, SUT 产通用 `capfit_extract.py`（纯 stdlib CLI）。
  - A=sample_A.spf（可见，2 net，TOP.CLK_SHARE 主 + TOP.RST_NET 干扰），hidden B=sample_B.spf（ANALOG.VDD_ROUTE 主，2 net，含 t1 陷阱 + @2/@3 族 + shield 目标 DRV0.MIMP0），hidden C=sample_C.spf（MIXED.BIAS_LINE，只 g+d 不 s，跨输入反硬编码）。
  - check.py 18 cond a-r（zip/py_compile/无泄漏/B exit0/B 非空/verbatim *|S/verbatim *|I/verbatim Cc·Cg·R/不泄漏他 net/Cfit 格式首字母C/数量=oracle/(node,val)多重集=oracle/连坐屏蔽/非g/d/s不加/单位解析 f·p·n·u/跨输入C=oracle且≠B/绝对路径建父目录/鲁棒 no-caps+missing-net）。
  - 4 neg{empty_shell→e, print_only→e, hardcode_a→c, core_removed→j} 全 FAIL；§4.9 三假（empty/print/core）全 FAIL。ref PASS 18/18，k_rationale=k_check=18≥8 ✓。
