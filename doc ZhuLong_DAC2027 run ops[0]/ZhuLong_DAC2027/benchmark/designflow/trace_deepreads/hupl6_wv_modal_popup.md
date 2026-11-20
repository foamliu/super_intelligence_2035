# deepread: hupl6 — WaveView Zhulong.tcl 弹窗模态化修复

- session: 1793587957934_hupl6.messages.json
- user: yanxvwei @ hfeg0pkn002 (10.129.2.11), mc=8, domain=spice_sim
- trace: 25 msgs, 85KB, agent=lead (无 tool_calls 之外的 EDA 工具，纯 editor/read_files/run_approved_command)
- 旧判定: parked "tcl-source how-to Q&A" → r705 reaudit 复活

## 用户意图链（原话）
1. [msg1] 「原有的功能要保留啊，zl的页面启动之前，弹窗要存在」
   —— ZL 页面起来之前弹窗要一直在，就绪后自动关。
2. [msg7] 「弹窗不见了，查找原因并修改。你每次改完代码自己检查一遍」
   —— 改完后弹窗没建出来。
3. [msg19] 「我需要弹窗的时候wv主页面savesignal一样，会无法操作」
   —— 弹窗期间 WV 主页面不可操作（模态），像 saveSignal。

## 真实任务
修 /home/yanxvwei/Script/Waveview/Zhulong.tcl：建一个 ZL 启动前的模态弹窗，
bjobs 轮询检测 ZL agent_queue RUN 就绪后自动关；不卡死、不多弹窗。

## agent 三轮修复（trace verbatim）
- v1 [msg2 edit]: popup 建在根 `.` 上，开头 `catch {destroy .}` → 把 `.` 销毁，
  紧接 `label .zl_lbl`/`wm title .` 全报错被外层 catch 吞 → 弹窗消失（bug 1 根因）。
- v2 [msg10 edit]: `catch {destroy .}` → `catch {destroy .zl_lbl}`（只清子部件），
  弹窗恢复，但建在根 `.` 上、无 grab → 不模态。
- v3 FINAL [msg20 edit]: 独立 toplevel `.zl_pop` + `wm transient .zl_pop .` +
  `grab set .zl_pop`（模态锁主页面）+ bjobs 轮询（zl_run_ids 过滤 STAT==RUN 且队列含 "agent"）+
  就绪 `destroy .zl_pop`（自动释放 grab）+ 无 tkwait + 无 grab 根窗口。
- agent 自检 [msg14-18]: 写 _selftest.py，用 tclsh 跑非 Tk 部分（job 解析），
  喂样例 bjobs 数据验证 zl_run_ids 排除 wv job（base_run=2214920 正确）。

## case 合成
- task_id: EDA-Eval-DesignFlow-WvModalPopupTclFix-001
- 形态: A 档 trace-faithful + produce-deliverable（产 wv_modal_launcher_gen.py，
  读 requirements.json 产参数化 TCL + launch_report.json）
- A: 真实 Zhulong.tcl(v1 有 bug) + scenario.txt(用户原话3条) + requirements.json(zl/agent/.zl_pop/180s)
- hidden B: Qualib 启动器（qualib/qualib_q/.ql_pop/240s/280x80+500+200），
  broken input 用 grab-root+tkwait 卡死 bug（与 A 的 destroy-root 消失 bug 同族不同例）
- check: 19 断言，含真跑 tclsh 抽 wv_run_ids 在 B bjobs 样本上验 {3301045,3302079} 排除 sim_q 3302078，
  A-leak/B-grounding/确定性/4 假提交
- 自验: ref 19/19 PASS + 4 negs 全 FAIL
