# trace_deepread: 1794884166048_jdv6s (dsgao @ hfhds201) — CDL 网表真值表自动化验证

**session**: 1794884166048_jdv6s.messages.json (115 msgs)
**user**: dsgao · **host**: hfhds201 (10.129.32.75) · **mc**: 166
**domain**: schematic_netlist (D)
**trace_source**: 真实 cline 轨迹

## 用户意图
1. `/proj/drcpa/V0/workdir/dsgao/R_2stepSenseAdjTempCtrl_0822.netlist 分析一下这个电路功能`
2. `做真值表自动化验证`
3. 后续追问：手动切LT→LT 怎么理解 / 检测到LT输出什么code / SW有什么实质作用 / 想把default输出改为LT有什么优化建议 / 把方案A改写成新的净表形式

## 电路
- 顶层 `R_2stepSenseAdjTempCtrl_0822`（drcoa_digital），6 位温度感测调节码选择器（温控 mux）
- 端口：Ts_HT/Ts_LT（温度标志）、cm1_ro_SenseTempEn（SE 使能）、cm1_ro_SenseLTHTSw（SW 手动切换）、6×Adj_HT、6×Adj_LT、6×Adjo
- 标准单元库：inv/invLx1/invLx4、nor2/nor2Lx2/nor2CS/nor2CSx1、nand2CS/nand2CSx1、mxi2LVx2（由 invenLV 构建的二选一反相 mux）
- 逻辑：HT_option = SE==0 ? 1 : (Ts_HT | ~(Ts_LT|SW))；默认 HT；Adjo = HT_option ? Adj_HT : Adj_LT

## agent 做法（参考解）
- 写 verify_2stepSenseAdjTempCtrl.py：def inv/nor2/nand2 门原语 → model_netlist() 逐门连线建模（XI13/XI11/XI15/XI5/XI7/XI9/XI2/XI62/XI10 + XI57 mux + XI22 inv）→ 遍历 16 组合 → 交叉校验门级模型 vs 化简布尔式 → 输出 16 行真值表 ALL CHECKS PASSED
- 预设码 Adj_HT=101001(0x29) Adj_LT=010110(0x16)
- 输出关键行：SE=0→HT(101001)；SE=1,SH=0,SL=0,SW=0→HT；SE=1,SH=0,SL=0,SW=1→LT(010110)；SE=1,SH=0,SL=1→LT；SE=1,SH=1→HT

## 合成的 case
- **id**: EDA-Eval-DesignFlow-CdlTruthTableVerify-001
- **A（可见）**: 真实 R_2stepSenseAdjTempCtrl_0822.netlist（191 行，default HT）
- **B（隐藏）**: R_2stepSenseAdjTempCtrl_defaultLT.netlist（default LT 变体，HT_option=Ts_HT&SE，3 控制门 vs A 的 9 控制门，连线/真值表全不同）
- **check**: 嵌入 B 的 base64，用 2 组预设码跑候选脚本，独立参考仿真逐行比对 16 行，9 条独立断言；3 假（print_only/core_deleted/hardcode_a）在 B 上全 FAIL
- **自验**: negative_selftest 4/4 PASS（REF PASS + 3 假全 FAIL）
