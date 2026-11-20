# r820 调查笔记：r528 subdir-path false-negative 发现 + 4 个 subdir-ALIVE 候选确认

## 核心发现（池复苏线索，重要）
r528「file-deleted-postscan」判定对一批候选是**假阴性**——cline session 文件实际在
`sessions/<sid>/<sid>.messages.json` **子目录**里（旧判定查直接路径 `sessions/<sid>.messages.json`，
子目录场景必然 NOFILE）。用 subdir-aware `find` 重扫可复活多条高价值造题料。

## 本轮探测结果（eda_flow session r820，.75 SSH）
### 4 个 r794 subdir-ALIVE 候选（mc5-9 A-pure，已证 weak/薄）
- `fl8g4` jkxu@10.129.32.80 mc7 digital — ALIVE 但仅 6 msgs，prompt「查看当前目录」(trivial ls)
- `720it` e0017484@10.129.35.73 mc6 — ALIVE 但 6 msgs，prompt「启动业务场景: 仿真与验证」(canned trigger, BLOCKER)
- `gheik` e0014566@10.129.35.82 mc5 — ALIVE 但 6 msgs，prompt=cimi-kb-search skill summary (KB-dependent, check 牙弱)
- `xq1yo` e0027435@10.129.8.237 mc5 — SSH 超时（10.129.8.237 不可达）
→ 4 候选全 weak，r794 subdir-ALIVE 池无造题价值

### 3 个 r528 parked 候选（高 mc，subdir-aware find 证 ALIVE）
- `gf2ud` tongfanl@10.129.32.80 mc213 verification — ALIVE 1.08MB/222msgs/18h
  - prompt「抽激励的环境：/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/ 帮我看下环境里 ZQLAT 命令到下一个 Valid Command 的时间 tZQLAT 是多少」
  - agent 得出 tZQLAT = tZQLAT_min = 30 ns；用户追问波形 14ns 偏差 + WTM pattern 检查
  - ⚠️ **跨 shard 碰撞**：已是他 shard B 的 case `EDA-Eval-DesignFlow-TzqlatLocate-001` (2026-11-08)。
    本轮曾据 gf2ud 合成 `TzqlatTimingExtractProduce-001` (B档 k=12/12, 全验证 PASS)，mark 时
    被 ledger 跨 shard 互斥拒绝 → **已回滚** A.jsonl 410→410 不变，assets/reference 已删。
    （B 的 TzqlatLocate-001 与本 case 近似意图，回滚正确）
- `h8pcp` jinhaoli@10.129.8.239 mc156 digital — ALIVE 1.05MB
  - prompt「...xcelium.trn 是理想的波形数据，...write_pattern_basic_new/...里read的数据dq_exp[15:0]和总线读出来的数据UPDQPad[7:0],LPDQPad[7:0]对不上，请帮忙查找电路里哪里出现了问题」
  - 波形比对 debug Q&A（开放诊断，check 牙弱，需 produce-task reframe 才可造）
  - **待查碰撞**：下轮 mark 前先核 ledger 是否已被他 shard 占
- `06htj` mike@10.129.32.85 mc275 pnr_signoff — ALIVE 4.8MB（偏大，>2MB 需分轮深读）

## 结论与 DEBT
- r528 subdir-path false-negative 是**确认的池复苏机会**：13 条 r528 parked A 域候选里，subdir-aware find
  抽查 3 条全 ALIVE。下轮应**全量 subdir-aware 重扫 r528 parked 候选**（预计可复活 5-10 条造题料）。
- 本轮 0 case：r794 subdir-ALIVE 4 候选全 weak；gf2ud 高价值但跨 shard 碰撞已回滚。
- **DEBT**：下轮 (a) subdir-aware 全量重扫 r528 parked 候选 → (b) 对未碰撞的候选（优先 06htj/h8pcp，
  mark 前先核跨 shard 占用）深读 + 造题。注意 h8pcp 是 debug Q&A 需 reframe，06htj 4.8MB 需分轮。
- 本轮有效产出：r528 复苏线索 + subdir-aware 探测方法固化（`find sessions/ -name "<sid>*" -type f`）。
