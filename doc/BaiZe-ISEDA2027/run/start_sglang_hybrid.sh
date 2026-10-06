commit 2fe14fd74ede6ca61c9025dfc383ef06f6e89ecd
Author: paul.liu <paul.liu@cxmt.com>
Date:   Mon Oct 5 21:02:35 2026 +0800

    auto-commit 2026-10-05 21:02:35

diff --git a/doc/BaiZe-ISEDA2027/run/start_sglang_hybrid.sh b/doc/BaiZe-ISEDA2027/run/start_sglang_hybrid.sh
new file mode 100755
index 00000000..946f41e2
--- /dev/null
+++ b/doc/BaiZe-ISEDA2027/run/start_sglang_hybrid.sh
@@ -0,0 +1,17 @@
+#!/bin/bash
+# P-9.11: Start sglang server for BaiZe hybrid (nemotron_h) on GPU0
+export CUDA_VISIBLE_DEVICES=0
+HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/hf_checkpoints/p3_hybrid
+PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
+$PY -m sglang.launch_server \
+  --model-path $HF \
+  --model-name baize-hybrid \
+  --port 30000 \
+  --host 127.0.0.1 \
+  --context-length 131072 \
+  --mamba-ssm-dtype float32 \
+  --mamba-full-memory-ratio 1.0 \
+  --mem-fraction-static 0.88 \
+  --dtype bfloat16 \
+  --disable-radix-cache \
+  --log-level info 2>&1
