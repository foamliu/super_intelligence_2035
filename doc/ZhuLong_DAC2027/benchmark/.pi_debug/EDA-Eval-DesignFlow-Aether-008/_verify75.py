import json, urllib.request, sys

URL = "http://10.129.32.75:8669/v1/run_code"
with open("_combined_ref.tcl") as f:
    code = f.read()
code += '\nputs "REF75_RESULT:[check layout_via_enclosure_audit]"\n'
body = json.dumps({"code": code, "lang": "tcl", "host": "waveview"}).encode()
req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=120)
    out = json.loads(resp.read())
    print("STDOUT:", out.get("print_log", "")[-1500:])
    print("STDERR:", out.get("error_log", "")[-800:])
    print("RESPONSE:", out.get("response", "")[-1500:])
except Exception as e:
    print("ERR:", e)
    sys.exit(1)
