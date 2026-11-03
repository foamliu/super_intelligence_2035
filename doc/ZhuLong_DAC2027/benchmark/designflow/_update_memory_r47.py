#!/usr/bin/env python3
"""Update MEMORY_DESIGNFLOW_A.md snapshot + append round-47 flow line."""
import re

PATH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_A.md"
text = open(PATH, encoding="utf-8").read()

# 1. Replace PHASE line (first bullet after DOMAINS)
new_phase = ("- **PHASE**: CalibreOpen1Fix-001 合成 ✓（轮47 新增 pnr_signoff/L2/A-faithful，"
             "Calibre OPEN1 错误诊断 + LAYOUT PRECISION 注入修复）。mc≥300 shard-A-tool 池枯竭，"
             "续挖 mc≥100 calibre 域台账已 claimed 的 xchvr(ellawu/mc122/calibre:2451+gds:945) → "
             "scp 1.39MB messages.json(75 msgs) 深读 → 轮[0]=干净提需求轮（逐字报错串 "
            "`ERROR: Error OPEN1 ... calibreSTIcmp.rule`）→ A-faithful。金标 = trace [74] 助手诊断"
            "（根因 = rule 文件缺 LAYOUT PRECISION，脚本算了 precision=10000 却从未注入；次要 "
            "rsync 返回未检查/文件未校验）。本轮**合成新 case**。")
text = re.sub(r"- \*\*PHASE\*\*: DeadLoopScan-001.*?本轮\*\*合成新 case\*\*。", new_phase, text, count=1)

# 2. Update the trace coverage line (32/1001 -> 33/1001)
text = re.sub(r"covered=32", "covered=33", text)
text = re.sub(r"touched=52", "touched=52", text)
text = re.sub(r"32/1001 = 3\.2%", "33/1001 = 3.3%", text)
text = re.sub(r"A jsonl 33 条\)", "A jsonl 34 条)", text)
text = re.sub(r"A jsonl 32M-bM-^FM-^R33", "A jsonl 33→34", text)  # fallback if encoded

# 3. Update 断言 heartbeat line
text = re.sub(r"33 条全达标", "34 条全达标", text)
text = re.sub(r"DeadLoopScan-001 k=20 达标（本轮已验）", "CalibreOpen1Fix-001 k=14 达标（本轮已验）", text)

# 4. Update A 档试点 progress 6/10 -> 7/10
text = re.sub(r"A 档试点 6/10", "A 档试点 7/10", text)

# 5. Prepend a new round-47 flow section before the round-46 section
flow47 = """### 2026-11-03 shard A 轮 47：CalibreOpen1Fix-001 合成 ✓（pnr_signoff / L2 / A-faithful，Calibre OPEN1 诊断 + LAYOUT PRECISION 注入修复，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。trace_ledger --shard A next 给 awk（verdi|vcs|dc_shell|...|pt_shell）mc≥300 → 顶候选 wb03t(cwei/mc691) 偏模拟 parked。续挖 MEMORY todo ④ mc≥100 calibre 域：台账已 claimed 的 xchvr(ellawu/hfeg0pkn005/mc122, calibre:2451+gds:945+cadence:395) → scp 1.39MB messages.json (75 msgs) 深读。
- **深读 = Calibre DRC OPEN1 错误诊断会话**：用户 [0] 逐字报错 `ERROR: Error OPEN1 - problem with access, file type, or file open of file: calibreSTIcmp.rule.`（干净提需求轮，规则②不命中 ✓）；[51]/[59]/[65]/[67] 用户贴脚本/rule 文件提供上下文；[63]/[69]/[71]/[73] 追问（简化/dummy/flow 问题/open1 是什么）→ 规则②命中🚫不可作 A 档。选 [0] 作 A 档 task 说明。
- **金标 = trace [74] 助手诊断（用户未反驳，会话自然结尾）**：OPEN1 = Calibre 文件打开错误（不存在/权限/是目录/类型不对/软链接断链/PRECISION 不匹配）。本 case 根因 = `calibreSTIcmp.rule` 有 `LAYOUT path/system/primary` 但**无 `LAYOUT PRECISION`**；脚本 `gen_preAA_G5_CIP_final.py` 计算了 `precision="10000"`（G5_CIP 0.1nm grid）却**从未写入 rule 文件**；Calibre 默认 PRECISION 1000 与 GDS 实际 10000 不匹配 → 报 OPEN1。次要：rsync 返回值未检查、calibre 前未校验文件存在、sed 仅改 PATH/PRIMARY 未改 PRECISION。**修复 = 注入 `LAYOUT PRECISION <precision>`（从 config 读，replace 若已存在 / insert 于 LAYOUT system 后）+ rsync 返回检查 + 文件校验**。
- **资产**：A = prompt.txt（[0] 逐字原文 89B）+ task_brief.md（3 行接口：交付 fix.py+diagnose.json）+ gen_preAA_G5_CIP_final_A.py（buggy 脚本 fixture，忠实复刻 trace 漏洞：无 PRECISION 注入 / 无 rsync 检查 / 无文件校验）+ calibreSTIcmp_A.rule（LAYOUT path LP4TOP.gds / system gdsii / primary LP4TOP，**无 PRECISION** + DRC CHECK 块 + INCLUDE）+ config_A.txt（process=cxmtG5_CIP, precision=10000, projName=decqa, libName=ella_train, topCell=AF_FsMrgNEnCount）。hidden B = calibreSTIcmp_B.rule（**不同层** LAYOUT path M2CORE.gds / primary M2CORE，无 PRECISION，不同 DRC 块 METAL2_ENC_VIA/METAL2_MIN_AREA）+ config_B.txt（**不同 process** cxmt10G7, **precision=1000**（≠A 的 10000，验泛化）, projName=iejoad, libName=vex_qa, topCell=DRAMCoreTop）+ gen_preAA_10G7_iejoad_B.py（不同 process/path）+ hidden_manifest.json。B 测试泛化：候选须从 config 读 precision（A=10000, B=1000），不得硬编码 10000。
- **交付件 = fix.py + diagnose.json**（python stdlib；CLI `python3 fix.py <rule_file> <config_file> <output_rule_file>`；从 config 读 precision，注入 LAYOUT PRECISION：已存在则 replace，缺失则 insert 于 `LAYOUT system` 行后；保留其余 LAYOUT 语句；exit 0；diagnose.json 含 root_cause/issues/fix_summary 三键）。
- **check.py 14 条断言(a)-(n)**：(a)zip恰含 fix.py+diagnose.json (b)py_compile (c)A 运行 exit0+输出 rule 含 LAYOUT PRECISION 10000 (d)A 保留 LAYOUT path LP4TOP.gds/system gdsii/primary LP4TOP (e)B 运行 exit0+输出 rule 含 LAYOUT PRECISION 1000（泛化） (f)B 保留 B 的 LAYOUT path M2CORE.gds/system/primary M2CORE (g)A 输出恰一条 PRECISION 行（无重复） (h)B 输出恰一条 PRECISION 行 (i)diagnose.json 合法 JSON+含 root_cause/issues/fix_summary (j)root_cause 提及 PRECISION (k)issues 为 list 且长度≥2 (l)fix_summary 提及 PRECISION 注入语义 (m)防硬编码:源码不含 A 专属字面量(cxmtG5_CIP/decqa/LP4TOP/ella_train/AF_FsMrgNEnCount)+不含 B 专属字面量(cxmt10G7/iejoad/M2CORE/vex_qa/DRAMCoreTop) (n)防硬编码:源码不含精度字面量 10000/1000（precision 必须从 config 读取，否则 B 侧 1000 会错）。**k_rationale=14=k_check=14≥8 GATE PASS ✓**。
- **自验**：gold_fix.py 在 A 上 → 输出含 `LAYOUT PRECISION 10000` + 保留 LP4TOP.gds/system/primary；在 B 上 → 输出含 `LAYOUT PRECISION 1000` + 保留 M2CORE.gds/system/primary；恰一条 PRECISION 行（无重复插入）✓。reference_submit.zip → check() **PASS 14/14**。4 negative（fake_empty→(a)zip 缺 diagnose.json / fake_print_expected→(c)无输出 rule / fake_core_deleted→(c)仅 copy 无 PRECISION 注入 / naive_stub→(n)硬编码 10000）**全 FAIL**，NEG_SELFTEST ALL-FAIL。§4.9 (a)空壳(b)print期望(c)删核心 三假覆盖。
- **难度评估**：L2（subprocess 在 A+B fixture rule 上跑 fix.py，§4.2；Calibre 二进制不参与=静态 rule 文本处理→结构判分）。A-faithful 真实难度 = 模型须从 verbatim 一行报错串（`ERROR: Error OPEN1 ... calibreSTIcmp.rule.`）推断：①读懂 buggy 脚本与 rule 文件上下文；②定位根因 = 缺 LAYOUT PRECISION（不是 rsync/权限/断链，是 PRECISION 不匹配）；③写 fix.py 从 config 读 precision 注入（replace/insert 两种分支）；④泛化到隐藏 B（不同 process/precision=1000/层名，不得硬编码 10000）；⑤diagnose.json 三键诊断。预期 ≤10% pass（A-档目标）。
- **防泄题**：资产仅 prompt+brief+buggy 脚本+A rule+A config（0 判分器/答案/隐藏/B）；hidden B 不进 SUT 沙箱；判分独立 /tmp，check.py+hidden 从 reference/ 复制；anti-hardcode (m)(n) 双向守卫防 fake_print_expected + 防精度硬编码。
- 落库：追加 EDA-Eval-DesignFlow_A.jsonl 第 34 行（task_id=CalibreOpen1Fix-001, domain=pnr_signoff, track=faithful, level=L2）。台账 mark case → covered 32→33, pnr_signoff 10→11。assets(prompt+brief+buggy 脚本+A rule+A config + hidden/B rule+config+buggy+manifest) + reference(check.py+gold_fix.py+reference_submit.zip+negative/4+negative_selftest.py+hidden/B) 落 EDA-Flow-Bench 仓。
- ⬜ 下轮：①CalibreOpen1Fix-001 cline 实跑（判分纯本地，验通过率）；②DeadLoopScan-001 cline 实跑；③PDKRunsetExplore-001 cline 实跑；④STAFlow ④naming 决策；⑤TLEFRules ④(w) guard；⑥SPFCoupling-001 cline 实跑；⑦mc≥100 calibre 域续挖（vajed/a15un fresh，需深读判料）；⑧DRCDeckOpt ③泛化缺口修复。

"""
# insert flow47 before the round-46 header
text = re.sub(r"(### 2026-11-03 shard A 轮 46：)", flow47 + r"\1", text, count=1)

open(PATH, "w", encoding="utf-8").write(text)
print("[mem] MEMORY_DESIGNFLOW_A.md updated; size =", len(text), "bytes")
