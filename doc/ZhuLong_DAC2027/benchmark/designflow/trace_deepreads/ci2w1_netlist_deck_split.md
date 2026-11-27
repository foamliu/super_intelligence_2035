# ci2w1 — netlist skill 语义清理（DUT/TB/RUN 三层拆分）深读

- **trace**: `1795661891979_ci2w1.messages.json` (1.65MB, 555 msgs, 290 user / 265 asst)
- **用户**: e0048306 @ hfeg0plg05
- **mc**: 689 (virtuoso:1384 / netlist:833 / cellview:490 / spectre:375 / schematic:278 / analog:201 / cadence:157)
- **域**: analog_context (Spectre/SPICE 晶体管网表语义清理)
- **claim**: 2026-11-28 05:12 入 D 台账

## 用户真实意图（核心可合成段 msg 0-89）

用户(e0048306)演示自研 `netlist` skill 的语义清理工作流——把一段**故意"脏"的生成 Spectre 网表**按 `cleaning.md` 规范改造成可复用参考网表：

1. **U1 (msg 2)**: 触发 `/netlist` skill，描述="Spectre/SPICE 晶体管网表语义清理与策展，用于 analog review 或可复用参考电路。脚本只做 checker，不做主清理引擎"。
2. **U3 (msg 8)**: "请使用 netlist skill，帮我检查下面这段网表有没有语法/语义问题"
3. **U5 (msg 15)**: "你自己造一个测试测试" → 助手造 `demo_bad_dut.scs`，故意塞 5 类问题：
   - 泛化实例名 `M0~M4`
   - 随机节点 `net1~net4` / `N_5`
   - MOS 尾参数 `ad/as/pd/ps/sa/sb/nrd/nrs` (layout 提取侧)
   - DUT 内混入 `dc dc dev=net1 start=0 stop=2` 分析语句
   - 无 MOS 端子顺序注释
4. **助手跑 checker** `check_spectre_netlist.py --mode dut` (msg 18-46，多轮排障 python-runner 环境问题，最终用 `/usr/bin/python3.11` 跑通)，checker 抓到 `info: generic-instance` / `info: random-node` / `warn: mos-tail-params`。
5. **U6 (msg 47)**: "那你基于 netlist skill 去修改" → 助手按 `cleaning.md` checklist 创建 `demo_clean/`：
   - `raw/demo_bad_dut.scs` — 原始档案原封不动归档
   - `netlist/dut/cmp_ota.scs` — DUT：MOS 端子顺序注释 + `subckt cmp_ota` + 语义重命名（M0→`mn_input_vinp_main`/M1→`mn_input_vinn_main`/M2→`mp_load_mirror_ref`/M3→`mp_load_mirror_out`/M4→`mn_tail`；net1→`net_inp_d`/net2→`net_inn_d`/net3→`net_tail`/net4→`net_mirror_g`/N_5→`bias_tail`）+ review notes（input drains 未接 mirror / bias_tail 未定义）+ **无分析语句、无电源、保留 MOS 尾参**
   - `netlist/tb/tb_cmp_ota.scs` — TB：电源 `vdd/vss vsource` + 差分激励 `vinp=vicm+vid/2` `vinn=vicm-vid/2` + 输出负载 `cload` + DUT 例化 `xdut ... cmp_ota`，**无分析/save/model include**
   - `netlist/runs/run_tb_cmp_ota.scs` — RUN：`include "cmp_ota.scs"` + model include placeholder + `parameters vdd=1.8 vicm=0.9 vid=0.01 cload=100f Tper=20n` + `dc dc dev=vout` + `tran tran stop=10*Tper maxstep=200p` + `save vout vinp vinn`，**无电路器件**
6. **助手复跑 checker** (msg 55-59)：DUT 只剩预期 `mos-tail-params` warn（默认保留尾参），TB/RUN 全清。

后段 msg 90+ 切到 SKILL `dbCreateRect` 查询 / `cdsListInstances.il` 列实例 / 可视化弹窗 / virtuoso-bridge 环境排障（GLIBC/libpython3.11 缺失），与 netlist 清理主线无关，不合成。

## cleaning.md 关键规则（用于 case 判分依据）

1. 保留 raw 生成物，不在原处编辑 → 归档到 `raw/`
2. 拆三层：DUT（subckt+器件）/ TB（电源/激励/负载/DUT 例化）/ RUN（model include/参数/分析/save）
3. DUT 不得含：电源 vsource / 时钟 / sweep / save / probe / analysis 语句 / model include / 顶层参数
4. MOS 器件文件顶部加端子顺序注释 `// MOS terminal order: D G S B`
5. 语义重命名随机节点/实例（`net1`/`_net23`/`N_*`/`M0`/`I42` → 语义名）
6. 默认保留 MOS 尾参；stripped reference 是显式选择
7. 无法确定的标注 review note，不静默"修"
8. checker 只报告，不重写

## case 合成 plan

- **task_id**: `NetlistDeckSplitProduce-001`
- **domain**: `analog_context`
- **asset_fidelity**: `synthesized-reframe`
- **grade**: L1 (offline python；check 解析 .scs 文本，无真实 EDA 二进制依赖；spectre 不在 .75 强求 L2.live)
- **judge_layers**: `["L0","L1"]` (LIVE-NA)
- **reframe**: spec-JSON 驱动「Spectre 网表语义清理 + DUT/TB/RUN 三层拆分生成器 `curate_netlist(spec)->report` + hidden-B 反硬编码」
- **spec schema**: `{design, raw_netlist(text), raw_subckt_name, dut_subckt_name, ports[], rename_map{old→new}, review_notes[], tb{supplies[], stimuli[], loads[], dut_inst_name}, run{parameters[], analyses[], saves[], model_include_placeholder}}`
- **curate_netlist 输出 report**: `{valid:True, files{raw,dut,tb,run}, raw, dut, tb, run(texts), dut_subckt_name, tb_subckt_name, instance_count, device_count, review_notes}`
- **A (visible) spec_A**: 比较器 OTA，5 MOS，raw_subckt=bad_cmp，dut=cmp_ota，rename M0-M4→语义名 + net1-4/N_5→语义名，TB 电源+差分激励+负载+xdut，RUN dc+tran+save，model include placeholder
- **hidden B spec_B (token-structurally 不同)**: 2 级 opamp，8 MOS + 1 cap = 9 器件（A=5），raw_subckt=raw_amp，dut=opamp_2stage，不同端口名(inp/inn)、不同 rename map、不同 analyses(ac dec 10 1 1G + tran)、不同 parameters(vac)⇒A 硬编码器在 B 全错
- **check.py ≥14 conds**：a zip 含 py ②b py_compile ③c A 运行 valid+4 文本非空 ④d A DUT 有 MOS 端子顺序注释 ⑤e A DUT subckt 名匹配+实例已语义化(无 M\d+/X\d+) ⑥f A DUT 无随机节点(无 net\d+/_net\d+/N_\d+ 裸名) ⑦g A DUT 无 analysis 语句(dc/tran/ac/save) ⑧h A DUT 无电源(vsource) ⑨i A TB 有电源+DUT 例化(xdut dut_subckt) ⑩j A TB 无 analysis 语句 ⑪k A RUN 有 model include placeholder+parameters+analyses+save ⑫l A RUN 无电路器件(无 MOS 实例/无 subckt 定义) ⑬m B 运行 valid+dut_subckt 名≠A+instance_count≠A ⑭n 反硬编码:源码无 A 专属 token 字面量
- **§4.9 三假**: empty→c / print_only→c / core_deleted→e(g) + extra: hardcode_a→m / dut_keeps_analysis→g / tb_has_analysis→j
- **LIVE-NA 理由**: deliverable=Python 脚本产 .scs 文本，check 解析文本+独立复算断言，无真实 EDA 工具二进制依赖；spectre 不在 .75 不强求 L2.live
