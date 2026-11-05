交付接口：outputs/submit.zip 内只含 pt_version_recon.py（纯 Python 标准库）。
CLI: python3 pt_version_recon.py <install_root>  （枚举 install_root 顶层条目，区分真实安装目录与符号链接，解析各版本 install.log 的 product/version/installer，检查 bin/pt_shell 与 bin/primetime，解析符号链接 readlink/realpath 并判定是否指向 install_root 树外，输出结构化 JSON 到 stdout，含 versions 列表与 recommendation——推荐用于 STA flow 调试的最新真实 pts 安装版本）。
工作目录下 primetime_install/ 为 /apps/synopsys/primetime 的真实目录快照（fixture，只读分析；其旁 primepower/ 为符号链接指向的树外目标，亦只读）。
