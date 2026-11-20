交付接口（≤3 行）：
- 入口：outputs/submit.zip，恰含 fix_cdl.py + T_IsmTop_fixed.cdl + diff_report.json
- CLI：`python3 fix_cdl.py <input_cdl> <output_cdl> <diff_report_json>`；同时生成 <input_cdl>.bak
- 输入 fixture：assets/EDA-Eval-DesignFlow-CdlBodyMapFix-001/T_IsmTop_A.cdl（先用它产出 T_IsmTop_fixed.cdl 与 diff_report.json）
