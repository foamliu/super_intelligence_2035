交付：outputs/submit.zip，含一个可运行的 Python 解析脚本 `sabl_summary.py`（CLI: `python3 sabl_summary.py <spf_file> <out_csv>`，纯字符串操作实现，不依赖第三方库）。
脚本读取工作目录下的 StarRC DSPF 1.3 格式 SPF 文件，按 prompt 中的列规范输出 SABL coupling 汇总 CSV（23 列）。
判分时会用一份结构不同但格式相同的隐藏 SPF 重新运行你的脚本，校验输出 CSV 的结构、CP 排序、Sa_BLa/Sa_BLb 配对、各类耦合累加值与 total/power。
