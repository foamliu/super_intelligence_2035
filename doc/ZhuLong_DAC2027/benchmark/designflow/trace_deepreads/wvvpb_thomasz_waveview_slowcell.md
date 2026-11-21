# Deepread: wvvpb (thomasz @ hfeg0pkn003) — waveform / slow-cell locate

- **session**: `1795153863375_wvvpb.messages.json` (60 msgs, 622 KB)
- **user/host**: thomasz @ hfeg0pkn003 (10.129.2.12)
- **match_count**: 78 ; **domain**: waveform
- **scan keywords**: cmos:373 / analog:296 / netlist:197 / drc:99 / mosfet:26 / hspice:21 / synopsys:19
- **ledger status**: case → `EDA-Eval-DesignFlow-WvvpbSlowCellLocate-001`

## 真实任务意图

用户给两份 Synopsys WaveView 导出的 `.list`（文本格式，preamble + 表头 `Signal_idcode \t Signal_hierarchy_name \t VC_count(this_sig_vc_percentage)` + 数据行）：
- `fast.list`：常温 30°C 基准仿真的 per-signal VC_count 列表（445 行数据）
- `slow.list`：仅把温度改成 45°C 后仿真明显变慢（只跑完约 20%）的同样导出（492 行数据）

`VC_count`（voltage convergence count）= 该信号每个 time-point 的收敛迭代次数，近似正比于该信号所属 cell 在该次仿真里耗费的时间。用户想对比两份 VC_count，定位哪些 cell 在慢仿真里花了大量时间（slow 相对 fast 涨得最多），以便后续把这些 cell 的 subckt 提升为 spicehd 模式来加速。

## trace 关键事实

- 两份 `.list` 来自同一仿真目录 `/rundata/ddgoa/V0/simdir/finesim/ddgoaF/MatrixRun_Netlist_IDD_20261019_aiden_1117_pdhammer/iddleakage-2n1bk-1019.x16.FF1`（FastSim MatrixRun IDD leakage 仿真）
- fast.list top 信号：`i(vbncore)` / `xi_c_top.x(inh_vbncore)` / `i(vbpcore)` / `xi_c_top.xi_channel.xi_chanmid.x(inh_vintcore)` 等 — 数字通道核心电源/偏置网
- slow.list top 信号：`xi_c_top.xi_channel.xi_chanmid.xi_ag_vdivstdind_com_0.isub(inh_vss)` / `xi_vdbiasactchindcomip_0` / `xi_ag_vdivactind_com_0` / `xi_analogspinelm_new` / `xi_analogchlamps_new` 等 — 模拟分压/偏置/电流镜类 subckt，正是温度敏感、慢仿真的瓶颈
- agent 最终交付：finesim_mode patch，把 `VdivStdIndComIP` / `VdivActIndComIP` / `VdbiasActChIndComIP` / `AnalogSpineLM_new` / `AnalogSpineRM_new` / `AnalogChLAmps_new` 等 subckt 提升为 spicehd 模式

## 选料判断

- D-pure（waveform/waveview），mc=78 充足，真实交付（finesim_mode patch）→ GOLD-deliverable
- 取真实意图的**离线 L1 复刻**：不要求 SUT 跑 WaveView（沙箱/许可依赖），而是写 Python stdlib 脚本解析两份 `.list`、算 per-hierarchy VC_count diff、输出 top-20 慢 cell 的 `report.json`。这与 trace 的"对比 fast/slow 定位慢 cell"意图一致，且 L1-boundary 可判分。

## 造题设计

- **asset A**（SUT 可见，真实数据裁剪 top-60）：`fast.list` + `slow.list`（真 xi_c_top 层级，未脱敏）
- **hidden B**（仅 check 可见）：合成 dram_top/bank0/saarray 层级 + vdd_core/vss_core/vref_buf 信号，20 fast / 21 slow（1 个 only-in-slow = xi_eqz），与 A token 全维不相交
- **hidden A'**（anti-hardcode）：B 的 VC_count ×2 + 每个 hierarchy 名加 `_r2` 后缀 → B-gold 与 A'-gold 完全不同（max_diff 150000 vs 300000，hierarchy `i(vdd_core)` vs `i(vdd_core)_r2`），击穿任何 B-hardcode stub
- **reference**：通用 stdlib 解析器（tab-split + idcode.isdigit + `count(pct%)` 正则），非写死
- **check.py**：19 条独立断言（zip/py_compile/跑B出report/8字段/计数/only集合/max_diff/max_hier/top0/top长度/anti-hardcode A'两查/跨输入护栏/§4.9三假FAIL/B-hardcode stub跑A'FAIL/3sha确定性）
- **§4.9 三假**：empty（空文件）/print_only（只 print）/core_deleted（main 调被删的 parse_list → NameError）跑 B 全 FAIL
- **B-hardcode stub**：`hardcode_B.py` 内嵌 B 表、忽略输入永远产 B-gold → 跑 B 能过、跑 A' 产 B-gold(150000) ≠ A'-gold(300000) → 被 condition ⑱ 击穿
- 自验：reference_submit.zip 跑 check.py PASS（all 19）；4 个 negative 行为符合预期

## 教训

- `.list` 经 base64 + shell echo 传输会偶发单字节腐蚀（'x'→'8'，"xi_c_top"→"8i_c_top"），必须用 read_file 直读 + write 工具直写，或 decode 后逐行校验
- WaveView 导出的 fast/slow top-N 信号集合重叠极低（fast 是数字电源网、slow 是模拟分压/偏置网）→ 可见 A 的 common_count 很小，但这不影响判分（check 跑隐藏 B，B 有良好重叠）
