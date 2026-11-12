# 深读笔记 · s9bc9 (e0039602@hfeg0pkn002, mc391, digital/verilog)

> session: `1793957377461_s9bc9.messages.json` (247 msgs, 1.7MB, 2026-11-09)
> 候选来源: 11/09 scan summary.tsv, clean-A-domain fresh, mc≥10

## 用户真实意图（5 轮迭代）

1. **r1 [msg 0,4]**: 用 `verilog_lib_trans_skill` 转换 `final_merged_netlist_digitial.v`，白名单 `block_name_digital.log`（279 module / 1755 instance）。原 skill 每 module 调 LLM API → 后台跑被 SIGKILL（量大超时）。
2. **r2 [msg 56]**: 杀掉后台进程。
3. **r3 [msg 64,65] — 核心需求**: 「转换功能不要依赖调用大模型接口，你自己实现，逐个写入完成检查修改」→ 把 skill 改成确定性规则引擎，零网络/零 token。
4. **r4 [msg 141]**: 把所有机械转换需要的代码 copy 到 `verilog_lib_trans_skill_aifree` 独立目录，可单独使用。
5. **r5 [msg 157,226]**: 用 `tb_family`（Xcelium xrun 功能对拍）测试转换结果 PASS 多少；再转 `stdcells_ac.v` 测一遍。

## agent 工具链（关键产物）

- `list_allowed_files` / `read_files` / `search_codebase` 读 skill 源码（rules_engine.py / netlist_parser.py / rules_prompt02.py / run_skill.py / simlib_base.sv）
- `editor` 新建 `src/deterministic_convert.py`（确定性引擎核心）+ `run_skill.py` 改 `--engine {deterministic,llm}` 默认 deterministic
- `run_approved_command` 跑验证：`_verify_det.py`（405 ok/612 unsupported）、`_summary.py`、`_make_aifree.py`（独立包）、tb_family `_run_one_shot.py`（xrun 对拍）
- 修 2 个 bug：① `rules_engine` 大小写致 `invYx4` 误落 `inv_base`（应 `invYx_base`）② `tb_family/_portmap.py` 解析 `PIN(net)` 端口语法失败致 xrun `EXPIDN` 错

## 核心转换规则（确定性，写死在 rules_engine.py）

**门族前缀 → base 单元映射表**：
| cell 名前缀 | 转成 | 输入处理 |
|---|---|---|
| `invY*` | `invYx_base` | 直传 |
| `inven*` | `inven_base` | 直传 |
| `invhiz*` | `invhiz_base` | 直传 |
| `inv*`（纯） | `inv_base` | 直传 |
| `fbs/fbr/fbenr/fbens/fbrs/fbsr` | 对应 `*_base` | 直传 |
| `nand*` | `inv_base` | `.A(A & B & ...)` 输入合并 |
| `nor*` | `inv_base` | `.A(A | B | ...)` 输入合并 |
| `aoi*` | `inv_base` | `.A((A&B)|C)` (aoi21) / `.A((A&B)|(C&D))` (aoi22) |
| `oai*` | `inv_base` | `.A((A|B)&C)` (oai21) / `.A((A|B)&(C|D))` (oai22) |

**电源脚改名表**: `vcc→vcc_`, `vss/vssz→vss_`, `vbn→vbulkn_`, `vbp→vbulkp_`

**全转或全不转**: module 内任一 cell `try_convert` 返回 None（非门族 / 端口不齐 / 缺脚）→ 整 module `[UNSUPPORTED]`，不产半成品。非门族 = `lat*/ff*/dff/mux/mx*/xor*/ntn/ptn/passgt/buf*/trim*/cap*` 等。

**ok module 处理**: 保留原 module 端口表 + input/output/inout 声明 + wire/reg 声明逐字不动，只替换缺失 cell 实例行。

## 实测数字（agent 报告）

- `final_merged_netlist_digitial.v`: 279 module → **80 ok + 199 unsupported**，final SV 1019 module=endmodule，0 残留标注，~1MB，秒级离线
- tb_family xrun 对拍（29 unique cell）: **23 PASS / 6 MISMATCH**（6 个 MISMATCH 是 `vwlp` 电源脚漏接，非合并逻辑错）
- `final_merged_netlist_stdcells_ac.v`: 883 module → 742 ok + 141 unsupported，tb_family 448/742 done → 419 PASS / 29 MISMATCH

## case 合成方向（B 档 synthesized, L2 spec-driven-gen, digital）

deliverable = `vlib_det_convert.py`（stdlib only，确定性，零网络）：接 `--netlist <v> --block-list <log> --out <report>`，产 result_map（per-module ok/unsupported + 转换后 module 文本）。
- A（可见）: 小样例 netlist + block-list + 转换规则说明 + simlib_base.sv 片段
- B（隐藏）: 不同 netlist（不同 module 名 / cell 名 / 电源脚），含可转(inv/nand2/nor2/aoi21/aoi22/oai21/invYx/inven) 与不可转(latch/FF/mux/xor) module
- check: 跑 B → 解析 result_map → 验 ok/unsupported 分类、门族映射正确（含 invYx≠inv_base 的 bug-fix）、表达式合并（nand→.A(A&B)）、电源改名、module 端口保留、unsupported 不产半成品、无网络调用、verilog 合法性
