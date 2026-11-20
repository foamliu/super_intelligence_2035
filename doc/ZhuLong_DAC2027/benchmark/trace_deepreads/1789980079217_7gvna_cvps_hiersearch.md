# Deepread: 1789980079217_7gvna — CVPS HierSearch SKILL 脚本调试

## Trace meta
- session: 1789980079217_7gvna
- user: thomasz @ hfeg0pfn058 (10.129.33.184)
- scene: 普通对话, status=failed, exit=1
- started 2026-09-21T08:41:19Z, ended 2026-09-29T01:59:01Z (8 days span, likely reconnects)
- cwd: /home/thomasz/zl_test/DRCOA_V0907_IDD5B/report
- model: deepseek-v4-flash (cxmt-deepseek-flash)
- 16 messages, 3 user inputs
- keywords: verilog:154;cellview:35;ddgetobj:33;schematic:20;virtuoso:11;dbget:10;dbopencellviewbytype:8;analog:8
- D-domain match_count: 14

## User intent (verbatim A档)
1. "/home/thomasz/tmp/CXMTseCVPSHierSearch.il\n读取一下这个脚本"
2. "哪个功能执行后会在我目录下生成.HierSearch隐藏目录"
3. "其他人遇到了 search verilog执行完了，但是没有.HierSearch的隐藏目录生成"

## Script under analysis
`CXMTseCVPSHierSearch.il` — 708 行 Cadence Virtuoso SKILL 层次化搜索工具 v2.0
- Author: AaronWang (v1.0a 2022/12/14), Wens (v1.1a-v1.4a 2024), hana.song (v1.1b)
- 12 procedures:
  - CXMTseCVPSHierSearch_Main_GUI (L42) — 4-tab GUI form
  - CXMTseCVPSHierSearch_Main_CB (L199) — callback, dispatch by tabNum
  - CXMTseCVPSHierSearch_all (L246) — main search dispatcher
  - CXMTseHierSearch_CVPS_loophier (L397) — recursive hierarchy walk
  - CXMTseCVPSHierSearch_cvpsHcell_loop (L491) — Hcell search
  - CXMTseHierSearch_CVPS_pParUsedCheck (L533)
  - CXMTseHierSearch_CVPS_Latch (L562)
  - CXMTseHierSearch_CVPS_VerilogParam (L588)
  - CXMTseHierSearch_CVPS_multipleDriver (L603)
  - CXMTseHierSearch_CVPS_multipleDriver_loop (L656)
  - CXMTseHierSearch_CVPS_traceNet (L687)
  - CXMTseHierSearch_CVPS_traceNetCB (L697)
- 4 search modes (tabs):
  1. Search Verilog — find cells with verilog view in hierarchy
  2. Search Pre-CVPS — Latch/multi-driver/non-TECHLIB pcell checks
  3. Search Pin Short — probeShort device check
  4. Search Hcell — CVPS Hcell search

## Bug analysis (agent's diagnosis, M11/M13/M15)
### Where .HierSearch is created
```skill
;; L258-260 in CXMTseCVPSHierSearch_all()
rootdir = ".HierSearch"
unless(isDir(rootdir)
  system(strcat("mkdir " rootdir))
)
```
- All 4 tabs call CXMTseCVPSHierSearch_all() → all create .HierSearch
- rootdir is a **relative path** ".HierSearch"
- Created in Virtuoso process's current working directory (cwd)

### Why .HierSearch not visible after search verilog
Agent's diagnosis (M15):
1. **目录被创建在了别的路径 (cwd 不同) ← 最常见**
   - `.HierSearch` is relative, based on Virtuoso process cwd
   - User may have started Virtuoso from a different directory than where they look
2. Virtuoso may have been started with `cd` to a system dir
3. mkdir may have failed silently (permissions)

### Fix approach
- Use absolute path: `rootdir = strcat(getWorkingDir() "/.HierSearch")`
  or `rootdir = strcat(getcwd() "/.HierSearch")`
- Or add a printf to report where directory was created
- Or make rootdir configurable via GUI field

## Case synthesis plan
- Case ID: EDA-Eval-DesignFlow-CVPSHierSearchFix-001
- Domain: schematic_netlist
- Task: write hiersearch_fixer.py that reads a .il script variant, fixes the rootdir relative-path bug, outputs fixed .il + report.md
- Visible A: original 708-line script (rootdir = ".HierSearch")
- Hidden B: variant with different relative path (e.g., ".hsearch_tmp") + different GUI defaults
- 12 check assertions (a-l): zip/compile/run/fix-logic/procedures-preserved/mkdir-preserved/case-structure/report-cwd/report-verilog/anti-hardcode/cross-input/determinism
