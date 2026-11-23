# r1055 deepread — fjy8k (chili@hfeg0pkn001, mc141, verification)

> **sister-turn 候选 deepread**。同 trace `1795078103891_fjy8k` 已有 case `EDA-Eval-DesignFlow-MsieWaveDumpDiagnoseQA-001`（覆盖 Q1-Q3：诊断脚本 produce）。本笔记聚焦 **Q4-Q6（机制解释 Q&A）**，与既有 case 结构正交，作 sister-turn 第 2 条候选。

## trace 概览
- 195 msgs, 6 个用户问题，DDR6 DScQA 数字后仿 + Cadence Xcelium AutoMSIE 多快照回归
- domain = verification（verilog:577 dominant）→ A 域
- 既有 case 覆盖 Q1-Q3（diagnose_msie_wave_dump.py produce，23 断言，hidden-B arb_package/6-partition）

## Q1-Q3（既有 case 已覆盖，仅摘要）
- Q1(msg0): 波形 `worklib.ddr6_package::timing` 显示不出值但 `$display` 有值
- Q2(msg36): timing 成员值不对
- Q3(msg48): 方案 1 改动太多，研究方案 2
- 诊断: `timing` 是 package 结构体变量（非 parameter），`(* msie_share *)` 属性 Xcelium 23.09 不识别；IEMTRG = 跨分区不共享；probe 绑到没人写的拷贝，display 读被写的拷贝
- 修复: `typedef struct {` → `typedef struct packed {`（TYPE_SpecTiming + TYPE_odt_param）→ IEMTRG=0

## Q4-Q6（sister-turn 目标 · 机制解释 Q&A）

### Q4 (msg156) — 用户原话
「目前，我要详细了解这个问题到前因后果，以及为什么把timing改为packed后就可以了；从msiebuild msierun机制开始说明，快照机制，快照之间到共享机制等等都要，请详细的解释给我，有我问的不详细的地方咱沟通一下」

**意图**：fix 已落地（IEMTRG=0），用户要的是**完整机制教程**——msiebuild/msierun 流程 → 快照机制 → 快照间共享机制 → 为什么 packed 修复有效。这是 explanation/teaching 意图，与 Q1-Q3 的 diagnose/fix 意图正交。

**agent 回答（msg175, 7698 字）核心论点链**：
1. 流程层: `run_build`→`vsim --msiebuild`→`xrun -automsie -xmsienumpartitions 10`；`--msiebuild` 注入 `-automsie`+分区数，`--msierun` 只注入 `-automsie` 复用快照
2. MSIE 动机: elaborate 内存峰值 55GB，切快照省内存+并行构建+增量复用
3. 三种快照: primary snapshot（实例子树）+ incremental snapshot（被多 primary 共用的 package/$unit）+ 装配（`-genpartition`→`Analyzing MSIE partitioning`→逐 primary elaborate→`Writing primary/incremental snapshot`）
4. package 在 MSIE 下: 独立增量快照，每个用到它的 primary 各加载一份实例（IESHPK 警告 = 同 package 在多 primary 各一份）
5. 共享机制: 工具自动尝试把跨分区引用的 package 变量统一成一份共享存储，成功无声，失败报 IEMTRG 保留多份私拷贝
6. 为什么 packed 有效: unpacked struct 23.09 不支持聚合类型跨分区共享；packed struct 语义=连续向量，落进 MSIE 成熟的「向量共享」通道（与跨分区共享宽 reg/net 同机制）→ 共享成功 → IEMTRG 消失 → probe 与写入方同一份存储

### Q5 (msg176) — 用户原话
「package 在 MSIE 下是独立的增量快照，会被每一个用到它的 primary 各加载一份实例；这句话是为什么」

**agent 回答（msg185, 3939 字）三层机制**：
1. package 编译模型: package 与 module 平级 design unit，**无实例、不在层次树**（`Verilog packages: 0 2` = 0 实例 2 单元）；MSIE 按实例树切（`-primtop`/`-incrtop` 全是 module 实例子树，无 package）→ package 不属任何子树但被多分区 import
2. 独立 elaborate 硬约束: 每个 primary 独立 elaborate（可并行/分布式），elaborate A 时 B 可能没开始，无法预先建全局共享 package → 唯一默认: 各 primary 各 elaborate 一份
3. 默认各一份存储而非共享: (a) 多数变量只被一分区访问，统一是纯开销 (b) 共享有性能税（每次读写路由 master）(c) 统一化有类型门槛（传输单元=向量）
- 精确化: 被多 primary 共用的 package（ddr6_package/arb_package）各 elaborate 进每个 primary；只被增量 top 用的（fgc_report_control）写成独立增量快照文件。两种净效果同：每个使用者一份实例

### Q6 (msg186, 重复 msg187) — 用户原话
「那么既然如此，每个分区的独立 elaborate，之间的值是相同的么，对于packed和unpacked 两种而言分别说明」

**agent 回答（msg194, 2945 字）两阶段框架**：
- **阶段一 elaborate 时刻初始值**: packed/unpacked 都相同。同一份编译产物 + 确定性字面量初始化器 + MSIE 禁止改 primary 参数 → 各实例初始值严格一致（timing 全 0，odt_timing 全 7993/5662/…）
- **阶段二 运行时刻分叉**:
  - unpacked（修复前）: 统一化失败 → 各分区独立私拷贝无同步 → 写入后只有写方变，其它永远停初值 → IEMTRG 语义=「机制上无共享，一旦写入就不一致」
  - packed（修复后）: 统一化成功 → master 存储 + 各分区镜像（二进制 `GLOBAL ACA SHARE MASTER`/`nettmp_share_master`/`cu_update_shared_reg`）→ 语义等价单快照全局唯一变量
- 数据库实证: ncsim.dsn 两实例 hash 仍在（`0x0c0da338`/`0x12cce3f0`），IESHPK 仍报 → **实例未合并，合并的是变量存储**（probe 绑的实例作镜像跟随 master）
- 时序细节: 跨分区同时刻一写一读有调度顺序问题（等同跨分区 signal 竞争），本设计配置阶段写之后读不受影响

## sister-turn 三闸门预审
- **(a') 结构正交**: 既有 case = diagnose 脚本 produce（解析 xrun.log/dsn 产出结构化 JSON 诊断）；本候选 = 机制解释 Q&A（产出解释文档，论证 msiebuild/msierun 快照模型 + package per-primary 加载 + packed/unpacked 值语义）。输出类型不同（doc vs JSON-script），问题域不同（why/机制 vs what/诊断）。✓
- **(b') ≥4 不可复用断言**: 机制论点（快照三类型 + package 编译模型无实例 + 独立 elaborate 硬约束 + packed 向量共享通道 + 两阶段值语义 + master/镜像存储）非诊断脚本能复用。✓
- **(c') 三向 token 不相交**: A-side 机制证据（xrun.log MSIE 装配段 + .dsn 两 hash + 二进制 share 字符串 + fix 验证 log）vs 既有 case A-side（IEMTRG/probe/dsn 成员计数事实）。token 不相交。✓

## 造题形态（拟）
- task_id: `EDA-Eval-DesignFlow-MsieMmchExplainQA-001`（msie mechanism explain）
- 形态: debug-Q&A / mechanism-explanation（11-15 reaudit 合法意图）
- 交付: `outputs/submit.zip` 内含 `msie_mechanism_explain.md`（机制解释文档）+ `verify_mechanism.py`（在 B-side 证据上验证关键机制断言，产出结构化 JSON）
- check(): ≥8 断言验机制论点（快照模型/package per-primary/packed 共享通道/两阶段值语义/master-镜像），anti-hardcode 用 B-side 不同 package/变量名，§4.9 三假 FAIL
- hidden-B: 类比但不同名（如 `cfg_package::settings` + TYPE_Config packed/unpacked + 不同分区数）

## DEBT
- 本轮 0 case 落库（40min 预算 + sister-turn 全套 check.py/hidden-B/negative 需完整一轮）。下轮兑现：合成 case + 自验 + §4.9。
- fjy8k ledger 已 sync（r1055 claim + mark case MsieWaveDumpDiagnoseQA-001，补 r1033-r1035 对账漏）。
