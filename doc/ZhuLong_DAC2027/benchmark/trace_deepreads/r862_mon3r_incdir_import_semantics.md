# r862 — mon3r deepread + synthesize: IncdirImportSemanticsQA-001

## trace
- session_file: `1792995847117_mon3r` (user e13zhang @ hfeg0pkn002 / 10.129.2.11, shard A, domain verification, mc=16)
- subdir-path ALIVE 213368B / 42 msgs / agent=lead (flat-path NOFILE, path-bug revival 第 N 例)
- liveness: `sessions/1792995847117_mon3r/1792995847117_mon3r.messages.json` (ssh 10.129.2.11 cat, e0031982 免密)

## 旧判纠偏 (重要)
- ledger A r553 (2026-11-15) note: "SDF SDFCOM_NL warning debug, troubleshooting not produce-task" → **全错**。
- 真实主题 = Cadence Denali LPDDR6 VIP / VCS-UVM 编译环境集成，多轮 consulting/debugging (20+ user turns)，无 SDF/SDFCOM_NL 内容。旧判可能是另一 session 误串或漏读。
- pool_reaudit_A.tsv r843 行旧判 "weak(Q&A非produce)" → 11-15 reaudit: analysis-Q&A/explain 合法 → 复活。

## 同 session 已有 case (sister-turn, 非碰撞)
- `EDA-Eval-DesignFlow-CadenceVipLinkErrorDiagnose-001` = U#40 链接错误 (cdsInit undefined) debug-Q&A，root cause = Cadence 公共库 libcdsCommonMT_sh.so 未链接/source env。
- 本 case = U#2/U#4/U#12 `+incdir+` vs `import`/package 编译语义 analysis-Q&A。
- 不同 turn / 不同意图 / 不同判分范式 (link-error-symbol-specificity vs filelist-include-mechanism-specificity) → 无判分重叠。同 r821/r822 sister-turn 模式。

## 用户原话 (逐字)
- U#2: `我如果写了+incdir+${DENALI}/ddvapi/sv  还需要把这个目录的文件一个一个给添加进filelist吗`
- U#4: `+incdir+  可以让import找到package吗`
- U#6: (贴完整 filelist，24 行，即 filelist_A.f)
- U#8: `Parsing included file '.../cdnVipTop.sv'. 我看到这个 然后package cdnLpddr6Uvm; import uvm_pkg::*; import DenaliSvLpddr6::*;import CdnSvVip::*; 我的import Cdnvip也没有报错`
- U#10: (贴 cdnVipTop.sv 内容，即 cdnVipTop_A.sv，里面 `package CdnSvVip`)
- U#12: `我的意思是  我都没有增加过cdnVipTop.sv 到filelist里面，只写了+incdir+${DENALI}/ddvapi/sv  发现一样可以import`

## trace assistant ground-truth (msg 5/7/13)
1. `+incdir+` 只作用于 `` `include "xxx" `` 文件搜索路径；**不**自动编译目录下文件；**不**让 package 对 `import` 可见。
2. `import pkg::*;` 前提 = `package pkg` 定义 `.sv` 被编译到编译单元。
3. package 被编译两路径: (a) 显式列 filelist；(b) 被某显式列出 `.sv` 用 `` `include `` 拉进 (靠 `+incdir+` 定位)。
4. VCS 打印: `Parsing design file` = 显式列 `.sv` (编译单元)；`Parsing included file` = 被 `` `include `` 拉进 (靠 `+incdir+` 定位)。
5. `cdnVipTop.sv` 未列却能 `import CdnSvVip::*` = 被某显式列出 `.sv` (很可能 `cdnLpddr6UvmTop.sv` / `denaliMem.sv`) `` `include `` 拉进 → `package CdnSvVip` 被编译 → import 生效。**不是** `+incdir+` 自己编译。
6. `.sv`/`.c` 编译单元 (denaliMem.sv/denaliLpddr6.sv/denaliMemSvIf.c/denaliLpddr6SvIf.c/cdnLpddr6UvmTop.sv) 必须显式列；`.svh` 不用逐个列。

## A 档可行性
fixture A 全部是 trace 里用户**逐字粘贴**的内容 (filelist U#6 / cdnVipTop.sv U#10 / parsing log U#8)，自包含，无需访问 `/proj/lagat` 或 `/apps/cdsmgr`。→ A档 trace-faithful。

## case 合成
- task_id: `EDA-Eval-DesignFlow-IncdirImportSemanticsQA-001`, domain=verification, mode=design_flow, entry=outputs/submit.zip
- deliverable: `incdir_import_explain.md` (中文 markdown 报告, analysis-Q&A)
- A (SUT 可见): filelist_A.f + cdnVipTop_A.sv + parsing_log_A.txt + prompt.txt + task_brief.md
- B hidden (judge-only, DDR4 Denali VIP 同构改名): hidden/filelist_B.f (cdnDdr4UvmTop.sv/denaliDdr4.sv) + hidden/cdnMemTop_B.sv (package CdnSvMem) + hidden/parsing_log_B.txt + hidden_manifest.json
- check.py: S5 第二范式 analysis-Q&A + specificity oracle + refuse-to-hallucinate, 13 独立断言, subprocess 解析 A 推导 ground-truth + 解析 B 推导 B-only 标识符
- ref: incdir_import_explain_ref.md
- negatives: neg_empty / neg_print_only_generic / neg_wrong_mechanism / neg_b_leak

## 自验
- REF self-check: PASS 13/13 (plain_len=987, cjk=340, headings=6, a_cu_hits=6, key_file_hits=3)
- 4 neg 全 FAIL 命中不同断言组: neg_b_leak→⑩ / neg_empty→① / neg_print_only_generic→① / neg_wrong_mechanism→③
- §4.9 (a)empty→① (b)print_only→① (c)core_del(wrong mechanism)→③ 三假提交全 FAIL
- jsonl test sha == disk check.py sha byte-identical (4961160a8ba12a8c)
- k_check == k_rationale == 13 ≥ 8 硬闸门过
- build_jsonl --check: 本 case 无 collision (IncdirImport 不在碰撞清单)

## 落库 (op-order V: cases/ 为唯一 source of truth, 不碰 jsonl)
- cases/A/EDA-Eval-DesignFlow-IncdirImportSemanticsQA-001.json (30304B)
- ledger A: mon3r parked→case (case 414→415, covered 414→415/2517=16.5%)
- pool_reaudit_A.tsv: mon3r 不可造(待深读)→可造(已造r862)

## eda_flow
- session r862: open + ssh 10.129.2.11 cat mon3r.messages.json (subdir-path 213KB ALIVE) + close cleaned
