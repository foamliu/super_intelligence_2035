# 污染扫描结果（自动生成）

- 黑名单来源（评测快照并集，任务数 5359）：
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-148.jsonl
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-46.jsonl
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-Updated102.jsonl
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether_TEST.jsonl
  - /nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/cuhk_benchmark_cxmt_format.jsonl
- 输入：/tmp/contam_s2_samples/finemath.jsonl
- 主阈值：n-gram=13，重合率 ≥ 0.8 判定命中
- 短文本兜底：n-gram=8，重合数 ≥ 1 判定命中（覆盖中文短 prompt 及嵌在长文档中的短串）
- 扫描文档数：12000（其中主 n-gram 无法覆盖、走兜底的有 0）
- **命中（污染）文档数：0**
