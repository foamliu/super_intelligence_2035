# Deepread — sid 1790065302917_0c5yk (weizhao / hfeg0pkn004)

- **user**: weizhao · **host**: hfeg0pkn004 (10.129.2.13) · **mc**: 201 · **domain**: physical_verify
- **session**: 243 msgs, agent=lead, model=zhulong (deepseek-v4-flash family), cwd /home/weizhao
- **tools**: 289 calibre + 3 pyAether（calibre rule deck 文本解析为主，无 live calibre / 无 OA 库操作）
- **status**: 会话末轮 assistant 请用户在终端执行 run_compare3.sh，无显式用户"成功了"接受，但末版脚本 drc_full_compare3.py 是用户多次 refine 后的最终产物 → A-档 faithful seed 取 U[0]，gold 取末版泛化

## 用户意图（逐字）
- **U[0] (msg#0, 254c) — A-档 seed**:
  > 帮我分析一下一下两个DRC rule，一份是Shrink factor =1 ，另一份是shrink factor = 0.318
  > 需要分析的内容：两份文件是否只有数值上的差别，且check数值是0.318倍
  > /home/pdk/weizhao/00_drc/LDDB/G4B/LDDB2.0_drc_SF1_v0d5_rev14/calibreDRC.rule
  > /home/pdk/weizhao/00_drc/LDDB/G4B/LDDB2.0_drc_v0d5_rev14/calibreDRC.rule
  - 纯需求委托轮：无根因、无修复方案、无追问 ⇒ 合规 A-档 seed
- U[1] (msg#41): 再对比一次，结果整理成 drcvaluecompare.txt 输出到 /home/weizhao/
- U[2] (msg#75): 用 SF=0.318 去对比 SF=1，比率算 0.318 而非 3.145（方向修正）
- U[3] (msg#99): 输出 txt 不要中文，全英文
- U[4] (msg#119): 忽略开关定义，对比所有开关下所有 rule
- U[5] (msg#149): 执行并输出到 /home/weizhao/zl
- U[6] (msg#157): python3 报 libpython3.6m.so 错（环境 bug）
- U[7] (msg#169): 仍用 python 脚本
- U[8] (msg#183): 回滚到 drcvaluecompare_en.txt 版本
- U[9] (msg#211): 重申 SF=0.318 对比 SF=1
- U[10] (msg#223): 把 _F 无数值 rule 也统计，同类 rule 放一起，不区分 Group

## assistant 工具链
- editor 62 次：写 compare_drc.py（7 个位置试写）→ drc_full_compare.py（8 版）→ drc_full_compare2.py（6 版）→ drc_full_compare3.py（5 版，末版 4444B）
- read_files 37 / run_approved_command 3 / list_allowed_files 4 / run_commands 2
- 无 RAG search_apis（纯文本正则解析，不调 EDA API）

## 真实附件
- /home/pdk/weizhao/00_drc/LDDB/G4B/LDDB2.0_drc_SF1_v0d5_rev14/calibreDRC.rule（550212B, 14282 行）
- /home/pdk/weizhao/00_drc/LDDB/G4B/LDDB2.0_drc_v0d5_rev14/calibreDRC.rule（549383B, 14285 行）
- 两文件均可在 .75 经 pyAether 读到（NFS 挂载）

## gold（末版 drc_full_compare3.py 泛化）
- 自包含 Python3 + re + argparse + OrderedDict
- 接受 CLI：`<file_a> <file_b> [--out <path>]`（trace 原为 hardcoded 路径 FA/FB/OUT，泛化为参数；--out 省略则写 stdout）
- 从 filename 推断 SF（sf0318→0.318, sf05→0.5, sf1→1.0，默认 0.318）
- parse：var_re = `^\s*VARIABLE\s+(\S+)\s+(\S+)`；rule_re = `^\s*([A-Za-z_]\w*)\s*\{`（排除 GROUP/CONNECT）
- diff：逐行比较，num_re.sub 归一化判定 numeric-only vs structural
- classify：ratio = fa/fb（shrink/ref = SF）；Scaled(SF) / Area(SF²) / Unchanged / OTHER
- report 5 section：分组全规则 / 非VARIABLE diff 行 / structural diff / WINDOW-STEP / Area 汇总 + CONCLUSION
- check-only 规则（_F_ 无 VARIABLE）也列出

## 与既有 case 区别
- DRCTimeStats（per-rule CPU/REAL 排序）/ DRCKDeckOpt（rule deck 优化建议）/ DRConnTiming（CONNECT 操作级耗时）/ DRCPatGen/DRCPatPlan（DRC pattern 生成）/ VTTFLayerMap（层映射）/ FreezeMaker（freeze layer）→ 本案两份 rule deck 的**数值缩放比对**（SF 比值 + 面积比 + 不变值分类 + structural 检测），主题独立，非 near-duplicate

## 判分设计
- L1（纯文本正则，subprocess 真跑候选 on hidden B，无需 live calibre / OA）
- hidden B：SF=0.5 MET/VIA/CO_F deck（规则名/分组 ≠ A 的 NW_W/TPZ/D1HSV_F），判分器内嵌生成
- check.py 16 条独立断言（a–p，f/f2 合并）：zip/py/size/NUL/compile/import re/CLI/exit0/report/scaled-var/area-var/unchanged-var/check-only/ratio0.5/cross-input-guard/only-numeric/determinism
- cross-input guard (n)：A 专属 token（NW_W/TPZ/D1HSV_F/TAM_F/BPZ_F/weizhao/calibreDRC_SF0318/LDDB2.0）不出现在 B 报告
- negative 4 个（empty_shell/print_only/naive_hardcode_A/core_deleted）全 FAIL
