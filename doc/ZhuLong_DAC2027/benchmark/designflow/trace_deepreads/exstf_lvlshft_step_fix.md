# trace_deepread: 1782803097375_exstf (e0025730@hfeg0plg49, mc=25)

- **shard**: D / schematic_netlist
- **session**: 1782803097375_exstf.messages.json (80 msgs)
- **keywords**: netlist:361; schematic:148; hspice:18 (100% D-domain)
- **outcome**: case `EDA-Eval-DesignFlow-LvlshftStepFix-001` (r667)

## trace 摘要

用户 e0025730 在 hfeg0plg49 上调用 `/lvlshft` skill（Level Shifter 电路设计优化工具链
统一 CLI）。agent 探查 `lvlshft_optimize/01_lvlshft_spec/` 下 lvlshft.py / run_pipeline.py /
soa_selector.py / render_sp.py 等代码，定位到一个 **--step 参数传递 bug**：

- `lvlshft.py` `build_pipeline_cmd()` 第 136 行：`cmd += ['--step', ','.join(args.step)]`
- `args.step` 是 argparse 解析出的 **字符串**（`'verify'` / `'optimize,verify'`），不是列表
- `','.join('verify')` → `'v,e,r,i,f,y'`（把每个字符当元素）
- 下游 `run_pipeline.py` 收到 `--step v,e,r,i,f,y`，校验 `v/e/r/i/f/y` 都非合法步骤名，
  报 `[FAIL] 未知步骤: v, e, r, i, f, y` 并退出

agent 用 editor 把 `','.join(args.step)` 改为 `args.step`（直接传字符串），然后多轮验证：
- dry-run `--step verify` → 输出含 `--step verify`（不再 `v,e,r,i,f,y`）
- dry-run `--step optimize,verify` → 输出含 `--step optimize,verify`
- 真跑 `lvlshft.py list` / `status` / `result` 均 exit 0
- grep 确认无其它 `','.join(` 残留

## case 取材决策

trace 原 lvlshft 全套工具链在 e0025730 私有 home（`/home/e0025730/devops/...`），
.75 SSH 身份无权读取，不可直接复现。但 trace 的 assistant text + editor diff +
dry-run 验证输出完整保留了 **精确 bug 根因 + 精确修复 + 精确验证命令**，足以做
**B-grade synthesized reframe**：

- 按 trace 精确结构合成最小可复现 `lvlshft.py`(buggy) / `run_pipeline.py`(下游) 对
- buggy 行 = `cmd += ['--step', ','.join(args.step)]`（与 trace 完全一致）
- 修复 = `cmd += ['--step', args.step]`（与 trace editor diff 完全一致）
- L2 真跑 candidate CLI 的 `--step` / `--from` / `--dry-run` 单步 + 多步 + 隐藏 B
  （4 步不同拓扑 Vcc2Vnn2vpp）做反硬编码判分

## 判分设计（10 条独立断言）

| # | 条件 |
|---|------|
| a | submit.zip 是合法 zip 且含 lvlshft.py |
| b | 修复后 lvlshft.py 不再含 bug 模式 `.join(args.step)` |
| c | 修复后 lvlshft.py 含正确修复 `['--step', args.step]` |
| d | subprocess 跑 `run Vcc2Vdleq --step verify --dry-run` 输出含 `--step verify` 且不含 `v,e,r,i,f,y`（单步）|
| e | subprocess 跑 `run Vcc2Vdleq --step optimize,verify --dry-run` 输出含 `--step optimize,verify`（多步）|
| f | subprocess 真跑 `run Vcc2Vdleq --step verify`（无 dry-run）exit 0 且无 `[FAIL]`（端到端）|
| g | subprocess 隐藏 B 跑 `run Vcc2Vnn2vpp --step sizing,fill,optimize,verify --dry-run` 输出含 4 步（反硬编码）|
| h | `--from` 处理保留：`run Vcc2Vdleq --from optimize --dry-run` 输出含 `--from optimize` |
| i | 无回归：`list` 和 `status` 子命令均 exit 0 |
| j | 修复后 lvlshft.py 是合法 Python（可编译）|

## negatives（3 个，全部 FAIL）

- `neg_split_tokens.py`: `cmd += ['--step'] + args.step.split(',')` —— 多 token，下游只取第一个
- `neg_pass_silent.py`: `pass` —— 直接丢弃 `--step`
- `neg_first_char.py`: `args.step[0]` —— 只取首字符

## §4.9 degenerate fakes（3 个，全部 FAIL）

- `deg_empty`: zip 里没有 lvlshft.py
- `deg_unchanged`: 原 buggy lvlshft.py（未修复）
- `deg_placeholder`: `print("fixed")` 占位

## 自验

- reference_submit.zip（lvlshft_bugfree_REF.py）→ CHECK PASS（10 条全过）
- 3 negatives → 全 FAIL correct
- 3 degenerates → 全 FAIL correct
- buggy 原版 → CHECK FAIL at cond [b]（bug 模式仍在）
