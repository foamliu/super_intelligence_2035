交付接口：submit.zip 内 scripts/flow_extractor.py + README.md。
flow_extractor.py 用法：python3 scripts/flow_extractor.py <session_dump.json> <workdir_listing.txt>，stdout 输出一个 JSON manifest（字段：design/workdir/process/num_cells/num_nets/innovus_version/starrc_version/tools_launched/key_scripts/key_result_files/timing_wns/timing_tns/spef_coverage_pct/num_violations/crit_path_levels/crit_path_endpoint）。
check 在隐藏 B 的 session_dump + workdir_listing 上跑你的 flow_extractor.py 校验 B 的事实。
