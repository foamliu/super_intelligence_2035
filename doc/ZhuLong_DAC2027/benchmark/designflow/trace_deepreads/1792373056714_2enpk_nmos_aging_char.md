# Deepread: 1792373056714_2enpk — jasonw NMOS aging characterization

- **user**: jasonw @ hfeg0plg55, mc=129 (hspice=356), 145 msgs, Oct 19 09:24–09:48
- **session file**: `/home/jasonw/.cline/data/sessions/1792373056714_2enpk/1792373056714_2enpk.messages.json` (362KB)
- **domain**: characterization / spice_sim (shard B)

## 真实任务流
1. 用户先问可访问目录、磁盘空间（探索）。
2. 「你可以通过bsub命令运行hspice仿真器」→ 用户让 agent 用 bsub + HSPICE 跑仿真。
3. agent 探测工具：bsub@/apps/lsf/10.1, hspice@/apps/synopsys/SRB/hspice/V-2023.12, spectre NOT found。
4. 发现 jasonw 已有 aging 表征网表 `/home/jasonw/aging/nrvt_age_tt.sp`（NMOS nlvt_ckt, HL22 aging PDK `top_pre_age.lib` TOP_TT_age, 125C, .meas dc vtlin/idlin/idsat，3 个 .data swpdata1/2/3，W=0.5u L=0.03u Vdd=0.8）。
5. 反复 bsub 提交（job EXIT→修环境→DONE），最终 `cd tmp/hspice_test3 && hspice ./nrvt_age_tt.sp -o ./` 跑通（PrimeSim HSPICE V-2023.12, 3.78s）。
6. **真任务轮 [101]**：「分析下刚才运行的aging仿真数据」—— agent 写 `analyze_aging_v2.py` 解析 .ms0/.ms1/.ms2 $DATA1 + .sw0 二进制，提取 Vtlin=52.74mV / |Idlin|=53.487uA / |Idsat|=342.913uA，算 Ion=0.686 mA/um (685.8 A/m) / Ilin=0.107 mA/um (107.0 A/m) / Idsat/Idlin=6.41x，打印表征报告。
7. 收尾问「仿真目录在哪里」。

## 关键产物（真实，已 scp 到 .75 workdir 作 case 资产样例）
- `nrvt_age_tt.sp`：aging 表征网表（foundry HL22 aging model，不可移植 .75）
- `nrvt_age_tt.ms0`：$DATA1，vtlin=5.2736e-02 V @ temper=125
- `nrvt_age_tt.ms1`：idlin=-5.3487e-05 A
- `nrvt_age_tt.ms2`：idsat=-3.4291e-04 A
- `nrvt_age_tt.lis`：HSPICE log（含 `vtlin= 5.27358e-02` / `idlin=-5.34867e-05` / `idsat=-3.42913e-04`）

## 便携化（合成 case = EDA-Eval-DesignFlow-NmosAgeChar-001）
真实网表用 foundry aging PDK（.75 无），取可复现子技能 = **level-1 NMOS Vtlin/Idlin/Idsat .meas 表征 + .ms $DATA1 解析 + 每微米驱动度量**。候选写 `aging_char.py`（CLI `--params --out`）：生成 level-1 deck（Vtlin: Vds=Vdlin 扫 Vgs 找 Ids=cc*W/L；Idlin: Vgs=Vgstr 扫 Vds 找 Vds=Vdlin；Idsat: Vgs=Vgstr 扫 Vds 找 Vds=Vdstr，全 .meas dc），调 HSPICE 真跑，解析 .ms0/.ms1/.ms2，算 Ion=|Idsat|/W (A/m, mA/um) / Ilin=|Idlin|/W / Idsat/Idlin 比，写 char_report.json。

**A-档合规性**：真任务轮 [101]「分析下刚才运行的aging仿真数据」是纯需求（未给根因/修复）→ A-档合规。但本 case 做成 **B 档 synthesized**（候选写便携 char 工具跑 HSPICE，而非只解析给定 .ms），因新建 case 须 L2/L3，纯解析是 L1。真实 .ms 样例作为格式/上下文参考附在 assets（foundry 数值 52.7mV 与 level-1 便携 216.8mV 不同，候选不能照抄）。

## .75 HSPICE 排雷
1. level-1 MOS 元件必须用 `M1 d g s b model l=.. w=..`，**不能** `XM1`（X=子电路调用→model not found）。
2. `.MODEL` 须放 `.LIB tt ... .ENDL tt` 块内 + `.lib 'corner.lib' tt` 加载；顶层裸 `.MODEL` 被报 "model not found"。
3. Vtlin .meas：Ids 随 Vgs 升高而增大（i(Vds) 变更负 = **falling**），须 `fall=1`（rise=1→failed）。Vgs 步长 0.002V 够细。
4. .dc 扫描范围用字面值（`.dc Vgs1 0 0.8 0.002`），`vdd` 等 .param 进范围会报 "Undefined parameter vdd"。
5. .meas `when i(Vds1)=<阈值电流字面值>`，阈值=cc*W/L（cc=-1e-8, W=0.5u, L=0.03u → -1.6667e-7）。

## Ground truth（.75 HSPICE V-2023.12-SP1-1 真跑）
- **A** (W=0.5u L=0.03u Vdd=0.8 kp=120u vto=0.5 temp=125): vtlin=0.2168V, |idlin|=37.30uA, |idsat|=241.96uA, ion=483.9 A/m, ilin=74.6 A/m, ratio=6.487
- **B** (W=1.0u L=0.05u Vdd=1.2 kp=150u vto=0.45 temp=85): vtlin=0.2832V, |idlin|=201.3uA, |idsat|=1032.7uA, ion=1032.7 A/m, ilin=201.3 A/m, ratio=5.130
- A/B 全异（vtlin 差 66mV，|idsat| 差 4.3x）→ 跨输入守卫成立。

## check.py 17 条断言 (a-q)
a zip含aging_char.py+char_report_A.json · b py_compile · c 候选A exit0+report · d 必需键 · e vtlin_A±5mV · f |idlin_A|±8% · g |idsat_A|±8% · h ion=|idsat|/W ±1% · i ilin=|idlin|/W ±1% · j ratio=|idsat|/|idlin| ±2% · k HSPICE曾调用(.lis/.ms证据) · l temper==params · m 跨输入守卫(B≠A) · n vtlin_B±5mV · o |idsat_B|±8% · p |idlin_B|±8% · q w/l==params

## selftest (.75 端到端)
ref **PASS 17/17** + 5 neg 全 FAIL(NEG_RC=0)，互异条件集：
- naive_empty→(a) [空壳]
- naive_hardcode_a→(k)(m)(n)(o)(p) [不跑HSPICE+硬编A，跨输入守卫击穿]
- naive_no_run→(k)(f)(g)(n)(o)(p) [公式代替HSPICE，A/B数值偏]
- naive_print_expected→(m)(n)(o)(p) [伪造.lis过(k)但硬编A值，B mismatched]
- naive_wrong_ratio→(j) [ratio=|idsat|+|idlin|非除法]
§4.9 三假(空壳/打印期望/掏空核心)全 FAIL。test字段==disk check.py md5 234ea515dd89a3377ab6239761fcfb98 (10967B) roundtrip OK。k_rationale=k_check=17≥8 闸门 PASS。

## distinct vs 已有 B case
Sram6tDcChar=SRAM bitcell DC 静态测、VihTripTune=判别器翻转点调优、OtaAcReport=WaveView AC 度量提取、TaperBufOpt=buffer DOE PDP 排序 —— 本条=**NMOS 单管 Vtlin/Idlin/Idsat 表征 + 每微米 Ion/Ilin 驱动比**（单器件表征子技能，shard B 此前未覆盖）。覆盖 characterization 域。

## 候选池（下轮选）
trace_ledger.py --shard B next 已排除 2enpk。高 hspice 密度未消费候选：
- 1792131744105_g48nq (adaml, hspice=1359, mc=192) — ⚠ 上轮 MEMORY 标注「spice-skill 撰写/优化会话非真跑仿真」，复核后再定
- 1792720528359_2tuxj (kaixuanx, hspice=382, mc=91)
- 1792394413650_b86q7 (tongni, hspice=381, mc=99)
- 1792487039292_qr1lv (yanghao, hspice=380, mc=98)
- 1792373325953_z6mt7 (tongni, hspice=351, mc=83)
- 1792378687851_j8vf6 (tongni, hspice=349, mc=156)
- 1790245155745_i5ae7 (jiangbaol, hspice=314, mc=119)
- 1792411915181_j8f3i (yutongy, hspice=198, mc=221)
