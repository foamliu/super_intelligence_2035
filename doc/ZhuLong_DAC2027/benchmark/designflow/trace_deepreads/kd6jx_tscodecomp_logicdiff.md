# deepread: 1793840720980_kd6jx — Ras_Tscodecomp_3bit netlist logic-diff Q&A

- session: `1793840720980_kd6jx.messages.json`
- user/host: dsgao @ hfhds201 (=10.129.32.75, the .75 sandbox itself — 本地可达, 无需 ssh)
- mc=15, domain=schematic_netlist, 11 msgs, 1 user turn
- parked 2026-11-12: "Q&A '两个电路有逻辑功能的区别不' netlist comparison analysis, not produce-task"
- revival: per 2026-11-15 令「Q&A-investigation 造-able」

## 用户原话 (msg[0], 逐字)
`@/proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp_3bit.netlist和/proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp_3bit_2.netlist  两个电路有逻辑功能的区别不`

## 助手动作链 (msg[1-9])
1. msg[1]: get_agent_policy_status + list_allowed_files(/home/dsgao/Desktop)
2. msg[4]: read_files 两份网表 (路径 /proj/drcpa/V0/workdir/dsgao/)
3. msg[6]: editor 写 compare_tscodecomp.py (按门函数 oai21=!(C&(A|B))/aoi21=!(C|(A&B))/nand2/inv 重建逻辑)
4. msg[8]: run_approved_command 跑 compare_tscodecomp.py
5. msg[9] stdout: `total combos: 64 / matching: 64 / differing: 0` + 完整真值表 (A=000..111 × C=000..111)

## 金标准 (msg[10], 用户接受无后续修正)
- 两网表都是 `Ras_Tscodecomp_3bit`, 端口完全一样: `A<2> A<1> A<0> C<2> C<1> C<0> Y vbn! vbp! vcc! vss!`
- 都用 `oai21 / aoi21 / inv / nand2` 门搭
- 结构差异: inv 5 个 (schematic) vs 7 个 (schematic_2); 节点名 n10~n18 vs AN/CN/net0~net4
- 门函数: `oai21(A,B,C)=!(C&(A|B))`, `aoi21(A,B,C)=!(C|(A&B))`, `nand2=!(A&B)`, `inv=!A`
- 穷举 64 组 (A,C 各 3-bit): **64/64 全一致, 0 差异**
- 功能: `Y = (C > A)` 三位无符号比较器 (C 严格大于 A 时 Y=1)
- 结论: 逻辑功能**完全相同**, 区别仅在结构/网表实现 (门吃载/扇出/反相器位置/节点命名)

## 验证 (本机 brute-force sim)
本地重建两网表门级仿真 (oai21/aoi21/inv/nand2 + 拓扑排序) 确认:
- netlist_A (schematic, 10 实例 5 inv): Y=(C>A), 64/64
- netlist_A2 (schematic_2, 12 实例 7 inv): Y=(C>A), 64/64
- 两网表 matching=64, differing=0, identical=True ✓ 与金标准一致

## 造-able 判定
✅ 造-able: 用户原话是 "request/goal" turn (非 root-cause/fix turn), 助手有 cited-evidence 金标准 (具体门函数 + 64/64 数字 + 功能 Y=(C>A)), 可写 teeth-ful check.py (16 独立断言: 顶层名/端口集/门库/identical/matching/differing/total_combos/function/gate_lib/conclusion + B2 robustness + B3 cross-input)。

## case 落地
- case_id: `EDA-Eval-DesignFlow-TsCodeComp3bitLogicDiffQA-001`
- D.jsonl 479→480 (r892)
- 资产 A = 真实两份 Ras_Tscodecomp_3bit.netlist (schematic/schematic_2)
- 隐藏 B = 合成 6-AND vs 6-OR (同顶层名+端口集, and2/or2 门库, different/2/62)
- B2 = 6-AND grouped vs interleaved (identical/64/0, 反硬编码 B)
- B3 = dangling-net (parse_error/0, 优雅)
- check.py 16 断言, reference_submit.zip PASS 16/16, 3 neg 全 FAIL (NEG_RC=0)

## 跨 trace 去重备忘
- 37j9u (lvyy@hfeg0pkn002, mc3373) + 3123n (lvyy@hfeg0pkn002, mc3554) = lvyy CML sizing Q&A, 与已有 case `CmlMp5SweepCurrentAnalysisQA-001` (g7b4c, lvyy@hfeg0pkn005) 同用户同主题跨 trace 重复 → 本轮 r891 不造 3123n, 转 kd6jx。
- kd6jx 是 schematic_netlist 域 (非 CML analog_context), 与 lvyy CML 簇无主题重叠, 安全。
