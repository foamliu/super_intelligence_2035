
## 13:3x (r395) · Mt0MetastabAudit-001 交付 · 推翻前轮0-case结论
- loop task card 13:33:14 派 1 case。mc-matrix mc10.fresh=36 非0。
- **独立重核**：本地 cross-shard diff candidates_mc10.tsv(486) vs 全 shard ledger(2438) → 43 fresh。前轮称「36 全非 spice-dominant」——逐条核验发现 lcbck(e0029495,mc10,spice-ratio=0.341) 卡在 0.35 阈值下方被滤掉，**推翻前轮结论**。
- eda_flow .75 scp+解析：olayh=Q&A太短 reject；**lcbck CLEAN**=「分析这份mt0文件，看看是否发生亚稳态」+ attached 01_coarse_bracket.mt0(PrimeSim HSPICE 55列 .measure)，agent 写 analyze_mt0.py 解析+出亚稳态报告。
- **case EDA-Eval-DesignFlow-Mt0MetastabAudit-001**(spice_sim/faithful/L1 k=16)：mt0_metastab_audit.py 解析55列含failed容错+判定亚稳态。A=真实mt0(末态收敛=无亚稳态)；hidden B=合成(末态卡中间电平=持久亚稳态,worst=q)。check.py 16断言(a-p)+A交叉核对击败print-only。自验 ref 16/16 PASS + 3neg全FAIL + §4.9三假全FAIL + 断言门16==16≥8✓。
- jsonl B 257→258, covered 159→160(spice_sim 126→127)。双仓已提交。
- **价值**：lcbck 印证 B r389「spice_sim hard part 在 parse 不在工具链深度 / spice-ratio 滤波对 parse-bound spice 域系统性低估」——讨论区论点获实测佐证。下轮继续核验剩余 41 cross-shard fresh。
