# Deepread: 1794272818268_ckhfh — SPF 寄生电容提取 (characterization, B-synthesized L1 候选)

## trace_source
- user: haoliu  host: hfeg0pkn004 (10.129.2.14)
- session: 1794272818268_ckhfh.messages.json (445KB, 80 msgs, mtime 2026-11-10 09:37)
- match_count: 0 (fresh-window, 不在 summary.tsv 快照内)
- domain: characterization (DSPF/SPF 寄生参数提取)

## 用户原话 (U#0, 唯一用户文本轮 — A-faithful 合规：提需求未给根因/修复)
```
1. 请在'/home/haoliu/Desktop/AI_Project/01_spf'目录下进行工作；
2. 请分析电路的后仿网表'/rundata/m2701/V0_DDR4/simdir/finesim/workdir/haoliu/simulation/00_spfDqIb_2stg_DfeM6V2IP.spf.TYP_98_RCC'，理清电路的架构；
3. 使用skill，帮助我提取网表中的寄生电容参数；
4. 提取完成后，请检查电容值是否准确。
```
注：用户路径多了 `00_` 前缀，实际文件在 `00_spf/` 子目录：`/rundata/.../00_spf/DqIb_2stg_DfeM6V2IP.spf.TYP_98_RCC` (1.70MB, 27971 行)。

## assistant 工具链 (TOOLS: list_allowed_files×7, read_files×12, editor×12, run_approved_command×7, skills×1, search_codebase×1)
1. policy engine 检查 + 工作目录探查
2. read_files 读取 .spf 网表（DSPF 1.3 格式，StarRC 生成，设计 DqIb_2stg_DfeM6V2IP = DDR4 DQ 输入缓冲器两级+DFE, corner TYP_98）
3. 探测格式：**无 `*|CAP`/`*|RES` 区块头**，电容/电阻内联在 `*|I` 行后；含对地电容 `Cg1_*`(node2=0)、耦合电容 `C160_*`(node2≠0)、电阻 `R1_*`、子节点 `vcc!:63`、MOS 器件行 `pulvt_ckt/nulvt_ckt/prvt_ckt`
4. 加载 `eda_agent` skill → 编写 Python DSPF 解析脚本（editor 写入，383 行）
5. run_approved_command 执行 → 一次成功
6. 编写独立交叉验证脚本（纯正则，无状态机）→ 修正 vcc! 引脚匹配后 PASS

## 金标准 (assistant A#55-A#79)
**主解析器**（383 行 Python，状态机解析 DSPF）：
- 架构分析：设计信息/端口/实例层级树/器件统计
- 电容提取：对地电容(node2=0) + 耦合电容(node2≠0) → CSV
- 精度校验 V1-V5：
  - V1 逐网核对：提取值 vs `*|NET` 声明值
  - V2 全局电荷守恒：ratio = sum(Cg+Cc) / declared
  - V3 原始行抽查复验
  - V4 无负值
  - V5 无重名

**结果**：68 网络、2054 对地电容(45.59 fF)、12253 耦合电容(60.09 fF)、12270 电阻
- V1: 68/68 通过（最差相对误差 4.5e-06）
- V2: ratio = 1.0000007
- vcc! 网：3.659866e-14 vs 声明 3.659870e-14，ratio 0.9999988

**独立交叉验证**（纯正则逐行，无状态机/无网表上下文）：
- 电容总数 14307、对地 2054/45.59fF、电阻 12270 — 与主解析器完全一致
- vcc! 块内全部电容（含实例引脚耦合）= 声明值（ratio 0.9999988）

## case 构想 (B-synthesized L1, 下轮交付)
- **资产 A**：合成 DSPF 1.3 格式 .spf（模拟 DqIb 两级结构：~15-30 网络，对地电容 Cg1_*、耦合电容 C160_*、电阻 R1_*、子节点 net:NN、MOS 器件行；无 `*|CAP`/`*|RES` 区块头，内联格式；`*|NET` 声明值块）
- **隐藏 B1/B2**：不同网络数/电容数/量级，反硬编码
- **reference**：泛化 DSPF 解析器（解析对地+耦合电容、`*|NET` 声明值、V1 逐网核对、V2 电荷守恒）
- **check.py k≥8 断言**：zip 内脚本可运行 / B1 对地电容数 / B1 耦合电容数 / B1 总对地 fF / B1 总耦合 fF / V1 逐网全通过 / V2 电荷守恒 ratio≈1 / B2 反硬编码值≠B1 / CSV 输出格式 / 网络数
- 真实 .spf 在 /rundata（仿真临时区，可能已 GC）→ 按 trace 文档化格式合成资产

## 状态
- 已 claim + **mark case**（台账 covered 228→229, characterization 35→36, claimed 1→0）
- **DEBT:1 已清偿** — 11-10 10:2x 合成交付 EDA-Eval-DesignFlow-DspfCapExtractValidate-001
- jsonl B 227→228；reference/ + assets/hidden/ 已落盘；check.py 14 断言 ref PASS + 6neg FAIL + §4.9 三假 FAIL
