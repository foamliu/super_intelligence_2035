# deepread: gavk7 — StarRC RCMAX plaintext tree diff

- **trace**: 1792489295926_gavk7.messages.json (xxchen / hfeg0plg49 / mc97)
- **size**: 1.35MB / 235 msgs (126 user / 109 assistant)
- **domain**: pnr_signoff (StarRC signoff extraction RCMAX corner data diff)
- **keywords**: synopsys:597; netlist:48; primetime:21; techfile:8; gdsii:6; pyaether:3; calibre:2

## 用户轮（genuine user text，9 条）

| msg | ts | 用户原话 | 性质 |
|---|---|---|---|
| 0 | 1792491913206 | Context summary: 三方对比与报告更新…（continuation，含根因分析） | ② 命中（已给结论） |
| **23** | 1792492019194 | **我放了issure_0810和normal下面放了cxmt10G5_1p9m3x4y1z1rdl_98C_RCMAX , 这里面是一些明文数据，请分析这两个目录里到文件，找到数据差别。** | ✅ clean intent（提出需求，未给根因） |
| 58 | … | M0U相关到电容是变大还算变小 | 追问（细节） |
| 68 | … | NTDM 代表到含义是什么… | 追问 |
| 73 | … | NDTM 代表到含义是什么… | 追问 |
| 75 | … | 我把starrc_doc 放到了当前目录下… | 给资料 |
| 127 | … | dp_logs 看起来很正常… | 追问 |
| 135 | … | 去这个目录下，看你能否查找到线索。/apps/synopsys/SRB/star | 给路径 |
| 232 | … | 继续完成分析 | 续 |

→ **A-faithful 任务说明 = msg 23 逐字原文**（rule ② 不命中：纯需求，未指出根因/未给修复方案）。

## 助手工具链（116 tool_use: editor 62 / read_files 12 / list_allowed_files 16 / run_approved_command 24 / get_agent_policy_status 2）

核心交付件 = **rcmax_compare.py**（msg 29 创建）— 递归比较两棵 StarRC RCMAX 明文树，产出 `rcmax_diff_report.txt`：
- `walk(root)` 收集 relpath→size
- `same_bytes(pa,pb,size)` 分块字节比对
- `line_diff_stats(pa,pb)` 逐行 diff（n_lines_a/b, n_differ, detail）
- report 结构：header（A/B 路径+文件数）→ summary 行（common/identical/DIFFERENT/only_in_normal/only_in_issue）→ only-in-A → only-in-B → differing common files(rel,sizeA,sizeB) → per-line diff details

辅件 = rcmax_ndtm_stats.py（msg 38，2 个 NDTM 文件的 top/left/bottom 列定量 % 变化统计 + task_count uint32 LE/BE 解码）。

## 数据结构（fixture 依据）

- 树根：`<root>/cxmt10G5_1p9m3x4y1z1rdl_98C_RCMAX/`
- `DTM/*.ADTM` / `*.NDTM` — 明文记录，格式 `<x> <y> top <v> left <v> bottom <v>`（8 token；rcmax_ndtm_stats.parse 验：t[2]=="top" t[4]=="left" t[6]=="bottom"）
- `task_count` — 4 字节二进制（uint32 LE/BE）
- 真实差异（trace 结论）：issure_0810 vs normal 仅 2 个 NDTM 文件不同（substrate-M0U-M1.NDTM、substrate-M0U-sky.NDTM），sec3=372B / sec5=243B

## 金标准

= trace 助手 rcmax_compare.py（faithful 复刻），但**改 hardcoded 路径为 CLI 参数**（`<rootA> <rootB> <out_report>`）以支持 check.py 在 A/B fixture 上独立跑。判分仅看 report 结构（文件计数、differing 列表、size、per-line diff count），不依赖 StarRC 二进制。

## 难度评估

L2（subprocess 在 fixture 上跑候选 rcmax_compare.py，§4.2 结构判分）。A-faithful 真实难度 = 模型须从一句中文需求写出递归树比对 + 字节级 + 逐行 diff + 结构化 report，且**不能硬编码路径/差异文件名**（B 用不同树+不同差异集，硬编码必挂）。预期 ≤10% pass（A 档目标）。
