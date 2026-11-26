import json, urllib.request
URL = "http://10.129.32.75:8669/v1/run_code"
def run(fname, tag):
    with open(fname) as f: code = f.read()
    code += '\nputs "%s:[check layout_routing_audit]"\n' % tag
    body = json.dumps({"code": code, "lang": "tcl", "host": "waveview"}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    out = json.loads(urllib.request.urlopen(req, timeout=120).read())
    print(tag, "STDOUT:", out.get("print_log","")[-400:].strip())
    print(tag, "STDERR:", out.get("error_log","")[-300:].strip())
run("_combined_ref.tcl", "REF75")
run("_combined_naive.tcl", "NAIVE75")
