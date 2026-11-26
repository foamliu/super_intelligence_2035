# 深读 · e3sf0 (ronghu@hfeg0pkn005 mc=192) — SiliconSmart inst add_function 诊断+修正

## trace
- session: 1793929850205_e3sf0.messages.json (474KB, 16 msgs, 8 user, GLM-5.2)
- 用户: ronghu，DRAM SiliconSmart 表征工程师
- 附件全部 NFS 可读: dynamic_inv_dphalf.cdl.spf(1504B) + deck.cir(85KB) + deck.lis(18KB) + deck.mt0(12KB)

## 对话流
- U0: 给 dynamic_inv_dphalf inst 描述(supplies/pins/function/switching_set/forbidden_state) + 上传 cdl.spf+deck.* → "网表及报错文件已经上传，请分析问题在哪，inst如何修改"
  - inst 关键: add_function AbusDnN `!LatPreN&((!ABusDn&!LatRd1N)|(!ABusDn&!LatRd2N))`
  - 网表: dynamic_inv_dphalf 6 FET (MMN1 gate=ABusDn drain=AbusDnN, MMN2 gate=LatRd1, MMN3 gate=LatPreN, MMP9 gate=ABusDn, MMP0 gate=LatRd1N, MMP2 gate=LatRd2N)
- #3 ASST: 分析 deck.mt0 → tout__abusdnn__hl 全 failed（121 sweep 点），根因 add_function 错误: ABusDn=0 时 MMN1 栅极=0 不导通，输出只悬空保持高，永不下降
- U2: "请给出正确的完整的inst文件"
- #5 ASST: 给修正 inst，说明 add_function 根因（动态预充/求值节点在 ABusDn=0 时下拉 MMN1+MMN2 不导通）
- U3: 给 DbusRcvnew_DbusMg inst（同 #424 scut3 的 cell）+ 附件
- #7-11: agent 用 ask-eda skill 查 SiliconSmart state 命令，分析 DbusL 从不翻转（RCP→DbusL 弧）
- U6: "请给出完整的Inst" → #13 给 DbusRcvnew_DbusMg 修正 inst
- U7: "请写出dynamic_inv_dphalf的inst文件" + 附加 cdl.spf → #15 给 dynamic_inv_dphalf 完整 inst

## 任务定位（本轮 case）
- 聚焦 dynamic_inv_dphalf 的 inst add_function 诊断+修正（U0→U2 produce-task）
- 输入: SiliconSmart inst(buggy add_function) + CDL 网表
- 输出: diagnosis.json(根因分析) + inst_fixed.txt(修正 inst)
- 核心能力: 解析网表晶体管拓扑 → 推导输出下拉/上拉路径 → 对比 inst function → 定位不匹配根因 → 修正
- D-domain ✓ (analog_context / SiliconSmart 表征)
- 真实资产 dynamic_inv_dphalf.cdl.spf 可读 → A 档用真实网表
- 与 #424 InstArcDiagFix 区别: #424 是 arc 在某 state 下不可造(state_partitions 抑制)；本 case 是 add_function 与拓扑不符导致输出永不翻转(function 重写)

## gold standard
- 根因: add_function 的下拉条件 (!ABusDn) 与实际 NMOS 下拉栈 (MMN1 gate=ABusDn 需 ABusDn=1 才导通) 矛盾
- 修正: add_function 应反映 AbusDnN 在 ABusDn=1&LatRd1=1 时被下拉；预充高在 LatRd1N=0/LatRd2N=0
