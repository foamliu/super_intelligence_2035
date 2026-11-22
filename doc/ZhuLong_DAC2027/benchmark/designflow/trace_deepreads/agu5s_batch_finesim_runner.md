# agu5s — BatchFinesimRunner-001 深读笔记

- **session**: `1794833913565_agu5s.messages.json`
- **user / host**: willz @ hfeahpc501
- **mc**: 21 (spice_sim, summary_20261121_151844.tsv)
- **shard**: B
- **case_id**: `EDA-Eval-DesignFlow-BatchFinesimRunner-001` (short `BatchFinesimRunner-001`)
- **status**: claimed r1016 → case r1016
- **layer**: L1 (pure bash, mock-bsub checkable, no EDA binary)

## 1. 用户真实意图演进 (U0 → delivered)

- **U0** (msg ~0): "参考 run_all.csh 创建批量仿真脚本，bsub finesim 所有 sp"
  - 用户提供 `run_all.csh` 作为参考模板（递归 find .sp → bsub hspice）。
  - 用户要求换成 **finesim** 而非 hspice，且要批量覆盖目录下所有 sp。
- **U16** (~msg 16): 反馈 "U16 那个 re_ 的目录不要提交，debug 的也不要"
  - 要求跳过 `re_*` 子目录（已仿真输出）和 `debug` 子目录（调试用例）。
  - 此为关键过滤规则，写入脚本。
- **U28** (~msg 28): 反馈 "outdir 用 re_<basename> 但不要再套一层子目录"
  - 原 draft 输出路径 `re_<basename>/<subfolder>/<basename>.sp` 在嵌套目录下会重复子目录。
  - 修正：outdir = `re_<basename>`，内部 mirror 相对子目录结构但不重复 basename 层。
- **delivered**: `run_all_finesim.sh` — bash 脚本，递归 find .sp，skip re_*/debug，bsub -q fqueue3_ams -J fm_<basename> -n 4 finesim+ -np 4 -o <outdir>，outdir=re_<basename> mirror subfolder。

## 2. 交付脚本摘要 (run_all_finesim.sh)

```bash
#!/bin/bash
# 递归 find 当前目录下所有 .sp，跳过 re_*/debug，bsub finesim
set -e
ROOT="$(pwd)"
COUNT=0
while IFS= read -r sp; do
  rel="${sp#$ROOT/}"
  base="${rel##*/}"; base="${base%.sp}"
  # skip re_* and debug subdirs
  case "/$rel/" in */re_*/debug/*|*/debug/*|*/re_*/) continue;; esac
  outdir="$ROOT/re_${base}"
  mkdir -p "$outdir/$(dirname "$rel")"
  bsub -q fqueue3_ams -J "fm_${base}" -n 4 \
    finesim+ -np 4 -o "$outdir/$(dirname "$rel")" "$sp"
  COUNT=$((COUNT+1))
done < <(find "$ROOT" -name '*.sp' -type f | sort)
echo "submitted $COUNT finesim jobs"
```

关键行为：
1. 递归 find `*.sp`，sort 保证顺序确定性。
2. 跳过路径含 `re_` 或 `debug` 段的 .sp。
3. `bsub -q fqueue3_ams -J fm_<basename> -n 4`（队列名固定 ams，job 名前缀 fm_，4 核）。
4. `finesim+ -np 4 -o <outdir>`（finesim+ 变体，-np 4 并行，-o 输出目录）。
5. outdir = `re_<basename>` 顶层，内部 mirror 相对子目录（不重复 basename 层）—— U16 修正点。

## 3. reframing 成 benchmark case

- **produce task**: 参数化 `run_all_finesim.sh`，递归扫 .sp，过滤 re_/debug，bsub finesim。
- **A 附件** (`assets/BatchFinesimRunner-001/dir_A/`): 6 .sp 在不同子目录（tt_rcx/re_tt_rcx/、debug/），参考 run_all.csh。
- **hidden B** (`assets/BatchFinesimRunner-001/hidden/dir_B/`): 7 .sp，不同子目录（ss_corner/re_ss_corner/、debug/、lev2/inner/），不同文件名（tx_driver/tx_clk/tx_preamp/io_pad/esd_clamp），5 submit + 2 skip。
- **check.py 12 条** (a-l): zip/syntax、exit0、count match、set match、bsub call count、-q fqueue3_ams、finesim+ -np 4、-o with re_、basename-only outdir、no re_/debug submissions、anti-hardcode A markers、3x determinism。
- **3 negs**: empty(空→a size0) / print_only(只 echo→b 无 submit 记录) / core_removed(无过滤→j 漏过 re_/debug)。

## 4. distinctness check

- vs **ZqSimRunnerProduce-001** (r1010): ZQ hspice deck runner（单 deck 参数化生成 + 提交），本 case=递归批量 finesim 提交（多 deck 扫描 + 过滤 + bsub）。无重复 ✓。
- vs **BatchBsubHspice-001** / **BatchHspiceSubmit-001**: hspice 批量提交，本 case=finesim+ 且含 re_/debug 过滤规则（U16 真实用户意图），判分齿完全不同。无重复 ✓。
- vs **FineSimWorkflowRunner-001**: 单 deck finesim 工作流（option/measure），本 case=多 deck 批量 bsub 提交脚本。无重复 ✓。

## 5. 自验结论

- ref `run_all_finesim_ref.sh` → check.py PASS 12/12 ✓
- 3 negs → 全 FAIL-as-expected ✓（§4.9 三假齐）
- 3-seed determinism ✓（PYTHONHASHSEED=1/2/3 + 顺序 find sort 稳定）

## 6. followup

- r1016 落库：cases/B 519→520, B.jsonl 519→520, ledger_B agu5s claimed→case。
- 无 DEBT 遗留。
