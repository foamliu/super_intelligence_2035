# 交付接口（仅接口与文件位置，不含"要做什么"）

交付件：`outputs/submit.zip`，必须包含一个可运行生成器脚本 `compare_itf.py`，以及它对当前可见 5 份 ITF（在 `assets/EDA-Eval-DesignFlow-ItfCompare-001/itf/` 下）运行后产出的 `comparison.json` 与 `comparison.md`。

`compare_itf.py` 的调用契约：`python3 compare_itf.py <input_dir>`，`<input_dir>` 是一个含若干 `.itf` 文件的目录；它必须把结构化对比结果写入当前目录的 `comparison.json`（机器可读）和 `comparison.md`（人读表格）。判分器会在一组**不同的隐藏 ITF**上重跑你的脚本并校验结果。
