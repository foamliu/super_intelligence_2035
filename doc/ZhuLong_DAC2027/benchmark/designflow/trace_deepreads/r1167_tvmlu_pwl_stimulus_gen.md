# r1167 deepread — tvmlu PWL current stimulus generator

## 选料链
- r1166 DEBT = 1124 scan pool 抽取。修 `_done_sessions_all.txt` 双 bug：
  (1) 4-shard 全 sid 提取（之前漏 shard）；(2) col1 后缀未剥（`.messages.json` / `.messages.archive.json`），
  用 awk `sub` 剥后缀 + split `_` 取末段 sid。4756→5330→4503（去重后）。
- 从 1124 scan `/home/t0002965/log/ssh_eda_search_20261124_023802/summary.tsv` 抽
  hspice/finesim/spectre-dominant 候选（simc≥10, mc≥5）→ 1015 uniq → .75 workdir `cand_1124_spice_uniq.tsv`。
- 全 1015 sid vs done_sessions 过滤 → **53 fresh**（top 50 by simc 全 DONE，深挖至 simc~70 才见 fresh）。
- 关键发现：.75 (hfhds201) 上**所有用户** `~/.cline/data/sessions/` 可本地读（共享 home），
  无需 ssh 即可 peek 任意候选的首条 user message。

## peek 拒/选
- kf7wc(t0002607 simc703)=hspice no-model 调试（reject：fuzzy 交付）
- zc8r5(vincentz simc694)=vtarget 二分法理解（reject：Q&A）
- tvmlu/os60p(yinyus simc336/319)=读 ivblh_idd5b2.sp 写 PWL 电流激励（**ACCEPT**：produce-action 干净）
- o8sy6/ya31r(e0030760)=solido RSNM 读取失败调试（reject）
- ilgqv(clarawu simc177)=DDR4 PreDrv sizing 迭代（复杂+文件不可达，备选）

## tvmlu trace 摘要
- session 1795425420593_tvmlu, yinyus@10.129.32.75, mc351, simc336, 242 msgs, spice_sim
- U0 逐字：读 ivblh_idd5b2.sp（WaveView 导出 time[s]/current[A] 表）→ 写成电流激励，
  仿照 `ivblh vblh! 0 pwl(0 0 120u 0 120.001u 2mA)`，数据加在 120us 后，存 ivblh_iloadIDD.sp。
- agent plan：+120us 偏移，前置 (0,0)/(120u,0) lead-in，输出 pwl+续行；
  修精度（1e-11s 细时间步在 6 位有效数字下撞 120us 成重复 → 提精度 + 丢连续重复时间点，HSPICE 要求严格递增）；
  python-runner 跑 gen_ivblh_pwl.py。
- 后续：改挂 200us；从 FSDB 高精度提取 isub(inh_vblh) 波形再生成。

## L1 reframe
- produce-action（写一条具体 PWL 激励）→ produce-tool（参数化 generator `pwl_stimulus_gen.py`，manifest 驱动）。
- manifest 字段：data_file / stimulus_name / node / gnd / start_offset(s) / lead_in_zero /
  drop_duplicate_times / output_file。
- hidden-B（iodd/vdd!/200us/data_B 14 点）反硬编码；check 仅跑 `sys.executable [gen,manifest,-o,out]` 产 .sp，不启动 hspice。

## check.py 9 断言（test_rationale）
①py_compile ②产非空 .sp ③PWL 源行 name/node/gnd ④零电流 lead-in(t=0→0,t=offset→0)
⑤偏移后数据点边界+计数(独立复算 data_A.csv) ⑥时间严格单调递增 ⑦A≠B 反硬编码
⑧确定性 3-run md5 ⑨退化空数据非零退出无 Traceback

## self-verify
- ref `pwl_stimulus_gen.py` → check **PASS**（全 9 断言）
- fake empty（空文件）→ FAIL @ ①
- fake print-only（只打印不产 .sp）→ FAIL @ ②
- fake core-deleted（产 .sp 但无 pwl 源行）→ FAIL @ ③
- 退化空数据 → exit≠0，stderr 无 Traceback ✓
- 确定性 3-run md5 一致 ✓
- case JSON `test` field == reference/check.py（byte-identical）✓

## 交付物
- cases/B/EDA-Eval-DesignFlow-PwlStimulusGen-001.json
- assets/EDA-Eval-DesignFlow-PwlStimulusGen-001/{manifest_A.json,data_A.csv,task_context.md,hidden/{manifest_B.json,data_B.csv}}
- reference/EDA-Eval-DesignFlow-PwlStimulusGen-001/{check.py,pwl_stimulus_gen.py}
- 台账 B：tvmlu → case（covered 598→599）
