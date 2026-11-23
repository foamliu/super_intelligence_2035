# deepread — 1795244789633_tdbkn · PCell .il 批量改库名 + 删 cell 名后缀

- **session**: 1795244789633_tdbkn.messages.json
- **user / host**: hktklin @ hfeg0pkn003 (IP 10.129.2.12)
- **agent**: lead (cline)
- **mc**: 205 · domain: layout_virtuoso (SKILL PCell dbcreaterect/dbcreatepath 重)
- **msgs**: 77 · size: 310KB
- **trace keywords**: cellview:403; dbcreaterect:251; virtuoso:224; ddgetobj:111; dbget:99; dbcreatepath:69

## 真实任务（用户原话，3 次重复）
> 如下路径 /proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/L20/AMN3P/ 文件中内容为 tap_p 的改为 lacaa_common，内容 _SKILL 删除

即：对该目录下 SKILL PCell 定义文件（.il）做两件事：
1. `ddGetObj("tap_p")` → `ddGetObj("lacaa_common")`（文件中所有 tap_p 出现处都改）
2. cell 名字符串里的 `_SKILL` 后缀删除（如 `"common_tap_L20_coner_pcell_SKILL"` → `"common_tap_L20_coner_pcell"`）
文件名保持不变，只改文件内容。

## trace 关键路径
- 目录 `/proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/L20/AMN3P/` 含 7 个 `*_SKILL.il` PCell 文件 + 1 个 readme。每个文件第一行：`pcDefinePCell(list(ddGetObj("<lib>") "<cell>" "layout") ...)`，body 为 `dbCreateRect` / `dbCreatePath`。
- agent 受 agent-policy-engine 约束：目标目录不在 writableRoots（只有 `/ai_sandbox/lacaa/...` 可写）。editor 直接写被拒（"Write target is outside policy.writableRoots"）。
- agent 转用 run_approved_command：先试 shell-runner `sed -i` → "Dynamic profile 'shell-runner' requires filePath"（shell-runner 必须给脚本文件路径，不能 `-c`）。
- 建了 `fix_tap_p.py` / `fix_tap_p.sh` / `fix_tap_p_v2.py` / `verify_tap_p.py` 一组脚本，用 python-runner / shell-runner(filePath) 执行。
- **关键坑**：shell-runner 的 `sed -i` 在部分文件上没真正落盘（`common_tap_L20_edge_lr_fin2_pcell_SKILL.il` 反复显示残留 tap_p/_SKILL），最终用 Python `open().write()` 直写文件系统才生效。
- 用户 3 次重复同一指令（msg 0/33/41/55/67），agent 每轮重新 verify，最后一轮 fix_tap_p_v2.py 用 `[MODIFIED]`/`[NO CHANGE]` 标注 + verify_tap_p.py grep 确认 8 文件全 clean。

## 7 个 PCell 文件（AMN3P 目录，按 trace 还原）
| 文件 | 原 lib | 原 cell 名 | 处理 |
|---|---|---|---|
| common_AMN_L20_pcell_SKILL.il | lacaa_common | common_AMN_L20_pcell | 已正确，幂等 |
| common_tap_L20_coner_pcell_SKILL.il | tap_p | common_tap_L20_coner_pcell_SKILL | 改 lib + 删 _SKILL |
| common_tap_L20_H_pcell_SKILL.il | tap_p | common_tap_L20_H_pcell_SKILL | 改 lib + 删 _SKILL |
| common_tap_L20_lr_fin2_pcell_SKILL.il | tap_p | common_tap_L20_lr_fin2_pcell_SKILL | 改 lib + 删 _SKILL |
| common_tap_L20_edge_V_pcell_SKILL.il | lacaa_common | common_tap_L20_edge_V_pcell_SKILL | 仅删 _SKILL |
| common_tap_L20_edge_coner_pcell_SKILL.il | lacaa_common | common_tap_L20_edge_coner_pcell | 已正确，幂等 |
| common_tap_L20_edge_lr_fin2_pcell_SKILL.il | tap_p | common_tap_L20_edge_lr_fin2_pcell_SKILL | 改 lib + 删 _SKILL（最难落盘的那个） |

## reframe（A-faithful produce-task）
原会话依赖 live Virtuoso 文件系统 + agent-policy shell-runner/python-runner，无法离线判分。reframe 为纯 stdlib 通用参数化重构工具：
- 交付 `pcell_refactor.py`，CLI `python3 pcell_refactor.py <input_dir> <old_lib> <new_lib> <suffix> <output_dir>`
- 全局字符串替换 `<old_lib>`→`<new_lib>`、删除 `<suffix>`（忠实 trace 的 sed 语义），仅处理 *.il，文件名不变，body 不动，幂等。
- A=sample_a 7 个 .il + readme（tap_p→lacaa_common, _SKILL）
- B=hidden 5 个 .il（test_lib→prod_lib, _DEV），文件名与 A 完全不 disjoint → 反硬编
- check.py 16 断言：zip+py_compile+B 运行 exit0+B 5 文件齐+B 每文件 lib+cell oracle+无 old_lib 残留+无 suffix 残留+pcDefinePCell 结构保留+body dbCreate 不变+反硬编 mux_l2_pcell+3-seed 一致+A 可见输出正确

## 自验
- ref pcell_refactor.py 跑 A → 7 文件 lib=lacaa_common / cell 无 _SKILL / body 不变 / 无 tap_p 残留 ✓
- ref 跑 B → 5 文件 lib=prod_lib / cell 无 _DEV ✓；幂等（再跑 A 输出 diff 空）✓
- check.py golden PASS；§4.9 三假(empty_shell/print_only/delete_core)全 FAIL；3 negatives(libonly/hardcode/breakbody)全 FAIL；3-seed 一致 ✓

## 选料笔记
- tdbkn fresh（4-shard ledger 4507 stems union 中无此 slug）· mc=205 · layout_virtuoso 域（dbcreaterect:251/dbcreatepath:69 强信号）· 子型 `pcell_lib_rename` 首例（SKILL PCell 文件批量改库名+删 cell 名后缀的通用重构工具，与 r991 stdcells_classify cell-name 解析、r970 库 cell 枚举正交）。
