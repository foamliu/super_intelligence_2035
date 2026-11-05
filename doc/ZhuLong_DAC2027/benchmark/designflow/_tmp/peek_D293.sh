#!/bin/bash
# serial peek runner for D293 batch
READER="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_tmp/reader_D281.py"
BATCH="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_tmp/peek_D293_batch.tsv"
OUT="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_tmp/peek_D293_out.txt"
> "$OUT"
tail -n +2 "$BATCH" | while IFS=$'\t' read -r rank sid user ip; do
  [ -z "$sid" ] && continue
  echo "===SID:$sid===" >> "$OUT"
  ssh -o StrictHostKeyChecking=no -o ConnectTimeout=12 "$ip" "python3 - $sid $user" < "$READER" >> "$OUT" 2>&1
  echo "" >> "$OUT"
done
echo "PEEK DONE"
