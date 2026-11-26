# Deep-read: 1794203850332_onym6 (hktklin @ hfeg0plg87)

- trace: 444KB / 138 msgs / status=completed / exit_code=0 / match_count=87
- domain: layout_virtuoso (PCELL pcDefinePCell cyclic param refactor)
- user: hktklin, host hfeg0plg87 (10.129.8.138), agent=lead
- 3 user iterations:
  - U#0 (msg_mw8unbj9_1): "这是一个PCELL的脚本文件，生成一份能实现 ntap_svt,ntap_lvt,ntap_ulvt,ptap_svt,ptap_lvt,ptap_ulvt 这六个选项，只能选择其中一项的PCELL 的脚本文件" + attachment common_tap_L20_edge_lr_fin4_SKILL.il (6 boolean params, default ntap_svt=TRUE, 42 geometry markers, lib lacaa_common / cell common_tap_L20_edge_lr_fin4).
  - U#55: "保留 6 个 boolean 参数但互斥" — assistant added if/else mutual-exclusion guards, but user found still multi-selectable.
  - U#108: "还是能多选，需要单选" — assistant produced final cyclic solution: single `tap_type cyclic` param + internal `case tapType` mapping each option string back to exactly one boolean = t.
- gold reference: /home/hktklin/common_tap_L20_edge_lr_fin4_SKILL.il (10890B / 517 lines, cyclic form).
- selected as round r296 shard-C case: EDA-Eval-DesignFlow-PcellCyclicMerge-001 (A-faithful, L1, layout_virtuoso).
- deliverable abstraction: a general Python transform `boolean_to_cyclic.py <in.il> <out.il>` that rewrites any boolean-param pcDefinePCell into the cyclic+case form, preserving geometry verbatim. Hidden B1 = renamed 6-param (sw_a..sw_f), B2 = synthetic 3-param (mode_a/mode_b/mode_c) to defeat hardcoded/6-option solutions.
