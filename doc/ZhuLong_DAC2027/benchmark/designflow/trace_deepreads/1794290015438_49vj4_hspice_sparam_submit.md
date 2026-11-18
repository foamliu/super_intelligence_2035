# trace_deepreads — 1794290015438_49vj4 (hspice sparam submit)

- **session**: `1794290015438_49vj4`
- **user/host**: mengzh @ hfeg0plg10 (10.129.35.10)
- **match_count**: 214 (hspice:2778 dominant, spice_sim domain)
- **trace size**: 888KB, 207 msgs, 10 user turns
- **selected round**: r863 (b_pool_1118_230537, mc≥10 fresh, NEW-user mengzh — 0 entries across all 4 shard ledgers)
- **case_id**: `EDA-Eval-DesignFlow-HspiceSparamSubmit-001`
- **reframe_driver**: portability (7th instance in B shard)
- **B.jsonl**: 409 → 410

## 真任务（real_task_summary）

用户要求把 DDR5 CA S-parameter 的 HSPICE 仿真提交到 LSF 队列跑 S-param 分析。msg[194] 用户给三件套：
1. `DDR5_CA_9_us_11um_21um_Z30_sparam.sp` — 主 deck（line_length=900*25.4*1e-6, Z=30, us=9, 11um/21um 几何）
2. `SPARAM_OPTION.inc` — .include 进来的 S-param option 文件
3. `.tab` — w_table_model 用的表格模型

agent 迭代多轮，msg[204/206] 抓到根因：**HSPICE first-line-is-title quirk** — deck 首行是 `.include SPARAM_OPTION.inc`，被 HSPICE 当作 deck title 行跳过 ⇒ SPARAM_OPTION.inc 没被 include ⇒ `.param line_length` 未定义 ⇒ `w_table_model` abort。修复 = `.include` 下移 + 显式 `.title`。最终交付 `submit_sparam.py`（硬编码 SIPI 路径 + DDR5 CA 设计名 + 直打印 stdout）。

## reframe（portability，第七实证）

原 agent `submit_sparam.py` 硬编码设计名/路径/队列/版本 → 参数化 `submit_hspice_sparam.py`：
- `--sp-file` / `--hspice-version` / `--queue` / `--outdir` / `--dry-run` argparse
- 结构化 `report.json`（jobs + deck + measures + status）
- `--dry-run` 模式可无 LSF/HSPICE 二进制 gradeable（check 不依赖 EDA 二进制）

## asset A（trace-verbatim）

- `DDR5_CA_9_us_11um_21um_Z30_sparam.sp` — 按 msg[194] verbatim 保留
- `SPARAM_OPTION.inc` — verbatim
- `.tab` 模型表 — format-faithful 重建
- ref 脚本纯 python deck 解析 + dry-run only（无 EDA 二进制依赖）

## hidden B（结构性差异 5 维度非仅文件名）

- 设计名 `DDR6_DQ_11_us_13um_23um_Z40`（vs A `DDR5_CA_9_us_11um_21um_Z30`）
- 队列 `DDR6`（vs A `SIPI`）
- `line_length=1500*25.4*1e-6`（vs A `900*25.4*1e-6`）
- hspice 版本 `W-2024.09-SP2-1`（vs A `W-2024.09-SP1`）
- title quirk 仍 PRESENT（B 首行 `.include` 同样被当 title 跳过 — 测候选是否真修了 quirk）

## hidden B2（anti-stub）

同 DDR6_DQ 设计但首行改为 `*comment`（无 title quirk）+ 队列 `DDR7` + `line_length=2000*25.4*1e-6`。stub 返回常量必 FAIL（B2 report 必与 B 不同）。

hidden B/B2 用相对 `.include` 路径让 ref 脚本能本地解析 .inc。

## check（k_check=k_rationale=14, a-n）

check **真跑**候选在 hidden B+B2 上：
- a zip 顶层含 submit_hspice_sparam.py 无泄漏
- b py_compile
- c --sp-file/--hspice-version/--queue/--outdir/--dry-run exit0
- d --dry-run 生成 report.json
- e JSON 含 jobs+deck+measures+status 字段
- f report.json 提交命令含 B 队列 DDR6（非硬编 A 的 SIPI）
- g bsub_command/hspice_binary 含 B 版本 W-2024.09-SP2-1
- h deck .param line_length=B 值 1500*25.4*1e-6
- i deck .include 非 deck 首行（title quirk 修复）
- j report.json measures 含 B 设计名 DDR6_DQ
- k 非 hardcode-A: cand(B) report 不全是 ref(A) 子集
- l anti-stub: cand(B2) report 与 cand(B) 不同且匹配 ref(B2)
- m 代码实质 ≥20 行+argparse+--dry-run+无 A 设计名/路径硬编码 token
- n 确定性 B 上 3 次运行逐位一致

layer=L1, track=faithful, domain=spice_sim, tier=B

## §4.9 退化提交（5 neg 全 FAIL）

- empty_shell / print_expected / hardcoded_A / core_deleted / no_dryrun
- NEG_RC=5/5, ref 14/14 PASS

## A-token 清洗

A-tokens 已从 ref 脚本 docstring/argparse help 清洗（移除 SIPI 例 + DDR5 CA 提及）以过 condition (m)。

## ledger

- trace_ledger_B.tsv 行 988：原 parked（unknown/0/"SIPI file read permission consultation"）→ 覆写为 case（mengzh/hfeg0plg10/mc214/EDA-Eval-DesignFlow-HspiceSparamSubmit-001）
- mark 命令确认：`1794290015438_49vj4 -> case`

## discuss

r862→r863 diff=1 < 4 不发言，mandatory due r866。

## 产物

- `cases/B/EDA-Eval-DesignFlow-HspiceSparamSubmit-001.json`
- `assets/EDA-Eval-DesignFlow-HspiceSparamSubmit-001/`：A files（sp/inc/tab/prompt.txt/task_brief.md）+ hidden/B + hidden/B2 + hidden_manifest.json
- `reference/EDA-Eval-DesignFlow-HspiceSparamSubmit-001/`：check.py + submit_hspice_sparam_ref.py + reference_submit.zip + negative_selftest.py + negative/5 stubs
- EDA-Eval-DesignFlow_B.jsonl line 410
