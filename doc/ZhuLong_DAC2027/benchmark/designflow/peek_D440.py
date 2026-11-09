import sys
sys.path.insert(0, '.')
from peek_dirbased import peek_one, extract_user_turns
import concurrent.futures

TARGETS = [
    ("1793672369557_fx2mf", "johnl", "10.129.2.10"),
    ("1793865688745_h12nr", "mike", "10.129.2.12"),
    ("1792460001779_paosw", "kaixuanx", "10.129.2.11"),
    ("1793843108682_lgbx4", "thomasz", "10.129.2.13"),
    ("1792743512849_1nuuf", "victorq", "10.129.2.11"),
    ("1793084065593_fg1kv", "ghyang", "10.129.2.12"),
    ("1793875415367_oue4a", "eva1wu", "10.129.2.11"),
    ("1793104325523_ad0nq", "jackjia", "10.129.2.12"),
]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:6]):
            print("  [U#%d] %s" % (i, tn[:600].replace("\n", " ")))
        print("---")
