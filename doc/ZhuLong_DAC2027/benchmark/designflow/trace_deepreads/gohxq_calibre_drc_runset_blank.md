# 深读笔记 — gohxq (calibre DRC runset "Layout Path cannot be blank")

- **session**: `1795228793423_gohxq.messages.json`
- **user/host**: felixw @ hfeg0pin004 (10.129.32.237)
- **match_count**: 29 (drc:430 / calibre:158 / .gds:37 / aether:23 / cmos:5 / pyaether:2 / pex:2 / lvs:2)
- **size**: 164785 bytes, 10 msgs (user 1 + assistant 4 + tool_results 5)
- **trace_source**: 真实 calibre DRC 调试 (keyword .gds+calibre+drc 难以被项目名膨胀, 真实物理验证域)
- **fresh**: 本轮首次发现, 不在 4-shard ledger (r1529 选料, prior r1528 仅 peek 最新 scan top-40 误判池耗尽)
- **domain**: physical_verify (shard C)

## 用户原话
> `/proj/drgqx/V0/agentdir/felixw/DRC_test/debug/` 这个是我跑DRC的一个路径，我直接使用 `calibre -gui -drc -runset drcRunset -batch` 这个命令跑的，我在 runset 文件中设置了 layout path，为啥还会报出 `Calibre Interactive Error: Layout Path cannot be blank` 这个错误

## assistant 工具链
1. `list_allowed_files` (debug/ 目录) → 发现 drcRunset, .drcRunset.swo, .drcRunset.swp (VIM 交换文件), test1.gds 等
2. `read_files` drcRunset → 第4行 `*drcLayoutPath: /proj/drgqx/V0/agentdir/felixw/DRC_test/test1.gds` 确已设置
3. `list_allowed_files` + `read_files` 其他线索文件
4. 输出诊断报告 (3456 字)

## assistant 诊断 (3 根因)
1. **`-runset` 相对路径 + symlink/CWD 解析**: CWD=`/ai_sandbox/drgqx/...` 但 runset 写 `/proj/drgqx/...`, 若 `/proj`→`/ai_sandbox` 是 symlink/mount, Calibre Interactive 在 `-gui` 模式解析相对路径 `-runset drcRunset` 时 CWD 解析与 shell 不一致 → 找不到/读不正确 runset → layout path 视为空。**解决**: 用绝对路径 `-runset /proj/.../drcRunset`。
2. **VIM 交换文件残留损坏 runset**: 目录有 `.drcRunset.swo`/`.drcRunset.swp`, 说明 runset 在 VIM 中非正常关闭, 文件尾可能有残留数据/编码问题, Calibre 解析到 layout path 行失败 → 值为空。**解决**: `rm -f .drcRunset.swo .drcRunset.swp` + 重新创建干净 runset。
3. **`-gui -batch` 模式特殊行为**: `calibre -gui -drc -batch` 可能先尝试从 Viewer (版图浏览器) 获取 layout path, 若无 viewer 连接则报 blank。

## 合成计划 (下一轮 r1530 交付)
- **任务形态**: debug-Q&A (合法真实意图, 2026-11-15 令) — 给定 DRC debug 目录快照 (drcRunset + .swp/.swo + 目录树 + 报错串), 产出根因诊断报告 (JSON/MD), 必须独立可失败断言 ≥8。
- **判分有牙设计**:
  - hidden B: 另一套 debug 目录 (B 的 runset 有不同根因组合, 例如 B=只有 symlink 问题无 swp; B2=swp 残留 + layout path 写在注释行被忽略), 不同于 A
  - 断言独立可失败: ① 报告解析为结构化 JSON ② 识别 "Layout Path cannot be blank" 是 Calibre Interactive(-gui) 特有 ③ 识别 runset 第N行 *drcLayoutPath 已设置 ④ 识别 .swp/.swo VIM 交换文件残留 ⑤ 识别相对路径 vs 绝对路径 / symlink 解析风险 ⑥ 给出绝对路径修复 ⑦ 给出 rm swp/swo 修复 ⑧ 识别 -gui -batch viewer 行为 ⑨ B 场景根因集合正确 (不同于 A) ⑩ 确定性
  - §4.9 trio: 空壳/只打印"VIM问题"/删核心诊断 全 FAIL
  - negative: always-blank-diagnosis / hardcode-A-根因 / miss-swp
- **LIVE 判定**: LIVE-NA (deliverable=诊断报告文本分析, 不需真跑 calibre; check 用独立 oracle 比对根因集合, 非 EDA 工具产物依赖)。注意: 若设计成"产出一键修复脚本并在 .75 真跑 calibre 验证 PASS"则升 LIVE-REQ, 但那超出原用户意图(用户只要解释为啥报错), 不为实跑而实跑。
- **资产**: 需从 .75 scp felixw 的 debug/ 目录快照 (drcRunset + .swp/.swo + 目录树) 作为 A 附件; B 自造 (反根因组合, 不同文件名/路径)。
- **DEBT**: 本轮 (r1529) 仅深读 + 选料, 未合成 case。下一轮 r1530 按 此计划 交付 1 条 case。

## 跨域清账
- **gccyq** (xmxu@hfeg0plg93 mc29, drc:961/lvs:670): 实为 Verilog xrun gate-level 仿真调试 (dut.v vs gld.v, 比对 vec/stg mismatch), keyword drc/lvs 来自项目名 "drcpa" + simlib_LVS.sv 库文件名膨胀, 非真 DRC/LVS。**归属 shard A (verification)**, 本轮 park 不自造 (防串台)。
