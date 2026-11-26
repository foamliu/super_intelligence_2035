# trace_deepread: 636qr — runModelQA refactoring-innovation summary Q&A

## 来源
- session: `1791457560417_636qr.messages.json`
- user: rongjiez @ hfeg0plg98 (10.129.8.230)
- mc: 112, domain: analog_context
- ledger note (旧): "doc/PPT task: user describes runModelQA_new.pl 7 refactoring innovations and asks 'organize PPT content'; documentation not code"
- 旧判 = 旧规则下判 "doc/PPT task not code" → 误杀。新标准（2026-11-15 令 §二）：code-grounded refactoring summary 是真实用户意图，恢复可造。

## 用户原话（MSG 0, verbatim）
> @runModelQA.pl @runModelQA_new.pl runModelQA_new.pl是我对原始代码runModelQA.pl进行重构得到的新代码，新的代码主要到创新与突破为：
> 1.device的数据结构优化，扁平化，同一个device name尺寸对应多个参数
> 2.从model文件中抓取对应的shrink和portname
> 3.支持对管子的w和l进行sweep的输入格式
> 4.spice语法更简洁，支持vtlin vtsat vtgm idsat idlin ioff cgg idvd idvg多种参数
> 5.支持多种仿真器：primesim finesim hspice nanospice，同时这些仿真器的输出文件目录格式不同，全部支持结果分析
> 6.输出的report格式同样扁平化，与model发布的文件中的数据表格格式一致，方便用户查阅
> 7.支持wavevie打开idvd和idvg的输出特性曲线
> 根据这几点和代码，帮我整理一份ppt内容

附件（嵌入 MSG 0 file content）：
- `/home/rongjiez/jira_dev/mpqa/scripts_t/runModelQA.pl` — 旧版, 3042 行, 137700 字符
- `/home/rongjiez/jira_dev/mpqa/scripts_t/runModelQA_new.pl` — 新版, 1630 行, 60216 字符

## 助手行为（13 msgs）
- MSG1-9: list_allowed_files → read_files 分段读两脚本 → 核对关键代码段
- MSG10-12: 用 editor 新建 `runModelQA_重构亮点_PPT_7大创新.md`，12 页 PPT 内容（每页 1 张幻灯片含核心+4~5 要点）：
  - P1 封面 / P2 背景痛点（旧 3042 行、6 套割裂哈希、仿真器硬编码、模板+正则修补）/ P3 总览（3042→1631 行 ~-46% + 7 阶段流水线）/ P4 创新①扁平化（{name,w,l,nf,params[]}）/ P5 创新②shrink（.lib 引用+grep -m1 SHRINK=，回退 scale_mos=）+drain 端口（首条 .subckt）/ P6 创新③sweep(start,stop,step)u 笛卡尔展开 / P7 创新④key=value 语法+九类参数+Vth 三法 / P8 创新⑤4 仿真器四层适配（*.md0/*#*.md0/*.ms*）/ P9 创新⑥单一扁平 MPQA.report 动态列 / P10 创新⑦.pd0→CSV→Excel 兼容 Waveview / P11 新旧对照表 / P12 总结
- 行数（3042/1631）、函数名、正则、选项（finesim_measout/-spice/-i）均来自实际代码核对

## 7 大创新点代码证据（new script 真实标识符）
1. **扁平化数据结构**: `sub getDevices` 返回 flat `@devices` list, 每个 `{name,w,l,nf,params=>[...]}`; `sub merge_devparams` 合并同 (name,w,l,nf) 的多参数行
2. **model 文件抓 shrink/portname**: `sub getShrinkFromModel` — 解析 model `.lib 'incFile'` 引用 → `grep -m1 SHRINK=` → 回退 `scale_mos=`; `sub extractDrnPortName` — `grep -m1 .subckt` 取首端口
3. **w/l sweep**: `sub _expand_sweep_dim` — `sweep(start,stop,step)unit` 笛卡尔展开，升降序均支持
4. **spice 语法 + 多参数**: `sub generateSpice` dispatch `type =~ /^(?:vtgm|vtsat|vtlin|idsat|idlin|ioff|cgg)$/` + idvd/idvg; `key=value` cfg 解析 in `parse_device`
5. **多仿真器**: `sub runSimulation` — finesim/primesim/hspice/nanospice 四分支; `sub summary_all_results` — primesim `*.md0`/finesim `*#*.md0`/hspice+nanospice `*.ms*` 输出布局适配
6. **扁平 report**: `sub generate_report` — 单一 `MPQA.report`，动态列（电压类 1 列、电流/电容类 total+normalized 两列 + SimCondition），对齐 model 发布表格
7. **waveview/iv 曲线**: `sub generate_csv_file` — `.pd0→CSV` (cxmt_spiceMeasurementDataConvert); `sub generateAllChart` — CSV→Excel charts，兼容 Waveview 打开 idvd/idvg

## 旧脚本对照（"before" state）
- 6 套割裂哈希: `$device_vth_info` / `$device_idsat_info` / `$device_ioff_info` / `$device_cgg_info` / `$device_idvd_info` / `$device_idvg_info`，每类独立 `generate_*_netlist` sub
- 仿真器仅 finesim/primesim 两分支（无 hspice/nanospice）
- sweep 仅 vth 电压 sweep 的 inline 正则（`/sweep(.*)/(\S+)/(\S+)/`），无专用 expand 函数
- shrink 仅从 cfg 读取（`read_cfg` 解析 `shrink=`），无 model 文件抓取
- report 两份分离文件（MPQA_total.report / MPQA_normalized.report），由 `merge_same_type_device_idsat_ioff_vth_cgg` 合并

## case 设计（套 #254 v2 code-grounded answer-extraction reframe）
- 用户意图 = 整理重构创新点 PPT（code-grounded refactoring summary）
- design_flow 契约需在隐藏 B 上跑候选 → 单份 PPT/散文无法参数化 → reframing 成 **code-grounded refactoring-innovation-summary tool**
- 工具读 旧+新 Perl 脚本 + 问题（含编号创新点清单）→ 结构化 JSON: question/scripts_summary/innovations[{claim_id,claim_text,status,evidence_in_new,evidence_in_old,cited_identifiers}]/cited_identifiers/overall_assessment
- 对每条创新点从新脚本真实抽取证据，判定 status(confirmed/partial/unconfirmed)，不照搬用户的话
- **第 8 sub-type**: refactoring-innovation-summary（前 7: code-review 86g62 / code-debug 9imo1 / netlist-explain bgrlw / manual-howto aihrj / mechanism-explanation 7sgr2 / circuit-id l2vvy / deck-diagnosis 1tymw）

## data-driven 2×2+degenerate（隐藏 B）
- **B1**（3 confirmed + 2 unconfirmed）: 新脚本有 flat-device + sweep + 3 仿真器(ngspice/xyce/quantumsim)，无 waveview/csv，无 model-file-shrink → 5 claims [confirmed,confirmed,confirmed,unconfirmed,unconfirmed]
- **B2**（partial mix）: 新脚本有 2 仿真器(partial) + 4 参数(partial) + report(confirmed) + 无 sweep(unconfirmed) → 4 claims [partial,partial,confirmed,unconfirmed]
- **B3**（graceful）: 旧==新 trivial 脚本，3 claims 全 unconfirmed
- B 用中性标识符（ngspice/xyce/quantumsim）区别于 A（finesim/primesim/hspice/nanospice）→ 反硬编码有牙

## check.py 15 条件 a-o
①zip含refactor_summary.py ②py_compile ③B1合法JSON+全键+合法innovations+count==5 ④B1 status数据驱动匹配ground-truth ⑤B1 cited grounded ⑥B1 confirmed有grounded evidence ⑦B2合法JSON+innovations+count==4 ⑧B2 status匹配(含partial) ⑨B2 cited grounded ⑩B3合法JSON ⑪B3优雅降级全unconfirmed ⑫B3 cited grounded或空 ⑬反硬编码A标识符不泄入B ⑭B1 question逐字 ⑮3-seed确定性

## 自验
- REF PASS 15/15 ✓（3 次稳定）
- NEG 3/3 FAIL ✓（neg1 硬编码A泄漏→fail@m / neg2 stub全confirmed→fail@d / neg3 print-only→fail@c）
- §4.9 退化 3/3 FAIL ✓（空zip→a / garbage→c / print-only→c）
- k_rationale==k_check==15≥8 ✓
- test field==disk check.py ✓
