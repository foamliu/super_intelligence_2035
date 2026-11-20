# =============================================================================
# common_setup.tcl : cfreq_ctrl 综合流程公共设置
# 被 scripts/dc_setup.tcl source, 用于库与通用变量设置
# =============================================================================

# ---- 补充 search path (可外部通过 ADDITIONAL_SEARCH_PATH 覆写) ----
set ADDITIONAL_SEARCH_PATH   ""

# ---- 目标/链接库文件 (按实际工艺配置) ----
set TARGET_LIBRARY_FILES     ""   ;# 例如 "slow.db" 或 "typical.db"
set LINK_LIBRARY_FILES       "*"  ;# 默认链接为当前 target library
set SYMBOL_LIBRARY_FILES     ""   ;# 例如 "generic.sdb"

# ---- Milkyway 参考库 / 设计库 (物理综合时使用) ----
set MW_REFERENCE_LIB_DIRS    ""
set MW_DESIGN_LIB            "mw_lib"

# ---- 通用综合变量 ----
set SAVE_DESIGN              ""   ;# 可写入保存逻辑
set COMPILE_FLOW             "ultra"