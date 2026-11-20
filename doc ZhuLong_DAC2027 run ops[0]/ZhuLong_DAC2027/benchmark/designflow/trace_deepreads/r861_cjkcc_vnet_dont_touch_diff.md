# 深读笔记 — 1795145070388_cjkcc (alan3zh / hfeg0plg80 / mc=56 / pnr_signoff)

**trace**：`/home/alan3zh/.cline/data/sessions/1795145070388_cjkcc/1795145070388_cjkcc.messages.json`（508KB / 29 msgs，agent=lead，updated 2026-11-20T03:31Z）
**scan**：ssh_eda_search_20261120_145529，shard A fresh 候选（r860 CLAIMED，r861 合成交付）
**cwd**：`/home/alan3zh/workspace/test_chip/test_chip_v1_svt/power/rtl_power/`
**keywords**：rtl:164;synopsys:22;innovus:16;netlist:9;verilog:8;.cdl:4;lvs:2;genus:2;.gds:2;.def:2;primetime:1

## 用户意图 (U#0，单轮核心，逐字)
「工作目录严格限制在/home/alan3zh/workspace/test_chip/test_chip_v1_svt/power/,读取./rtl_power/下的hl22_porting_test_chip_v1.v和hl22_porting_test_chip_v1_dont_touch.tcl，完成如下事项：1. 写一个脚本，提取.v中的名称，存入单独文件；2. 对比输出的文件内容和dont_touch.tcl中的instance名称，列表总结两份文件中不一样的地方」

= 数字后端 power RTL 工程师对门级 Verilog 网表与 dont_touch 约束 tcl 做"名称核对"：提取 .v module 名 + instance 层级全路径；提取 tcl set_dont_touch [get_cells ...] 路径；列表对比不一致（一致/仅tcl/仅.v 三类）。

## agent 工具链 (29 msgs, 单轮闭环)
list_allowed_files → read_files(.v + .tcl 分批) → editor 写 extract_v_names.py → editor 清死代码 → run_approved_command(python-runner) 跑脚本 → read_files(compare_report) 核验 → editor 写 verify_outputs.py → run_approved_command 跑校验 → list_allowed_files 确认产物 → 文字总结。

## 真实输入 (A，已 scp 到本地 assets，A档 trace-faithful)
- `hl22_porting_test_chip_v1.v` 120340 字节 / 2805 行 / **13 module**
- `hl22_porting_test_chip_v1_dont_touch.tcl` 114369 字节 / 1310 行 / **1308 条 set_dont_touch**（0 条 placement_pair 注释）

## 真实结果 (参考解 extract_v_names_ref.py 在真实 A 上跑，本地实测)
- 13 module / **1904 instance 层级全路径** / 1308 tcl 路径
- **一致 1308 | 仅 tcl 0 | 仅 .v 596**
- 仅 .v 组：TOPPMBLK_Blk4129(212) / TOPTMINVRINGBLK_Blk4120(184) / TOPTMNOR2RINGBLK_Blk4122(184) / TOPTimingMeasureMUXBLK_Blk4119(16)
- 即：tcl 的 1308 条路径全部能在 .v 层级中解析（tcl ⊆ v），596 个 .v instance 无 dont_touch 覆盖（普通单元，正常）。

## ⚠️ 关键保真发现：trace agent 自报数字为幻觉
trace msg28（assistant 文字总结）自报：「tcl 实际 5480 行」「tcl 提取出 5223 条路径」「256 条 placement_pair 注释行」「tcl 多出 7 个整块（TOPTMNAND2RINGBLK_Blk4121 等）共 3915 条路径，占 75%」。
**经核（在 .75 上 wc -l + grep -c + 跑 agent 自己的脚本于真实文件）：全错。**
- 真实 tcl = 1310 行（非 5480）；set_dont_touch = 1308 条（非 5223）；placement_pair 注释 = 0 条（非 256）；仅 tcl = 0 条（非 3915）；不存在"7 个 tcl 多出整块"。
- 唯一巧合：自报「一致 1308」恰好等于真实 tcl 路径数（因真实 100% 一致）。
- 推测成因：agent 早期 read_files 误把"请求行号区间"当"文件总行数"（msg18 自承"之前 read 的截断提示 of N 是我请求的行号而非文件总行数"），其后 5223/5480/256/3915 等数字疑似在此基础上幻觉放大；verify_outputs.py 的 stdout「dont_touch_tcl_names.txt=5223」亦与真实 1308 不符（疑 stdout 被 hallucinate 或当时 tcl 文件状态不同）。
- **对本 case 影响**：本 case 忠实用户原始意图（提取+对比），判分用独立合成 B + 独立 gold oracle，不依赖 trace agent 的自报数字。真实 A 的结果（1904/1308/一致1308/仅tcl0/仅v596）由参考解在真实文件上实测得出，作为 task_brief 的"真实结果"记录。

## case 合成 (r861)
- task_id: `VnetDontTouchDiffProduce-001` · domain: pnr_signoff · A档 trace-faithful produce-task
- A（SUT 可见）= 真实 .v + .tcl（assets/A/）
- B（隐藏判分）= 合成 tc_power_chip.v (7 module/10 路径) + tc_power_chip_dont_touch.tcl (9 路径)，含 tcl-only 块 DloopBlk_B99 + 注释剥离测试（commented_inst_B99 + CommentedCell_B88）
- check.py 自包含（B base64 内嵌），独立 gold oracle（与 SUT 实现无关），14 条独立断言 k=14 ≥ 8
- ref PASS 14/14 + 3 neg FAIL（空壳 11/14 / 只print硬编A 10/14 / 删注释剥离 6/14）+ §4.9 三假全 FAIL
- 落库：`cases/A/VnetDontTouchDiffProduce-001.json`（op-order V：cases/ 为唯一 source of truth，不写 jsonl）
- ledger A: 1795145070388_cjkcc claimed→case（case 413→414, pnr_signoff 45→46）

## 教训
- trace agent 自报统计数字不可全信，须用真实文件 + 独立脚本复核（本轮发现 5223/5480/3915 全幻觉）。
- .75→本地无共享 FS/无直 ssh，经 MCP HTTP /mcp JSON-RPC read_file 桥接（curl+python urllib，二次 json.loads 取 .content）把真实 .v/.tcl（120KB+114KB）拉到本地 assets。
- op-order V（15:24 并发落地）删 shard jsonl，切 cases/<shard>/<id>.json；本轮据此改写落库路径，不碰 jsonl。
