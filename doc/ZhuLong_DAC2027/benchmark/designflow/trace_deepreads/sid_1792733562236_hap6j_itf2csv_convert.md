# deepread: sid_1792733562236_hap6j (claire1l @ hfeg0pkn001 / 10.129.2.13) — ITF→CSV 转换

## trace_source
- user: claire1l, host: hfeg0pkn001 (10.129.2.13), session: 1792733562236_hap6j
- match_count: 11, keywords: schematic:12;virtuoso:5;aether:2 (D-domain by shard-D filter; task is ITF parsing = analog_context)
- size: 500KB / 137 msgs / 11 user turns (NTURNS)
- scan src: ssh_eda_search_20261113_131349

## 用户意图（逐字 user turns，produce-task）
- U0「将itf转化为csv文件，itf路径：/home/maxwella/.../cxmttsi_isc_6m5y1rdl_98C_TYP.itf，csv文件参考格式：/proj/lacaa/.../test.csv」
- U23「thickness不要shrink，优化脚本」(去掉 0.9 缩放)
- U35「csv中via的thickness和height也写进去」
- U45「via/metal的height需要底面的高度」
- U59「via的thickness和height不对，例如IMD5_4和IMD5_3为M5的同层介质，PAS1_2和PAS1_1为RDV的同层介质，RDV的thickness为PAS1_2和PASS1_1两层介质的thickness之和，为0.8um」
- U73「conductor的height不对，例如C4_bump的height应该与ILDB0的height一致，为0.001um，M1的height应该与IMD1_1的height一致，为101.882um」
- U85「TSV type为I的DK与itf中INSULATION_ER的值相同，为4.2，电导率应该写在Cond列，TC1和TC2列写温度系数，Tref值与itf中的GLOBAL_TEMPERATURE相同」
- U97「…其他VIA/conductor一样的改法」(所有 conductor/via Tref=GLOBAL_TEMPERATURE)
- U111「所有的CONDUCTOR/VIA的电导率都要写到Cond列，温度系数写在TC1和TC2列，温度写在Tref列」
- U115「TSV type为I时不要写Cond和Tref」
- U125「没有温度系数的层不许要写Tref，例如C4_bump和TSV」
- 末尾 assistant 确认完成（U125 后 #136 收尾）。**用户接受**：无 further correction。

## 助手工具链与产物
- read_files(itf + ref csv) → search_codebase(timeout) → editor 写 `/home/claire1l/itf2csv.py`（6225B）→ run_approved_command(python-runner) 运行验证 → editor 写 `/home/claire1l/cxmttsi_isc_6m5y1rdl_98C_TYP.csv`（1732B, 40 行）。多轮 editor 修订 SCALE/cond_h/via L/TSV I 行。
- 真实 ITF 可达（maxwella 所有，只读 2487B/50 行）；参考 test.csv 不可达（/proj 权限拒绝）→ 助手靠逆向 itf 自洽推出规则。
- 最终 itf2csv.py + 最终 CSV 均已抓取（gold_itf2csv.py / gold_csv.csv on .75 workdir）。

## 最终转换规则（gold 验证一致）
1. parse `GLOBAL_TEMPERATURE`→glob_temp(int)；parse `DIELECTRIC/CONDUCTOR/VIA/TSV <name>{attr=…}`（跨行合并）。
2. **frontside** = 第一条 VIA/TSV 之前的 DIELECTRIC/CONDUCTOR（文件序，自顶向下）。`substrate_top=100.002`，`anchor = substrate_top + Σ frontside DIELECTRIC THICKNESS`。
3. **介质行(D)**：Thickness=原 THICKNESS（不缩放），Height=anchor−zdown（zdown 按已遍历介质累计，导体不推进），DK=ER。
4. **固定三行**：SUBSTRATE(D,100,0.002,DK=11.9) / ILDB0(D,0.001,0.001,1) / ILDB(D,0.001,0,1)。
5. **导体行(C)**：Thickness=原值，Height=anchor−zdown(=紧邻上方介质高度)，Cond=1/(RPSQ×(t×1e-6))，TC1=CRT1,TC2=CRT2(sci)，Tref=glob_temp(仅当有 CRT)。
6. **C4_bump(C,固定)**：0.001/0.001/Cond=1e+15，无 TC/Tref。
7. **过孔行(V)**：序 = TSV 最先，其余 VIA 按 TO(上层金属) 在 frontside 导体序中的位置升序。Thickness=metal_lower[TO](=TO 金属正下方相邻 2 层介质 THICKNESS 之和)，Height=metal_top[FROM](下层金属 Height)，Cond=L×1e6/(RPV×AREA)，TC1/TC2=CRT，Tref=glob_temp(仅当有 CRT)。TSV 特殊：Thickness=ITF THICKNESS(100),Height=0.001,Cond=1/RHO×1e6，无 TC/Tref。
8. **TSV 绝缘行(I,最后)**：Thickness=INSULATION_THICKNESS,DK=INSULATION_ER，**不写 Cond/TC1/TC2/Tref**。
9. 格式：Thickness/Height/DK = `%.3f` 去尾 0；Cond = `|x|≥1e12` 用 `%.0e` 否则 `%.2f` 去尾 0；TC = `%.2e` 指数去前导 0；Tref=整数。

## 合成计划（已交付 Itf2CsvConvert-001）
- **case_id**: EDA-Eval-DesignFlow-Itf2CsvConvert-001, domain=analog_context, grade=B, difficulty=L1（纯 stdlib ITF 解析→CSV，离线）。
- **SUT 产**：`outputs/submit.zip` 内 `itf2csv.py`（通用 CLI `<in.itf> <out.csv>`）。
- **A(visible)**：`sample.itf` 3-metal 栈(TOPM/M2/M1+RDL+TSV+C4_bump, GT=85, 层名 PAS_A/IMD2_A…)。
- **hidden B**：`sample_b.itf` 4-metal(RDL/M4/M3/M2/M1+vias V1/V2/V3/RDV+TSV, GT=110, 层名 OXY/PAS/IMD) — 不同金属数/层名/温度，反硬编码。
- **hidden C**：`sample_c.itf` 2-metal(UPM/LOM+via LOV+TSV, GT=25, 层名 TOP/MID) — 跨输入反硬编码。
- **check.py**：独立 oracle 重算 B/C 期望 CSV，subprocess 跑 SUT 脚本，逐字段数值容差比较。14 条件 a-n。
- **negatives**：empty_shell(d+)/print_only(f+)/hardcode_a(c+)/core_removed(c+) — 4 个 distinct failure set，§4.9 三假(empty/print/core)全 FAIL。
- **k_rationale = k_check = 14 ≥ 8 ✓**。
