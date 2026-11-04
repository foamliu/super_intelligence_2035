交付接口：outputs/submit.zip 内含 apply_opt.py（纯 Python 标准库，无第三方依赖）。
CLI: python3 apply_opt.py <report.txt> <src_deck.rule> <output_deck>  （读取报告里给出的优化内容并应用到源 deck，写出优化后的 deck）
输入文件位于工作目录：report_A.txt（DRC Log 分析报告）、calibreDFM_A.rule（源 calibre DRC rule deck）。
