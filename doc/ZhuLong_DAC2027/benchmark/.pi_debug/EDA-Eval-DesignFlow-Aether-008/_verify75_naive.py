import json, urllib.request
URL = "http://10.129.32.75:8669/v1/run_code"
with open("_combined_naive.tcl") as f:
    code = f.read()
# combined_naive = naive_impl + checker; need a driver call. Check what proc check expects.
code += '\nputs "NAIVE75_RESULT:[check layout_via_enclosure_audit]"\n'
body = json.dumps({"code": code, "lang": "tcl", "host": "waveview"}).encode()
req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=120)
    out = json.loads(resp.read())
    print("NAIVE STDOUT:", out.get("print_log", "")[-1800:])
    print("NAIVE STDERR:", out.get("error_log", "")[-400:])
except Exception as e:
    print("ERR:", e)
