# trace_deepread: vxorx (1793091129423_vxorx) — Formality RTL2RTL flow

- **session**: `1793091129423_vxorx.messages.json`
- **user/host**: e0046913 @ hfeg0pkn003 (10.129.2.12), mc=159
- **size**: 240 msgs, single archive (no compaction)
- **domain**: verification (Formality RTL2RTL)
- **keywords**: rtl:2340 / verilog:642 / synopsys:268 / netlist:48 / icc2:9 / pdk:8 / vhdl:7 / synthesis:7

## 用户原始任务（USER#0）

> 在当前 /rundata/lacaa/TV1_digital/simdir/yutingq 目录下，参考 feint 文件内的 formality 相关脚本，
> 为我在 fm_r2r 目录下开发 rtl2rtl 功能，并使用 ref_verilog 和 imp_verilog 中的 test 案例去跑通。

USER#162 追加：跑通 1 ref (`cr_ifu_ibuf`) → 2 imp (`cr_ifu_ibuf_r2rQA1` + `cr_ifu_ibuf_r2rQA2`) 案例，
预期 PASS；并在结果处 echo 醒目的 PASS/FAIL ASCII 图案。

## 真实 5 轮迭代 + 4 个 bug 修复

1. **LD_PRELOAD 污染**：eda_agent 注入 `LD_PRELOAD=.../eda-agent/.../libstdc++.so.6`，让 `fm_shell`
   启动失败。修复 = launcher 里 `unset LD_PRELOAD`（smoke.sh 验证 fm_shell 可启）。
2. **FM-236 中止 imp 读入**：`read_verilog -i -f` 后报 "Top design has not been successfully linked
   in container 'r' (FM-236)"。根因 = container `r` 的 auto-top 未 link 会把后续 imp 读入一起打断。
   修复 = **`set_top r:/WORK/<ref_top>` 必须先于 `read_verilog -i`**（diag2.sh 确认 reorder 后 imp
   能载入全部 4 文件）。
3. **`set_dont_verify_points` 不生效**：QA1 的 32-bit `ifu_iu_ex_inst[31:0]` 被特意删除，期望用
   dont_verify 跳过，但 verify 仍 FAIL。三连修：
   - 加 `-type port`（端口名与同名 net 二义，`set_dont_verify_points r:/WORK/.../ifu_iu_ex_inst` 报 FM-036 Unknown name）；
   - 加通配符 `*`（端口被展开成 `name[bit]`，裸名解析不到）；
   - 用 **双引号** 不能用 `{}` 花括号（braces 阻止 `${ref_top}`/`${pt}` 变量替换 — puts 回显
     展开后形式但实际命令传字面量）。最终 `set_dont_verify_points -type port "r:/WORK/cr_ifu_ibuf/ifu_iu_ex_inst*"` → QA1 PASS。
4. **PASS/FAIL ASCII 图案**：用户要求结果醒目化。tcl 末尾按 `overall_pass` 分支 puts PASS/FAIL
   ASCII 字形。

## 最终交付物（均在 /rundata/.../fm_r2r/）

| 文件 | 说明 |
|---|---|
| `scripts/fm_r2r.tcl` | 核心 Formality 脚本（read ref → set_top r → read imp → 每 imp top set_top i+match+verify → dont_verify 通配 → PASS/FAIL banner） |
| `run_fm_r2r.sh` | launcher（unset LD_PRELOAD, 调 fm_shell） |
| `Makefile` | qa1/qa2/one2two/pass/all targets |
| `README.md` | 流程文档 |

4 case 全跑通：qa1=FAIL(32 unmatched ifu_iu_ex_inst) / qa2=FAIL(10 unmatched) /
one2two=FAIL / pass=PASS(88 passing, dont_verify 生效)。

## r405 B 档合成 plan（FmR2rFlowGen-001）

- **deliverable**: `gen_fm_r2r_flow.py`（纯 stdlib，`--spec <json> --out <tcl>`）
- **A (visible)**: spec_a — ref_top=cr_ifu_ibuf, imp_tops=[cr_ifu_ibuf_r2rQA1],
  dont_verify=[ifu_iu_ex_inst], report_dir=reports
- **B (hidden)**: spec_b — ref_top=cr_ifu_top, imp_tops=[cr_ifu_top_r2rQA1, cr_ifu_top_r2rQA2],
  dont_verify=[debug_inst, spare_out], report_dir=fm_reports (规模/名字/值全不同)
- **check.py**: 13 条件 (a-m)，解析生成 tcl 校验 4 个 bug 修复不变量（顺序、-type port+*+双引号、
  每 imp top set_top i+match+verify、PASS/FAIL banner、report 重定向、纯 stdlib、确定性），
  3 seed 随机化一致性。
- **negatives**: naive_empty / print_only / core_removed(顺序反) / no_dontverify_fix(花括号无-type无*)
  全 FAIL。
- **自验**: gold PASS 13/13, 4 neg FAIL, §4.9 (a)(b)(c) FAIL。断言闸门 k=13 ✓。
