# 深读笔记：1789545344007_xchvr (ellawu / hfeg0pkn005 / mc122 / pnr_signoff)

## trace 概览
- 75 msgs，1.39MB messages.json，scp 自 10.129.2.14:/home/ellawu/.cline/data/sessions/1789545344007_xchvr/
- 关键词：calibre:2451; gds:945; cadence:395; aether:139; gdsii:31; virtuoso:8 — **Calibre DRC 主导**（pnr_signoff / physical verify 域）
- 工具分布：2246 calibre / 8 virtuoso / 7 schematic / 6 pyAether / 2 dbGet

## 用户轮逐条（A 档选料判料）
| # | 用户输入（原文/还原） | 类型 | 规则②命中？ |
|---|---|---|---|
| [0] | `ERROR: Error OPEN1 - problem with access, file type, or file open of file: calibreSTIcmp.rule.` | **提需求**（报错求诊断） | ✗ 干净提需求轮 ✓ |
| [51] | 贴完整 gen_preAA_G5_CIP_final.py 脚本 | 提供上下文 | — |
| [59] | 贴 workDir 构造代码片段 | 提供上下文 | — |
| [63] | `jiandianyidande`（简单一点的） | 追问 | — |
| [65] | 贴长 Calibre DRC implant fill rule 文件 | 提供上下文 | — |
| [67] | 贴完整 IMCleFillImplantDRC.py auto_implant 脚本 | 提供上下文 | — |
| [69] | `ruguobucunzai xiayigeminglingyebushengchengdummy zenmeban`（如果不存在下一条命令也不生成 dummy 怎么办） | 追问流程 | — |
| [71] | `flow youshenmewentima`（flow 有什么问题吗） | 追问 | — |
| [73] | `open1 shishenme`（open1 是什么） | 追问概念 | — |

**选 [0] 作 A 档 task 说明**：唯一干净"提需求"轮——逐字报错串，无根因无修复方案（规则②不命中 ✓）。

## 金标 = trace 末尾助手 [74]（用户未反驳，会话自然结尾）
助手最终结论（[74] + [58] + [50] 综合诊断）：
- **OPEN1 = Calibre 文件打开错误**：文件不存在 / 权限 / 是目录 / 类型不对 / 软链接断链 / **PRECISION 不匹配**。
- **本 case 根因 = 缺 `LAYOUT PRECISION` 语句**：`calibreSTIcmp.rule` 有 `LAYOUT path / system / primary` 但**无 `LAYOUT PRECISION`**；脚本 `gen_preAA_G5_CIP_final.py` 计算了 `precision="10000"`（G5_CIP 0.1nm grid）却**从未写入 rule 文件**；Calibre 默认 PRECISION 1000 与 GDS 实际 10000 不匹配 → 报 OPEN1。
- 次要问题：rsync 返回值未检查、calibre 前未校验文件存在、sed 仅改 PATH/PRIMARY 未改 PRECISION。
- **修复 = 注入 `LAYOUT PRECISION <precision>`**（从 config 读 precision，replace 若已存在 / insert 于 `LAYOUT system` 后）+ rsync 返回检查 + 文件存在校验。

## case 合成方案（A-faithful / L2 / pnr_signoff）
- **task_id**：EDA-Eval-DesignFlow-CalibreOpen1Fix-001
- **prompt**：[0] 逐字原文（仅错误串）
- **交付件**：outputs/submit.zip 含 `fix.py`（CLI `python3 fix.py <rule_file> <config_file> <output_rule>`，从 config 读 precision 注入 LAYOUT PRECISION）+ `diagnose.json`（根因诊断 JSON）
- **A 资产**：prompt.txt + task_brief.md（3 行接口）+ gen_preAA_G5_CIP_final_A.py（buggy 脚本上下文，忠实复刻 trace 漏洞：无 PRECISION 注入 / 无 rsync 检查 / 无文件校验）+ calibreSTIcmp_A.rule（LAYOUT path LP4TOP.gds / system / primary，**无 PRECISION**）+ config_A.txt（process=cxmtG5_CIP, precision=10000, projName=decqa, libName=ella_train, topCell=AF_FsMrgNEnCount）
- **隐藏 B**：calibreSTIcmp_B.rule（不同 LAYOUT path M2CORE.gds / primary M2CORE，无 PRECISION）+ config_B.txt（process=cxmt10G7, **precision=1000**, projName=iejoad, libName=vex_qa, topCell=DRAMCoreTop）+ gen_preAA_..._B.py（不同 process/path）+ manifest。B 测试泛化：候选须从 config 读 precision（A=10000, B=1000），不得硬编码 10000。
- **check.py k≥8 条断言**：zip 内容 / py_compile / A 运行 exit0+输出含 LAYOUT PRECISION 10000 / A 保留 LAYOUT path/system/primary / B 运行 exit0+输出含 LAYOUT PRECISION 1000 / B 保留 B 的 LAYOUT path/system/primary / 输出恰一条 PRECISION 行（无重复）/ diagnose.json 合法 JSON 含 root_cause/issues/fix_summary / root_cause 含 PRECISION / fix_summary 含注入语义 / 防硬编码（源码不含 A+B 专属字面量 cxmtG5_CIP/decqa/LP4TOP/ella_train/10000/M2CORE/iejoad/DRAMCoreTop/1000-as-PRECISION-literal）。
- **真跑候选**：subprocess 在 A+B fixture rule 上跑 fix.py，断言输出 rule 结构（§4.2 L2）。
- **防泄题**：资产仅 prompt+brief+buggy 脚本+A rule+A config（0 判分器/答案/隐藏/B）；hidden B 不进 SUT 沙箱；判分独立 /tmp，check.py+hidden 从 reference/ 复制。
