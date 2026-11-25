#!/usr/bin/env bash
# baize_posttrain_install_ray_patch.sh — Install .pth file for Ray worker patch propagation
#
# R53 (2026-11-08): Resolves R-009 — Ray workers don't inherit in-process monkey-patches.
#
# This script creates a .pth file in the venv's site-packages directory that:
#   1. Adds the run/ directory to sys.path (so baize_posttrain_sglang_patch.py is importable)
#   2. Conditionally imports baize_posttrain_sglang_patch when BAIZE_SGLANG_PATCH=1
#
# When Ray starts workers, it propagates env_vars to them. By setting
# BAIZE_SGLANG_PATCH=1 in the Ray runtime_env (or just exporting it before
# ray.init()), all worker processes will auto-import the patch module.
#
# Usage:
#   bash baize_posttrain_install_ray_patch.sh                    # Install into cu124 venv
#   bash baize_posttrain_install_ray_patch.sh --venv /path/to/venv  # Custom venv
#   bash baize_posttrain_install_ray_patch.sh --uninstall         # Remove the .pth file
#   bash baize_posttrain_install_ray_patch.sh --check             # Check if installed
#
# ⚠️ Must be run on .17 where the cu124 venv exists.
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

VENV_DIR="${BAIZE_VENV_DIR:-$HOME/code/verl_cu124_venv}"
ACTION="install"

while [ $# -gt 0 ]; do
  case "$1" in
    --venv) VENV_DIR="$2"; shift ;;
    --uninstall) ACTION="uninstall" ;;
    --check) ACTION="check" ;;
    *) echo "Unknown: $1" ;;
  esac
  shift
done

PTH_FILE_NAME="baize_posttrain_sglang_patch.pth"
PATCH_MODULE="baize_posttrain_sglang_patch.py"

# Find site-packages directory
SITE_PACKAGES=""
if [ -d "$VENV_DIR" ]; then
  # Try common locations
  for sp in "$VENV_DIR/lib/python3.10/site-packages" \
            "$VENV_DIR/lib/python3.11/site-packages" \
            "$VENV_DIR/lib/python3.12/site-packages" \
            "$VENV_DIR/lib/python3.*/site-packages"; do
    if [ -d "$sp" ]; then
      SITE_PACKAGES="$sp"
      break
    fi
  done
fi

case "$ACTION" in
  check)
    echo "=== Ray Patch .pth Check ==="
    echo "  Venv: $VENV_DIR ($([ -d "$VENV_DIR" ] && echo 'exists' || echo 'MISSING'))"
    if [ -z "$SITE_PACKAGES" ]; then
      echo "  Site-packages: NOT FOUND"
      exit 1
    fi
    echo "  Site-packages: $SITE_PACKAGES"
    PTH_PATH="$SITE_PACKAGES/$PTH_FILE_NAME"
    if [ -f "$PTH_PATH" ]; then
      echo "  .pth file: ✅ INSTALLED"
      echo "  Content:"
      cat "$PTH_PATH" | sed 's/^/    /'
    else
      echo "  .pth file: ❌ NOT INSTALLED"
    fi
    # Also check if patch module is reachable
    if [ -f "$SCRIPT_DIR/$PATCH_MODULE" ]; then
      echo "  Patch module: ✅ Found at $SCRIPT_DIR/$PATCH_MODULE"
    else
      echo "  Patch module: ❌ NOT FOUND at $SCRIPT_DIR/$PATCH_MODULE"
    fi
    ;;

  uninstall)
    if [ -z "$SITE_PACKAGES" ]; then
      echo "❌ Cannot find site-packages in $VENV_DIR"
      exit 1
    fi
    PTH_PATH="$SITE_PACKAGES/$PTH_FILE_NAME"
    if [ -f "$PTH_PATH" ]; then
      rm -f "$PTH_PATH"
      echo "✅ Removed $PTH_PATH"
    else
      echo "ℹ️ .pth file not found (nothing to remove)"
    fi
    ;;

  install)
    echo "=== Installing Ray Patch .pth ==="
    echo "  Venv: $VENV_DIR ($([ -d "$VENV_DIR" ] && echo 'exists' || echo 'MISSING'))"

    if [ ! -d "$VENV_DIR" ]; then
      echo "❌ Venv directory not found: $VENV_DIR"
      echo "   Run baize_posttrain_setup_cu124_venv.sh first, or specify --venv <path>"
      exit 1
    fi

    if [ -z "$SITE_PACKAGES" ]; then
      echo "❌ Cannot find site-packages in $VENV_DIR"
      echo "   Searched: $VENV_DIR/lib/python3.*/site-packages"
      exit 1
    fi

    echo "  Site-packages: $SITE_PACKAGES"

    # Verify patch module exists
    if [ ! -f "$SCRIPT_DIR/$PATCH_MODULE" ]; then
      echo "❌ Patch module not found: $SCRIPT_DIR/$PATCH_MODULE"
      exit 1
    fi
    echo "  Patch module: $SCRIPT_DIR/$PATCH_MODULE ✅"

    # Create .pth file
    # .pth files: lines starting with "import" are executed by site.py at startup
    # We add SCRIPT_DIR to sys.path, then conditionally import the patch module
    PTH_PATH="$SITE_PACKAGES/$PTH_FILE_NAME"
    cat > "$PTH_PATH" <<PTHEOF
# R53: Auto-propagate MiniCPM5 SGLang parser patch to all Python processes (including Ray workers)
# Only activates when BAIZE_SGLANG_PATCH=1 is set in the environment
import sys; sys.path.insert(0, '$SCRIPT_DIR')
import os; os.environ.get('BAIZE_SGLANG_PATCH') == '1' and __import__('baize_posttrain_sglang_patch')
PTHEOF

    echo "  .pth file: $PTH_PATH ✅"
    echo ""
    echo "  Content:"
    cat "$PTH_PATH" | sed 's/^/    /'
    echo ""
    echo "✅ Installation complete."
    echo ""
    echo "To activate the patch in Ray workers:"
    echo "  export BAIZE_SGLANG_PATCH=1"
    echo "  # Or in Ray runtime_env:"
    echo "  ray.init(runtime_env={'env_vars': {'BAIZE_SGLANG_PATCH': '1'}})"
    echo ""
    echo "To verify:"
    echo "  BAIZE_SGLANG_PATCH=1 $VENV_DIR/bin/python -c \\"
    echo "    'import baize_posttrain_sglang_patch; print(\"applied:\", baize_posttrain_sglang_patch.is_applied())'"
    ;;
esac
