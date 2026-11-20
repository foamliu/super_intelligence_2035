# deepread: 1793069063742_76i4q — hlmc22ull nmoscap/pmoscap 区别 Q&A

## trace 源
- session: 1793069063742_76i4q
- user: wnyu @ 10.129.2.13
- host: 10.129.2.13 (NFS-synced)
- match_count: 18 (keywords: eda_other; doc-search + PDK investigation)
- agent: lead
- msgs: 80 (user 41 / assistant 39)
- size: 374003 B; ALIVE (subdir path sessions/1793069063742_76i4q/)
- mtime: 2026-11-13 16:41

## 用户意图（2 问，逐字）
- U#2: `/home/adaml/wv_ace_skill_build/docs_txt/，这里的txt文件gvim打开吗？ 里边有包含finesim stb仿真的吗`
- U#15/16: `hlmc22ull 里nmoscap/pmoscap什么区别`

## gold 答案
### Q1 (msg#26)
- txt 文件 gvim 可打开（纯 ASCII）
- **没有**直接 FineSim STB 仿真内容（目录是 Synopsys Custom WaveView ACE Command Reference）
- 但有 STB 后处理命令: `sx_gmeas_gain_m`(Gain Margin), `sx_gmeas_phase_m`(Phase Margin), `sx_meas_gain_m`, `sx_meas_phase_m`

### Q2 (msg#79) — 主要判分对象
基于 PDK `/apps/imctf/extpdk/HL22/22HK_V0P5_0D10_for_vodka` (HLMC CL022UL 22ULL "Vodka" v0.5):
1. **官方器件列表** (Vodka_DeviceList_PDK_V0.5_Rev01): nmoscap=0.8V Varactor (NMOS Capacitor), pmoscap=0.8V Varactor (PMOS Capacitor), nmoscap_26=2.6V, pmoscap_26=2.6V；归类为 **Varactor**（变容管）
2. **模型结构** (hlmc_cl022ul_spice_v0p5_0d16 模型库): 两者都二端器件 `(ng nds)`，ng=栅, nds=源漏短接
3. **C-V 方程互为镜像**:
   - nmoscap: `cgmin+dcg*(1.0+tanh((v(ng,nds)-dvgs)/vgnorm))` → V↑ C↑
   - pmoscap: `cgmin+dcg*(1.0-tanh((v(ng,nds)-dvgs)/vgnorm))` → V↑ C↓
4. **_26 后缀**: 2.6V 域，栅氧加厚 43Å，gdf1 漏电元件**注释掉** (`*gdf1`)，纯电容
5. **0.8V 版**: gdf1 漏电元件**激活**；pmoscap 的 gdf1 比 nmoscap 多几何项 (lb2/wb2/wlb2)
6. **corner**: tt/ff/ss/mc_moscap26
7. 沟道载流子: nmoscap 电子(高迁移率), pmoscap 空穴

## PDK 实地核实（r890 在 .75 上验证）
- `/apps/imctf/extpdk/HL22/22HK_V0P5_0D10_for_vodka/model/0.0.7/hspice/hlmc_cl022ul_spice_v0p5_0d16_for_vodka_shrink0d855.lib` 可读
- `.subckt nmoscap (ng nds)` line 264307, `+tanh`, active `gdf1`
- `.subckt pmoscap (ng nds)` line 264317, `-tanh`, active `gdf1` (with lb2/wb2/wlb2)
- `.subckt nmoscap_26 (ng nds)` line 264384, `+tanh`, `*gdf1` (commented)
- `.subckt pmoscap_26 (ng nds)` line 264397, `-tanh`, `*gdf1` (commented)
- corners: mc_moscap26, tt_moscap26, ff_moscap26, ss_moscap26

## 可造性判定
**MAKEABLE** — A档 trace-faithful analysis-Q&A。
- gold (msg#79) 有 ≥12 个独立可验条件（器件名/Varactor 分类/端口/C-V 镜像/电压域/gdf1 漏电/几何项/corner）
- fixture A 自包含：device_list.txt + moscap_subckts.lib(真实 PDK 提取) + topusage_corners.txt + task_brief.md
- hidden B 变体：不同 PDK 名/器件名/电压/oxide/方程符号/corner → anti-leak
- check.py 动态解析 A 推导 ground-truth + 解析 B 推导 B-only token anti-leak + 反退化

## 合成方案
- CID: EDA-Eval-DesignFlow-HlmcMoscapDiffQA-001
- domain: eda_other
- 档: A (trace-faithful, 用户原话 + 真实 PDK 内容)
- k ≥ 12 断言
