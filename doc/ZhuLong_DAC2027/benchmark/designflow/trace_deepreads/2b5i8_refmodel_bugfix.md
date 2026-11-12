# Deep-read: 2b5i8 — RefModel bug 定位+精修 (RefModelBugFix-001)

- **session**: `1793705624840_2b5i8` (102 msgs / 602KB, session 目录 autofs)
- **user**: e0039602 @ hfeg0pkn002
- **match_count**: 137 (digital, verilog:745)
- **shard**: A · round r445 · status: **case** (EDA-Eval-DesignFlow-RefModelBugFix-001)
- **lineage**: 同 user r428 verilog_lib_trans 项目, 但 deliverable 零重叠

## 三个 user turn

| turn | 内容 | 类型 |
|---|---|---|
| U#1 | 核 result_map dlybias1500ps 极性(1500ps 延迟极性写反) | 调试 Q&A |
| **U#67** | tb_ffq RefModel blocking `_q = D` 应改 NBA `_q <= D`(posedge Ck DFF) | **produce-task** (lead) |
| **U#84** | tb_xord2 RefModel `((A^B)^(~AN^~BN))` 应改 `(A ^ B)`(差分 XOR 冗余项) | **produce-task** (lead) |

## A-faithful 判定: 合格

U#67/U#84 均 produce-task(修 RefModel bug)且**未给根因**——用户只说"同事改好了, 帮我对一下", agent 须自己读 repo vs fixed diff 定位 bug 行 → A-faithful 合格。

deliverable = 修私有 `/home/e0039602/Documents/verilog_lib_trans_v2/` 下 .sv 文件 → SUT 沙盒不可达 → INFEASIBLE → B档合成。

## B档合成设计 (RefModelBugFix-001)

**新 archetype**: `refmodel-bug-localizer-surgical-fixer`

deliverable = `refmodel_bug_fix.py` — 通用 RefModel bug 定位+精修脚本:
- 输入: `--repo <dir> --fixed <dir> --candidates <list.txt> --out <dir> --report <json>`
- 按 LHS 变量名配对 RefModel 行(`assign <var> = ...` / `always @(...edge...) <var> <=|=`)
- 定位 buggy 文件(RefModel 行与 fixed 不一致), 其余记 match
- 精修: 只替换 RefModel 行, 保留用户加装探针/flag, 写到 --out
- JSON report: `{candidates[{file,status,diff_lines[{var,buggy,fixed}]}], buggy_file, buggy_count}`

### 可见输入 A (tb_xord2 XOR 表达式 bug)
- `repo_A/tb_xord2.sv`: `assign Y_model = ((A^B)^(~AN^~BN));` (buggy) + 用户加装 `diff_rail_chk` 探针
- `fixed_A/tb_xord2.sv`: `assign Y_model = (A ^ B);` (同事修好, 无探针)
- `repo_A/tb_xnor2.sv` / `tb_xnord2.sv`: repo==fixed, match

### 隐藏输入 B (tb_ffq blocking→NBA bug, 不同 bug 模式)
- `hidden/repo_B/tb_ffq.sv`: `always @(posedge Ck) _q = D;` (buggy, blocking) + 用户加装 `tog_cnt` 探针
- `hidden/fixed_B/tb_ffq.sv`: `always @(posedge Ck) _q <= D;` (NBA)
- `hidden/repo_B/tb_dff.sv` / `tb_dffr.sv`: repo==fixed, match

**核心 trap**: B 用 blocking→NBA 模式 vs A 用 XOR 表达式模式 → 击败 hardcoded_A(把 A 的 XOR 修法写死的 stub 在 B 上对不上)。

## 判分 (check.py, 17 条 a–q)

- 独立 oracle: 纯 string-method(find/split/手动引号检测, NO regex)vs ref LHS-key regex → 结构分化避同 bug 互掩
- ⑨非 RefModel 行逐行对账(oracle string-replace 一致)
- ⑧tog_cnt + ⑮diff_rail_chk 双探针保留
- ⑯跨输入守卫: A=tb_xord2 且 B=tb_ffq(双向击败 hardcoded)
- ⑰3 次确定 sha256 稳定

自验: ref SELFTEST 17/17 PASS; 5neg(naive_empty/print_only/copy_fixed_only/hardcoded_A/core_removed)全 FAIL; §4.9 fake-submit 3 形全 FAIL; NEG_RC=0; k_rationale=k_check=17 ✓
