# r1138 · 1795433900792_mpcdi · UlvtDelvtoNetlistModifierProduce-001 · 1-case 产出轮

**日期**: 2026-11-24 · **轮次**: r1138 · **shard**: B · **结果**: 1-case 产出

## 选料

- 扫描: `/home/t0002965/log/ssh_eda_search_20261124_023802/summary.tsv` (Nov 24 02:38, 比 r1137 的 1123_064315 新)
- 池: `all_B_cands.tsv` (1414 B 域 mc≥5 候选, spice 关键词过滤, sid 规范化)
- 规范化 diff (strip `.messages.json`/`.messages.archive.json`/`.json`, vs 全 4 shard 台账 4657 sid): top 260 候选里仅 **15 fresh**; 其中 **9 个是 joeyl@hfeg0pkn004 同一 opamp/ULVT-delvto 任务** 的近重复 (kw profile 完全一致: netlist:1103-1156;schematic:99-109;hspice:92-102;opamp:24)。
- 其余 fresh: 43l0n(jiashengz/aether-pyaether-schematic 主, hspice 仅 39, 弱 B)、txjim(binwenh/analog-schematic-netlist-verilog 混合, hspice 仅 38)、os60p/omzbr/tvmlu(yinyus, 与 r1137 7xub5 同 kw profile, 近重复)。
- yinyus 三个判近重复 7xub5 (r1137 WaveformPwlStimGenProduce); 43l0n/txjim 偏 schematic/mixed-signal, 非纯 spice_sim。

## Peek (mpcdi, mc269, joeyl@hfeg0pkn004 / 10.129.2.13)

- 文件 689752 B / 178 msgs (cline 新格式: top-level dict, `messages` key)
- 真实任务: 用 `/home/joeyl/ulvt_delvto/reduce_vth.py` + `config.cfg` 给 FinESim/HSPICE 抽出的 DDR4 子块 netlist (Bias / CML_C2C / Solo_Divider / WCKTop / Divider_and_C2C) 中 ULVT 器件实例 (subckt `pulvt_ckt`=PMOS-ULVT / `nulvt_ckt`=NMOS-ULVT) 末尾追加 `_delvto=<带符号值>` 施加 ΔVth。
- 工具结构: `reduce_vth.py`(主, 6 次 editor) + `config.cfg`(10 次) + `work/verify_netlist.py`(3) + `work/copy_netlist.py` + `work/verify_model_delvto.py`; 运行方式 run_approved_command(profile=python-runner, filePath=...)。
- **关键修正 (U@52)**: PMOS 与 NMOS 阈值移动方向相反——`pulvt_ckt`→`_delvto=+<mag>`(正)、`nulvt_ckt`→`_delvto=-<mag>`(负), 由 `config.cfg` 的 `delvto_by_model = pulvt_ckt:+0.2, nulvt_ckt:-0.2` 显式给出。之前所有 netlist 都给统一 -0.2 (PMOS 错), 修正后 4 个 netlist 全部重做。
- 规则: 幂等(已有 `_delvto=` 则更新不重复追加)、支持 `+` 续行(追加到整条语句最后一条续行末尾)、不误改 `delvto_user=0` 等既有参数、不动 `nlvt_ckt`/`plvt_ckt`/`nrvt_ckt` 等非 ULVT、输出文件名含 delvto 值 (`<stem>_delvto-0.2`)。

## Case 合成

- **task_id**: EDA-Eval-DesignFlow-UlvtDelvtoNetlistModifierProduce-001
- **mode**: design_flow / entry_point: outputs/submit.zip / test: check(deliverable, workdir) 双参
- **L1**: 纯 Python stdlib `reduce_vth.py` (config 驱动, key=value)
- **A (给 SUT)**: `netlist_A` (Bias 子块, delvto=-0.2, 3 pulvt+3 nulvt, 含单行/+多行/delvto_user=0) + `config_A.cfg` + `task_brief.md`
- **B (隐藏, 反硬编码)**: `netlist_B` (Divider_and_C2C 子块, **delvto=0.05**, 不同实例名/数量/续行布局, 6 ULVT: 3 pulvt+3 nulvt, 4 非 ULVT) + `config_B.cfg` + `hidden_manifest.json`
- **check.py 13 条独立断言 (a-m)**:
  - a: zip 完整 + reduce_vth.py 存在 + size>200
  - b: 候选在 B 上 exit0 + 输出 netlist 非空
  - c: ULVT 识别: 恰 6 个(3 pulvt+3 nulvt)被改、4 非 ULVT 未改
  - d: pulvt 的 `_delvto` 值 > 0 (+0.05)
  - e: nulvt 的 `_delvto` 值 < 0 (-0.05)
  - f: 多行 continuation: `_delvto` 在最后一条 `+` 续行末尾 + 续行结构仍合法
  - g: 幂等: 对候选输出再跑一次内容不变(无重复 `_delvto=`)
  - h: 既有参数 `delvto_user=0` 保留不变
  - i: 行数守恒(只改行不增删)
  - j: 输出文件名 == config.output 且符合 `<stem>_delvto<delvto>` 约定
  - k: 符号交叉: 无 pulvt 为负 / 无 nulvt 为正
  - l: 非 ULVT X-instance 行字节级一致
  - m: oracle 独立重解析 B+config 重算期望文本逐行比对 (count+per-line+filename+per-model 符号)
- oracle 与 reference 独立实现 (不 import), 在 check.py 内重算期望文本逐行 diff。

## 自检

- ref 13/13 PASS (a-m 全 PASS)
- 3 假全 FAIL: `empty.py`(什么都不做) / `only_print.py`(只打印不处理) / `core_deleted.py`(读 config+netlist 但原样写出不加 `_delvto=`)
- sanity: reduce_vth.py 在 B 上产出 `netlist_B_delvto-0.05`, diff 仅 6 行 ULVT 变化(3 pulvt +`_delvto=+0.05` / 3 nulvt +`_delvto=-0.05`, 多行语句追加在 `+` 续行末尾), 非ULVT 4 行 + delvto_user=0 行数/内容守恒。

## 台账

- mpcdi claimed→case (UlvtDelvtoNetlistModifierProduce-001)
- 8 个 joeyl 近重复 parked (66pvf/xydly/wffbw/2gpt3/6rx0t/utow7/7165o/tyawz, 同 opamp/ULVT-delvto 任务 kw profile 完全一致)
- yinyus 三(os60p/omzbr/tvmlu) 未 park (本轮未 peek, 下轮若再 surfacing 应判近重复 7xub5)
- covered=595/4529=13.1% (+1)

## 备注

- 坑1: ledger_norm 上传到 .75 经 write_file `content_base64` 被破坏 (90KB→0 行), 改为读 .75 的 `all_B_sids_norm.txt` 回本地 + 本地 ledger 做 comm 解决。
- 坑2: cline 新版 messages.json 是 dict (`messages` key), 不是 list; peek 脚本要 `data["messages"]`。
- 坑3: joeyl `run_approved_command` input 是 `{profile, filePath}` (跑 py 文件), 不是 `{command}`; editor input 是 `{path, new_text}` (new_text 是被编辑的**片段**, 非整文件)。
