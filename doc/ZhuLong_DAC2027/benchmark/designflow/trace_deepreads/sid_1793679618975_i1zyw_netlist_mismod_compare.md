# Deepread: sid 1793679618975_i1zyw — Netlist mis_mod compare

- **session**: `1793679618975_i1zyw.messages.json` (e0030760@hfeg0pkn004, ip 10.129.2.13)
- **match_count**: 158 (hspice 411, netlist 334, schematic 244, virtuoso 9, spectre 1, calibre 1)
- **trace size**: 913 KB, 216 msgs (113 user / 103 assistant)
- **tools used**: read_files×11, run_approved_command×41 (python-runner), editor×42, list_allowed_files×9, get_agent_policy_status×1

## User turns (the conversation arc)
1. **USER#0 (idx=0) — clean A-档 "提出需求"**: 「对比一下这两个路径下的网表，其中一个调用的mis_mod是用来做什么的？」+ 两个 .netlist 路径(`/proj/lacaa/V0/workdir/e0039809/...` 与 `/proj/lacaa/V0_FS/.../ALPS__fqueue3_lacaa/...`)。**只给目标(对比+解释 mis_mod 作用)，无根因、无方案** → 选作 A-档任务说明。
2. USER#18: 「如果要用第一个 netlist 做 MC 3sigma hspice 仿真，模拟 HNM/SNM/WSNM/Iread/Iwrite/Ileak，应该怎么写 .sp」(follow-up how-to)
3. USER#42/53/61: hspice 环境检查 + glibc 报错诊断 + 运行指令
4. USER#69: 「读取 test1_out.lis 数据，分析所有结果，绘制 SNM/RNM/WSNM 蝴蝶曲线、node 扫描曲线」(分析+绘图任务)
5. USER#102/107/108: sw0 波形查看 + xhost DISPLAY 报错(图形界面问题)

## USER#0 deepread (gold standard = assistant ASST#33 结论)

agent 经 list_allowed_files(发现 `/proj/lacaa/V0_FS` 映射到 `/rundata/lacaa/V0_FS`) → read_files 两份网表(首份>47k 字符被截断) → 写 compare_netlists.py/diff_netlists.py/find_mismod.py 经 python-runner 跑 → 清理临时脚本。

**两份网表结构**：
- 两者均为 Aether-SE 导出的 HSPICE 格式单 bitcell SRAM DC 仿真网表，顶层 `BitCell_FS_Simulation_CH336`，都定义相同子电路 `switch_close`/`switch_open`/`BitCell_FS_CH336`(6T: XPU1/XPU2 hc_pu_fs, XPG1/XPG2 hc_pg_fs, XPD1/XPD2 hc_pd_fs，w=25e-9 l=6e-9 nfin=1 wgaa=0.025e-6)。
- 顶层都例化 9 个标准 SRAM DC 测试场景: ILEAK/S_RSNM/SB_RSNM/S_HSNM/SB_HSNM/S_WNM/SB_WNM/IREAD/IWRITE。
- **网表1**(V0/workdir/e0039809, Aug 26 2026, 141 行): `BitCell_FS_CH336` 子电路声明 6 管×9 轴=54 个 `BitCell_FS_CH336_{XPD1,XPD2,XPG1,XPG2,XPU1,XPU2}_sda_rnd_mis_0..8_local` 接口参数(默认 0)，每管携带 `sda_rnd_mis_0_local..8_local`，每测试实例传随机高斯采样值(如 ILEAK: XPD1 mis_5=-1.225795, mis_7=1.984887; XPG1 mis_0=0.558243; 其余多为 -3.0 哨兵)。
- **网表2**(V0_FS, Oct 13 2026, 50 行): 干净无 sda_rnd_mis，仅 nominal 6T bitcell + 9 测试实例。

**mis_mod 是什么**(ASST#33 结论):
- 字面 `mis_mod` 子电路在两份网表及 simulation 目录中均不存在；它位于 PDK 器件模型库 `hc_pu_fs/hc_pg_fs/hc_pd_fs` 内，网表只引用这些模型并把失配参数传给它们。
- `sda_rnd_mis_*_local` = `sda(失配扰动的标准偏差) + rnd(random 随机) + mis(mismatch 失配) + local(片内局部/器件间)`，作用是给 6T bitcell 每管注入随机的「器件与器件之间(intra-die)制造工艺偏差」(典型 ΔVth + ids/u0 偏差)，耦合进 hc_* 器件模型。`0..8` 是 9 个独立随机变化轴(Monte-Carlo 扰动源)，`-3.0` 是 -3σ 截断/饱和哨兵值，非 -3.0 的数才是实际高斯采样 sigma 值。
- **用途**: 网表1(含 mis_mod)做统计/Monte-Carlo DC 分析(看工艺失配下 bitcell 读稳定性/写裕量分布/yield)；网表2(干净)做标称单点 DC(无失配裕量，速度快)。

## Case 抽取
交付 `compare_netlists.py <net1> <net2> <out.json>`：解析两份 SPICE 网表 → 对比结构(subckt/model/管/测试实例) → 识别哪份带 `*_rnd_mis_*_local` 失配注入参数 → 分类 mis_mod 作用 → 产结构化 JSON 报告。

**资产**：真实网表在 `/proj/lacaa`(权限拒，e0031982 身份不可读)，A/hidden 资产按 trace 结构忠实复现：
- A: `BitCell_FS_CH336`/6T/`sda_rnd_mis_*_local`/9 axes/9 tests (gen_assets.py)
- hidden B: `BitCell_FS_CH340`/8T(加 XPG3/XPG4 差分 WL)/`mtp_rnd_mis_*_local`/5 axes/6 tests (gen_hidden.py) — 强制泛化检测，防硬编码 sda_rnd_mis/6T/9-test。

## 验证
- reference `compare_netlists_ref.py` 对 A 对与 hidden 对均产正确 JSON。
- check.py k=14 断言 a..n，reference PASS，5 negatives(naive_empty/always_clean/hardcode_A/print_stub/fake_core_deleted)全 FAIL @ 预期条件，NEG_RC=0。
- §4.9 三假提交(empty/print/ref-minus-core)全 FAIL。
