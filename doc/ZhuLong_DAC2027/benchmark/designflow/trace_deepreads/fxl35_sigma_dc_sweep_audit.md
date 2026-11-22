# Deepread: fxl35 — HSPICE .DC sigma_adam 扫描波形不变诊断

- **slug**: 1793250261601_fxl35
- **user**: cong3li @ hfeg0plg72 (10.129.8.110)
- **mc**: 5, **domain**: spice_sim, **scan**: summary_20261121_151844.tsv
- **keywords**: hspice:35;transistor:13;netlist:8;aether:3;pdk:2;schematic:1;pyaether:1
- **file**: 7 msgs / 42KB / Oct 29 13:08
- **fresh**: r1024 cross-diff 4-shard union ledger → fresh (r1023 误判"hspice≤9 noise"未 peek，实际 hspice:35 最强 B-spice 信号)

## 真实意图（逐 msg）

- **U0** [msg 0]: 粘贴完整 HSPICE 网表 + 问「为什么这个用hspice仿真，波形结果没有变」。网表关键：
  - `.DC sigma_adam 0 5 0.1`（扫 sigma_adam 0→5 步 0.1）
  - `XMMN1 net666 WL vad2! ntk_wl w=28e-9 l=40e-9 nf=1 sigmaflag_array=sigma_adam`（instance 上 sigmaflag_array=sigma_adam）
  - `.lib '.../model.sp' ss_array` + `ss`（HKMG V3 模型）
  - `.probe I(*)`，`.print DC I(vvcell)` 被注释
  - 读电流路径：vvcell(0.8V) → R666(34.48k) → net666 → NMOS drain；NMOS gate WL=2.2V, source vad2=0.4V
- **A1** [msg 1]: tool_use list_allowed_files + search_codebase（工作目录空，/proj /apps 外部路径不可访问）
- **A4** [msg 4]: 5 点诊断：
  1. `sigmaflag_array` 是统计/失配标志位，普通 .DC 扫描不注入 σ 扰动 → I(vvcell) 不变（最可能）
  2. 模型参数预解析，DC 扫描期间不逐点重算 model 内部公式
  3. σ 对电流影响太小，波形默认坐标看不出变
  4. `.print` 被注释，可能看错波形文件
  5. `sigmaflag_array` 可能是整型开关（0/1），0.1 步进大多落开/关两态
  - 建议：单点对比 σ=0 vs σ=5 确认；开 .print DC 看 .lis 数值；改用 .mc 或 .alter
- **U5** [msg 5]: 「试过了，结果不变」（确认 σ=0 vs σ=5 电流一样）
- **A6** [msg 6]: 确认 sigma_adam 在 DC 求解路径不参与模型计算，是统计/失配机制，需蒙特卡洛(.mc)或显式统计模式；给方案 A(.mc) + 方案 B(.alter 逐段)

## 合成决策

- **取**: msg 0-6 整体（debug-Q&A → 诊断工具 produce）
- **reframe**: `sigma_dc_audit.py --netlist <deck> --report <out.json>`（L1 纯 Python 静态分析）
  - 解析 HSPICE 网表 → 提取 `.DC` 扫描变量 / `.param` / instance `sigmaflag_*=` / `.mc`/`.monte`/`.alter`/`.measure` / `.lib`
  - 分类每个 .DC 扫描变量：electrical | statistical
    - statistical 启发式：变量名匹配 `sigma*`/`*_mis`/`*sigma*`/`sigmaflag*`；或变量作为 instance `sigmaflag_*=` 的值出现
  - 检测统计构造存在性（has_mc/has_monte/has_alter/has_measure）
  - 生成 recommendations（statistical 变量在 .DC 且无 MC → 建议 .mc；有 .alter → 建议 .alter 逐段）
  - 生成 corrected_skeleton（.mc 块模板 / .alter 块模板）
  - JSON report: {dc_sweeps, params, statistical_params, instance_sigmaflags, statistical_constructs, recommendations, corrected_skeleton}
- **便携可判分**: 纯 Python 静态解析，无需 HSPICE 二进制
- **核心齿**: statistical 分类（反 naive all-electrical）+ sigmaflag 映射（反 naive 仅变量名）+ 构造检测（反 naive all-false）+ 混合分类（反 naive all-statistical）+ anti-hardcode

## A / hidden B 设计

- **A** (dir_A): 忠实重建 fxl35 网表 — `.DC sigma_adam 0 5 0.1`，`sigmaflag_array=sigma_adam`，无 .mc/.alter
- **hidden B** (hidden/dir_B): 五重 anti-hardcode — `.DC sigma_emi 0 3 0.2` + `.DC vdd 0 0.9 0.1`（混合 statistical+electrical），`sigmaflag_cell=sigma_emi`，有 .alter(2) 无 .mc，参数名/值/sigmaflag 名/构造全异

## distinct

- vs SanadjRblDeckSweep-001 (RBL deck 生成，非 statistical 分类审计)
- vs SpLibIncTokenRewrite-001 (.lib token 替换，非 DC-sweep 审计)
- vs FinesimTbCodebaseAuditProduce-001 (Python 代码库审计，非网表静态分析)
- vs PigzResolverProduce-001 (可执行文件解析器，非网表分析)
- vs QuadClkSkewMeasDeckGen-001 (.measure deck 生成，非审计)
- 本 case = HSPICE 网表 statistical-param DC-sweep 静态审计器，无重复 ✓
