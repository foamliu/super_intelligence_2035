# 深读笔记：314mt — CMOS 反相器 PVT 优化（sophiaw / hfeg0plg49 / glm-5.2）

**trace**: `1787903140887_314mt` · user `sophiaw` · host `hfeg0plg49` · mc=378 · 86 msgs / 559KB · 2026-08-28~09-01
**agent**: cline lead, model glm-5.2, cwd `/proj/train/AI_Virtuoso/workdir/sophiaw`
**user 唯一输入**（msg[0]，plan 模式）: `<user_input mode="plan">启动业务场景: 模拟电路优化·二次执行</user_input>` — 业务场景自动触发，无后续用户轮（其余 user msg 全空 = 工具批准/结果）。

## 真实任务流（AnasimPro SPICE 流）
"二次执行"= 对已有 `testbench_inv/`（首次执行 baseline_v1）重跑优化。AnasimPro CLI 链：`analyze-spice` → `generate-alters` → `build-runsim` → `submit-jobs`(LSF) → `monitor-jobs` → `collect-meas` → `benchmark`。

### 首次执行（baseline_v1）问题
- CMOS 反相器 testbench：PMOS w=2u / NMOS w=1u，tran + DC，PVT = 5 MOS corner × 3 temp × 4 cload = 65 alters
- **所有 65 角点瞬态测量全 FAILED**（tpdf/tpdr/tpd/tfall/trise_meas），DC 正常（voh=1.8, vol≈0）
- 根因（agent 推断）：HSPICE Level-1 用默认 `tox=100nm` 计算 `cox`，致有效 KP 仅指定值 ~1/7（20.7µA/V² vs 150µA/V²）→ 晶体管驱动不足 → 输出不翻转
- LSF job 一次失败：runsim.sh 的 cwd 是 `runsim/` 而非 `testbench_inv/`，相对路径找不到 inv_tb.sp

### 二次执行（optimized_v2）
修模型 + 加大 sizing + 改负载扫描 + post=1：
- model.sp 显式 `tox=13.8n` + u0 → cox=2.50mF/m²，KP 计算正确
- NMOS 1u→4u，PMOS 2u→10u（P:N=2.5:1 平衡 rise/fall）
- cload 扫描 1p/5p/10p/50p → 100f/1p/5p/10p（移除 50pF，单反相器不现实）
- `.option post=2`→`post=1`（生成可解析测量文件）
- 最坏角（FS/125°C/10p）：tpdf=3.04ns（was 65.98ns/failed）、tpdr=6.15ns（was failed）、tpd=4.59ns、tfall=6.95ns、trise_meas=failed（仅绝对最坏角）、voh=1.8、vol≈0、pavg=-559.5µA、pwr=-1.007mW
- 生成 `benchmark_report.xlsx`（baseline_v1 vs optimized_v2，3 domains）

### agent 调试子流（可复现性参考）
- 诊断 deck（diag_test.sp / diag_test2.sp / diag_inv.sp）：隔离 sizing/model/load 单变量，确认简单 case（TT/5p）tpdf=3.47ns/tpdr=4.72ns PASS → 证明优化对简单角有效，问题在 `.alter` 最坏角（50pF 过重）
- `.tr0` 二进制无法直接读 → 改 `.option post=1` + 改 `.measure` 触发
- `collect-meas` 找 `.ma0/.mt0/.ms0` 但 HSPICE `.alter` 只写 `.mt64`（末角）→ 手动 `cp inv_tb.mt64 inv_tb.mt0` + 手写 `.ma0`

## 可移植性判定
- **不可移植**：CXMT foundry 模型、LSF 集群（bsub/bjobs）、AnasimPro CLI、`/proj/train/AI_Virtuoso/` 路径、真实 50pF/10p 负载与 FS/125°C 角点依赖 foundry 模型参数
- **可复现子技能**（本 case 取）：PVT 全交叉 `.alter` 表征 + `.measure tran tpdf/tpdr/tpd` + `.measure dc voh/vol` + 逐 alter `.lis` 解析 + argmax tpd 最坏角识别 + 规格合规判定
- **Level-1 KP/tox gotcha 在 .75 HSPICE V-2023.12 不复现**：.75 上 HSPICE 直接用指定 `kp=`（broken/fixed 模型 tpdf 几乎相同 3.26ns），故不作为本 case 难度内核；改取 (a) `voh=1000.0000m` 无空格 m 后缀解析陷阱（vdd=1.0 时真实出现）、(b) 最坏角=SS×vdd_min×cload_max 非标称 TT、(c) `.alter` 全交叉不可缺角

## .75 HSPICE GT（自验）
- 可见 A：corners×vdds[1.4,1.6,1.8]×cloads[1p,3p,5p]=45 alters，sizing 6u/12u → worst tpd=3.2046ns @ (ss,1.4,5p)，voh_min=1.4，vol_max=8.28e-10
- 隐藏 B：vdds[1.0,1.2,1.5]×cloads[200f,500f,1p]=45 alters，sizing 4u/8u，kp 95-145u → worst tpd=2.6087ns @ (ss,1.0,1p)，voh_min=1.0，vol_max=1.90e-9
- 最坏角对 A/B 均为 (ss, vdd_min, cload_max)，单调、无歧义
