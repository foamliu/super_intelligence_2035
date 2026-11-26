# r562 deep-read: ds6nz — duplicate origin+rotate / pin-bbox detector (layout_aether)

- **session**: `1794462982889_ds6nz` · user `haiquanp`@`hfeg0pkn003`(10.129.2.12) · mc=78
- **kw**: pyaether:232;dbget:124;aether:73;virtuoso:19;cellview:19;schematic:8;dbopencv:6;cadence:6
- **msgs**: 60 (4 real user turns) · 680KB → pulled via .75 ssh cat
- **trace_source**: real, single-user produce-task + iterative refine

## 意图演进（user 原话）

- **U#0 (produce-task author-new-script, A档合格)**: 「实现一个 layout pyaether 脚本，对当前选中的全部 object，检查其 origin 属性，如果发现两个或以上 origin 值重复的对象，将其加进 list 里。最后全部取消选中，只选中 list 里的 obj」
  - 提需求、未给根因/修复方案 → A档合格
- **U#38**: 贴出 `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe7` traceback（pyAether load() 按 ascii 读含中文脚本失败）
- **U#48 (refine, 3 点)**: ① per-duplicate 打印刷屏，只报 total ② 增加 rotate 判断，rotate 也一致才认定 duplicate ③ 推广到 pins 对象（无 origin，只有 bbox，bbox 完全重叠=duplicate，另设函数）
- **U#55**: 「中断了吗？继续」

## assistant 工具链

- search_apis×12 + get_api_details×4（查 aeGetCurDesign / aeGetSelectedSet / dbGetInstTransform / dbGetInstTransformF / getBBox / aeDeselectAll / aeSelectFig）
- editor×7（find_duplicate_origin.py 三版 + _syntax_check.py ×多）
- SandBox run_code×2（pyAether 沙箱未启动→ASCII 编码失败→改纯 ASCII）
- run_approved_command×3（python-runner ast.parse 语法校验）

## 最终算法（msg#53 find_duplicate_origin.py）

两函数：
1. `select_duplicate_origin()` — 处理普通对象（instance + rect/polygon/path/label shape）
   - get_origin(fig): instance → dbGetInstTransform (x,y) round 9；shape → getBBox left-bottom (x,y) round 9
   - get rotate: dbGetInstTransformF → ((x,y), orient)
   - **group by (origin, rotate)**；组内 ≥2 → duplicate
   - 只打印 total（不逐条）
   - aeDeselectAll() → aeSelectFig() 逐个重选
2. `select_duplicate_pin()` — 处理 pin 对象（无 origin，只有 bbox）
   - **group by identical bbox（完全重叠）**；组内 ≥2 → duplicate
   - 另设函数（与普通对象分离）
   - 只打印 total

## 核心 traps（判分要点）

1. **rotate trap**: 两 instance 同 origin 不同 orient → 非 duplicate（必须 origin AND rotate 都一致）
2. **shape origin = bbox lower-left**: shape 用 bbox 左下角当 origin（非 instance 的 placement origin）
3. **shape origin-only grouping**: 两 shape 同 lower-left 但不同尺寸 → 仍 duplicate（普通对象只比 origin+rotate，不比完整 bbox）
4. **pin full-bbox grouping**: 两 pin 同 lower-left 但不同尺寸 → 非 duplicate（pin 比完整 bbox，非 lower-left）—— 与 trap 3 形成对照
5. **pin/normal 分离**: pin 不能混入普通对象分组（pin 无 origin，必须另设函数按 bbox 处理）
6. **total-only console**: 不逐条打印 duplicate（U#48 点①）

## case 设计

- **case_id**: EDA-Eval-DesignFlow-DupOriginRotate-001
- **domain**: layout_aether · **track**: B（synthesized mock-behavioral，承 r539-r561 族）
- 把「live pyAether 选中对象 duplicate 检测」抽成纯 Python JSON layout deck fixture（mock pyAether API 依赖，核心 (origin,rotate) 分组 + pin bbox 分组 + total-only + deselect/reselect 算法不变）
- 可见 A: layout_deck_A.json（instance same-origin-diff-orient rotate trap + shape same-lower-left-diff-size + pin identical-bbox + pin same-lower-left-diff-size）+ input_spec.json + task_brief.md
- 隐藏 B/B2: 同格式同算法，deck 不同（更多对象、不同坐标、含全部 6 traps）
- 交付 find_dup_origin.py，读 deck → dup_result.json（design/obj_dup_groups/pin_dup_groups/totals/selected_ids），确定性 sort_keys
