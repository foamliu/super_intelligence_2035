# 深读笔记 — sid 1789003661429_4fhmt (Calibre DRC Log 拆解)

- **trace**: 1789003661429_4fhmt · user=miccao · host=hfeg0plg37 · mc=353 · 119 msgs / 60 user turns
- **真实任务**: 操作员用 `calibre-drc-log-analysis` skill 分析 9.8MB Calibre DRC-H rundrc.log（DDR5TOP_DFM0909，143439 行），产出四模块简化报告并落盘 txt。
- **用户四模块规格**（T3 定义，T4 定为 skill 模板，T5 落 /home/miccao/zl/rep/*.txt）：
  1. 各大步骤时间占比总结（MODULE COMPLETED + cumulative 操作类别分布）
  2. 连接关系建立时间总结（CONNECT REAL/NETS/EPINS + deck 语句 + 冗余检查）
  3. 图形计算耗时 Top-N（REAL TIME 排序，含 HGC/FGC/FEC/所属 rule/log 行号 + 核心源层放大倍数 + VHC=F 比例）
  4. deck 优化建议（改前/改后 + 预估节省 + 优先级）
- **关键真实数据**（来自被用户接受的 rep.txt，236 行 / 15KB）：
  - TOTAL CPU 121069s · REAL 20206s(5.6h) · 36 核 · 143 rules · 83984 results · 加速比 6×
  - 模块: Rule File Compile 0 / Licensing 0 / Layout Data Input 275 / HDB Constructor 269 / Results DB Init 0 / DRC Executive 19931(98.6%)
  - cumulative: WITH WIDTH 17468 / EDGE TOPOLOGICAL 6773 / ONE-LAYER DRC 4264 / TWO-LAYER BOOLEAN 3383 / EDGE MEASUREMENT 1668 / POLYGON TOPOLOGICAL 1401 / SIZE 1393 / TWO-LAYER DRC 1256 / CONNECT 49
  - CONNECT: 1 次 REAL 50s · NETS 5,896,486 · EPINS 4,770,436 · cumulative 49s · 5 条 deck 语句(M1→M2→...→RDL) · 无冗余
  - Top-1: R_C_MT2_F_01_M::A0 `M0C_Total WITH WIDTH < 0.102` REAL 16853s(占 83.4%) HGC 34,281,403 FGC 98,815,942 FEC 434,519,423 VHC=F · **Results=0**
  - Top-2: R_C_M0C_ENC_01_H::A5 REAL 1730s HGC 1,053,006,510 FGC 3,587,555,892
  - VHC=F: 1020/1036 (98.5%)，仅 9 保留层次 → 几乎全扁平
  - 源层: MT2_CORE(HGC 46698→FGC 124,346,682, 2663x) / M0C_First / M0C_Total(35.6M→170.2M, 4.8x) / PC_Total(38.1M→274.4M, 7.2x) / TMP<12>(64.8M→356.7M, 5.5x)
  - 3 条优化建议（P0 M0C_Total 空间预过滤 / P1 INTERACT 中间层缩小 / P2 源层层次保留）
- **SKILL.md** 定义了精确的 log 字段格式（`--- X MODULE COMPLETED. CPU TIME=.. REAL TIME=..` / `--- TOTAL CPU TIME = X REAL TIME = Y` / `<Layer> (HIER TYP=.. HGC=.. FGC=.. HEC=.. FEC=.. VHC=.. VPC=..)` + 下一行 `CPU TIME=.. REAL TIME=.. OPS COMPLETE = m OF N ELAPSED TIME=..` / `DRC RuleCheck <N> COMPLETED. Number of Results = X (Y)` / `Cumulative <CAT> Time: CPU=a/b REAL=c/d` / `cell: <name>, instance: <N>, box: <B>, polygon: <P>, path: <P>, text: <T>`）。
- **本 case 抽取**: 「Calibre DRC-H rundrc.log 结构化解析器」离线确定性核心 → **drc_log_analyzer.py**（纯 stdlib；CLI --log/--out；解析四模块数据 → JSON）。
- **A(可见)**=合成 rundrc_A.log（按真实 DDR5 结构/数值）· **隐藏 B**=rundrc_B.log（不同总数/不同 top rule/不同 VHC 比例/含冗余 CONNECT/不同 huge cell）杀硬编码。
- **判分 16 条 a–p**：见 check.py。
- **真实性保留**: 真实 log 不可读(权限)，但 SKILL.md 字段格式 + 被用户接受的 rep.txt 数值完整 → 合成 log 严格按 Calibre DRC-H 字段格式构造，数值取自真实 trace。
