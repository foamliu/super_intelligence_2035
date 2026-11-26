# r580 fast-path 复活池耗尽实证（shard A · 2026-11-15）

> 结论：**note-bearing 复活候选（pool_reaudit_A.tsv 标"可造" + 有 deepread note + 未交付）已全部耗尽**。
> 32 条 available 中，去掉 .messages.json 后缀归一后 **仅 5 unique 真未交付**，逐条 deepread note 复核 **全部 non-viable**。
> 下一轮起若要继续造 case，必须走 **note-less fresh-deepread**（pool_reaudit 262 条 A-domain 可造中 ~208 条无 note）。

## 方法
1. `pool_reaudit_A.tsv` 取 A-domain(digital/eda_other/pnr_signoff/verification) + 新判定含"可造" → 262 行。
2. 交叉 `trace_deepreads/*.md` → 54 条有 deepread note。
3. 对 54 条做 ledger 状态匹配（full session string），保留 status≠case → 32 条 available。
4. 用**全部 4 shard jsonl + 主 jsonl + reference/ 目录**构建 used-sids 集合（2732 条），**suffix-aware 归一**（strip `.messages.json`/`.json`）后判定 delivered。
5. 32 条中仅 **7 行（5 unique session）真未交付**；其余 25 行的 session_file（带 `.messages.json` 后缀）已在某 shard jsonl 的 trace_source 中 = 已交付（ledger "parked" 标记为 stale）。

## 5 unique 真未交付 — 逐条 non-viable 判定（均据 deepread note 原文）

| session | sid | domain | note 判定 | 不可造理由（note 原文依据） |
|---|---|---|---|---|
| 1793165088136_0suhi | 0suhi | pnr_signoff | 不可合成 | note L23-29：doc-gen（autosim README/设计文档 + mermaid），L1 文档、隐藏 B 机制不适配、金标巨大、§4.2 结构断言弱。parked。 |
| 1792120944014_78z8d | 78z8d | pnr_signoff | Q&A | note L18：genus 时间单位 / timing report 单位 / netlist 层级展平 纯 Q&A，RAG 空、sandbox refused，最终 markdown 答案，无交付物。parked。 |
| 1791962616204_7j1bw | 7j1bw | digital | 跨 shard 碰撞 | note L48-55：AsyncFifoSim-001 已由 **shard D** commit（3e9a310）落 EDA-Flow-Bench，同一 trace 7j1bw 同一合成。A 标 parked-collision，非 A 的 case。 |
| 1792399916731_sbaad | sbaad | digital | 近重复 | ledger note（r320）："near-duplicate of SignalXrefBuilder-001 (u54d9) — same 3-level signal xref task, different user/project; skip per r313 duplicate discipline"。另一同 sid session 1793967043660_sbaad 已交付为 SignalFileXref-001。 |
| 1793790637246_aafag | aafag | pnr_signoff | trivial Q&A | note L9-16：用户只发一个拼写错误 "innouvs"，agent 识别为 Innovus 笔误 + AskEDA 综述。0 produce-task / 0 innovus 执行。trivial。 |
| 1794466237270_iyyzq | iyyzq | eda_other | 关键词假阳性 | note L36-43：真实任务是 sed 文本处理（corner 名 newline→space + sed one-liner），innovus/lvs/aether/calibre 计数来自 list_allowed_files 列出的目录名，非工具执行。"非 design_flow"。 |

## 含义
- r560-r579 交付的 18 条复活 case 消耗了全部 viable note-bearing 复活候选。
- 剩余 note-bearing 复活候选 = Q&A / doc-gen / 假阳性 / 跨 shard 碰撞 / 近重复 —— **按任务初衷第 2 条（写不出区分真假交付的 check）+ 第 3 条（真实性）不可造**，强行造会违 §4 判分牙门 + "不为凑数字而挑题"。
- **不删 pool_reaudit_A.tsv 的"可造"标**：这些是"旧 weak 筛子误杀"的复活判定本身仍成立（旧筛子确实误杀），只是经 deepread 复核后落入两条硬排除标准之一（无真实 design_flow trace 能力 / 写不出有牙 check）。pool_reaudit 的"可造"是准入资格，deepread 复核是造题前的第二道门，两者不矛盾。

## 下一轮方向（按可行性）
1. **note-less fresh-deepread**：pool_reaudit 262 条 A-domain 可造中 ~208 条无 deepread note。按 mc 降序、kw 含 build 信号（write_file/create_file/run_approved_command 产物）优先 scp trace 到 .75 解析。r569/r574 fresh-deepread 命中率参考（非 0）。
2. 接受 A-core note-bearing 枯竭 → 转向 mc≥5 note-less 池（r555 recompute fresh=500 含 mc5-9 +179）。
3. 自动止损令（11-15）：本轮为 mc≥5 下第 **1** 个 0-case（r560-r579 连续 18 case），未触 3 连止损；继续观察。

## 本轮台账动作
- 0 case mark / 0 claim / 0 jsonl append / 0 reference|assets 新建。
- 本审计文件落 `designflow/fastpath_exhaustion_audit_r580.md` 作证据。
- MEMORY_A r580 流水一行；daily_A 追加一行；仅提交本 shard 文件。
