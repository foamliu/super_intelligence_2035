# r1001 deep-read — 1795075206381_ozvhc (CosimEnvProjectExtractProduce-001)

## 选料

- scan: ssh_eda_search_20261122_172249 (r995 新扫)
- A-pure filter (mc≥5, ak>c/b/d, dedup): 141 cands → fresh-diff vs 4-shard ledger (4159 sids): 21 fresh
- peeked 8 top fresh; chose `1795075206381_ozvhc` (guangmingz@hfeg0plg58, mc=24, kw verilog:94)
  - 新用户首次出现，无 dedup 冲突
  - 干净 A-domain produce-task 意图（digital/verilog 主导）
  - trace 38 msgs / 23 user msgs / 90KB

## trace 要点

- msg0/10/21/30/35 用户逐轮加需求：
  - 起步：搭 `create_block_cosim_env.py` 的 `--fullchip`/`--block` argparse 框架
  - 中段：要求「中文注释改成英文」
  - 最终（msg35 逐字）：`--fullchip`/`--block` 两参均为必填路径 + 新增 `get_project_name(fullchip_path)` 从 fullchip 路径下的 `si.inp` 中按关键字 `Project` 提取项目名称作为返回值
- msg11/24/33 editor tool_use：agent 交付了 v1（中文注释）/ v2（英文注释）/ si.inp search stub 三版脚本
- msg36：agent 的 `find ... si.inp` 命令 SIGKILL 超时，**最终 si.inp 提取版未交付**
- 本 case 取用户最终意图（msg35）综合前序英文注释约束，合成一个可交付的 produce-task

## case 设计

- CID: `EDA-Eval-DesignFlow-CosimEnvProjectExtractProduce-001`
- domain: digital
- 交付件: `create_block_cosim_env.py`（打包进 submit.zip）
- 核心契约:
  1. argparse `--fullchip PATH`（必填）/ `--block PATH`（必填），缺任一非零退出
  2. `get_project_name(fullchip_inp_path)` 读取 si.inp 文件，找首 token 为 `Project` 的行，返回其后一个 token
  3. `main()` 调 `get_project_name(args.fullchip)` 并 print 到 stdout
  4. 纯英文注释（无非 ASCII 字节）
  5. 可 `import` 不报错

## fixture 设计（flat-file，harness 兼容）

**关键约束发现**: eval harness `run_one.sh` 用 `shutil.copy`（仅文件）向 SUT workdir 投递 A 附件，用 `[ -f ] && cp`（仅文件）向 judge dir 投递 A 附件；只有 `hidden/` 走 `cp -r`（可目录）。因此 A 附件**必须是扁平文件**，不能用目录。早期版本用 `fullchip_A/si.inp` 目录结构导致 workdir 投递崩溃 + judge dir 找不到 A — 已修复为扁平文件。

- A（可见）: `fullchip_A.inp`（si.inp deck，Project `dscqaF2_DDR6TOP_X1P6`，corner X1P6/11600/TT0.92V25C）/ `block_A_meta.txt`（block `dscqa_io_IO_CABufCore`）
- B（隐藏）: `hidden/fullchip_B.inp`（Project `decqa_LPDDR6_F2_X2P6`，corner X2P6/8800/SS0.81V-40C）/ `hidden/block_B_meta.txt`（block `decqa_phy_pll_clkdiv`）
- A/B 完全不相交：Project 名、corner、deck 内容、block 名全不同

## check.py（16 断言，k=16 ≥ 8 门槛）

- ① zip 含 `create_block_cosim_env*.py` ② py_compile 通过 ③ `get_project_name` 存在
- ④ `get_project_name(B)` == B_PROJECT ⑤ `get_project_name(A)` == A_PROJECT（反硬编码，必须真读文件）
- ⑥ 无参非零退出 ⑦ 仅 `--fullchip` 非零 ⑧ 仅 `--block` 非零 ⑨ 两 B 路径 exit0
- ⑩ stdout 含 B 项目名 ⑪ stdout 不泄漏 A 项目名（反硬编码 A）
- ⑫ 脚本无非 ASCII 字节 ⑬ 含 `def get_project_name` + `import` + 体积>200B
- ⑭ 三次调用一致（确定性）⑮ si.inp 缺失时抛异常（反空壳）⑯ forged deck 返回其 Project 值（反硬编码，证明真读文件）

### `_locate_fixtures` 双布局兼容

- in-place（reference/<CID>/check.py 自测）: `../../assets/<CID>/` 找 A/B
- judge temp（harness 提取 check.py 到 <judge>/g1/g2/）: A 文件作为附件被 copy 到 g1/g2/ 同级 → `os.path.dirname(__file__)` 直接找；B 经 `workdir/hidden` symlink → `$JUDGE/hidden/`

## 验证

- `negative_selftest.py`（in-place）: ref PASS, 3 negatives（empty/print_only/core_deleted）FAIL ✓
- E2E（模拟 harness judge-temp 布局，check.py 从 jsonl `test` 字段提取）: ref PASS, 3 negatives FAIL ✓

## ledger

- `trace_ledger_A.tsv`: 1795075206381_ozvhc.messages.json → status=case, case_id=EDA-Eval-DesignFlow-CosimEnvProjectExtractProduce-001
- A.jsonl: 458 → 459（digital +1）
- 覆盖率: 459/9542 ≈ 4.8%
