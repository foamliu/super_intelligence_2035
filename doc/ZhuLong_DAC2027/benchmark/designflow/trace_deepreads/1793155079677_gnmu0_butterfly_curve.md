# Deepread — 1793155079677_gnmu0 (e0030760 @ hfeg0pkn002, mc=293)

**domain**: characterization (6T SRAM DC SNM) · **session**: 简短 · **file**: `/home/e0030760/.cline/data/sessions/1793155079677_gnmu0/1793155079677_gnmu0.messages.json`（scp'd 到 .75 session workdir 后 inline 解析）

## 用户意图轮（A 档选轮分析）
- **msg idx28** ✅: 「仿真SRAM 蝴蝶曲线试一下」—— **纯需求轮**（规则②✓：用户只表达目标，未给根因/修复），A 档 faithful 原文。这是 SRAM 6T 单元直流静态噪声裕度（SNM）表征：对交叉耦合反相器对画"蝴蝶曲线"（两条 VTC 交叉形成的最大内接正方形边长 = SNM）。

## 助手工具链（msg 28 → 完）
助手手写两个 HSPICE deck + 一个 Python 后处理：
- `vtc_a.sp` — 把 Q 当输入扫（.DC Vs 0 vdd step），Mp/Mn 内联成反相器（Mp qb q vdd vdd pmos, Mn qb q 0 0 nmos），.PRINT DC V(qb) V(q) → 得 VTC_A = (V(Q), V(QB))。
- `vtc_b.sp` — 把 QB 当输入扫（.DC Vs 0 vdd step），反相器输入接 qb（Mp q qb vdd vdd pmos, Mn q qb 0 0 nmos），.PRINT DC V(q) V(qb) → 得 VTC_B = (V(Q), V(QB))，是 VTC_A 关于 y=x 的镜像。两条曲线交叉成蝴蝶形。
- `plot_butterfly.py` — 解析 .lis 的 DC 打印表（**SI 后缀感知 parser**：m/u/n/p/f，bare float() 会把 `1000.0000m` 解析成 1000.0 而非 1.0），在 45° 旋转坐标系 (u=(x+y)/√2, w=(y−x)/√2) 找两条曲线之间的**最大内接正方形边长** = SNM ≈ 0.306V。

## 金标准（用户实际接受）
助手产出的 vtc_a.sp/vtc_b.sp + plot_butterfly.py，SNM≈0.306V。真实 trace 用 foundry PDK（本环境不可移植）。

## 合成决策
- **档位**：A 档 faithful（用户原文「仿真SRAM 蝴蝶曲线试一下」直接作 prompt 开头）。
- **便携化**：foundry BSIM PDK 不可移植 .75 → 取可复现子技能 = 两条 VTC 的 HSPICE .dc 仿真 + .lis SI 后缀解析 + 蝴蝶曲线交叉 + 最大内接正方形 SNM，便携化为 level-1 Shichman-Hodges MOS（corner.lib `.LIB tt` 块，`.lib 'corner.lib' tt` 加载）+ 内联 Mp/Mn（非 `.SUBCKT PARAMS:`，.75 HSPICE 对带 PARAMS: 子电路报 nodes mismatch/model not found）。
- **交付**：submit.zip 含 `butterfly_gen.py` + `butterfly_data_A.csv`（可见 A 上跑出的 VTC 数据）。
- **A 可见**：vdd=1.0, wn=0.5u, wp=1u, ln=lp=0.13u, n_points=101, step=0.01；corner vto=0.35/kp_n=250e-6/kp_p=90e-6/lambda=0.05 → SNM=0.3062, 101 pts。
- **B 隐藏**：vdd=1.2, wn=0.8u, wp=1.2u, ln=lp=0.15u, n_points=81, step=0.015；corner vto=0.40/kp_n=200e-6/kp_p=80e-6/lambda=0.04 → SNM=0.3681, 81 pts。跨输入 diff 20.2%（守卫击破 hardcode-A）。
- **check**：18 条 a–r 独立断言（含 (j) 轴镜像对称陷阱、(m) 跨输入守卫、(q) SI 后缀解析 sanity、(l) B SNM 匹配 ref、(e) hspice_ran=true）；subprocess 真跑 HSPICE on B，独立从 butterfly_data_B.csv 计算 SNM 比对 ref。
- **自验（.75 HSPICE V-2023.12-SP1-1）**：ref **PASS 18/18**；5 negatives 全 FAIL 且 fail_set 两两 distinct（NEG_RC=0）：
  - naive_empty → (e)(f)(g)(h)(i)(j)(k)(l)(r)
  - naive_print_expected → (e)(l)(m)
  - naive_hardcode_a → (l)(m)
  - naive_unmirrored_b → (j)(l)
  - naive_raw_float → (f)(g)(h)(i)(j)(k)(l)(r)
- §4.9 三假（empty/print-expected/hardcode-a）全 FAIL ✓；🧾 k_rationale=18 == k_check=18 ≥8 ✓。

## 与既有 case 的区分
- **vs SramSNM-001**（.measure 式 hold/read/write SNM 扫描）：本 case 不用 .measure，而是 .PRINT DC 表解析 + 蝴蝶曲线交叉 + 最大内接正方形。
- **vs Sram6tDcChar-001**（PVT 5 指标 DC 表征）：本 case 只聚焦 SNM 单指标 + 蝴蝶曲线交叉几何，不做 PVT 扫。

## 资产回传路径
源机 hfeg0pkn002 与本地 .36 无 NFS 互通 → session json scp 到 .75 → eda_flow read_file/run_commands inline 解析 → 本地 write 落 assets/reference。reference solver `butterfly_gen_ref.py` 在 .75 真跑 HSPICE 验证 A/B 双输入后回传 GT。check.py/negatives 经 write_file(plain content) + String.raw 模板字面量（避 backslash 转义）+ sed 修补 (l) 标签到 .75。.75 workdir `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/shardB_shardB-20261103_ShardB-20261103-run01_0`（NFS 但不挂 .36，仅 eda_flow MCP 可达）。
