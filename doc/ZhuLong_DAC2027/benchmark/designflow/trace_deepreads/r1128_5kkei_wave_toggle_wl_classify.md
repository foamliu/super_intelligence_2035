# r1128 — 5kkei (ypzheng@hfeg0plg103) → WaveToggleWlClassifyProduce-001

## 选料（r1128 选料轮）

继续 r1127 令「peek b_fresh_r1126_xshard_dedup.tsv 剩余 spice 5–14 段未 peek 候选」。
本轮 peek 20 个 spice_count 5–14 段未 peek 候选（修正前轮 peek 脚本两个 bug：
① SID_MAP 错取低 mc 的 `.json` 变体而非 `.messages.json`；② session 路径坑——
文件在子目录 `/sessions/<sid>/<sid>.messages.json` 非 `/sessions/<sf>`，r1123 已记）。
正确 IP 取自 ssh_eda_search_20261124_023802/summary.tsv 的 max-mc `.messages.json` 条目。

peek 20 候选结果（取首条 `<user_input>` 文本）：

| sid | user@host | mc | spice | U#0 意图 | 判定 |
|---|---|---|---|---|---|
| w0hwk | e0025730@plg49 | 88 | 5 | 执行 DRAM 流程 (无 user_input 标签) | flow-driving 拒 |
| 592po | dandans@pbn11 | 87 | 5 | run_all.sh 报错帮看 log | debug-Q&A 拒 |
| onepv | tongfanl@hfhds206 | 82 | 10 | matrix-job-status skill 触发 | dup MatrixJobStatusParse 拒 |
| ntu0p | e0025730@plg49 | 68 | 11 | 执行 DRAM Sense Margin 全流程仿真 (SKILL.md) | flow-driving 拒 |
| qam5v | steveny@pnd001 | 64 | 12 | 更新 eda agent skill 覆盖版本 | skill-mgmt 非 B 拒 |
| jyria | t0002801@pbn03 | 55 | 6 | 比较两个仿真网表是否一样 | dup NetlistCmp 拒 |
| 5kkei | ypzheng@plg103 | 46 | 5 | 找到 toggle 的 WL，包括 normal 和 redundancy | **✅ B 域 spice_sim 产出** |
| uh4tf | mhyu@plg52 | 45 | 5 | 比较两个 netlist 差异（已知一处，找其它） | dup NetlistCmp/Diff 拒 |
| fqmvu | binwenh@pkn004 | 35 | 5 | (ssh EMPTY) | skip |
| cw0n0 | zoeyr@pkn004 | 31 | 7 | (TIMEOUT) | skip |
| dodfi | pdsong@pkn002 | 26 | 7 | 分析 test.sp 实现什么功能 | analysis-only 拒 |
| 7apcg | yuchens@plg75 | 26 | 6 | Resource... (skill-mgmt 嫌疑) | 非 B 拒 |
| d7rmo | yuyingc@pkn001 | 26 | 10 | (TIMEOUT) | skip |
| 1qky7 | rhyanw@pkn005 | 27 | 11 | 粘贴 runsim job 提交 log | debug/meta 拒 |
| 8r2in | t0002607@pkn001 | 21 | 11 | 粘贴 LVS Netlist Compiler Subcircuit not found 错误 | debug-Q&A 拒 |
| jpu8x | e0047547@pkn003 | 8 | 5 | 集成电路设计中... | 太短/泛 拒 |
| yqtos | rowanl@pkn003 | 17 | 5 | hello | 噪声 拒 |
| yjwjo | zhenglu@pkn003 | 12 | 5 | /home/zh... (路径片段) | 太短 拒 |
| e9l40 | johnl@pkn003 | 16 | 8 | 看一下我的.ba... | infra 拒 |
| yetqt | krisluo@plg96 | 13 | 8 | 这是后仿文件，等下问激励写法 | Q&A/doc-search 拒 |

→ 20 peek（17 真 peek + 3 timeout/empty），1 产出 (5kkei)。

## 深读 5kkei (53 msgs / 545KB)

ypzheng 在已连接的 WaveView bridge 上要求「找到 toggle 的 WL，包括 normal 和 redundancy」。
cline 通过 `SandBox_MCP_Server__run_code` (tcl) 在 WaveView ACE 上操作 FSDB：
- U#1-7: 探测 bridge → 374 个 sx_* 命令可用；当前 sim file = finesim.fsdb
- U#10-14: 查 sx_report_net_wl 文档（误以为是字线，实为晶体管 W/L 宽长比）→ 改用
  sx_wdf_info $f -waveforms 枚举全部 2660 个顶层信号
- U#15-23: 按名称候选 (*wl*/*row*/*negvwl*) 筛 629 个，用 sx_scan_data_points POINT
  逐信号扫描，统计 abs 电压步进 > 0.15V 的跳变次数 + ymin/ymax → 全设计中仅 40 个
  信号跳变，WL 相关仅 hb_negvwln2vssco(5次) / hb_neg2vssspine0..3ci(3-6次)
- U#24: ask_question 确认 WL 定义
- U#25-32: 用户指网表 /proj/ddgoa/.../Netlist_Vcap_20261012PM_kejun → cline shell grep
  网表(719991 行/334MB)，确认 normal=行译码 RasToXdecDrv(Ra 行地址)、
  redundancy=eFuse 修复 RowRed2New_vint/RowRed96New(EFsBit 匹配行地址)
- U#33-39: 确认 redundancy WL(vintzrowred*/vintzrowredbuf* 共 80 个)全部恒定 0.83V 零跳变；
  normal WL 驱动路径 hb_negvwln2vssco(5)/hb_neg2vssspine(3-6) 跳变；字线轨 vwln/vwlp/vmwln 恒定
- U#40-53: 封装 find_toggle_wl.tcl proc + 清理临时文件

**reframe**: 核心意图 = 波形采样清单 + 分类规约驱动的 WL 跳变检测与 normal/redundancy 分类器。
L1 纯 Python 复刻：把 FSDB 采样抽成文本 waves.txt，把 cline 推断的命名分类抽成显式
class_spec.json（first-match-wins 子串匹配），SUT 解析+算跳变(>threshold)+分类+结构化报告。

## 合成

**case = EDA-Eval-DesignFlow-WaveToggleWlClassifyProduce-001** 落库 cases/B/。

### 设计要点
- **A (visible)**: waves_A.txt 53 信号(LPDDR5X 风格名)：normal_wl steady(vintzrowctrlb0..7/
  vdd2hzrowselb0..7) + toggling(hb_negvwln2vssco 5次, hb_neg2vssspine0..2ci 3/5/6次)；
  redundancy_wl steady(vintzrowred0..5b0..1! + vintzrowredbuf0..5b0..1! 共 24 个全恒定)；
  wl_rail(vwln/vwlp/vmwln 恒定)；other(ck_t/ck_c/ca0..3 跳变)。class_spec_A 阈值 0.15V。
- **hidden B (五重 anti-hardcode)**: waves_B.txt 41 信号：
  ① 信号名异 A (rrowctrl*/rrowsel*/ngvwl2vssco/ng2vsssp*/rrowred*/rrowredbuf*/pwln/pwlp/pmwln/clk_t/cb*)
  ② 信号数异 A (41 vs 53) ③ 阈值异 A (0.2 vs 0.15V) ④ 类 patterns 异 A (rrowred/rrowctrl/rrowsel/ngvwl/ng2vsssp/pwln/pwlp/pmwln)
  ⑤ redundancy_wl 出现跳变信号 rrowredx_tog0(2次)——A 的 redundancy 全恒定，防「red 全 steady」硬编码
- **交付**: find_toggle_wl.py <waves> <spec> <out_json> → signals/summary/toggling_by_class JSON

### check 13 条断言
a(zip+compile) b(B exit0+out_json) c(三顶层 key) d(信号数==41+名字集一致) e(每信号 toggle_count==truth)
f(vmin/vmax==truth 1e-9) g(class==truth first-match-wins) h(redundancy_wl>=10 且匹配 rrowred)
i(toggling_by_class 恰为 toggle_count>0 且反向完备) j(summary total==toggling+steady)
k(反硬编码 A 名片段 vintzrowctrlb/hb_negvwln/vwln 等 10 个不入 B 输出)
l(反硬编码 B redundancy_wl 跳变信号非空 + rrowctrl0 在阈值 0.2 下恒定 toggle_count=0)
m(3-seed sha256 一致)

### 自验
- REF 13/13 PASS
- NEG 3/3 FAIL：neg_empty(out_json 不产) / neg_print_only(信号数 2≠41，A 名泄漏) /
  neg_core_removed(toggle_count 全 0，ngvwl2vssco 0≠4)
- §4.9 三假齐 ✓

台账 5kkei claim→mark case ✓。📊 covered=590/4529=13.0%(mc>=10,+1)。
