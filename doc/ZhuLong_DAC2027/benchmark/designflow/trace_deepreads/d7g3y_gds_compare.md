# d7g3y deepread: GDS cell structure comparison

- **session**: 1795424420539_d7g3y (michael1l@hfeg0plg87, mc=126, 134 msgs/738KB)
- **domain**: schematic_netlist (GDS cell structure)
- **user intent**: "看一下这两个gds的区别" — compare DBC-modified GDS vs GOLDEN GDS for HD1P_LEAFCELL_GIO_M1B1CR1_CRC leaf cell
- **agent flow**: search pyAether GDS APIs → pyAether sandbox unavailable → fallback to gdspy → write gds_compare.py iteratively → script lists cells (72), shapes, refs, compares differences
- **keywords**: pyaether:538;dbget:210;cellview:172;.gds:112;netlist:50;dbopencv:50;schematic:47
- **deliverable**: Python CLI script using gdspy to compare two GDS files → structured JSON output (cell list, per-cell shape/layer/ref counts, diff report)
- **case**: EDA-Eval-DesignFlow-GdsCellStructCompareProduce-001 (k_check=12, 3 neg all FAIL, ref PASS)
- **scan source**: ssh_eda_search_20261124_023802 (new in 1124, not in 1123 scan)
