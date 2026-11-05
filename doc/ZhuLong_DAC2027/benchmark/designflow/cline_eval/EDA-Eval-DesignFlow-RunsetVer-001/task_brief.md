交付修改后的 RunsetVersionFinder.py 到 outputs/submit.zip（zip 内顶层即该 .py 文件）。
输入脚本：assets/RunsetVersionFinder.py；可参考的 calibre runset 目录树样本：assets/calibre_tree_A.tar.gz（解压后用 VersionScanner(baseDir=<解压目录>) 扫描自测）。
判分：在隐藏的 calibre runset 目录上调用候选脚本的 VersionScanner(baseDir).scan()，校验 release/beta 版本分类与目录跳过规则。
