# 6niih 深读笔记 — yfguo WaveView FSDB 整芯片电流分析

- **trace**: `1795144377582_6niih.messages.json` / yfguo @ hfeg0pkn003 / mc=158 / 282 msgs / 911KB
- **scan keywords**: waveview:383;synopsys:116;cmos:86;schematic:84;analog:75;netlist:52;pyaether:32;hspice:23
- **domain**: spice_sim (FineSim FSDB 电流分析)

## 用户意图
yfguo 要分析一个 FineSim 仿真产生的 FSDB 波形文件的整芯片电流消耗。使用 waveview-fsdb-readerV2-2 技能，通过 bsub 提交到计算节点跑 WaveView Tcl。

## assistant 工具链（关键转折）
1. **技能加载 + 基础读取器缺失**：waveview-fsdb-readerV2-2 技能目录里 `waveview_fsdb_reader.py` 缺失，wv_tmp 里只有其他用户(e0039602)的历史模板。assistant 自己写了基础读取器。
2. **license 服务器不可达**：沙箱无法解析 license 服务器主机名（无网络）→ 改用 **bsub 提交到计算节点**（计算节点有 license）。
3. **bsub 坑**：wrapper PATH 覆盖了 LSF bin → 加 LSF bin 目录；bsub 提交了 .tcl 文件而非 wrapper 脚本（`sh wv_s_...tcl` 被 bash 当 sh 脚本）→ 修复提交命令。
4. **信号枚举突破**：`sx_signal` 返回内部 void 名；改用 `sx_first_wave`/`sx_next_wave`/`sx_get_name` 遍历波形对象恢复逻辑名；最终用 `sx_wdf_info -waveforms` 一次性拿到全部 → **1,162,795 信号**。
5. **测量 API**：`sx_meas_average/max/min`（支持 `-xrange`），直接返回数值。`sx_meas_max` 对 `sx_meas_average` 的返回值会报 "argument type error"（不能链式传 sig_obj）。
6. **Phase B 加速**：单作业 ~7 行/秒（测量本身是瓶颈），改 12 切片并行 → 队列限并发 2 → ~35 行/秒；再改 avg-only（去掉 max/min 调用）→ ~50 行/秒。

## 关键真实数据
- **信号清单**: total=1,162,795 = 顶层 v()=415 + i()=264 + 层级 v()=550,337 + isub()=538,857 + **i()=72,922 元件电流**
- **元件类型**: mn1=34,996 (NMOS) / mp1=32,100 (PMOS) / d1=5,806 (diode) / v0=20 / distinct=4
- **scope depth**: 2:5, 3:1805, 4:2620, 5:14047, 6:12743, 7:25616, 8:10210, 9:4330, 10:1522, 11:24
- **2nd-level scope top**: xi_io_tsacmdlrd.xi_io_tsacmdlrdclk=19,941; xi_dl_dlltop.xi_dl_tdcdlylv=4,555; xi_dl_dlltop.xi_dl_fdlregx4=2,822; xi_dl_dlltop.xi_dl_pdgen=2,586; xi_dl_dlltop.xi_dl_flreg=1,877; xi_dl_dlltop.xi_dl_clk2dl=1,733; xi_dl_dlltop.xi_dl_thermo2sel=1,728; xi_dl_dlltop.xi_dl_cdl_cmde=1,558
- **顶层电源电流 (Phase A)**: vvdd1 avg_ss=0.02151A(主导,VDD1 1.8V)/vdpg -0.01876A(VDPG 1.17V)/vvss -0.008184A(VSS return)/vvdll 0.003541A(VDLL 1.1V DLL core)/vvssdll -0.003534A(VDLL return)/vvddqca 0.00327A/vvddq 0.002174A/vvcc 2.352e-09A/vvwlp -6.978e-10A 等 16 源
- **元件电流样本 (Phase B)**: xi_dl_dlltop.xddd1.i(d1) av=-8.50091e-13 max=-3.33272e-14 min=-1.13322e-12; xi_io_tsacmdlrd.xddd0.i(d1) av=-1.1e-12; xi_dl_clockbuffer_ca2dll_883.xi152.xi0.xmm0.i(mn1) av=1.29292e-08 max=7.5676e-06 min=-2.95383e-08
- **Phase C 结论**: xi_io_tsacmdlrd.xi_ag_vdpgacttop (Vdpg LDO) 为最大电流模块 (47mA |avg|和, 与 vdpg 域 19mA 吻合, |avg|和双计 PMOS+NMOS)

## reframe（复刻 Phase C 报告聚合器，离线 L1 Python）
真实任务是端到端 FSDB 电流分析（需 WaveView sx_meas_* + bsub 计算节点）。可离线判分的交付件 = **Phase C 报告聚合器**：给定 manifest（信号清单）+ supply_meas.tsv（顶层电源电流）+ element_meas.tsv（层级元件电流测量子集），聚合成结构化 JSON 报告。

核心齿：
- 层级信号名前两 token 分组规则（`xi_a.xi_b.....i(mn1)` → `xi_a.xi_b`）
- sum_abs_avg / sum_avg / peak_max 聚合
- top-N 模块排序
- 元件类型统计
- 测量子集 vs 全 FSDB 区分（n_elements_measured != manifest.hierarchical.i）
- 反硬编 B（不同 FSDB/不同清单/不同模块名/不同电流量级）

**case = EDA-Eval-DesignFlow-FsdbCurrentReportAggregate-001** 落库（k=16 a-p, ref 16/16 PASS, NEG 3/3 FAIL §4.9 三假齐 empty→C1/print-only→C4/core-removed→C9, 3-seed sha256 一致 ✓）。
