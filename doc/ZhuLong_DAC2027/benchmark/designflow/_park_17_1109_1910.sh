#!/bin/bash
# Batch park 17 new un-ledgered spice sids from 11-09 cron diff (0 viable)
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark
# format: sid user host hspice note
park() {
  local sid=$1 user=$2 host=$3 mc=$4 note=$5
  python3 designflow/trace_ledger.py --shard B claim --session "$sid" --user "$user" --host "$host" --match "$mc" --domain spice_sim 2>/dev/null
  python3 designflow/trace_ledger.py --shard B mark --session "$sid" --status parked --note "$note" 2>/dev/null
  echo "parked $sid ($user@$host mc=$mc): $note"
}
park 1793674432523_cpvbl e0039602 hfeg0pkn004 9 "1109cron-diff peek: 6msg trivial no-user-text; calibre-dominant wrong-shard C"
park 1791425249788_4ldaa colinxu hfeg0pkn002 6 "1109cron-diff: virtuoso-dominant(25) wrong-shard D, not peeked"
park 1793778171219_tq83u e0046686 hfeg0pkn005 5 "1109cron-diff: 316netlist+5hspice but NFS-flaky unreadable on pkn005"
park 1794133038396_0nnlr e0023936 hfeg0pkn004 3 "1109cron-diff: virtuoso/schematic-dominant wrong-shard D"
park 1791795684242_lxy78 e0039602 hfeg0pkn004 3 "1109cron-diff peek: 6msg trivial no-user-text reject"
park 1794125570732_twmgl e0023936 hfeg0pkn004 2 "1109cron-diff: 4msg-class trivial low-spice"
park 1794124556477_6mnn7 e0023936 hfeg0pkn004 2 "1109cron-diff: schematic/virtuoso-dominant wrong-shard D"
park 1793955833843_7hcwf e0039602 hfeg0pkn004 2 "1109cron-diff: 2hspice+1calibre trivial"
park 1793951773950_guxvg e0047722 hfeg0pkn001 2 "1109cron-diff: pyAether-dominant(68) wrong-shard D/aether"
park 1793760816185_ahiez e0046686 hfeg0pkn005 2 "1109cron-diff: 2netlist+2hspice trivial"
park 1794045295255_m9zo4 legendd hfeg0pkn002 1 "1109cron-diff: virtuoso/schematic-dominant wrong-shard D"
park 1794044717680_q5znu thomasz hfeg0pkn001 1 "1109cron-diff peek: 6msg trivial no-user-text reject; calibre-dominant"
park 1793925634338_7qzdr e0046686 hfeg0pkn005 1 "1109cron-diff: 36netlist+1hspice low-spice pkn005-flaky"
park 1793619261390_uyqhw e0039602 hfeg0pkn004 1 "1109cron-diff peek: 6msg trivial no-user-text reject; pyAether-dominant"
park 1793188714775_8nyrm e0044587 hfeg0pkn004 1 "1109cron-diff: pyAether-dominant(11) wrong-shard D"
park 1793169071103_vafrf e0039602 hfeg0pkn004 1 "1109cron-diff: 1hspice trivial"
park 1793103814409_kxeno e0044587 hfeg0pkn004 1 "1109cron-diff: 1hspice+1calibre trivial"
echo "=== done park 17 ==="
python3 designflow/trace_ledger.py --shard B stats 2>&1 | head -6
