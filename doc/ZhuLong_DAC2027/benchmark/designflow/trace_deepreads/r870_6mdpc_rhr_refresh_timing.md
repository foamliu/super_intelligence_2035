# r870 deepread — DRAM RHR refresh timing & attack-count semantics analysis-Q&A (6mdpc)

## Trace
- session: `1794987681428_6mdpc` (user xuluo, host hfeg0plg74 / 10.129.8.112, also hfeg0plg15 / 172.16.8.191)
- mc=183, kw: verilog:797;rtl:352;netlist:88;systemverilog:25 (clean A-pure digital/verification)
- 221 msgs / 21 real user turns, messages.json 1.1MB, ALIVE (Nov 20 15:08)
- r870 session eda_flow open+scp+close

## User intent (U#1 = full context summary, 3668 chars)
User pasted a complete context summary of PyRHR(Python) vs SV(RTL) row-hammer test alignment work, then asks 20 follow-up analysis-Q&A questions about DRAM refresh timing, attack count semantics, and Python-vs-SV divergence.

## 4 key questions selected for case (all single-turn analysis-Q&A, self-contained from U#1 context)

### Q1 (U#15, msg 205): "我需要确定的是，多久时间下所有DRAM中WL都被刷新了一轮，怎么确定"
**Gold (msg 206)**: tREF = rows_per_bank × tREFI_m = 8192 × 15.6µs ≈ 127.8ms.
Key insight: DDR auto-refresh REF refreshes ALL banks' same row simultaneously (rank-level), so one full round = 8192 REFs (not 262144). NOT total_rows × tREFI (=4.09s, wrong).
Python comparison: 132096/3 × 3900ns ≈ 171.7ms (explicit per-3-row sweep).
tREF = 3900*8*1024 = 8192 × tREFI (standard DDR full-refresh-cycle definition in rhr_parameter.pkg).

### Q2 (U#17, msg 209): "全部刷完一轮的时候，所有WL的攻击次数要清0吧，RTL是怎么判断刷到哪一跟WL了"
**Gold (msg 210)**: NO. Normal refresh (auto-refresh) is completely transparent to the monitor — rhr_monitor.sv performance_monitor has only 4 branches (ACT, negedge rhr_pump, posedge rhr_pump, finish_attack), NONE monitor normal REF. Normal refresh neither increments nor clears any attack count.
4 clearing mechanisms (all local or time-based, preserve max_hammer_count):
1. ACT → actflush_update (clear that row's current count if in hammer_queue as victim)
2. RHR pump → flush_update (clear RHR-restored row's current count)
3. time decay → ref_decay_update (~255.6ms = tREFI_m×16×1024 timeout)
4. noise cleanup → noise_update (idle>1ms && count<10 → delete)
Python divergence: Python DOES count normal refresh as hammer/clear event (normal_refresh addr merged into df).

### Q3 (U#20, msg 217): "RTL中ACT某一行，该行攻击次数清0？"
**Gold (msg 218)**: YES. ACT triggers two simultaneous actions in rhr_monitor.sv L31-32:
1. hammer_update(act_flag=1) — act_add as aggressor, +1 to ±1 neighbors, +a to ±2 neighbors
2. actflush_update(act_add) — clear that row's current count (hammer_plus1/plus2/minus1/minus2=0) when victim_add1==act_add in hammer_queue
Key: preserves max_hammer_count (historical peak NOT cleared). Normal REF does NOT clear.

### Q4 (U#21, msg 219): "大概多少时间会RHR到同一行"
**Gold (msg 220)**: ≈ DLUT_depth × tREFI.
DLUT_table_depth=6, round-robin (rri+1)%6. RHR pump embedded in normal REF (every tREFI). Each REF → 1 RHR →刷 DLUT one item.
SV: 6 × 15.6µs ≈ 93.6µs. Python: 6 × 3900ns ≈ 23.4µs.
Caveats: row must stay in DLUT table (discard may evict), rhr_cnt/val_lfsr variability, only RHR1 walks round-robin (RHR2/RHR3 are ±2/±3 邻行).

## Case design
- A档 trace-faithful analysis-Q&A, k=12
- Fixture A: context_summary_A.md (U#1 verbatim) + rhr_params_A.txt (key params from trace)
- Hidden B: same structure, different params (tREFI=31200, nWL=65536, DLUT_depth=8, BANK_NUM=16, rows_per_bank=4096)
- check.py: dynamically parse B params, verify 4 answers with correct formulas + numeric values + anti-leak + refuse-to-hallucinate
