# trace_deepread: 1794812159537_exhq3 (dsgao@hfhds201, mc=140, physical_verify/PEX)

**session**: `/home/dsgao/.cline/data/sessions/1794812159537_exhq3/1794812159537_exhq3.messages.json` (704KB, 128 msgs)
**meta**: started 2026-11-16 14:55, ended 17:09, model glm-5.3-flash, cwd `/proj/drcpa/V0/ver/pex/dsgao/...`, title "spf 替换仿真"
**fork**: forkedFromSessionId 1794539296413_hf7nj (desktop fork)

## 用户真实意图（5 条 user_input 提炼）

用户 dsgao 在做 DRAM 块 `R_SaCtrol_sub_UV_normal_iso` 的 PEX 后仿对比：
1. (#0) 把顶层网表 `R_XdecGap_35p5.spf_RCC` 里 `drcpa_array/R_SaCtrol_sub_UV_normal_iso` 这个模块的 spf 替换成新 PEX 抽出的 `R_SaCtrol_sub_UV_normal_iso.spf.TYP_98_RCC` 进行仿真
2. (#38) 检查后仿日志 `full_testbench_far_spicehd.log` 是否真把后仿网表吃进去了
3. (#60) 要跑这个 block 的前后仿真对比
4. (#100/#116) 后仿日志全是错，反复让 agent 重新读日志找根因

## agent 工具链 + 关键产物

agent（glm-5.3-flash + agent-policy-engine，shell-runner/python-runner profile）走了一条很典型的 PEX 后仿 debug 链路：
- **探索阶段** (#1-#35): 7 个 explore_spf*.sh 脚本，逐层 head/grep/wc 两个 spf 文件，发现：
  - 顶层 `R_XdecGap_35p5.spf_RCC` 是 StarRC 扁平 DSPF 1.3（~850 万行，41360 条 *|NET，单条 .SUBCKT），子模块被**打平**嵌在顶层（grep `XI0.XI1<0>.XI0.XMMN1` 命中 695 处）
  - 子模块 `_iso.spf` 定义 `.SUBCKT R_SaCtrol_sub_UV_normal_iso`（73 端口，62520 R / 87807 C / 509 net）
- **诊断阶段** (#37-#59): 读 finesim 日志，发现 `Reading Netlist` 第 52 行确实读入了 `_iso.spf`，但 elaboration 出来是 schematic 级（854 MOS / 34 R / 2705 C），不是寄生级（应该 62k R / 87k C）→ **spf 被解析但没作为 DUT 实例化**
- **合成阶段** (#61-#99): 写 `make_post.py` 解析 spf 73 端口，生成 `post_dut_stim.net`（`X0 <73端口> R_SaCtrol_sub_UV_normal_iso` + .include spf + .GLOBAL 8 rails，不带 .END）；写 `build_prepost.py` 生成 post 主 .sp（只换 DUT 那行，其余原样）
- **修复阶段** (#101-#127): 重跑 post 又报 `ERROR! no reference ckt switch_open/switch_close`（26+23 处）→ 写 `extract_switches.sh` + `check_spf_leaves.py` 发现 spf 引用了 3 个叶子子电路但定义在 schematic 网表里 → 把 `switch_open`/`switch_close`/`brknet` 定义补进 `post_dut_inc.net`；再跑又报 `brknet` 缺 → 写 `find_brknet.py` 一次性找全 → 补进 → 给出重跑命令 `finesim post_full_testbench_far_spicehd.sp -o POST_rundir3/ -np 8`

## 关键技术点（可计算子意图）

1. **DSPF/SPF 顶层 .SUBCKT 解析**：取子电路名 + 有序端口列表（73 端口顺序敏感，X0 实例化必须按此顺序接）
2. **日志缺失叶子集提取**：从 `ERROR! no reference ckt <name>` 行去重提取，需忽略 `WARNING:`、`Error: convergence`、`ERROR! exit due to`、以及 name 位置是 `for`/`in`/`library` 这类英文词或空的噪声行
3. **schematic 网表叶子定义体提取**：从 `.SUBCKT <name> ... .ENDS <name>` 块逐行原样取出
4. **post-DUT include 网表合成**：`.GLOBAL rails` + 叶子定义体 + `X0 <ports> <block>` 实例 + `.include "<spf绝对路径>"`，**不带 .END**（要被顶层 .sp include）

## reframe 决策

真实 trace 依赖 live finesim + 大型 PEX 网表（850 万行），无法离线判分。取其**可计算子意图**：纯文本解析 spf/schematic/log → 合成 post-DUT include 网表。这是 PEX 后仿流程的核心可自动化部分，物理验证（PEX）属性明确，离线 stdlib 可跑，判分可对隐藏 B（不同 block/端口/叶子/rails）独立验证。

## 同 sharding 判断

trace 关键词 drc:1583/netlist:1258/pex:74/lvs:29 中，drc 计数被路径 `/proj/drcpa/` 中的 "drc" 子串虚高（实际非 DRC 任务）；真实任务是 PEX 后仿 DUT 构造，**属 C 域 physical_verify**（PEX 寄生网表操作），非 B 域 spice_sim（不跑仿真本身，只构造 DUT 网表）。

## 同时 parked 的 sibling

`1795045425613_3yqt8` (e02141@hfhds201, mc=187): 误判为 C 域（关键词 lvs:520/synopsys:370），实际是 TCAD Sentaurus sprocess/sdevice/sdevice/svisual 建 VCT GAA NMOS 器件仿真 deck，非 physical_verify，已 parked。其兄弟 `1795045078666_y1q1z` 同样 parked。
