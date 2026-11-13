# 深读笔记 — 1794483960840_mhqy7 (joeyl / hfeg0pkn004 / 10.129.2.13)

- **slug**: 1794483960840_mhqy7 · **mc**: 163 · **user**: joeyl · **host**: hfeg0pkn004
- **domain**: spice_sim (B) · **archetype**: netlist param 注入 (ULVT delvto shift) — presim netlist-edit produce
- **trace 源**: 11/13 快照 summary_1113.tsv，constitution-lens 命中 (netlist:581 hspice:52 opamp:22, analog sig, dig 0%)
- **deliver case**: EDA-Eval-DesignFlow-ULVTDelvtoNetlistMod-001 (spice_sim, L2, k=14)

## 用户意图（原话）
「请帮忙用这个：/home/joeyl/ulvt_delvto/ 给这里的 netlist：/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/simulation/Bias/hspiceD/schematic/netlist/netlist 加 vth=-0.2v」

## 真实执行流（98 msgs / 253KB）
1. 读 AI_USAGE.md / config.cfg / reduce_vth.py 了解工具
2. 策略限制：/rundata 只读、/home/joeyl 可写 → 拷 netlist 到 work/ 副本
3. 改 config.cfg 指向副本，delvto=-0.2，默认 models=pulvt_ckpt,nulvt_ckpt
4. 跑 reduce_vth.py：修改 3 器件 (XM10/XM9 pulvt_ckt, XNM18 nulvt_ckt)，输出 netlist_delvto-0.2
5. verify_netlist.py 逐行 diff：orig=84 mod=84，仅 L59/L60/L83 变

## reduce_vth.py 工具机制
- 扫 netlist，给 model ∈ {pulvt_ckt,nulvt_ckt} 的 X 实例语句末尾追加 `_delvto=<值>`
- 幂等：已有 `_delvto=` 则替换其值（DELVTO_RE 带 `(?<![A-Za-z0-9_])` 防误匹配 delvto_user）
- 支持 `+` 续行（_delvto 追加到语句最后一条物理行末尾）
- 行尾 `$`/`//` 注释时插到注释前（find_unquoted_comment）
- 跳过 .subckt 定义行、`*`/`//` 注释行、非 X 开头行

## 输入网表结构（84 行）
- subckt: switch_close/open, invFx4, invFx1, WCKIbBias_Res, WCKIbBias_Opamp + 顶层 Bias
- ULVT 器件：XM10/XM9 (pulvt_ckt, WCKIbBias_Opamp 内), XNM18 (nulvt_ckpt, 顶层 Bias)
- 非 ULVT：nlvt_ckt/plvt_ckt/nrvt_ckt/prvt_ckt/rndif_3t/XI_* 子电路调用 — 不动
- 所有器件带 delvto_user=0（须保留，不能腐蚀成 _delvto）

## case 化要点
- 便携化：netlist 是纯文本 84 行 + reduce_vth.py 纯 Python，无需 EDA license → 便携 L2 (subprocess 跑候选脚本)
- 隐藏 B：合成 10 行网表，4 ULVT (XM2/XM7 pulvt, XNM5/XNM11 nulvt) vs A 的 3，delvto=-0.15 vs -0.2；含 +续行(XM7) + $注释(XNM5) 边缘
- 判分 14 条 (a-n)：结构(行数/实例/计数) + delvto_user 保留 + 幂等 + 交叉验证(值/计数/边缘)
- 5 negative: fake_empty / fake_print_expected / fake_core_deleted / naive_add_to_all / naive_hardcode_a — 全 FAIL (NEG_RC=0)
- selftest: REF 14/14 PASS + 5 neg FAIL

## 同源 session（joeyl 同任务重试，未用）
1794532032531_sd44n / 1794535620076_2qn6y / 1794538116856_7s3gj(文件已清) — 首消息完全相同（同任务），不可作 hidden B。
