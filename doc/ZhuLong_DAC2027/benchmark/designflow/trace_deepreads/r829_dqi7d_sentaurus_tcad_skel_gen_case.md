# r829 — NOFILE-parked revival 第四矿脉 mc5-9 A-recoverable 4 候选深读 + dqi7d 造题兑现

> 类型：造题 1 case（SentaurusTcadProjectGenProduce-001, eda_other, B档, k=16/16）+ 治理（3 候选域判/weak 判定）
> 日期：2026-11-20
> eda_flow session r829 (open + close cleaned)

## 一、r828 DEBT(b) 4 待评低 mc5-7 A-recoverable 候选深读

r828 batch subdir 探测确认 8/9 ALIVE，留下 4「待评」候选（uhla7/dqi7d/otgh9/gucnl，9scu4 已判 trivial synthesis:3 pyAether only）。本轮逐条 scp + 读首用户意图 + assistant 工具链：

| slug | user@host | mc | size | msgs | 真实意图 | 真域 | 判定 |
|:--|:--|--:|--:|--:|:--|:--|:--|
| **dqi7d** | liyingw@172.16.8.14 | 5 | 62KB | 16 | 「在当前目录下生成一个sentaurus swb project」→ agent editor 一次生成 4 文件 SWB TCAD pn-diode 项目骨架(.prj/.par/sde_dvs.cmd/sdevice_des.cmd) | **eda_other (TCAD)** | **造题！** |
| otgh9 | e0045488@10.129.2.13 | 5 | 136KB | 49 | FIT(Flow-Induced Thermal) current-direction PEX DSPF CSV 分析 + direction_table.py off-by-one 修复 | **characterization (B)** | defer to B |
| uhla7 | e0025730@10.129.8.86 | 5 | 65KB | 38 | nihowa/zenmeqiehuanzhongwenshuru → 通用 Linux ibus 中文输入法终端配置 | IT/env (非 EDA) | weak |
| gucnl | e02141@10.129.2.14 | 6 | 63KB | 15 | 帮我配置 swb-python-api + 数 skill + 继续执行 → skill env-config/setup | setup (thin) | weak |

**根因**：scan 关键词（verilog/dbget/synopsys）与真实域弱相关。Sentaurus SWB 的 synopsys kw 把 dqi7d/otgh9 桶进 A，但真实意图分属 TCAD(eda_other, A) 与 characterization(B)。域判定必须读首用户意图 + assistant 工具链。

**处置**：
- dqi7d → 造题（eda_other, A 域，见 §二）
- otgh9 → A 台账 --force 更新 parked note（subdir-ALIVE + 真域 characterization + defer to B，未碰 B 台账）
- uhla7/gucnl → A 台账 --force 更新 parked note（subdir-ALIVE + weak 理由，check 牙弱不可造）

## 二、造题：SentaurusTcadProjectGenProduce-001（dqi7d 兑现）

dqi7d (liyingw@172.16.8.14, mc5, 62KB/16msgs/lead, 单轮):
- UT#0: 「在当前目录下生成一个sentaurus swb project」
- trace agent fetch_web_content 被 agent-policy-engine 拒绝 → 按标准 Synopsys Sentaurus pn-diode 用 editor 一次生成 4 文件
- 4 文件结构完整语法正确（按 Sentaurus 标准），但内容**静态固定** pn_diode

**§5 produce-task reframe**：静态固定 4 文件无法用 hidden-B 反硬编（SUT 可直接拷贝 A 固定文件）。reframe 为参数化生成脚本 `swb_gen.py`（读器件规格 JSON → 渲染 4 个 SWB 文件），使 hidden-B（不同器件规格）能 subprocess 真跑反硬编。reframe 忠实保留 SWB 项目 4 文件结构与语义（.prj/.par/sde_dvs.cmd/sdevice_des.cmd）。

- **资产 A**（可见）：`pn_diode_spec.json`（pn 结二极管器件规格：p_region/n_region Silicon 10×5μm + Anode/Cathode + Boron/Arsenic @p_doping@/@n_doping@ + Anode -0.5..0.7V 扫描 + diode_des 输出）
- **隐藏 B**（不进 SUT）：`moscap_spec.json`（MOS 电容：oxide SiO2 + substrate Silicon + Gate/Substrate + Boron @substrate_doping@ + Gate 0→2V 扫描 + moscap_des 输出，与 A 在项目名/区域/材料/电极/掺杂 species/扫描/输出文件名全异）
- **判分范式**：S5 第一范式 produce-task + hidden-B 真跑 + anti-hardcode。check 把 SUT 的 swb_gen.py 在 B 上 subprocess 执行，断言生成的 4 文件 SWB 结构正确 + @param@ 引用与 .par 一致 + 电极跨文件一致 + 区域/材料/掺杂/扫描取自 B（反硬编 A）+ 确定性 + 反退化。ground truth 由 check 自身按 B 规格独立推导（非硬编金答案串）。
- **check 16 条独立断言**（真跑 swb_gen.py on B）：①swb_gen.py 存在+py_compile ②B 上 exit 0+outdir ③4 文件齐全非空 ④.prj Project/Tool/Parameter ⑤.par B 参数 ⑥sde 区域+材料(SiO2) ⑦sde 电极(Gate/Substrate) ⑧sde 掺杂 @param@+B species ⑨refinement+save/build mesh+@node@ ⑩sdevice File 块 B 输出 ⑪Electrode 与 sde 一致 ⑫Physics B 模型 ⑬Solve B 扫描电极/电压 ⑭跨文件一致 ⑮反硬编 B-only 在/A-only 不在 ⑯3 seed 随机化(打乱顺序)
- **自验**：ref PASS 16/16 + §4.9(a)empty(b)print-only(c)core-deleted 全 FAIL + 4 neg(empty/print_only/hardcoded_a/core_deleted)全 FAIL 命中不同断言组 + 3 seed 确定性 + e2e(从 A.jsonl test 字段抽 check.py 跑 ref submit → PASS)
- **k_rationale == k_check == 16 ≥ 8 GATE PASS**

**命名**：初拟 SwbProjectGenProduce-001，发现 cases/A 已有 SwbProjectCreate-001（e02141/mc96/kbs81，用 swbpy2 Python API 创建项目+工具+扫描参数，不同 user/session/交付形态）。为避免混淆改名为 **SentaurusTcadProjectGenProduce-001**（强调 TCAD deck 骨架生成，区别于 API 创建）。两 case 非 duplicate（不同 user/session/意图/交付物）。

**落库**：cases/A/EDA-Eval-DesignFlow-SentaurusTcadProjectGenProduce-001.json (27237B, 5 attachments)；`build_jsonl --shard A` → A.jsonl 含本 case（1 occ）；ledger mark dqi7d→case（--force unpark+mark）。

## 三、A.jsonl 计数说明

build_jsonl --shard A 产出 414 行（cases/A 433 文件 / 414 unique task_id，19 task_id 碰撞去重）。本 case 已在 414 中（grep SentaurusTcadProjectGenProduce = 1）。注意：r828 ZtypeWaveCompareProduce-001 未出现在 cases/A（r828 可能未持久化 case JSON）——这是 r828 的遗留，本轮不修，仅记录。

## 四、纪律

- 🚫 未改题/图/check；🚫 未碰他 shard jsonl/MEMORY/台账（A 台账 --force 仅改 A 自己的 4 行：dqi7d→case + otgh9/uhla7/gucnl parked note）
- ✅ trace 溯源：dqi7d 真实 trace, real_task_summary 含用户原话「在当前目录下生成一个sentaurus swb project」
- ✅ 隐藏 B 与 A 在项目名/区域/材料/电极/掺杂 species/扫描/输出文件名全异
- ✅ k_check == k_rationale == 16 ≥ 8
- ✅ eda_flow session r829 open + close cleaned
