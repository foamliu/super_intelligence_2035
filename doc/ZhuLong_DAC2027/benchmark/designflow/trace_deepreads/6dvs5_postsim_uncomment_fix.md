# trace 深读：6dvs5（reedchen @ hfeg0pkn002，FineSim 后仿网表取消注释 bug 修复）

- sid: 1794187865687_6dvs5 · user: reedchen · host: hfeg0pkn002(10.129.2.11) · 47 msgs/28 user · 219KB · mtime 2026-11-09
- 来源：11-05 重扫令 pkn125 fresh(≥11-06) 扫描，pkn002 reedchen kw=7，un-ledgered → scp 到 .75 peek → CLEAN
- 选用：A-faithful ✓（U#0 提需求，未给根因/修复）

## U#0 逐字原文（task 说明）
```
/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ReedChenWork_TB_DbusRcvWritePostSim/scripts/
我在这个目录下运行这个命令：python gen_sp_write.py --pvt ../../PVT_HighVolt.csv --template ../template/template.sp --outdir ../sim_run_pre/ --sim post
后仿的网表没有正确取消注释出来，请你帮我定位和修复bug
```

## 工具链（assistant）
1. list_allowed_files(scripts/) + get_agent_policy_status
2. read_files(gen_sp_write.py) + list(project, depth3) + list(template, sim_run_pre)
3. read_files(gen_sp_write.py L71-167) + list(template) + list(sim_run_pre)
4. read_files(template.sp, sim_run_pre/dbus_TT_8V25C.sp) — 发现 post 输出 line27(.inc spf)/31(XI_) 仍注释，仅 line28(.inc subckt) 解开
5. read_files(sim_run/dbus_TT_8V25C.sp[旧], PVT_HighVolt.csv)
6. read_files(agent-policy.json, run_all.sh) — 复现准备
7. editor(run_repro.sh) → run_approved_command → **复现 bug 确认**：post 输出 27/31 仍注释
8. list(/home/reedchen/script_dbus_rcv_write) + search_codebase → 找到真源
9. read_files(真源 gen_sp_write.py L137-167, deploy.py)
10. **editor 修复真源** `_netlist_cat()`：硬编码块名 → 模式匹配
11. editor 修复工程副本（被 writableRoot 拒）→ 改用 cp 同步
12. 重跑复现 → **修复后 post 输出 27/28/31 全解开，36 仍注释 ✓**
13. 回归 `--sim pre` → **pre 输出 36 解开，27/28/31 全注释 ✓**
14. 最终 sync + read 验证函数干净

## 根因（assistant M#29/M#46 定位）
`scripts/gen_sp_write.py` 的 `_netlist_cat()` 用**写死的旧块名** `DOutFIFOx1_Dmi_PN1p76_DbusMg` 分类后仿行：
- `t.startswith("XI_DOutFIFOx1_Dmi_PN1p76_DbusMg")` → inst
- `"DOutFIFOx1_Dmi_PN1p76_DbusMg.spf" in t` → post

但当前 `template/template.sp` 块名/实例名是 `latsqmuxPF_DPmux_Dbus_length46_rev0`：
- `.inc ...spf` 行：块名对不上 → None → 保持注释
- `XI_latsqmuxPF_...` 实例行：startswith 不匹配 → None → 保持注释
- 仅 `.inc .../subckt` 因含通用 "subckt" 被解开

`sim_run/` 旧文件能正确解开是因旧模板+旧匹配串；模板改了块名脚本没跟。

## 修复（金标准）
`_netlist_cat()` 改成**按模式匹配**，不依赖写死块名：
```python
def _netlist_cat(ln):
    t = ln.strip().lstrip("*")
    if t.startswith(".inc") and not t.startswith(".include"):
        path = t.lower()
        if ".spf" in path or "subckt" in path:
            return "post"
        if "netlist" in path:
            return "pre"
    if t.startswith("XI_"):
        return "inst"
    return None
```
`set_netlist_mode` 不变：active={"post","inst"}(post) 或 {"pre"}(pre)；c in active → lstrip("*")，else → "*"+lstrip("*")。

## 验证输出（修复后）
post 模式（dbus_TT_8V25C.sp 关键行）：
```
27:.inc "...latsqmuxPF_DPmux_Dbus_length46_rev0.spf.TYP_98_RCC"   ← 解开
28:.inc ".../subckt"                                              ← 解开
31:XI_latsqmuxPF_DPmux_Dbus_length46_rev0 Din0 ...                ← 解开
36:*.inc ".../netlist"                                            ← 保持注释(前仿行)
```
pre 模式（回归）：
```
27:*.inc "...spf"   ← 注释
28:*.inc ".../subckt" ← 注释
31:*XI_...          ← 注释
36:.inc ".../netlist" ← 解开
```

## 用户接受
trace 末轮 assistant 给出完整修复总结 + 验证；session 在此结束（无显式 U 回复但任务闭环，assistant 验证两模式均正确）。

## 案例化
- case_id: EDA-Eval-DesignFlow-PostSimUncommentFix-001
- domain: spice_sim · track: faithful(A) · level: L1
- A 资产: buggy gen_sp_write.py + template_A.sp(latsqmuxPF) + PVT_A.csv(9 corners)
- hidden B: template_B.sp(异块名 wbufMuxPF_RdPath_length52_rev3) + PVT_B.csv(异 corners) + template_C.sp(再异块名 rdqMuxPF_DqPath_length38_rev5，验泛化) + hidden_manifest.json
- 交付: outputs/submit.zip 含 fixed gen_sp_write.py
- check.py 10 断言: a(zip含py) b(py_compile) c(B post exit0+生成.sp) d(B post spf解开) e(B post subckt解开) f(B post XI_解开) g(B post netlist注释) h(B pre netlist解开) i(B pre spf+subckt+XI_全注释) j(C post[全新块名] spf+XI_解开=泛化)
- 3 negative: naive_uncomment_all(全解开,pre netlist应注释会失败) / hardcoded_A(只加latsqmuxPF名,B/C异名失败) / always_identity(不改,B post仍bug)
