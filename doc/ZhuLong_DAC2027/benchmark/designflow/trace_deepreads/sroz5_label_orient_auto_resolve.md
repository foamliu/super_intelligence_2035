# Deepread — trace 1788488738438_sroz5 (junxu@hfeg0plg79, mc1101, layout_virtuoso)

## 真实任务

junxu 维护 `virtuoso-cli` skill（Python 封装 Virtuoso SKILL，TCP bridge 驱动
Virtuoso 画原理图）。`scripts/virtuoso_cli/api/schematic.py` 的
`add_pin`/`wire_pin`/`add_wire`/`name_net`/`connect_by_name` 方法给 net 打
label，但放置逻辑有 bug：

1. **水平方向**：所有 label 硬编码 `lowerLeft`，文字总向右延伸。pin 在器件
   左侧时 label 文字延伸进 body → 重叠。
2. **纵向方向**：纵向 net 用横向 `R0` label，视觉不协调；旋转 `R90` 后锚点
   还在 pin 处，旋转后 label 宽度横跨 body x 范围 → 仍重叠。

## 用户迭代过程

- @0：上一位 agent 的 HANDOFF，要求优化 label api（打 label 总在右侧，pin
  在左侧时不友好）。
- @200/@280：纵向 net 的 label 应纵向放置；纵向 label 与器件重叠。
- @384/@500/@523：用 mx4x1（4:1 MUX）器件验证（引脚在四侧）；纵向线 label
  应纵向放在线旁，参考手动放好的 SEL0/SEL1。
- @608：assistant 验证 ALL OK — 所有纵向 label 用 R90 放在线中点，文字向
  stub 末端方向延伸（远离器件）。
- @613/@615：user 要求总结最近 api 优化改动（trace-end-gold 满足）。

## 正确放置规则（从 schematic.py `_DIR_LABEL` + auto-orient/justify 提取）

```
_DIR_LABEL = {
    "right": ("R0", "lowerLeft"),    # 水平文字，向右延伸
    "left":  ("R0", "lowerRight"),   # 水平文字，向左延伸（远离 body）
    "up":    ("R90", "lowerLeft"),   # 纵向文字，向上延伸
    "down":  ("R90", "lowerRight"),  # 纵向文字，向下延伸
}
```

- 水平 net：锚点 = pin tip (src)，R0，justify 背离 body。
- 纵向 net：锚点 = 线中点（不是 pin），R90 旋转后文字宽度=label 高度，紧贴
  线旁；justify 向 stub 末端延伸。
- 锚点不在 body_box 内部（防重叠）。

## reframe (档 B produce-tool)

抽象为 `label_place.py` CLI：读 net manifest JSON（direction/src/tgt/body_box），
按规则输出 (orient, justify, anchor) JSON。纯 Python，无 EDA 工具运行时 →
judge_layers=[L0,L1]。

## 自造 A/B

- A（可见）：DATA0/MUX_OUT/SEL2/SEL0，几何 src=[10,5]/[0,5]/[5,0]/[5,20]。
- B（hidden）：DIN/DOUT/CLK/RST，几何完全不同 src=[50,25]/[0,30]/[25,0]/[25,100]，
  防硬编码（A!=B cross-input guard）。

## check.py 16 条断言

a ast.parse / b CLI 退出0输出非空 / c labels 结构 / d-f DIN right(R0/lowerLeft/src) /
g DOUT left(lowerRight) / h-j CLK up(R90/lowerLeft/中点) / k-l RST down(lowerRight/中点) /
m CLK anchor 不在 body 内 / n 3 跑 md5 一致 / o A!=B 防硬编码 / p 非法方向抛 ValueError。

## 自验

ref self-test PASS(16/16) + neg_selftest 4-neg ALL-FAIL distinct(b/o/c/f) +
§4.9 trio {empty→b, print→o, copy→c}=3-distinct + harness SKIP_RUN workdir 建 OK +
leak CLEAN。judge_layers=[L0,L1]（mock 纯 Python）。
