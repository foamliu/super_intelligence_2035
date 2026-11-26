# 交付接口

- 交付件：`outputs/submit.zip`，内含一个 Python 程序 `pdk_dir_size_check.py`（+ 若需辅助文件一并打包）。
- 程序须可用 `python3 pdk_dir_size_check.py --root <dir> --threshold <GB> --out-dir <out>` 运行，扫描 root 下每个一级子目录大小，筛选大于阈值(GB)的目录，按从小到大输出 HTML 报告，并生成可被 `/home/xxchen/mail/autoMail.py + input.js` 方式发送邮件的 `input.js`。
- 资产目录内附 `autoMail.py`（邮件工具，含 `autoMail(input)` 接口）与 `input.js`（格式样例），供参考其调用约定。
