#!/bin/bash
# Pre-install astropy in the rootfs template (P1-1 prebuild)
# Runs pip install -e .[test] inside unshare sandbox with host gcc/gfortran
set -e
R=/nas_train/app.e0031982/harness_work/rootfs/astropy__astropy-12907
echo "[prebuild] git reset --hard HEAD..."
cd "$R/testbed" && git reset --hard HEAD && git clean -fdq
echo "[prebuild] starting pip install -e .[test] (timeout=3600s)..."

timeout 3600 unshare --user --map-root-user --mount --fork bash -c "
    mount --bind /usr $R/usr || exit 11
    mount -t tmpfs tmpfs $R/tmp || exit 13
    chroot $R /usr/bin/env HOME=/tmp TMPDIR=/tmp PIP_NO_INPUT=1 \
        http_proxy=http://172.19.92.25:13128 \
        https_proxy=http://172.19.92.25:13128 \
        PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
        PIP_NO_BUILD_ISOLATION=1 \
        /bin/bash -c 'source /opt/miniconda3/bin/activate && conda activate testbed && cd /testbed && python -m pip install -e .[test] --verbose 2>&1 | tail -80'
"
RC=$?
echo "[prebuild] finished with rc=$RC"
if [ $RC -eq 0 ]; then
    echo "[prebuild] SUCCESS"
    # Verify astropy is importable
    timeout 60 unshare --user --map-root-user --mount --fork bash -c "
        mount --bind /usr $R/usr || exit 11
        mount -t tmpfs tmpfs $R/tmp || exit 13
        chroot $R /usr/bin/env HOME=/tmp /bin/bash -c 'source /opt/miniconda3/bin/activate && conda activate testbed && python -c \"import astropy; print(astropy.__version__)\"'
    " 2>&1 | tail -5
else
    echo "[prebuild] FAILED or TIMEOUT"
fi
