交付接口：outputs/submit.zip 内含 fix.py（纯 Python 标准库）与 diagnose.json（根因诊断）。
CLI: python3 fix.py <rule_file> <config_file> <output_rule_file>   （从 config 读取 precision，将 LAYOUT PRECISION 注入 rule 文件：已存在则替换，缺失则于 LAYOUT system 行后插入；保留其余 LAYOUT 语句不动；exit 0 成功）
diagnose.json 须含字段 root_cause(str) / issues(list[str]) / fix_summary(str)，记录 OPEN1 错误根因与修复要点。
工作目录下 gen_preAA_G5_CIP_final_A.py 为出错脚本上下文（fixture，只读），calibreSTIcmp_A.rule 与 config_A.txt 为真实输入。
