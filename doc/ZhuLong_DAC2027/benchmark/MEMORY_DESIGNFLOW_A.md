WAITING: 0（shard A 轮 32：合成 EDA-Eval-DesignFlow-CdlVbnBulkRemap-001 ✓ 并落 A.jsonl 第 49 行。trace 1792552971568_dnkz8（johnl@hfeg0plg99,mc=99,pnr_signoff 域）T_IsmTop StarRCXT RCC 抽取失败修复：用户轮 0「I37 底层没map vbn 到vss vbp 到vcc 要改cdl…修改并完成RCC」——用户已给根因+方案→不符 A 档规则②，归 **B 档 synthesized**。深读 679KB/148 msgs 定位：CDL T_IsmTop.cdl(emy2netlist,3575行) 顶层 `T_IsmTop ... vbn! vbp! vcc! vdbias! vss!`，buf 族子电路 bufLx4/bufLx16 签名 `A Y vbn! vbp! vcc! vss!`；实例 XI37(bufLx4) bulk 端接 vbn!/vbp! 未映射 vss!/vcc!，备份 .bak_vbnfix 的 vbn/vbp 计数各多 1 印证修复=单行 XI37 vbn!→vss!、vbp!→vcc!。assistant 后续重抽 RCC 连环遇 VCO=aok/aoi、GLIBC、libtbb 环境问题转 bsub，session 最终 failed（RCC 实跑未纳入判分，太脆弱）。scope 聚焦确定性可判分子任务=CDL 体偏置修复器。交付=submit.zip 含 fix_cdl.py(通用 bufLx* bulk 重映射,按子电路名+bulk 端取值定位,不硬编实例)+T_IsmTop_fixed.cdl+fix.diff。A 可见=T_IsmTop(XI37/bufLx4/JudgeN<8>/imc19n TYP_98 0.72V)；B 隐藏=T_DacTop(XI52/bufLx16/DacCtrl<3>/cxmt10G4 TYP_125 0.90V)——跨输入守卫击破硬编 XI37/bufLx4。check.py **14 条 a-n** 独立断言，本地自验 ref **PASS 14/14** + 3 negatives 全 FAIL（fake_empty→f-n / fake_print_expected→f-n / naive_hardcode_xi37→f,g,h,l）+ §4.9 三假(空壳/只print/删核心)全 FAIL ✓。check.py 资产路径加了 _resolve_assets_dir() 兼容 exec(test,ns) 无 __file__ 的 validator 路径（inline-exec 也 PASS 14/14）。🧾 断言: k_rationale=k_check=14 ≥8 ✓。台账 dnkz8 claim→case，covered 47→48，pnr_signoff 19→20，DEBT=0。候选池：本轮改用 10/28 summary.tsv mc≥50 shard-A 工具候选（mc≥100 已耗尽），手动排除台账 71 条后得 fresh 候选 wb03t(691,但 analog 主)/l36g5/97mj2/4xt0p/d1cgz/dnkz8(99)等——多属 analog-dominant 顺带碰 innovus；选 dnkz8 因 calibre/netlist 重(pnr)。下一轮=继续从 mc≥50 fresh 候选选 verification/eda_other（覆盖偏低）。）

## 顶部快照
- **PHASE**: shard A 合成轮 32（A jsonl 49 行/covered=48）· covered=48 / target=696 (mc≥100) = 6.9% · domain: digital:12 · eda_other:7 · pnr_signoff:20 · verification:7
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=48 / target=696 = 6.9%（10/28 summary.tsv mc≥100 shard-A 工具候选已耗尽；本轮切到 mc≥50 fresh 候选，已用 dnkz8 mc=99；每日扫描 eda_trace_2026110*.log 备用）
- 📦 体积：TASK≈17KB / MEMORY_A≈小
- DEBT: 0（dnkz8 已合成 CdlVbnBulkRemap-001）；rewrite_queue 全 done
- 🧾 断言: k_rationale=k_check=14 ≥8 ✓（今日 1/30 达标，存量断言清单进度仍 1/30）

## 迁移说明
- 本 MEMORY 为 shard A 独立文件（首次创建，此前仅有 MEMORY_A_archive.md 存旧轮次流水）
- 旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）
