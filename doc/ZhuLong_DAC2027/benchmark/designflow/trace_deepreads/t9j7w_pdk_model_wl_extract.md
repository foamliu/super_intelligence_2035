# 深读笔记 · t9j7w · PDK hspice 厚栅氧 model W/L 提取

## trace_source
- session: `1794210761770_t9j7w` (子目录 `1794210761770_t9j7w/`)
- user: owench · host: hfeg0pkn002 · mc=24 · domain: spice_sim
- session_file: `/home/owench/.cline/data/sessions/1794210761770_t9j7w/1794210761770_t9j7w.messages.json` (279 msgs / 1.39MB)
- provider: cxmt-deepseek-flash · model: deepseek-v4-flash · cwd: /home/owench
- 抓取: r669 .75 open_session ssh hfeg0pkn002 scp 全流

## 用户真实意图（原话序列）
1. U#0: `/apps/imctf/extpdk/HL22/22HK_V0P5_0D10_for_vodka/hspice/model_thick.sp` + `分析一下这个model`
2. U#N: `HL22的model中的 ntk_asy1和ntk_asy2与另外两个model的ntk_sv1和ntk_sv2有区别吗？`
3. U#N: `/apps/imctf/models/V1/model_local/V1_HK_Model_D5_v0d5p3/model.sp` + `里面的ntk ptk ntk_lv ptk_lv ntk_s ptk_s ptk_sv 这些管子的尺寸范围WL都是多少`
4. U#N: `...V1_HK_Model_D5_v0d5p3_t5/model.sp` 同上 W/L
5. U#N: `这两个model 有NTK_asy1/2 PTK_sv吗？`
6. U#N: `0.9中的ntk_sv1 ntk_sv2的尺寸都是多少`

→ 真实意图：**分析 PDK hspice 厚栅氧(thick-oxide/TK) model 文件，识别有哪些管子(subcircuit)，提取各管子 W/L 尺寸范围与 bin 数，跨版本对比**。纯分析 Q&A，无仿真、无 deliverable 产物——agent 写 Python 脚本解析 .sp/.lib 提取 lmin/lmax/wmin/wmax。

## agent 工具链
- `list_allowed_files` 探目录 → `read_files` 读 model 文件片段 → `editor` 写解析脚本（verify_wl.py / compare_asy_sv.py / check_v0d5p3.py / find_subckts.py / parse_v1_hk.py / get_wl_ranges2.py）→ `run_approved_command` (profile=python-runner) 跑脚本
- 核心解析逻辑（verify_wl.py 终版，msg[178]）：逐行扫 `.subckt <name> <ports>` → 进入该 subckt 边界内 → 命中 `.model`/`.MODEL` 卡 → 续行(`+`开头)拼接 → 正则 `lmin\s*=\s*([0-9eE.+-]+)` 提取四参数（IGNORECASE，兼容 LMIN 大写）→ 收集所有 bin 取 min/max → µm 报数(`*1e6`)
- 坑：v0d5p3 用大写 `LMIN/LMAX/WMIN/WMAX`（小写正则漏匹配，需 IGNORECASE）；ntk 首个 model 卡用表达式 `1.0E-6 - dxl_ntk` 而非纯数字（取纯数字 bin）

## 真实 .model 卡格式（msg[171] D5_v0d9_t07 原文）
```
.MODEL ntk.1 nmos
+level   = 77.0            version = 107.0           lmin    = 2.0E-6
+lmax    = 2.02E-6         wmin    = 2.0E-6          wmax    = 2.02E-6
```
- subckt 头: `.subckt ntk DRN GATE SRC BULK` (4 端口)
- 单位：米 (lmin=2.0E-6 = 2.0µm)
- 续行以 `+` 开头，注释行以 `*` 开头（解析时跳过）

## 真实 W/L 数据（从 trace 提取）
| model | 器件 | Lmin~Lmax(µm) | Wmin~Wmax(µm) | bins |
|---|---|---|---|---|
| HL22 (scale=0.855) | ntk | 0.110295~1.9998451 | 0.199215~2.5651 | 9 |
| HL22 | ntk_asy1 | 0.1103~0.1103 | 0.2539~0.2539 | 1(固定) |
| HL22 | ntk_asy2 | 0.1103~0.1103 | 0.2539~0.2539 | 1(固定) |
| D5_v0d9_t07 | ntk | 0.11~2.02 | 0.21~2.02 | 24 |
| D5_v0d9_t07 | ntk_sv1 | 0.125~0.127 | 0.164~0.166 | 1(固定) |
| D5_v0d9_t07 | ntk_sv2 | 0.125~0.127 | 0.132~0.134 | 1(固定) |
| D5_v0d9_t07 | ptk | 0.124~2.02 | 0.21~2.02 | 24 |

## 拟造任务形态
spice_sim L1 离线 · analysis Q&A → 造「PDK hspice 厚栅氧 model W/L 提取器」
- A 档 trace-faithful：A=model_thick.sp(用 trace 真实 HL22/D5 .subckt+.model 卡重建) + task_spec.json + 用户原话
- hidden B：合成 XJ28 model（不同器件名 ntk2/ptk2/... + 不同 W/L 数值 + 不同 bin 数），cross-input guard
- 任务：写 pdk_wl_extract.py(workdir,out_dir) 解析 doc/model_thick.sp 产 pdk_wl_report.json
- check.py：≥15 断言（zip 含脚本 / subprocess 真跑 / JSON 合法 / 器件数 / 器件集 / 各器件 W/L cross-input 值守卫 / bin_count / port_count / type / has_model_card / A-leak / 确定性 3 rerun）
