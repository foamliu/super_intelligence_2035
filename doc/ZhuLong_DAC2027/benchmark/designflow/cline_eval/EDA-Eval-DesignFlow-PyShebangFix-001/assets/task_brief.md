交付接口：outputs/submit.zip 内含 fix_shebang.py（纯 Python 标准库）与 diagnose.json（根因诊断）。
CLI: python3 fix_shebang.py <drc_auto_py> <bashrc> <output_py>   （诊断 drc_auto.py 的 shebang 与 .bashrc 中 module 加载的 Python 版本冲突，将硬编码绝对路径 shebang 改写为 #!/usr/bin/env python3，保留文件其余内容不动；成功 exit 0）
diagnose.json 须含字段 root_cause(str) / shebang_before(str) / shebang_after(str) / module_python_version(str) / env_vars_conflict(list[str]) / fix_summary(str)。
工作目录下 drc_auto_A.py 与 .bashrc_A 为真实输入（fixture，只读）。
