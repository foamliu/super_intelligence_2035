# Deepread — 1793685353350_ydezg (leozhao, wl-adjacent-detection)

- **session**: 1793685353350_ydezg, leozhao @ hfeg0plg36 / 10.129.32.46, mc=117, NEW user, model=glm-5.3-flash, status=failed, 83 msgs, 1.95M input tok
- **keywords**: drc:345; calibre:233; aether:48; .gds:17; pyaether:11; lvs:6; virtuoso:3; pdk:3
- **cwd**: /ai_sandbox/ddgoa/V0/agentdir/leozhao ; project /proj/ddgoa/V0/ver/drc/ddgoa_array_core/Ary_m512Meg_U_fbcc_leo
- **domain**: physical_verify (Calibre DRC deck + ASCII results parse)

## 用户真实意图
- U#0: 「/home/leozhao/wl-adjacent-detection.md 读一下这份文档，了解背景 / /proj/.../agent/wl_adjacent.drc 这份 drc deck 基本能实现功能」
- U#6: 「所以我们要做什么」
- U#24 (ask_question 回答): 「跑通全流程：运行 Calibre → 解析三个 .rep → 生成最终邻接表」

目标：从版图自动找出所有相邻 WL 对，输出名字对表格。命名 `sec<S>m<M>wl[O|E]<B>`；相邻判据 = 两根不同 WL 在 M1ANET/M2ANET/M3ANET 任一层 spacing < 0.182um；连接 `CONNECT M2ANET M1ANET BY V1A` / `CONNECT M3ANET M2ANET BY V2A` / `CONNECT HSP M3ANET BY HSV`。deck 用 v2 属性链架构（静态 4791 行，零生成，DFM TEXT/PROPERTY/NODAL MULTI 名字链 + 引号 check 名 `"PAIR <A> <B>"` 报告 + TVF strict name 过滤）。空 check 被 Calibre 丢弃 → 结果文件里出现的 PAIR check 名 = 相邻对。解析器 grep `PAIR (\S+) (\S+)` 聚合即得表格。

## assistant 工具链（83 步）
1. read_files 读 wl-adjacent-detection.md (concept 笔记, Q1-Q8 + v2 属性链分步表) + wl_adjacent.drc (4791 行, 前 4440 LAYER MAP, 4441-4791 核心检查逻辑)
2. search_codebase 找 SPACE/EXTERNAL/INTERNAL/ENCLOSURE/NET/CONNECT/DFM/TEXT/ATTACH/SELECT/LAYER 关键字
3. 分段 read_files deck 核心逻辑 4465-4791 (ATTACH HSP_pin HSP + TEXT DEPTH PRIMARY + 3 CONNECT + NET "s?m?wl?" + DFM TEXT PRIMARY ONLY + DFM PROPERTY MERGE + DFM PROPERTY wl_hsp wl_marker OVERLAP ABUT + DFM PROPERTY NET + NODAL MULTI NOPUSH + SPACE/EXTERNAL + DRC RESULTS DATABASE + DRC SUMMARY + TVF member_proc strict filter `^s[0-9]+m[0-9]+wl[oe]<[0-9]+>$`)
4. list_allowed_files 看 agent/ 目录配套文件（parse_wl_pairs.py + 历史 wl_pairs_mN.rep + wl_adjacent_table*.rep + wldrc.summary + cal2020/cal2023 运行目录 + _cluster.master_）
5. read_files parse_wl_pairs.py (46 行: argparse nargs+ + -o, regex `PAIR\s+(\S+)\s+(\S+)`, bidirectional set, skip a==b, sorted output `key\tadj,adj`, print hits+wls) — **naive grep, 不区分 comment/MESSAGE/header/false-substring, 不校验 WL 命名**
6. read_files rundrc.log:1-60 + _cluster.master_ (历史用 bsub 提交 LSF pv 队列, calibre v2020.1_36.18, 2 核, real time 66s, GDS 223MB)
7. editor 写 probe_env.sh → run_approved_command shell-runner → 勘察: calibre OK / bsub OK / license OK / GDS 223MB / 26T 空闲 / test.drc vs agent/wl_adjacent.drc md5 不同
8. editor 写 run_wl_adjacent.sh → bsub 提交 Job 773700 → **1 秒退出**: LD_LIBRARY_PATH 指向 eda_agent 自带新版 libstdc++ (要 GLIBC_2.18), 计算节点 CentOS 7 (GLIBC 2.17), LSF res 启动器加载失败
9. 修正: unset LD_LIBRARY_PATH/PYTHONHOME/PYTHONPATH → 重提 Job 775679 → **仍失败** (污染来自执行节点侧, eda-agent 2026-11-02 安装进入节点守护进程环境)
10. 对照实验: probe_lsf.sh 只 echo → 不同节点 hfeg0pfn011 同样 EXIT → 确认是节点登录环境被 eda-agent 污染
11. read_files /home/leozhao/.bashrc (PROJ_NAME=drjoa, 各种 export) → session 在 thinking 中结束 (status=failed, 未能跑出结果)

## 关键产物（真实）
- /proj/.../agent/wl_adjacent.drc (4791 行 deck, 真实 v2 属性链)
- /proj/.../agent/parse_wl_pairs.py (46 行 naive parser, 真实)
- 历史 wl_pairs_mN.rep / wl_adjacent_table*.rep / wldrc.summary / rundrc.log / _cluster.master_ (在 /proj, e0031982 无读权限; .rep 内容未在 trace 中读出, 故本 case B-synthesized)

## 为何 B-synthesized
- 真实 run 被 LSF 节点 eda-agent libstdc++ 污染阻塞, 未产出新的 .rep / 邻接表
- 真实 GDS 223MB + Calibre + LSF 集群无法在 SUT 沙盒复现 (L2/L3 不可行)
- 但 parse 子任务 (归并 3 份 .rep → 邻接表) 接口清晰、可离线 L1 合成
- 真实 parse_wl_pairs.py 是 naive grep, 漏掉 4 类真实陷阱 (comment/MESSAGE/header 假 PAIR + 非 PAIR check 名子串 + 命名校验 + 自配对); 本 case 把这些陷阱做成判分条件, 金标 = 正确语义 (只认 CHECK "PAIR netA netB" 行 + 严格命名 sec[0-9]+m[0-9]+wl[oe]<[0-9]+> + 跳自配对 + 双向去重)

## DISTINCT from 现有 physical_verify 系
- r239 DrcRuleTimeRank (per-rule CPU/REAL time 排名) / r237 DrcLogTeardownReport (4 模块时间拆解) / r208 DrcUnusedVarClassify (variableUnusedDrc 分类) / r218b DrcQaWidthTypeGeom (QA width 几何) — 本案**首次 ground on Calibre DRC ASCII 结果归并成 WL 邻接表** (check-name → pair → bidirectional adjacency + dedup across layers), 互补不重叠

## case 设计
- case_id: EDA-Eval-DesignFlow-WlAdjacentPairParse-001, physical_verify, B-synthesized, L1, k=18 a-r
- SUT 写 parse_wl_pairs.py (CLI `<rep>+ -o <out.rep>`, stdlib only): 解析 Calibre ASCII .rep, 提取 `CHECK "PAIR netA netB"` 行, 严格校验 `^sec[0-9]+m[0-9]+wl[oe]<[0-9]+>$`, 跳自配对, 双向 + 跨层去重, 输出 `key\tadj,adj` (sorted), stdout `hits: N` / `wls: M`
- A (可见): 3 份 .rep, 8 WL, hits=8 (含 M1+M2 跨层重复), 含 6 类陷阱 (comment/MESSAGE/header/substring/malformed/self-pair)
- 隐藏 B: 不同 WL 名 (sec12m3/sec13m4/sec14m3/sec15m5), 8 WL, hits=7, 同 6 类陷阱
- B2 (退化, 2 文件): 4 WL, hits=2, 含仅自配对的网 sec70m7wlo<1> (须不出现)
- B3 (空): 无 PAIR check, 输出空, hits=0
- 自验: ref PASS 18/18, 6 negatives (empty/print_expected/naive_grep/greedy/core_deleted/naive_hardcode_a) 全 FAIL, §4.9 (a)(b)(c) 三假提交全 FAIL
