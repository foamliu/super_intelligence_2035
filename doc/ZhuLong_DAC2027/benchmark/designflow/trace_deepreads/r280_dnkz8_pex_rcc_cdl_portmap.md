# 深读：1792552971568_dnkz8 — johnl @ hfeg0pkn001/10.129.2.10 (r280)

**trace**: 1792552971568_dnkz8 · johnl@hfeg0pkn001 · mc=146 · 148 msgs · 2 real user turns (U#0 seed, U#115 "改好没有")
**markers**: innovus12 / netlist389 / calibre371 / schematic156 / hspice24 / pyAether3 (eda_trace summary)
**shard C · domain: physical_verify (PEX / RCC)**

## 种子（U#0 逐字，B-synthesized — 用户给出根因+修复方向，不合 A-档）
> /proj/drcoa/V0/ver/pex/johnl/T_IsmTop 这个文件夹抽IsmRCC失败了 说是I37底层没map底层没map vbn 到vss vbp到vcc 要改cdl你改下记得 对所有目录下到文件的修改都要比较修改前后确保合适修改没问题 修改并完成RCC抽取 你别想太多 就这一个cell连线可能需要修改一下 最后完成RCC

用户已指出根因（XI37 底层没 map，vbn→vss / vbp→vcc）+ 修复方向（改 CDL）→ B-档 synthesized。

## 真实 assistant 工具链 + 产物（grounded from MSG#1–#146）
- list_allowed_files(/proj/drcoa/V0/ver/pex/johnl/T_IsmTop) → read_files(logs/CDL)
- 真 run path 解析为 /rundata/drcoa/V0/ver/pex/johnl/T_IsmTop
- read_files(T_IsmTop.cdl, T_IsmTop.cdl.bak_vbnfix, lpe logs)
- editor 一系列 analyze_cdl*.py / scan_logs.py / diff_check.py / grep_err.py / find_tbb*.sh / bsub_job.sh / poll3.sh
- 关键发现：
  - XI37 是 bufLx4 的 instance（CDL 行 3249），端口连接 `vbn! vbp! vcc! vss!`
  - 修复 = vbn!→vss!, vbp!→vcc! → `vss! vcc! vcc! vss!`
  - 当前 .cdl 已含修复（vs .bak_vbnfix 备份原始未修复行），RCC SPF 输出 T_IsmTop.spf.TYP_98_RCC 陈旧（mtime Aug 25 2026），CDL 修复于 Oct 21 2026 → RCC 未用修复后 CDL 重跑
  - calibre LVS step 因 VCO env mismatch (aok vs aoi) 在交互 host 失败；bsub compute node 环境正确
  - 提交 bsub job 259548 到 star queue 重跑 RCC pipeline（StarXtract step3）
- 工具计数：editor×33 / run_approved_command×29 / read_files×9

## 为何 B 档重定义为离线 L1-boundary
真实 PEX/StarXtract/calibre/live /proj/drcoa 不可沙盒复现。离线核心 = 给定 CDL 网表 + 端口映射修复 spec →
1. 按 target_instance 定位 instance 行
2. 应用 port_remap（仅目标行的 net 参数替换）
3. 产 fixed CDL + diff（before/after 行）+ validation JSON（net count delta 校验）
4. 断言仅目标行变更，其余行 verbatim

check.py 在 hidden B 上 subprocess 真跑候选脚本，断言输出结构（diff 精确 / net delta / instance 命中 / 行 verbatim）。

## B-track 防硬编码
- B target_instance=XI52 ≠ A XI37（挫败硬编码实例名）
- B cell=ampBias ≠ A bufLx4
- B port_remap={vpw!:vss!, vdd!:vcc!} ≠ A {vbn!:vss!, vbp!:vcc!}（挫败硬编码 net 名）
- B 含诱饵：XInn 同 cell 但已正确连接（不应改）、XId 另一 instance 含 vpw!/vdd! 但非目标（不应改）
- B net delta 不同（挫败 print_expected_A）

## DISTINCT from 现有 physical_verify 系
- r275 ConnPriorityDupCheck=connectivity 重复端点+priority / r273 DummyRuleCfgParse=Dummy config schema / r266 DrcPatternGeomGen / r259 DrcConnectGraph / r256 LdrSvrfRuleGen / r241 SvrfPvrsRuleTranslate / r237 DrcLogTeardown
- 本案首次 ground on **PEX/RCC CDL 网表 instance 端口连接 net 映射修复（vbn→vss/vbp→vcc power-net remap）+ before/after diff + net-count delta 校验 + 仅目标行变更守卫**，核心是 SPICE netlist instance-arg 定向替换 + 一致性校验，非 DRC/LVS log 解析或 SVRF 规则翻译。
