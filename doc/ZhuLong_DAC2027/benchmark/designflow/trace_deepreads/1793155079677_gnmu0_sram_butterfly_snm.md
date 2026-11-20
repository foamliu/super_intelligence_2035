# Deepread: gnmu0 — SRAM 6T 蝴蝶曲线 / SNM 表征

- **trace**: `1793155079677_gnmu0` (e0030760 @ hfeg0pkn002, mc=102/293, hspice:381/synopsys:61/netlist:48)
- **agent**: zhulong (lead), deepseek-v4-flash, 67 msgs, 211KB messages.json
- **session path (.75)**: `/home/e0030760/.cline/data/sessions/1793155079677_gnmu0/1793155079677_gnmu0.messages.json`
- **domain**: characterization (SRAM SNM 静态噪声容限)

## 真实对话流（用户轮原话）
1. `[0]` "nihai" — 问候
2. `[2]` "please help me open the hspice software" — agent 查找 HSPICE V-2023.12-SP1-1 安装 (`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`)，跑 RC 低通 smoke test 验证环境通过
3. `[28]` **"仿真SRAM 蝴蝶曲线试一下"** — 纯需求轮（A-档合规：用户提出目标，未指出根因或修复方案）
4. `[61]` "help me open image" — 打开 butterfly.png

## 关键技术流（T28 后 agent 工作链）
- 构建 SRAM 6T 单元的两条 VTC（电压传输特性）deck：
  - `vtc_a.sp`：扫 V(Q) 0→VDD 101 点 DC sweep，测 V(QB)（反相器 A 的 VTC）
  - `vtc_b.sp`：扫 V(QB) 0→VDD 101 点 DC sweep，测 V(Q)（反相器 B 的 VTC）
- level-1 Shichman-Hodges MOS 模型（无 foundry PDK 依赖）：
  - NMOS: vto=0.35, kp=250e-6, lambda=0.05
  - PMOS: vto=-0.35, kp=90e-6, lambda=0.05（PMOS 较弱 → 反相器非对称 → 蝴蝶眼非退化）
- 6T cell sizing: Wn=0.5u Ln=0.13u, Wp=1.0u Lp=0.13u, VDD=1.0
- `.model` 内联在 deck 顶层（**.75 验证：顶层内联 .model 可用**；`.lib 'corner.lib' tt` + `.LIB tt...ENDL tt` 块也可用）
- 跑 HSPICE → 解析 `.lis` 的 `.PRINT DC` 表（3 列：sweep/V(out)/V(in)）
- **关键陷阱**：HSPICE `.lis` 用 SI 后缀（`m`/`u`/`n`），`float('540.5006u')` 崩溃 → 必须写 `hnum()` 后缀解析器（trace [52] 修复）
- 蝴蝶曲线 + SNM：在 (V(Q), V(QB)) 平面画两条 VTC，45° 旋转到 (u,w) 框架，求**最大内接正方形**边长 = SNM
  - SNM 算法（trace [48]）：对每个中心 u_c，二分搜索最大 s 使得正方形 [u_c±s/2, mid±s/2] 完全落在两曲线 wup/wlo 之间，s 上界=VDD
- **GT (.75 真跑，trace 方法)**: SNM = **0.306205 V**（约 31% VDD，合理）

## 便携化（.75 可复现子技能）
- foundry PDK 不可移植，但 trace 本就用 level-1 Shichman-Hodges（无 foundry 依赖），可直接在 .75 复现
- 子技能 = **SRAM 6T 蝴蝶曲线 VTC 对 + DC sweep + .lis SI 后缀解析 + 45° 旋转最大内接正方形 SNM**
- 候选交付：`sram_butterfly.py` (CLI `<params.json> <corner.lib> <out_dir>`) — 读 params 生成两条 VTC deck → 跑 HSPICE → 解析 .lis → 算 SNM → 写 snm_report.json + butterfly_data.csv

## A/B GT (.75 真跑)
| 输入 | VDD | Wn/Wp/L | 模型 | sweep (step, n_pts) | SNM |
|---|---|---|---|---|---|
| A | 1.0 | 0.5u/1.0u/0.13u | vto_n=0.35/kp_n=250e-6, vto_p=-0.35/kp_p=90e-6, λ=0.05 | 0→1.0 (0.01, 101) | **0.306205** |
| B | 1.5 | 0.65u/0.9u/0.15u | 同上 | 0→1.5 (0.015, 101) | **0.436626** |

跨输入守卫：SNM 差 42.6%（>5%）；snm/VDD 比 A=0.306 vs B=0.291（不同 sizing， defeats snm=k·vdd 硬编码）。

## distinct vs 已有 B case
- GmidLut-001 = Gm/Id 网格扫表（characterization，.alter 多点）
- NmosAgeChar-001 = 单点 MOSFET 参数提取
- VihTripTune-001 = VIH DC trip 调优
- TxRonSize-001 = DDR5 TX 线性区 Ron 表征
- 本条 = **SRAM 6T 蝴蝶曲线 / SNM 几何（双 VTC + 45° 旋转最大内接正方形）** — shard B 首个 SNM 几何 case，distinct 子技能

## 核心陷阱（烤进 check.py）
1. **HSPICE .lis SI 后缀** — naive_plain_float (float() 无后缀解析) → parse 崩溃 → n_A=0 → FAIL
2. **双 VTC 必须** — naive_single_vtc (只生成 vtc_a) → n_B=0 → FAIL
3. **SNM = 最大内接正方形（非 max width）** — naive_max_width (rotated max lens width=1.4) → SNM 错 → FAIL
4. **DC sweep 非 tran** — (隐含，tran 无 VTC)
5. **跨输入守卫** — naive_hardcode_a (硬编 SNM=0.306) → B (0.437) 击穿
6. **防 print-expected** — naive_print_expected (不跑 HSPICE) → 运行目录无 .lis
7. **完整 sweep 范围** — naive_partial_sweep (0→0.5, 51pts) → n_A=51 + VTC 端点错
8. **防造假** — 候选 fresh-run A 与 check.py ref 重跑一致

## 教训
- `.model` 顶层内联 + `.lib 'corner.lib' tt` + `.LIB tt...ENDL tt` 均在 .75 HSPICE V-2023.12-SP1-1 可用（与 GmidLut 的 .lib 报 not found 不同：GmidLut 用外部 corner.lib 文件 + .lib include，本处 inline 或 .lib 同目录均 OK；差异可能是 GmidLut 的 corner.lib 路径/块名问题，本轮已 .lib 同目录 corner.lib 验证通过）
- SNM 最大内接正方形：s 上界用 VDD，正方形上下边界约束在 wup/wlo 之间；naive max-lens-width (1.4) 远大于正确 SNM (0.306)
- HSPICE `.lis` `.PRINT DC` 表用 SI 后缀，解析必须 hnum()
