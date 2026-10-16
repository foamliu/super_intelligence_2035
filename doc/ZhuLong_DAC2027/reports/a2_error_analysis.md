# A2: Error Analysis — full_v3 r3 (batch 2026_1012_071034, 129/158 pass, 29 fail)

## Execution-stage failures (12) — L1-L4 classification

| Level | Count | Tasks | Description |
|-------|-------|-------|-------------|
| L1 (syntax/API name) | 0 | — | All exec-fail code ran without syntax errors |
| L2 (parameter/signature) | 0 | — | No pure parameter-type errors (074 reclassified as L4) |
| L3 (semantic/logic) | 4 | 017, 052, 058, 144 | Valid APIs, wrong composition logic |
| L4 (situated/design-state) | 8 | 010, 063, 068, 074, 109, 142, 146, 155 | Hidden type contracts, internal state, runtime context |

### L4 details:
- **010** (add_instance_to_schematic): `target_cv must be an opened cellview object` — cellview handle valid in agent context but not "opened" per test oracle
- **063** (get_cell_file_type): function returns "maskLayout" but test expects "cellFileType" — internal type representation
- **068** (create_cartoon_box): `failed to create the cartoon box instance` — hidden preconditions
- **074** (create_qstring_list): `NameError: create_wrapped_qstring_list` — C++ binding expects QStringList, doc doesn't show how to construct from Python
- **109** (create_cdf): `Failed to create CDF` — hidden preconditions on internal state
- **142** (create_inverter_layout): `Expected 2 instances, found 0` + `MOS instance: None` — internal state dependency
- **146** (classify_device_types): `Param has no attribute 'value'` — internal type doesn't expose attribute in test path
- **155** (get_command_point): `Function returned False, expected emyPointF` — return type depends on GUI context (headless vs GUI)

### L3 details:
- **017** (count_cell_instances): counting logic returns 0 instead of 2
- **052** (check_view_list): custom validator instead of mandated EmyNtlUtil.checkViewList
- **058** (batch_oge_job_policies): substring matching instead of equality check
- **144** (tag_dummy_shapes): property set to None where concrete value expected

## Generation-stage failures (17) — breakdown

| Cause | Count | Tasks | Note |
|-------|-------|-------|------|
| Timeout (>2500s) | 4 | 105, 123, 124, 129 | 24-41 APIs, ongoing reasoning at termination |
| Wrong save path | 10 | 104, 106, 112, 118, 119, 128, 131, 145, 152, 158 | Code saved to ws/ not ws/pyAether_code/ |
| No code produced | 3 | 013, 072, 120 | Session cancelled or ended without code file |

### Session status:
- 013: cancelled (33 msgs), 072: cancelled (16 msgs), 120: completed (153 msgs but no code)
- 105: completed (235 msgs, timeout), 124: completed (511 msgs, timeout), 123: completed (371 msgs, timeout), 129: completed (316 msgs, timeout)
- All wrong-save-path tasks: completed, code exists but in wrong location

## Key finding
L4 (situated truthfulness) = 67% of exec-fail, L3 = 33%, L1/L2 = 0%. Directly supports §4 grounding-gap framework: correctness is an L4 property, execution is the only observation channel.
