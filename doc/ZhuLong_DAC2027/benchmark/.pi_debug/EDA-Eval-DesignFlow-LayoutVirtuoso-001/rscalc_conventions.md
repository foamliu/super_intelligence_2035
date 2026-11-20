# RTEXT / RNODE / rscalc 约定 (layout_virtuoso 域)

## 背景
针对 DRAM 配置 `cxmt10G4plus` + 金属堆叠 `1p5m1x3y1z`，电源网络电阻用 `rscalc`
工具计算。`rscalc` 从每个 **RNODE**（检查点）测量到对应 **RTEXT**（电源 pad / 源点）
的电阻，需要电源网络上 RTEXT 与 RNODE 都"打齐"才能跑。

## label 三类 purpose
| purpose | 含义 | label 文字 | 例子 |
|---------|------|-----------|------|
| `RTEXT` | 电源 pad / 源点（rscalc 的电阻起点） | 网络名，**不带 `!`** | `vcc` / `vss` / `viso` |
| `RNODE` | 检查点（rscalc 的电阻终点） | 网络名，**不带 `!`** | `vcc` / `vss` / `viso` |
| `drawing` | GDS 网络名标签 | 网络名，**带 `!`** | `vblh!` |

`drawing` purpose 的 label 是 GDS stream-out 用的网络名标签，**不是** RTEXT/RNODE，
审计工具**必须忽略**（按 `purpose != RTEXT && purpose != RNODE` 排除）。

## 支持打 RTEXT/RNODE 的图层
`MT2, M0U, M1, M2, M3, M4, M5, RDL`（NetLayers/PointLayers）。
本 case 的 Array16G_B rail 处只有 RDL 层有可打金属，故全部 RTEXT/RNODE 在 RDL 上。

## "打齐" 判定（aligned）
每个真实电源网络在每个所用图层上：
- `RTEXT 数 > 0` **且** `RNODE 数 > 0`（缺一不可）
- 没有"垃圾"网络（RTEXT>0 但 RNODE==0，即只打了源点没打检查点，多为调试残留坐标）
- 没有重复 label（同 layer + purpose + net + xy 出现多次）

满足以上 = `ALIGNED`，可跑 rscalc；否则 = `MISALIGNED`，需清理后再跑。

## 参考打 label 方式（gen_test_layout.py flow_6）
```skill
; RTEXT: 放在 rail 起点和中间（电源 pad 位置）
dbCreateLabel(cv list("M1" "RTEXT") list(x y) "vdd" "centerLeft" "R90" "roman" 1.0)
; RNODE: 放在 rail 沿线检查点
dbCreateLabel(cv list("M1" "RNODE") list(x y) "vdd" "centerLeft" "R90" "roman" 0.8)
; TEXT (drawing): 带 ! 的 GDS 网络名
dbCreateLabel(cv list("M1" "drawing") list(x y) "vdd!" ...)
```

## 真实流程（cgqd1 session, e0014566 / hfeg0pkn001）
1. `dbOpenCellViewByType("auto_austin_case1" "Array16G_B" "layout" "maskLayout" "r")`
2. 遍历 `cv~>shapes`，对 `objType=="label"` 取 `lpp` / `theLabel` / `xy`
3. 按 purpose 分 RTEXT / RNODE / drawing，按 net 分组审计
4. 清理：`dbDeleteObject` 删垃圾 + 重复 label，`dbSave`
5. 验证：重新扫描，3 真实网 vcc/vss/viso 全部 ALIGNED

本 case 把上述审计 + 清理逻辑抽象为离线 Python 工具（不依赖 virtuoso，纯标准库）。
