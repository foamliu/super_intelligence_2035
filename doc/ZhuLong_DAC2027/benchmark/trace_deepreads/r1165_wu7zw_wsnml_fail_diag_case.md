# r1165 deepread — wu7zw HSPICE MC WSNML 5000 全 fail 诊断 → WsnmlMcFailDiagProduce-001

## trace 溯源
- user: e0030760 @ hfeg0pkn001 (10.129.2.10)
- session: `1795415009363_wu7zw` (目录式, 内含 `1795415009363_wu7zw.messages.json`, 379KB / 46 msgs)
- scan: ssh_eda_search_20261124_023802/summary.tsv, mc=51, kw=hspice:306;netlist:22;synopsys:17
- domain: spice_sim (HSPICE Monte-Carlo)

## 用户意图(原话)
> /proj/lacaa/V0/workdir/e0039809/MC_hspice/HD_FS_CH252_6T_dspf/ttg_25C_0.75V_dspf_WSNML 这是根据后仿真网表仿真的WSNML，检查一下为什么全部仿真失败？

单一诊断任务：6T SRAM WSNML 写翻转 DC 测试，5000 MC 采样全 fail，问根因。

## assistant 诊断链(真实)
1. sim.ms0: 5000 行全 `failed`
2. sim.ava.log: `WARNING! Measure wnml be skipped due to all sample data is failure` + `ERROR! all measures be dropped` + `Abnormal program termination` exit 101
3. su0: `dc sweep` `complete` —— 仿真器没崩，是测量全 fail
4. deck.sp `.MEASURE DC WNML find v(VIN1) when par('v(Q_WNML)-v(QB_WNML)')=0 cross=1` —— 找 Q-QB 过零穿越点
5. sim.lis DC 传输曲线(sample 1): Q_WNML 从 VIN=0→0.75V 全程 0.000(0.40-0.52V 反转区也 0) → 单元从不 1→0 翻转 → 穿越点找不到
6. pin mapping: `.SUBCKT HD_CH252_6T_SRAM_Bitcell BL BLB Q QB VDD VSS WL` + `XWSNML VIN1 VDD Q_WNML QB_WNML VDD VSS VDD HD_CH252_6T_SRAM_Bitcell` → BL=VIN1(被扫), BLB=VDD(恒高), WL=VDD(使能)
7. **根因**: BLB 恒接 VDD, 两条位线起点同为高, 无差分写驱动, 单元没进确定可写状态, Q 节点从一开始被钉在 0
8. 次要(非致命): VDD/2 附近 DC 收敛问题(0.44-0.50V); ETA0=-0.023 被钳 0; 未用 rail(vwlp!/vssz!/vddq!) singular supplies 警告(无害)

## 资产获取
- /proj/lacaa/ 对沙盒权限拒绝(r1163 已记)。本轮从 .messages.json 摘录的真实 lis/ms0/ava.log/sp 内容**复刻重建** asset A仿真目录。
- 远程 session 是目录式(`/home/e0030760/.cline/data/sessions/1795415009363_wu7zw/1795415009363_wu7zw.messages.json`), 非 .messages.json 单文件。

## reframe (造题)
- 真实任务是"诊断文本输出"。reframe 为**通用 Python 诊断器** `wsnml_diag.py <sim_dir>` → 结构化 JSON, 避免纯文本判分无牙。
- asset A: 复刻 wu7zw 场景(BLB=VDD / 5000 / WNML / Q_WNML / VVDD=0.75 / HD_FS cell), 由 gen_wsnml.py 程序化生成 sim.lis(751 点 DC 曲线 q_wnml 全 0) + sim.ms0(5000 failed) + ava.log + deck.sp + bitcell.dspf + option/pwr + spec_A.json。
- hidden B(嵌 check.py, 不进 SUT): 六重 anti-hardcode —— (1)cell HD_CH252_HP_6T 异 A HD_FS (2)measure RSNML 异 A WNML (3)node Q_RSNML 异 A Q_WNML (4)VVDD=0.9 异 A 0.75 (5)MC 3000 异 A 5000 (6)错接线 WL=VSS 异 A BLB=VDD; B 的 BLB 改由驱动源 BLBX(V_blb BLBX 0 DC=0)给以消除"两个控制脚都接恒定轨"的歧义, 使 WL=VSS 成为唯一 miswire。
- 判分 k=14 条独立断言(见 case JSON test_rationale): measure名/target节点/mc数/failed数/all_failed/ava_status+exit/flat_node+value/subckt名+pins/pin_mapping[WL]/root_cause/miswired_pin/secondary_issues/确定性3跑。
- 判分契约: check() `return True`(PASS)/`return False`(FAIL, 22 个 _fail 分支), 符合 11-24 运维令。
- §4.9 退化回归: neg_empty(空{}) / neg_print_only(纯文本非JSON) / neg_hardcode_a(写死 A 的 WNML/5000/BLB, B 上全错) 三假提交, selftest 验证均 FAIL。
- 随机化: check() 跑 B 3 次归一化 JSON 完全一致(确定性)。

## 自验
- ref wsnml_diag_ref.py 在 A: root_cause=pin_mapping, flat_node=q_wnml, miswired_pin=BLB, mc=5000 ✓
- ref 在 B: miswired_pin=WL, root_cause=pin_mapping, mc=3000, flat_node=q_rsnml ✓
- check.check(submit.zip of ref) → True (PASS) ✓
- negative_selftest.py: REF PASS / 3 negs 全 FAIL / 3 跑确定性 OK ✓
- ast.parse + 判分契约 return True/False ✓

## 台账
- ledger B: wu7zw claimed→case(EDA-Eval-DesignFlow-WsnmlMcFailDiagProduce-001); covered 597→598/4529=13.2%
