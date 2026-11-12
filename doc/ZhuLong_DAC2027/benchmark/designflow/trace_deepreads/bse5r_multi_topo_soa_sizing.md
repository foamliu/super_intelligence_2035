# trace_deepread — 1783316151876_bse5r (e0025730 / hfeg0plg49 / 10.129.8.86, mc=24)

**session**: `1783316151876_bse5r.messages.json` (68 msgs, 221KB)
**user**: e0025730  **host**: hfeg0plg49 (10.129.8.86)  **mc**: 24
**keywords**: netlist:125 / schematic:74 / rtl:15 / analog:8 / virtuoso:2 / cadence:2 / hspice:1
**domain**: characterization（多拓扑 SOA 选型）

## 用户意图
`启动业务场景: 模拟电路生成`（与 zy2q7 同一入口，但本 session 走多拓扑 SOA 选型分支，zy2q7 走单拓扑 Case3 SPICE 全流程）。

## agent 工具链
1. 探索 `/home/e0025730/lvlshft/lvlshft_optimize`（空）→ 找到真 bundle 在
   `/home/e0025730/devops/eda_data_bridge/bundle/lvlshft/lvlshft_optimize/01_lvlshft_spec/`。
2. Python 版本：系统 python3.6 可跑但缺 openpyxl；最终用
   `/apps/local/anaconda3-2021.05/bin/python` (Python 3.8.8, 含 openpyxl 3.0.7 + pyyaml)
   跑 lvlshft 工具链。
3. **SOA 选型**（核心）：
   - `soa_selector.py Vcc2Vdleq` → SOA 选型 + 写 `sizing/netlist_sizing.yaml`
   - `soa_selector.py Vcc2Vdleq --sizing` → 完整 sizing 输出
   - 逐拓扑跑：Vcc2Vdleq(Case2) / Vss2VkbVcc(Case3) / Vss2VkbVdd1(Case4) /
     Vdd12Vwlp(Case5) / Vint2VdleqAryA(Case6) + Vcc2Vdd1(Case1)
4. `lvlshft.py run Vcc2Vdleq --dry-run` → 规划 4 步流水线
   (SIZING→FILL→OPTIMIZE→VERIFY)，Vss2VkbVcc 同样 dry-run 规划。
5. `lvlshft.py list/status/result` 查看拓扑列表 / 当前配置 / 上次结果。

## 关键产物（trace msg 62 / 65）
- **6 个 Case × 23 拓扑映射表**（msg 65）：
  | Case | 类型 | 代表拓扑 |
  | 1 | 标准正压转换 | Vcc2Vdd1, Vcc2Vwlp, Vcc2Vpcsg |
  | 2 | 简化正压转换 | Vcc2Vdleq, Vcc2Vdiv, Vint2Vcc |
  | 3 | 负压转换-输入p管 | Vss2VkbVcc, Vss2VncsgnVintAry |
  | 4 | 负压转换-简化 | Vss2VkbVdd1 |
  | 5 | 高压转换 | Vdd12Vwlp |
  | 6 | AryA系列 | Vint2VdleqAryA |
- **逐拓扑 SOA 选型**（msg 62，器件型号 + width + 电压参数）：
  - Vcc2Vdleq(Case2): input_n=ntn_m/600e-9, protect_n=ntn_lv/130e-9, pullup_p=ptn(default); pvnn=1.05/pvpp=1.15/pvppmax=1.33
  - Vss2VkbVcc(Case3): input_p=ptn/600e-9, protect_p=ptn_lv/300e-9, feedforward_n=ntk_lv(default), pulldown_n=ntk(default); pvnn=1.05/pvpp=-0.7/pvppmax=-1.175
  - Vss2VkbVdd1(Case4): input_p=ptk_lv/391e-9, feedforward_n=ntk(default), pulldown_n=ntk(default); pvnn=1.8/pvpp=-0.7/pvppmax=-1.175
  - Vdd12Vwlp(Case5): input_n=ntk_hv/476e-9, protect_n=ntk_hv/476e-9, feedforward_p=ptk(default), pullup_p=ptk(default); pvnn=1.8/pvpp=2.9/pvppmax=3.475
  - Vint2VdleqAryA(Case6): input_n=ntn/300e-9, feedforward_p=ptn/240e-9, pullup_p=ptn(default); pvnn=0.86/pvpp=1.15/pvppmax=1.33
  - Vcc2Vdd1(Case1): input_n=ntn_m/600e-9, protect_n=ntn_lv/130e-9, feedforward_p=ptn(default), pullup_p=ptn(default); pvnn=1.05/pvpp=1.15/pvppmax=1.33
- **netlist_sizing.yaml**（msg 60，Vcc2Vdleq 片段）：
  `vcc2vdleq: opti0: ntn_lv w='800e-9*beta2' l=130e-9 nf=beta2; opti2/opti: ptn w=2.64e-6 l=270e-9 nf=1`
- **流水线 4 步**（msg 53/64）：SIZING(SOA 选型+写配置) → FILL(render_sp.py 渲染 SPICE 模板+填 netlist 参数) → OPTIMIZE(L/W/S 迭代 opti0→opti1→opti2) → VERIFY(性能+老化 SPICE 仿真)
- **上次 Vss2VkbVcc 运行结果**（msg 65，与 zy2q7 一致）：beta1=70/S=0.05/L=1.30um/W=1.00, Rise 0.573ns@PVT/Fall 0.304ns@PVT/Ioff 1.588nA@PVT/Aging 7.42%

## case 化决策
- **抽子流**：多拓扑 SOA 选型合规检查 + 汇总报告（characterization L2）。
- **与 zy2q7(LvlShftSpecCompliance-001) 互补**：zy2q7 = 单拓扑 Case3 SPICE 验证报告
  解析+合规检查+参数注入；本 case = 6 拓扑 SOA 器件选型合规检查 + 汇总。
- **deliverable**：submit.zip{soa_sizing_report.json + soa_sizing_checker.py}
- **Input A**：6 拓扑选型 JSON（每 Case 一个，trace 真实数据）
- **hidden B**：6 拓扑，3 违规(2 器件越级 + 1 电压越界) + 3 合规
- **check.py**：12 断言 k_check==k_rationale==12≥8，subprocess 真跑 checker 在 B 上
- **自验**：check.py 12/12 PASS + 3 §4.9 fakes + 3 naive 全 FAIL

## 同用户近邻 session
- zy2q7 (mc=29, r475 已 case)：同 user e0025730，lvlshft Case3 单拓扑 SPICE 全流程
- fct93 (mc=24, r476 parked)：同 user，同「启动业务场景: 模拟电路生成」入口，near-dup
- 本 bse5r 与 zy2q7 同入口不同子流（多拓扑选型 vs 单拓扑 SPICE），判定为可独立 case
