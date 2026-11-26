# deepread: 1795049089951_yy8pd (alan17z @ hfeg0pkn004, mc146)

**scan_snapshot**: ssh_eda_search_20261119_172105/summary.tsv
**keywords**: netlist:358;hspice:219;cmos:15;.spi:7;schematic:6
**host**: 10.129.2.13 (hfeg0pkn004)
**session_file**: /home/alan17z/.cline/data/sessions/1795049089951_yy8pd/1795049089951_yy8pd.messages.json (849KB, 230 msgs)
**fetched**: r900 (2026-11-20) via eda_flow run_commands ssh from .75

## 用户真实意图（trace 原文）

唯一一条用户文本消息是一份「Context summary」交接：
- **目标**：合并 3 个 IBIS 抽取相关 skill（`ibis-t2b-gen` / `ibis-zq-calib` / `ibis-zq-sim-gen`）为一个端到端 skill `ibis-extract`，实现从 source 到 t2b 交付的完整自动化工作流（hspice 直接跑 ZQ 校准，t2b 由用户手工抽取）。
- 已完成：新 skill `ibis-extract/` (SKILL.md + references + 7 scripts)；run_sims.py 用 `LD_PRELOAD= bsub -q SIPI ...` 绕开 agent LD_PRELOAD 污染提交 hspice；gen_t2b.py 参数化生成 4 个 t2b 配置；ZQ 校准全链路 6 个码（ff/ss/tt × PU/PD）误差 ±0.34Ω。
- 关键坑：Agent 的 LD_PRELOAD 被设成 agent 自身旧 libstdc++.so.6 会注入到 hspice 导致缺 GLIBCXX_3.4.30 崩溃，修复 `LD_PRELOAD= bsub ...`。

## assistant 工具链（230 msgs）

- tool_use 计数：run_approved_command 58 / editor 24 / read_files 21 / list_allowed_files 12 / skills 1 / get_agent_policy_status 1
- harness 非 cline：用 `run_approved_command`（profile=python-runner, filePath, args）跑脚本，用 `editor`（path + old_text/new_text）改文件
- 主要产物（editor 写）：`/home/alan17z/.cline/skills/ibis-extract/scripts/gen_model_sp.py`（5 次编辑，156/174/184/192 行为关键迭代）、`gen_top.py`、`SKILL.md`、`ibis_extract_background.md`，以及一批 `ibis_extract_verify/*.py` 验证脚本

## 核心产物 gen_model_sp.py 演化

Stage 4 的 DQ-driver model 子卡生成器，产生 `[ExtSpiceCmd]` 配置共享 DQ driver 的 ODT/drive 模式的小子卡：
- CIO/ODT (Rx)：drive=0（output driver off）、vodten='1*pvcc'（ODT enable）
- BOOSTOFF/BOOSTON (Tx)：drive=1（PU40/PD40 ON）、vodten='0*pvcc'、podt=111（ODT disabled）
- ODT 分支编码 podt2:1:0：40=111 48=110 60=101 80=100 120=010 240=001 off=000
- 输出 11 个文件：1_CIO/odt{40,off}.sp、2_ODT/odt{40,48,60,80,120,240,off}.sp、3_BOOSTOFF/pu40_pd40.sp、4_BOOSTON/pu40_pd40.sp
- 统一两段式布局：开头空行 + `** Drive Strength Setup **` + 6 个 .param pdqpudrv/pdqpddrv(=drive) + 空行 + `** ODT Setup **` + vodten 行 + 3 个 .param podt2/1/0

编辑迭代（关键）：
- idx156：初版，ODT_ENCODING dict + render(drive,vodten,podt2,podt1,podt0) + main() 写 11 文件，LF 结尾
- idx174：加 trailing blank line 对齐参考文件
- idx184：改成 CRLF 结尾 + 末尾 LF（逐字节匹配参考）
- idx192：**回退**到干净 LF（"Unified, clean Linux LF output"——参考文件本身混 CRLF/LF，归一为 LF 与 pipeline 其余脚本一致）
- idx217：gen_top.py TX_POWER_LINES 加回 DataFooterEn/VFootOutEn 使 Tx 输出级完整配置

## reframe 决策（portability-reframe）

trace 原意图是 skill-build/characterization（写 one-off gen_model_sp.py 把 ODT 编码/drive/vodten/子目录全写死）。reframe 成 produce 型参数化生成器：把 trace 里写死的值抽成 spec.json 驱动（odt_encoding + modes{subdir,filename,tags,drive,vodten} + line_ending），对任意配置输出两段式子卡 + JSON 摘要。

## case 落地

- case_id: EDA-Eval-DesignFlow-IbisModelSpGen-001
- domain: spice_sim, layer: L1
- k_check = k_rationale = 16 (a-p)
- 隐藏 B 结构性反转：重映射 ODT 编码（48->[0,1,1] 非 A 的 [1,1,0]）、drive=2 非 1、重命名子目录 rx_cio/rx_odt/tx_boostoff/tx_booston、CIO tags=[48,off]、ODT tags=[48,60,80,120,240,off]（去掉 40）
- B2 反 stub：空 modes + 空 encoding → 生成器 exit 0 写 0 文件（写死 A 的 11 文件的 stub 必 FAIL）
- self-verify: ref 16/16 PASS, 5 neg 全 FAIL (NEG_RC=5/5), 确定性 3-run sha256 一致
- B.jsonl 440 → 441

## ⚠️ r900 duplicate-detection 处置（重要）

**结论**：yy8pd 是 r892 已落 case 的 cross-session near-duplicate，本轮不建新 case。

- r892 已落 **EDA-Eval-DesignFlow-IbisModelSpGen-001**（commit 3a1b79026, 2026-11-20 00:06:49），trace = `1795055873026_3bis4`（alan17z, mc167）——**同一用户 alan17z**。
- 两个 session 是同一意图的 continuation：3bis4 是「flagged model .sp files as format-wrong + unified two-section layout」，yy8pd 是「合并 3 IBIS skill + build gen_model_sp.py」。real_task_summary 关键词重叠（ibis-extract / gen_model_sp / model .sp / Drive Strength Setup / ODT Setup）>80%。
- r892 schema：inline SPEC_A/B/B2 + label-based（{label,mode,podt}）。我的 r900 schema：external hidden/ + odt_encoding+modes{subdir,filename,tags,drive,vodten}。不同 schema 但同一生成器意图。

**处置**：
1. EDA-Flow-Bench：`git restore --staged --worktree` 还原 r892 的 check.py/gen_model_sp.py/spec_A/hidden/negative_selftest + rm 8 个我的 stray 文件（example_odt40.sp/example_pu40_pd40.sp/task_spec.json/negative/empty_stub.py 等）→ working tree 回到 HEAD，r892 case 完整保留。r892 negative_selftest 复跑 NEG_RC=5/5 完好。
2. B.jsonl：回滚 441→440（移除我的 IbisModelSpGen-001 append，gitignored 本地文件）。
3. ledger：yy8pd `case` → `parked`（note: duplicate of r892 3bis4, same user alan17z, same IBIS DQ-driver model .sp generator intent）。

**教训**：claim 前缺「case_id 已存在」+「同 user 同意图」双闸门。修法：claim 前 (a) grep reference/ 查同名 case；(b) grep ledger_B 查同 user 已 case/parked session，比对 real_task_summary 关键词重叠度。纳入 §3 选料 SOP。
