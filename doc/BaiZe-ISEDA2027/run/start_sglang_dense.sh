commit 2fe14fd74ede6ca61c9025dfc383ef06f6e89ecd
Author: paul.liu <paul.liu@cxmt.com>
Date:   Mon Oct 5 21:02:35 2026 +0800

    auto-commit 2026-10-05 21:02:35

diff --git a/doc/BaiZe-ISEDA2027/run/start_sglang_dense.sh b/doc/BaiZe-ISEDA2027/run/start_sglang_dense.sh
new file mode 100755
index 00000000..94d7ef14
--- /dev/null
+++ b/doc/BaiZe-ISEDA2027/run/start_sglang_dense.sh
@@ -0,0 +1,15 @@
+#!/bin/bash
+# P-9.11: Start sglang server for BaiZe dense (Llama) on GPU1
+export CUDA_VISIBLE_DEVICES=1
+HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/hf_checkpoints/p3_dense
+PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
+$PY -m sglang.launch_server \
+  --model-path $HF \
+  --model-name baize-dense \
+  --port 30001 \
+  --host 127.0.0.1 \
+  --context-length 131072 \
+  --mem-fraction-static 0.88 \
+  --dtype bfloat16 \
+  --disable-radix-cache \
+  --log-level info 2>&1
