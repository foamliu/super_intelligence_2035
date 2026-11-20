# calibre_env_excerpt.sh -- excerpt of Calibre 2020.1_36 calibre_env script.
# Shows the VCO autoswitch logic that fails on RHEL 8 (VCO=aok) when run as a
# non-interactive process (no .bashrc -> no module load -> CALIBRE_HOME unset).
#
# Bug: the grep below uses shell variable names that bash parses as
#   $SW_WKSTN_  and  $MGC_VCO_   (names WITH trailing underscore -> empty)
# instead of   $SW_WKSTN + "_"  and  $MGC_VCO + "_".
# So the grep almost never matches -> autoswitch not enabled -> aok tree not
# found -> error.  CALIBRE_SKIP_OS_CHECKS=1 does NOT skip this.

MGC_VCO_REAL=aok            # OS reports aok (RHEL 8)
INSTALLED_TREE=aoi          # installed Calibre tree is aoi

# --- calibre_env (excerpt) ---
# unconditional VCO detection (runs even if CALIBRE_HOME is set):
MGC_VCO=$(/opt/mentor/bin/calibre_vco)        # returns 'aok'

# autoswitch grep (BUGGY):
echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'
# bash sees  $SW_WKSTN_  (empty) and  $MGC_VCO_  (empty)  ->  echo "__"  -> no match
# intended:  echo "_${SW_WKSTN}_${MGC_VCO}_"  ->  echo "_<wkstn>_aok_"  -> match

if [ $? -ne 0 ]; then
    echo "ERROR: VCO $MGC_VCO not supported by autoswitch; no matching tree" >&2
    exit 1
fi
