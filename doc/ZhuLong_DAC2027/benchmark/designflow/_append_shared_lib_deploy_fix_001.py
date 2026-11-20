#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate EDA-Eval-DesignFlow-SharedLibDeployFix-001 (spice_sim A-faithful L1).
Trace: 1793944907619_ddo96 e0024852@hfeg0pkn004 — FineSim gxrc_t libdizo.so missing fix.
Gold: copy missing non-system .so from P004 ref install, exclude system/glibc libs, set LD_LIBRARY_PATH.
"""
import json, os, shutil, zipfile, hashlib, subprocess, sys, tempfile

CASE_ID = "EDA-Eval-DesignFlow-SharedLibDeployFix-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE_ID)
REF = os.path.join(BENCH, "reference", CASE_ID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

SYSTEM_LIBS = ["libc.so.6", "ld-linux-x86-64.so.2", "libm.so.6",
               "libpthread.so.0", "librt.so.1", "libdl.so.2", "libgcc_s.so.1"]

# ---- A config ----
A_NEEDED = ["libdizo.so", "libabseil_dll.so", "libamd.so", "libcamd.so",
            "libcholmod.so", "libstdc++.so.6", "libnetcdf.so",
            "libfoo1.so", "libfoo2.so", "libfoo3.so", "libfoo4.so"] + SYSTEM_LIBS
A_P010_HAS = ["libfoo1.so", "libfoo2.so", "libfoo3.so", "libfoo4.so",
              "libextra1.so", "libextra2.so", "libextra3.so", "libextra4.so"]
A_MISSING = ["libdizo.so", "libabseil_dll.so", "libamd.so", "libcamd.so",
             "libcholmod.so", "libstdc++.so.6", "libnetcdf.so"]  # 7 missing non-system
A_P004 = A_NEEDED + ["libextra5.so", "libextra6.so", "libextra7.so"]  # 21 (dedup handles)
A_CRITICAL = ["libdizo.so", "libabseil_dll.so", "libstdc++.so.6"]  # gxrc_t checks these

# ---- B (hidden) config: different counts ----
B_MISSING = ["libdizo.so", "libsparse.so", "libumfpack.so", "libmetis.so",
             "libscotch.so", "libstdc++.so.6"]  # 6 missing non-system
B_P010_NEEDED_PRESENT = ["libfoo1.so", "libfoo2.so", "libfoo3.so"]
B_NEEDED = B_P010_NEEDED_PRESENT + B_MISSING + SYSTEM_LIBS  # 16
B_P010_HAS = B_P010_NEEDED_PRESENT + ["libextra1.so", "libextra2.so", "libextra3.so"]  # 6
B_P004 = B_NEEDED + ["libextra4.so", "libextra5.so"]  # 18
B_CRITICAL = ["libdizo.so", "libsparse.so", "libstdc++.so.6"]

def write_mock_gxrc_t(path, critical_libs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cl = " ".join(critical_libs)
    script = f"""#!/bin/bash
# mock gxrc_t - checks critical shared libs in ../lib/lib
LIBDIR="$(cd "$(dirname "$0")/.." && pwd)/lib/lib"
for lib in {cl}; do
    if [ ! -f "$LIBDIR/$lib" ]; then
        echo "$0: error while loading shared libraries: $lib: cannot open shared object file: No such file or directory" >&2
        exit 1
    fi
done
echo "gxrc_t: simulation ready"
exit 0
"""
    with open(path, "w") as f:
        f.write(script)
    os.chmod(path, 0o755)

def write_sos(dirpath, names):
    os.makedirs(dirpath, exist_ok=True)
    for n in names:
        with open(os.path.join(dirpath, n), "w") as f:
            f.write("# mock shared library placeholder\n")

def write_needed(path, libs):
    with open(path, "w") as f:
        for l in libs:
            f.write(l + "\n")

# ========== Generate A assets ==========
shutil.rmtree(ASSETS, ignore_errors=True)
A_ROOT = os.path.join(ASSETS, "GloryEX_2026.06_P010")
write_mock_gxrc_t(os.path.join(A_ROOT, "tool", "bin", "gxrc_t"), A_CRITICAL)
write_sos(os.path.join(A_ROOT, "tool", "lib", "lib"), A_P010_HAS)
A_P004_ROOT = os.path.join(ASSETS, "GloryEX_2026.06_P004")
write_sos(os.path.join(A_P004_ROOT, "tool", "lib", "lib"), list(dict.fromkeys(A_P004)))
write_needed(os.path.join(ASSETS, "needed_libs.txt"), A_NEEDED)

# ========== Generate hidden B ==========
HIDDEN = os.path.join(ASSETS, "hidden")
B_ROOT = os.path.join(HIDDEN, "GloryEX_2026.06_P010")
write_mock_gxrc_t(os.path.join(B_ROOT, "tool", "bin", "gxrc_t"), B_CRITICAL)
write_sos(os.path.join(B_ROOT, "tool", "lib", "lib"), B_P010_HAS)
B_P004_ROOT = os.path.join(HIDDEN, "GloryEX_2026.06_P004")
write_sos(os.path.join(B_P004_ROOT, "tool", "lib", "lib"), list(dict.fromkeys(B_P004)))
write_needed(os.path.join(HIDDEN, "needed_libs.txt"), B_NEEDED)
with open(os.path.join(HIDDEN, "hidden_manifest.json"), "w") as f:
    json.dump({"P010": "GloryEX_2026.06_P010", "P004": "GloryEX_2026.06_P004",
               "needed": "needed_libs.txt", "system_libs": SYSTEM_LIBS,
               "expected_copied": B_MISSING}, f, indent=2)

# ========== prompt + task_brief ==========
PROMPT = ('in /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/CH231_FS_guojing '
          'i run /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/GloryEX_2026.06_P010/tool/bin/gxrc_t '
          '-c gxrc_cci_cmd_V0d1_Rev07 and got error /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/GloryEX_2026.06_P010/tool/bin/gxrc_t: '
          'error while loading shared libraries: libdizo.so: cannot open shared object file: No such file or directory how to fix it')
with open(os.path.join(ASSETS, "prompt.txt"), "w") as f:
    f.write(PROMPT + "\n")
with open(os.path.join(ASSETS, "task_brief.md"), "w") as f:
    f.write("交付: outputs/submit.zip 内含 fix_missing_libs.sh。脚本接受 P010 P004 needed_libs.txt 三个路径参数，"
            "从 P004 补齐 P010 缺失的非系统 .so（排除 libc/ld-linux/libm/libpthread/librt/libdl/libgcc_s），"
            "并生成 setup_env.sh 导出 LD_LIBRARY_PATH 指向 P010/tool/lib/lib。判分在隐藏 GloryEX 目录上重跑。\n")

# ========== Reference gold solution ==========
shutil.rmtree(REF, ignore_errors=True)
os.makedirs(REF, exist_ok=True)
GOLD = r"""#!/bin/bash
# fix_missing_libs.sh P010_DIR P004_DIR NEEDED_LIBS_TXT
# Copy missing non-system shared libs from P004 to P010, create setup_env.sh
set -e
P010="$1"; P004="$2"; NEEDED="$3"
P010LIB="$P010/tool/lib/lib"
P004LIB="$P004/tool/lib/lib"
SYS_RE='^(libc\.so|ld-linux|libm\.so|libpthread|librt\.so|libdl\.so|libgcc_s)'
mkdir -p "$P010LIB"
copied=0
while IFS= read -r lib; do
    [ -z "$lib" ] && continue
    if [[ "$lib" =~ $SYS_RE ]]; then continue; fi
    if [ ! -f "$P010LIB/$lib" ]; then
        if [ -f "$P004LIB/$lib" ]; then
            cp -f "$P004LIB/$lib" "$P010LIB/$lib"
            copied=$((copied+1))
        fi
    fi
done < "$NEEDED"
SETUP="$P010/setup_env.sh"
cat > "$SETUP" <<ENVEOF
export LD_LIBRARY_PATH="$P010LIB:\$LD_LIBRARY_PATH"
ENVEOF
chmod +x "$SETUP"
echo "Copied $copied non-system libs from P004 to P010"
echo "Run 'source $SETUP' before gxrc_t"
"""
with open(os.path.join(REF, "fix_missing_libs.sh"), "w") as f:
    f.write(GOLD)
os.chmod(os.path.join(REF, "fix_missing_libs.sh"), 0o755)

# ========== check.py ==========
CHECK = r'''# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-SharedLibDeployFix-001.
Judges submit.zip by running fix_missing_libs.sh on hidden GloryEX_2026.06_P010_B
and verifying: missing non-system .so copied from P004, system/glibc libs excluded,
setup_env.sh exports LD_LIBRARY_PATH, gxrc_t runs after fix, originals preserved.
"""
import os, sys, shutil, zipfile, subprocess, tempfile, json

SYS_LIBS = ["libc.so.6", "ld-linux-x86-64.so.2", "libm.so.6",
            "libpthread.so.0", "librt.so.1", "libdl.so.2", "libgcc_s.so.1"]
SYS_PREFIXES = ("libc.so", "ld-linux", "libm.so", "libpthread", "librt.so", "libdl.so", "libgcc_s")

CONDITIONS = [
    ("a", "submit.zip unpacks and contains fix_missing_libs.sh"),
    ("b", "fix_missing_libs.sh passes bash -n syntax check"),
    ("c", "after fix, libdizo.so exists in P010/tool/lib/lib"),
    ("d", "all expected missing non-system libs copied (count == expected)"),
    ("e", "no system/glibc libs present in P010/tool/lib/lib after fix"),
    ("f", "setup_env.sh exists and contains LD_LIBRARY_PATH with tool/lib/lib"),
    ("g", "setup_env.sh passes bash -n syntax check"),
    ("h", "sourcing setup_env.sh then running gxrc_t exits 0"),
    ("i", "original P010 libs preserved (all originally-present files still exist)"),
    ("j", "libstdc++.so.6 present in P010/tool/lib/lib after fix (non-system needed lib)"),
]

def is_system(name):
    return any(name.startswith(p) for p in SYS_PREFIXES)

def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="chk_libfix_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmp)
        fix = os.path.join(tmp, "fix_missing_libs.sh")
        ok = {}
        # a
        ok["a"] = os.path.isfile(fix)
        if not ok["a"]:
            raise AssertionError("a: fix_missing_libs.sh not in submit.zip")
        os.chmod(fix, 0o755)
        # b
        r = subprocess.run(["bash", "-n", fix], capture_output=True, text=True)
        ok["b"] = (r.returncode == 0)
        # locate hidden B in workdir
        hidden = os.path.join(workdir, "hidden")
        if not os.path.isdir(hidden):
            # assets may be under assets/hidden
            hidden = os.path.join(workdir, "assets", "hidden")
        manifest_path = os.path.join(hidden, "hidden_manifest.json")
        with open(manifest_path) as f:
            manifest = json.load(f)
        P010 = os.path.join(hidden, manifest["P010"])
        P004 = os.path.join(hidden, manifest["P004"])
        NEEDED = os.path.join(hidden, manifest["needed"])
        expected_copied = manifest["expected_copied"]
        P010LIB = os.path.join(P010, "tool", "lib", "lib")
        # record original files
        orig_files = set(os.listdir(P010LIB)) if os.path.isdir(P010LIB) else set()
        # run fix
        env = dict(os.environ)
        r = subprocess.run(["bash", fix, P010, P004, NEEDED], capture_output=True, text=True, env=env, timeout=60)
        if r.returncode != 0:
            raise AssertionError(f"fix script failed: {r.stderr[:500]}")
        files_after = set(os.listdir(P010LIB)) if os.path.isdir(P010LIB) else set()
        # c
        ok["c"] = os.path.isfile(os.path.join(P010LIB, "libdizo.so"))
        # d
        copied = files_after - orig_files
        missing_expected = set(expected_copied)
        ok["d"] = missing_expected.issubset(copied) and len(copied - missing_expected) == 0
        # e
        sys_in_p010 = [f for f in files_after if is_system(f)]
        ok["e"] = (len(sys_in_p010) == 0)
        # f
        setup = os.path.join(P010, "setup_env.sh")
        ok["f"] = False
        if os.path.isfile(setup):
            content = open(setup).read()
            if "LD_LIBRARY_PATH" in content and "tool/lib/lib" in content:
                ok["f"] = True
        # g
        if ok["f"]:
            r2 = subprocess.run(["bash", "-n", setup], capture_output=True, text=True)
            ok["g"] = (r2.returncode == 0)
        else:
            ok["g"] = False
        # h
        gxrc = os.path.join(P010, "tool", "bin", "gxrc_t")
        ok["h"] = False
        if os.path.isfile(gxrc):
            r3 = subprocess.run(["bash", "-c", f"source {setup} && bash {gxrc}"],
                                capture_output=True, text=True, env=env, timeout=30)
            ok["h"] = (r3.returncode == 0)
        # i
        ok["i"] = orig_files.issubset(files_after)
        # j
        ok["j"] = os.path.isfile(os.path.join(P010LIB, "libstdc++.so.6"))
        # verdict
        failed = [k for k, v in ok.items() if not v]
        if failed:
            raise AssertionError("FAILED conditions: " + ", ".join(failed) +
                                 " | details: " + json.dumps({k: ok[k] for k in failed}))
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: check.py <submit.zip> <workdir>")
        sys.exit(2)
    try:
        check(sys.argv[1], sys.argv[2])
        print("ALL PASS")
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
'''
with open(os.path.join(REF, "check.py"), "w") as f:
    f.write(CHECK)

# ========== negatives ==========
NEG = os.path.join(REF, "negative")
os.makedirs(NEG, exist_ok=True)
# naive: copy ALL missing libs including system (will fail e)
with open(os.path.join(NEG, "naive_copy_all.sh"), "w") as f:
    f.write("""#!/bin/bash
P010="$1"; P004="$2"; NEEDED="$3"
P010LIB="$P010/tool/lib/lib"; P004LIB="$P004/tool/lib/lib"
mkdir -p "$P010LIB"
while IFS= read -r lib; do
    [ -z "$lib" ] && continue
    [ ! -f "$P010LIB/$lib" ] && [ -f "$P004LIB/$lib" ] && cp -f "$P004LIB/$lib" "$P010LIB/$lib"
done < "$NEEDED"
cat > "$P010/setup_env.sh" <<EOF
export LD_LIBRARY_PATH="$P010LIB:\$LD_LIBRARY_PATH"
EOF
chmod +x "$P010/setup_env.sh"
""")
# stub: always echo success, do nothing (fails c,h)
with open(os.path.join(NEG, "always_ok.sh"), "w") as f:
    f.write("""#!/bin/bash
echo "fix done"
""")
# print_expected: hardcode expected libs (fails on B different counts)
with open(os.path.join(NEG, "hardcoded_A.sh"), "w") as f:
    f.write("""#!/bin/bash
P010="$1"; P004="$2"; NEEDED="$3"
P010LIB="$P010/tool/lib/lib"; P004LIB="$P004/tool/lib/lib"
mkdir -p "$P010LIB"
for lib in libdizo.so libabseil_dll.so libamd.so libcamd.so libcholmod.so libstdc++.so.6 libnetcdf.so; do
    [ ! -f "$P010LIB/$lib" ] && cp -f "$P004LIB/$lib" "$P010LIB/$lib" 2>/dev/null
done
cat > "$P010/setup_env.sh" <<EOF
export LD_LIBRARY_PATH="$P010LIB:\$LD_LIBRARY_PATH"
EOF
chmod +x "$P010/setup_env.sh"
""")
for n in ["naive_copy_all.sh", "always_ok.sh", "hardcoded_A.sh"]:
    os.chmod(os.path.join(NEG, n), 0o755)

NEG_SELFTEST = r'''#!/usr/bin/env python3
import subprocess, sys, os, tempfile, zipfile, shutil
NEG = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(NEG)
CHECK = os.path.join(REF, "check.py")
CASE = os.path.dirname(REF)
BENCH_ROOT = os.path.dirname(os.path.dirname(CASE))
ASSETS = os.path.join(os.path.dirname(REF), "..", "assets")
# find hidden dir
hidden = None
for root, dirs, files in os.walk(os.path.join(BENCH_ROOT, "assets")):
    if "hidden_manifest.json" in files:
        hidden = root; break
if not hidden:
    print("no hidden found"); sys.exit(2)
results = {}
for neg in ["naive_copy_all.sh", "always_ok.sh", "hardcoded_A.sh"]:
    tmp = tempfile.mkdtemp()
    try:
        zp = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.write(os.path.join(NEG, neg), "fix_missing_libs.sh")
        r = subprocess.run([sys.executable, CHECK, zp, os.path.dirname(hidden)],
                           capture_output=True, text=True, timeout=120)
        results[neg] = (r.returncode != 0)
        # restore hidden (copy fresh from git is ideal; here we just re-extract needed)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # NOTE: negatives modify hidden dirs; we accept state may be dirty across runs
all_fail = all(results.values())
print("negative results:", results)
print("ALL FAIL" if all_fail else "SOME PASS (BAD)")
sys.exit(0 if all_fail else 1)
'''
with open(os.path.join(NEG, "negative_selftest.py"), "w") as f:
    f.write(NEG_SELFTEST)

# ========== self-verify ==========
def make_submit(fix_path):
    tmp = tempfile.mkdtemp()
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.write(fix_path, "fix_missing_libs.sh")
    return zp

def run_check_on_B(fix_path):
    """Run check.py against hidden B. Returns (ok, msg). Reverts B after."""
    hidden_dir = os.path.join(ASSETS, "hidden")
    # snapshot B original state
    b_p010 = os.path.join(hidden_dir, "GloryEX_2026.06_P010", "tool", "lib", "lib")
    orig = {}
    if os.path.isdir(b_p010):
        for f in os.listdir(b_p010):
            orig[f] = open(os.path.join(b_p010, f)).read()
    setup_path = os.path.join(hidden_dir, "GloryEX_2026.06_P010", "setup_env.sh")
    setup_existed = os.path.exists(setup_path)
    try:
        zp = make_submit(fix_path)
        r = subprocess.run([sys.executable, os.path.join(REF, "check.py"), zp, ASSETS],
                           capture_output=True, text=True, timeout=120)
        return (r.returncode == 0, r.stdout.strip() + r.stderr.strip())
    finally:
        # revert B
        if os.path.isdir(b_p010):
            cur = set(os.listdir(b_p010))
            for f in cur - set(orig):
                os.remove(os.path.join(b_p010, f))
            for f, c in orig.items():
                with open(os.path.join(b_p010, f), "w") as fh:
                    fh.write(c)
        if setup_existed:
            pass
        elif os.path.exists(setup_path):
            os.remove(setup_path)

# ref must PASS
ok_ref, msg = run_check_on_B(os.path.join(REF, "fix_missing_libs.sh"))
print(f"[self-verify] ref PASS={ok_ref}: {msg[:200]}")
assert ok_ref, f"REF must PASS but: {msg}"

# negatives must all FAIL
for neg in ["naive_copy_all.sh", "always_ok.sh", "hardcoded_A.sh"]:
    ok, msg = run_check_on_B(os.path.join(NEG, neg))
    print(f"[self-verify] neg {neg} FAIL={not ok}: {msg[:120]}")
    assert not ok, f"negative {neg} must FAIL but PASSED"

# §4.9 fake submissions
FAKES = {"empty": "", "print_expected": '#!/bin/bash\necho "libdizo.so libabseil_dll.so libamd.so libcamd.so libcholmod.so libstdc++.so.6 libnetcdf.so"\n',
         "del_core": GOLD.replace('cp -f "$P004LIB/$lib" "$P010LIB/$lib"', 'true')}
for name, content in FAKES.items():
    tmp = tempfile.mkdtemp()
    fp = os.path.join(tmp, "fix.sh")
    with open(fp, "w") as f:
        f.write(content)
    os.chmod(fp, 0o755)
    ok, msg = run_check_on_B(fp)
    print(f"[self-verify] fake {name} FAIL={not ok}")
    assert not ok, f"fake {name} must FAIL"
    shutil.rmtree(tmp, ignore_errors=True)

k_check = 10  # a-j in check.py CONDITIONS
assert k_check >= 8, f"k_check={k_check} < 8"

# ========== append jsonl ==========
TEST_SRC = open(os.path.join(REF, "check.py")).read()
entry = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        {"name": "GloryEX_2026.06_P010", "source": "GloryEX_2026.06_P010",
         "desc": "真实 FineSim gxrc_t 安装目录（A 资产，trace ddo96 e0024852@pkn004 原文路径结构）：tool/bin/gxrc_t（模拟二进制，检查 ../lib/lib 中关键 .so）+ tool/lib/lib/（缺失 libdizo.so 等 7 个非系统库，仅含 4 needed+4 extra）"},
        {"name": "GloryEX_2026.06_P004", "source": "GloryEX_2026.06_P004",
         "desc": "参考完整安装（P004，含全部 11 非系统 needed + 7 系统 glibc + 3 extra = 21 .so）；从中补齐 P010 缺失的非系统库"},
        {"name": "needed_libs.txt", "source": "needed_libs.txt",
         "desc": "gxrc_t 依赖的 18 个共享库清单（11 非系统 + 7 系统/glibc）；系统库不得复制"},
        {"name": "prompt.txt", "source": "prompt.txt",
         "desc": "真实用户原话（A-faithful，e0024852 @ hfeg0pkn004，trace 1793944907619_ddo96 U#0 逐字原文）：gxrc_t 运行报 libdizo.so missing，问 how to fix it"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口说明（≤3 行）：outputs/submit.zip 内含 fix_missing_libs.sh，接受 P010 P004 needed_libs.txt 三参数，补齐缺失非系统 .so + 生成 setup_env.sh"},
    ],
    "test": TEST_SRC,
    "metadata": {
        "trace_source": {
            "user": "e0024852",
            "host": "hfeg0pkn004",
            "session_file": "1793944907619_ddo96.messages.json",
            "match_count": 218,
            "real_task_summary": "FineSim gxrc_t 共享库部署修复：P010 安装 tarball 截断导致 libdizo.so 等 7 个非系统库缺失（186/1349 库）。金标准=从 P004 参考安装补齐缺失非系统 .so，排除 glibc 系统库（libc.so.6/ld-linux/libm/libpthread/librt/libdl/libgcc_s）避免段错误，保留 libstdc++.so.6，生成 setup_env.sh 导出 LD_LIBRARY_PATH。trace ddo96 e0024852@pkn004（11-06 fresh，218 spice hits，FineSim SRAM bitcell DTCO）。"
        },
        "domain": "spice_sim",
        "shard": "B",
        "a_faithful": True,
        "track": "faithful",
        "level": "L1",
        "k_check": k_check,
        "k_rationale": k_check,
        "test_rationale": "10 条断言：① submit.zip 含 fix_missing_libs.sh ② fix_missing_libs.sh bash -n 语法通过 ③ 修复后 P010/tool/lib/lib 存在 libdizo.so ④ 全部缺失非系统库从 P004 补齐且无多补（count==expected） ⑤ P010/tool/lib/lib 无任何系统/glibc 库（libc.so.6/ld-linux/libm/libpthread/librt/libdl/libgcc_s 缺席） ⑥ setup_env.sh 存在且含 LD_LIBRARY_PATH 与 tool/lib/lib ⑦ setup_env.sh bash -n 语法通过 ⑧ source setup_env.sh 后跑 gxrc_t 退出码 0 ⑨ P010 原有库全部保留未被删除 ⑩ libstdc++.so.6 在 P010 修复后存在（非系统 needed 库须补齐）",
        "negatives": ["naive_copy_all", "always_ok", "hardcoded_A"],
        "negatives_all_fail": True,
        "section_4_9_fake_submissions_fail": True,
    }
}
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print(f"Appended {CASE_ID} to {JSONL}")
print(f"k_check={k_check} k_rationale={k_check}")
print("DONE")
