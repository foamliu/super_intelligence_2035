# Deepread: iqvz3 — MBIST PPR twincell error-injection diagnosis

- **trace**: 1793343432760_iqvz3 (thomas1w@hfeg0pkn005, mc149, 145 msgs, 794KB)
- **user**: thomas1w (thomaswu path owner)
- **domain**: verification (MBIST PPR sim debug, LPDDR5 DFT)
- **tool calls**: read_files:20, run_approved_command:17, editor:17, list_allowed_files:5
- **assets location**: /rundata/ddgoa/V0/simdir/verilog/thomaswu/... + /proj/ddgoa/V0/workdir/thomas1w/... (on 698 hosts, large/proprietary → B-synth)

## User turns (13 total)
- USER#1 (msg0, clean need): "/rundata/.../tm_mbistppr_twincell.x16/ 这个路径下，是我仿真的 log，测试用例 mbistmppr.v，注错 mbistmppr_auto_check.v，twincell==1 路径，row0=08200 row1=0C001 bnk0=2 bnk1=1 col0=2 col1=3，为啥我现在随机出来的这部分地址没有进行两笔特造错"
- USER#3 (msg51, check-my-fix): "看下 mbistmppr.v 569行 row0_map[15:12]={addr[14],addr[0],addr[13],addr[12]} 这么写可以么" (rule2 violation: user gives fix)
- USER#11 (msg107, clean need): "irun.log twincell 路径，我随机出来的只注错来三次，row0=06201 row1=03E00，看下是为什么"
- USER#12 (msg133, expected-behavior): "希望0和1注错两次，所以是4次，为啥 log中给的是三次注错打印"
- USER#4-10: conceptual Q&A (mbistrow_error_addr bit layout, RAMsb meaning, section selection)

## Root-cause diagnosis (assistant msg28, msg50, msg66)
- `mbistrow_error_addr[15:13]` = mat code (RAMsb counter, drives RA[15:13])
- Hardware `mBistRAMsbCnt`: `RA[15] = Cnt[2] & FullDensity`, `FullDensity = !(HalfDensity | cm1_gc_Twincell)`
- Under twincell==1: `FullDensity=0` → `RA[15]=0` → `RA[15:13]` clamped to {0,1,2,3} (mat 4-7 unreachable)
- Error injection condition (CA_QForce): requires `mbistra_error_cnt == mbistrow_error_addr[err_num]` (full 16-bit row match). Since `mbistra_error_cnt[15:13]` ∈ {0,1,2,3} under twincell, any `mbistrow_error_addr[err_num][15:13]` > 3 can NEVER match → the special manufactured error (mbisterror_bit_num=2, errforcebit=-3000) is skipped.
- USER#1 addresses: row0=0x08200 → mat=(0x08200>>13)&0x7=4 (>3, skip); row1=0x0C001 → mat=(0x0C001>>13)&0x7=5 (>3, skip). BOTH special errors skipped → matches "没有进行两笔特造错".
- USER#11 addresses: row0=0x06201 → mat=3 (in clamp, inject); row1=0x03E00 → mat=1 (in clamp, inject). Both in clamp → both should inject... but user says "只注错来三次" (3 not 4). The 4th missing error is a different sub-bug (err_num 0/1 each inject 2 bits? or ecc vs special counting). The trace's final resolution for USER#11 is less clean.

## Gold for case
- Use USER#1 (clean A-faithful need, both special errors skipped, clearest root cause).
- B-synth: build a Python diagnostic `diag_mbist_twincell.py` that parses (1) auto_check.v Verilog snippet → extracts RAMsb twincell clamp_max, (2) sim log → extracts errcheck + IO_FORCE_APPLY, (3) addr.json → row0/row1/bnk0/bnk1/col0/col1; computes mat=(row>>13)&0x7 for each special err_num, determines in_clamp (mat<=clamp_max) and injected (IO_FORCE_APPLY present), reports injected_count + skipped_err_nums + root_cause.
- Hidden B: different clamp_max (halfgood→1, or full→7), different addresses (some in/some out), different expected count. Anti-hardcode: source must not hardcode A's 08200/0C001/clamp=3.

## Case plan
- ID: EDA-Eval-DesignFlow-MbistTwincellDiag-001
- domain: verification, track: B-synth, level: L1-static (subprocess on hidden B)
- check.py ~14 conds: a zip+filename, b py_compile, c [B] exit0+JSON, d [B] required JSON keys, e [B] clamp_max correct, f [B] injected_count correct, g [B] err_num_0 injected flag, h [B] err_num_1 injected flag, i [B] skipped_err_nums correct, j [B] root_cause mentions mat>clamp, k [B] parses sim log IO_FORCE_APPLY count, l source no A-specific addrs hardcoded, m [A] runs on A assets gives A result (anti-hardcode guard), n randomization B' (mutated clamp+addrs) consistent structure
