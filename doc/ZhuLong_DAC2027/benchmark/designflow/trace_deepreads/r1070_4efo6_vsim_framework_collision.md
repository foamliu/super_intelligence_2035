# r1070 deepread: 4efo6 vsim 框架分析撞题 + parked revival 3 大风险

## 选料
- session: 1792118902296_4efo6 (e0039102@hfeg0pkn002, mc=567, digital)
- parked_reaudit_A.tsv: revivable=yes, new_cat=REVIVABLE_QA
- ledger 状态: **retired** (r1047), 原因: "与 VsimFrameworkAnalyzeProduce-001(qzx4z) 同主题且 Produce 版已 active" + "reference incomplete"
- 用户意图: "./bin/run_vsim_uvs_vps.pl 帮我看下这个文件框架" + 12 条概念 Q&A

## session 深读
- 492KB/83msgs (47 user/36 assistant)
- assistant 详析 vsim_vps 框架: 6 阶段 + 10 子程序 + irun/xrun + LSF bsub + VPS/UVS + LPDDR4/5/6/DDR5
- 真实代码级细节: genrunfile (line 1345-1358) 生成 verilogrun csh, irun +access+rwc +define+PROJECTNAME top.sv -input probe.tcl
- 12 条概念 Q&A: DUT/SDF/pin/前仿后仿/.v.sv是否RTL/vsim-verilogrun关系/数字前端后端/综合网表

## 撞题
- 已 synth 完整 case (A_proj + B_proj + check.py 14 断言 + 4 negative + selftest ALL OK)
- 发现 cases/A 已有 VsimFrameworkAnalyzeProduce-001 (qzx4z, sfeng@hfeg0pkn005, mc=73, r996)
- qzx4z: LPDDR6 dejoa vsim 框架分析, LP6TOP, Perl vsim, JSON 报告 — 同主题同 DUT 同项目同输出形式
- r1047 已因此 retired 4efo6
- cases/A 已有 8 个 Vsim* case + DDR4TbFramework

## 教训
1. **选料前必查 cases/A/ 同主题**: grep 关键词 (Vsim/Framework/DDR4Tb/...) 避让已有 case
2. **ledger retired 状态必读**: 4efo6 在 ledger 是 retired(r1047), parked_reaudit 标 revivable=yes 但 retired 原因(同主题)仍有效
3. **parked_reaudit_A.tsv revivable=yes 不代表可造**: 需交叉 ledger retired 原因 + cases/A/ 同主题

## parked revival 池 3 大风险 (r1070 观察)
1. **文件老化**: 4efo6 bin/vsim_vps(1869行) 已消失, uqv0 session 文件消失; 旧 session(10月)项目文件被清理
2. **同主题撞题**: Vsim* 已 8 case; revival 选料需先查 cases/A/ 避让
3. **ssh 嵌套 peek 慢**: 每条 ssh .75→host 2min 超时, 逐条 peek 效率低

## 下轮选料建议
- 优先等 11-24 scan fresh 候选(避免老化+撞题)
- 若续 revival: 选非 vsim/framework 主题 + 先 ssh 验证文件存活 + 先查 cases/A/ 同主题
- 候选优先级: env-config(jwwqf) / install(yhqp5) / 非 vsim 的 code-comp
