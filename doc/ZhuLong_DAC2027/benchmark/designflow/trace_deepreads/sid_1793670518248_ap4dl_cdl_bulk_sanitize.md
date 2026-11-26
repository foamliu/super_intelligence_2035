# Deepread: ap4dl — CDL 3-port MOS bulk sanitization for HSPICE

- **trace**: `1793670518248_ap4dl.messages.archive.json` (e0029495@hfeg0pkn002, 10.129.2.11)
- **size**: 4.2 MB, 750 msgs, 13 user turns, hspice=188, mc=1, spice_ratio=0.629
- **domain**: spice_sim (standard-cell functional cross-validation, CDL/HSPICE vs Verilog/VCS vs Liberty)
- **ledger**: claimed 2026-11-06 (shard B, spice_sim)

## Task (USER#1, MSG[233] — clean A-档 need turn)

verbatim:「我在/home/e0029495/xval_tool/目录下更新了个test文件夹，里面包含cdl、lib、verilog，请测试并在最后给出测试结果及测试的全部用时，测试可以使用LSF服务器lacaa_sram队列64个服务器，脚本的lsf应该做成api可配置模式」

- 提出需求轮：给 folder (cdl/lib/verilog) + 目标 (测试 + 结果 + 用时) + 约束 (LSF lacaa_sram 64 服务器, lsf api 可配置)。无根因/无修复方案。
- 注：USER#0 (MSG[0]) 是用户贴的方法论长方案（三方对比 CSV schema），属"给出方案"轮，**不可**作 A-档任务说明；但其催生的 Phase-1 demo 工具链是金标准基础。

## Assistant tool chain (两阶段)

### Phase 1 (MSG[0]–[232]): 构建 xval_tool + demo 库验证
- 探测环境: HSPICE V-2023.12 + VCS R-2020.12 可用 (run_approved_command python-runner)
- 构建 12 模块: liberty_parser / pinmap / vectors / gen_spice / gen_verilog / runner / parse_spice / parse_verilog / liberty_eval / compare + 6 CLI 脚本 + config.yaml
- demo 库 (6 cell: INVX1/NAND2X1/NOR2X1/OAI21X1/TBUFX1/DFFQX1) + demo_models.sp (LEVEL=1 nch/pch, VTO=0.2/-0.2, VDD=0.75)
- 端到端: gen_pins→gen_decks→run_batch→parse_to_csv→liberty_eval→compare → **96/96 PASS** (32 vec × 3 比较)
- 负向测试: 注入 NAND2 bug (改 ~(A&B)→(A&B)) → 工具抓到 4 hard mismatch, 全在 NAND2X1 ✓
- 关键格式: HSPICE .mt0 折行 (measure 名字行 + 数值行, >4 measure 时折多行); SI 后缀解析 (m=1e-3, u=1e-6...)

### Phase 2 (MSG[233]–[523]): test1 真实库测试 + LSF
- test1 = DBCP51H180L6W25T5 SRAM 库 (BASE/MB × LVT/SVT/ULVT, 3 PVT corner), 456 cell
- Liberty 单文件 125–300MB → 写 liberty_extract.py 流式抽取目标 cell
- Verilog 单文件 686KB 456-module → 抽取 per-cell module; BASE 有功能体 (118 always), MB 纯时序
- LSF 10.1 可用, lacaa_sram queue (MAX 2400, JL/H 96) → 写 run_batch_lsf (bsub 全参数 config 可配置: queue/project/ncores/resource/extra_args/max_concurrent=64)
- gen_vectors.py: 从 Liberty ff/function 语义自动生成向量 (comb 穷举, seq 复位/释放/沿/D 组合, tri Z 覆盖)
- **工具故障**: editor 的 `path` 参数被框架系统性丢弃 → 无法写文件; SandBox run_code 未启动; run_commands 被策略禁用
- **绕过**: 用户手动 heredoc 粘贴 (assistant 输出带 `|` 标记保护缩进, 用户 sed 还原)
- 修复 3 bug: (1) vlog LSF 双层 sh -c 引号冲突 (2) gen_vectors 粘贴截断丢时钟沿 (3) parse_to_csv/liberty_eval 旧版不认 `vectors: auto`

### **核心发现 (MSG[476]–[521]): 3-port MOS bulk 缺失**
- test1 真实 CDL 用 **3 端口 MOS** (d g s, 无 bulk):
  ```
  .SUBCKT INVD1DBCP51H180L6W25T5SVT I VDD VSS ZN
  MMMM1 ZN I VDD psvt_dbc l=6.0n w=0.025u m=1   ← PMOS 3-port
  MMMM14 ZN I VSS nsvt_dbc l=6.0n w=0.025u m=1  ← NMOS 3-port
  .ENDS
  ```
- HSPICE 对省略 bulk 的 MOS 默认衬底接 node 0 (地) → **PMOS bulk 错设为 VSS** → 上拉失效, 输出停 0.4727V (应 0.75V)
- 136 个 X_RELATED (spice=X, vlog/liberty 正常) 全是 SPICE 拉不到 VDD
- **修复 (sanitize_cdl)**: 检测 3-port M 行 (model 名在第 4 token), 按模型名首字母推断衬底 (n→VSS, p→VDD), 在 model 前插入 bulk 端子
- demo 库正常因 CDL 用显式 4-port (`MP1 Y A VPWR VPWR pch`)
- 修复后: 19 HSPICE 作业全 rc=0, INVD1 v_zn_0=0.75 ✓, **x_related 136→6, hard=0, fail_cells=0**

### **最终金标准 (MSG[523], 19-cell test1)**
| 指标 | 值 |
|---|---|
| total_vectors | 152 |
| match | 1058 |
| hard_mismatch | 0 |
| z_related | 0 |
| missing | 0 |
| fail_cells | 0 |
| x_related | 6 (spice measure 边界 X, vlog/liberty 一致) |

19 cell: INVD1/BUFFD1/ND2D1/NR2D1/AN2D1/OR2D1/XOR2D1/XNR2D1/AOI21D1/OAI21D1/MUX2D1/HA1D1/DFQD1/SDFQD1/SDFRPQD1/SDFSNQD1/LHQD1/TIEH/TIEL (移除 ICGD1, Liberty 无 ff/latch)
用时: run_all.log 有 6 步分解 (gen_pins/gen_vectors/gen_decks/run_batch LSF/parse_to_csv/liberty_eval/compare)

### **二次修复 (MSG[507]–[517]): LSF 环境污染**
- 衬底修复后重跑 LSF spice 全 EXIT: `GLIBC_2.18 not found` — run_approved_command 继承代理环境 LD_LIBRARY_PATH 指向老 agent lib, 经 bsub 传到 LSF 节点致 glibc 冲突
- 修复: LSF runner 提交时剥离 LD_LIBRARY_PATH/LD_PRELOAD (干净环境)
- 修复后 19 HSPICE 全 rc=0

## 可移植子技能 (本案提取)

**CDL 3-port MOS bulk 显式化**: 解析 CDL → 检测 3-port M 行 (d g s model) → 按模型名推断衬底 (n*→ground rail, p*→positive rail, PG 名从 .SUBCKT header) → 在 model 前插入 bulk 端子 → 输出 sanitized CDL。HSPICE 在 sanitized CDL 上跑出正确轨值 (inv out high≈VDD, low≈0)。

- L2: check.py 在 .75 真跑 HSPICE 验证 sanitized CDL 的 inv 输出
- 防硬编码: hidden B 用不同 PG 名 (VPWR/VGND) + 不同模型名 (nmos_x/pmos_x) → 强制从 header 解析 PG + 从模型名推断极性
- 真实: test1 INVD1 CDL verbatim (3-port, nsvt_dbc/psvt_dbc)

## 资产 fetch
- INVD1 3-port CDL: 从 trace MSG[497] verbatim 提取
- demo models: 从 trace MSG[76] (LEVEL=1 nch/pch) 改用 nsvt_dbc/psvt_dbc 名
- hidden B: 同结构不同 cell (INV + NOR2) + 不同 PG (VPWR/VGND) + 不同模型名 (nmos_x/pmos_x) + 不同 VTO
