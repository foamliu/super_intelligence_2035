# 交付接口

交付件：`outputs/submit.zip`，内含 `rcmax_compare.py`（Python3，递归比较两棵 StarRC RCMAX 明文数据树）。

CLI：`python3 rcmax_compare.py <rootA> <rootB> <out_report.txt>` —— 递归 walk 两棵树，字节级比对同名文件，逐行统计差异，把结构化报告写入 `<out_report.txt>` 并 stdout 打印摘要。
