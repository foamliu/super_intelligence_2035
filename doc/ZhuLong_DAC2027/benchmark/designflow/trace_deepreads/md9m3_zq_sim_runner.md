# md9m3 — ZQ Calibration HSPICE Deck Runner (run_sims.py)

**session**: `1794999211646_md9m3.messages.json` (57 msgs, 287KB)
**user**: alan17z @ hfeg0plg10 (注意：D 台账 r958 误记 host=hfeg0pkn004，实际 hfeg0plg10)
**mc**: 38 (hspice=229 dominant in body, B-spice)
**domain**: spice_sim / IBIS ZQ calibration
**case**: `EDA-Eval-DesignFlow-ZqSimRunnerProduce-001` (shard B, r1010)
**status**: case ✅

## r958 wrong-domain correction

r958 shard-D triage 只读了 msg#0（skill-creator "Context Engineering" meta-skill
设计任务的 wrapper），判定 off-domain meta-skill REJECT。**这是误判**。
真正的工作在 msgs 24-54：用户合并 3 个 IBIS skill 后，要求写 `run_sims.py` ——
参数化 hspice ZQ 校准 deck runner。r1010 重新 deep-read 全 conversation，确认
主线是 spice_sim produce（hspice 命令行跑 deck + $DATA1 结果解析），归 shard B。

## 用户真实意图（trace-faithful）

用户 alan17z 在 hfeg0plg10 上做 IBIS 模型提取流程。ZQ 校准阶段
（`gen_zq_decks.py`）产出 6 个 hspice deck 文件（命名
`{prefix}_{kind}{resistance}_pre_{corner}`，无扩展名），每个跑 64-code 扫描。
hspice 跑完吐 `$DATA1` sweep 结果文件（glob `<deck>*`），由 `parse_zq.py` 的
`parse_result(path)` 解析成 `[(index, code_str, resistance)]`（满 64 条）。

用户原话：
> hspice 在命令行是可以直接跑的，t2b 不用，生成 t2b 文件集我自己打开软件跑就行

→ scope = **hspice 自动化 + 参数化 runner**，t2b 文件集生成停在"用户自己开软件跑"。
本 case 取 run_sims.py 主线 reframe，不含 t2b 后处理。

## trace 里的 run_sims.py（关键逻辑）

- `discover_decks(dir, prefix, resistance, corners, kinds, dry)`：按模式发现 6 个
  deck，missing = hard error（exit 2）；dry 模式打 `[PLAN]` + result glob + would-run。
- `run_one(deck, args)`：`subprocess.run([hspice, deck, -o, deck], cwd=dir, timeout)`；
  returncode≠0 或 timeout = exit 3。
- `verify_result(out_glob, min_records=60)`：glob → `parse_result` → `len>=min_records`
  才算通过，返回 `(path, n)` 否则 `(None, None)`。
- `--dry-run`：只打 plan 不调 hspice，exit 0。
- `--gen-corners`：sims 全过后链 `merge_zq.py --gen-corners --corner <file>`。
- `parse_zq.py` 经 `sys.path.insert(0, dirname(abspath(__file__)))` 导入。

## reframe 为 design_flow case

| 维度 | A（可见） | B（隐藏） |
|---|---|---|
| prefix | `pdt` | `zq` |
| resistance | 40 | 60 |
| model | `model_A.sp` | `model_B_v2.sp` |
| pvcc / pvddq | 0.89 / 0.50 | 0.86 / 0.55 |
| deck 文件 | `pdt_r{pu,pd}40_pre_{ff,ss,tt}` | `zq_r{pu,pd}60_pre_{ff,ss,tt}` |

**五重反 hardcode-A**：prefix、resistance、model 名、电压、温度全不同。
A 标记 `pdt_rpu40`/`pdt_rpd40`/`pdt_`/`rpu40`/`rpd40`/`pvcc=0.89`/`pvddq=0.50`/`model_A.sp`
在 B 输出中必须全部缺席。

## 隐藏 B_corrupt（防 stub）

`dir_B_corrupt` 有 6 个 deck + 6 个 result，但 `zq_rpu60_pre_ff_result.txt` 只有
20 条记录（65 行 = 5 header + 60 data = 20 records，低于 min-records=60）。
- verify_result 对 corrupt rpu/ff → 必须 `(None, None)`
- verify_result 对 corrupt rpd/tt（满 64 条）→ 必须 `(path, 64)`

这是对 naive `return (path, 64)` stub 和 core-removed fake 的牙齿。

## check.py 12 断言（a-l）

1. (a) zip 含顶层 run_sims.py + py_compile + size>200
2. (b) --dry-run 在 B 上 exit 0
3. (c) dry-run 输出 6 行 [PLAN]
4. (d) B 标记 present + A 标记 absent
5. (e) ≥6 行 would-run/hspice
6. (f) 全部 6 kind/corner 组合
7. (g) discover_decks 返回 6
8. (h) verify_result B rpu/ff → (path,64)
9. (i) verify_result corrupt rpu/ff → (None,None)
10. (j) verify_result corrupt rpd/tt → (path,64)
11. (k) 源码含全部 CLI 参数 + verify_result 函数
12. (l) 3-seed dry-run sha256 一致

## 验证

- reference `run_sims_ref.py` → CHECK PASS 12/12 ✅
- neg_empty.py → FAIL (a: size 0) ✅
- neg_print_only.py → FAIL (g: discover_decks missing) ✅
- neg_core_removed.py → FAIL (i: corrupt 返回 fake 64) ✅

## 教训

1. **deep-read 不能只看 msg#0**：skill-creator wrapper 会把真实 EDA 工作藏在后续
   message 里。r958 只看了 msg#0 就判 off-domain，漏了 msgs24-54 的真 produce。
   今后 triage 至少扫 msg#0 + 最后 5 条 + body 里 `def `/`subprocess`/CLI 关键词。
2. **hspice-dominant filter 有效**：mc=38 但 hspice 关键词 229 次，远超 mc，说明
   body 主体是 spice 仿真代码。这种 kw/body 比值是比 mc 更强的 domain 信号。
