# 任务说明 · RTEXT/RNODE 标签审计 + 清理工具 (layout_virtuoso 域)

## 背景
你是 EDA 版图工程师 e0014566 在 hfeg0pkn001 上为 DRAM 版图 `Array16G_B` 做电源网络
电阻计算前的 RTEXT/RNODE 标签核验。真实流程用 virtuoso SKILL 扫版图 label，但你想
把审计逻辑固化成一个可复用的离线工具：输入 label inventory 文本 dump，工具审计
rscalc 所需的 RTEXT/RNODE 完整性，识别"垃圾网络"和"重复 label"，产出清理报告 +
建议删除清单，让别处可复用（cgqd1 session 末用户明确要求"总结出一个打 RTEXT RNODE
的切实有效的方法，让别的地方可以复用"）。

参考约定见 `rscalc_conventions.md`（RTEXT=电源源点 / RNODE=检查点 / 打齐判定 /
支持图层 / label 文字不带 `!` / rscalc 算 RNODE→RTEXT 电阻 / drawing purpose 须忽略）。

## 输入（随会话注入到 workdir）
- `label_inventory_unclean.txt` — 清理**前**的 label dump（含 3 类问题：垃圾网络
  `test2`/`edit_test`（RTEXT>0 但 RNODE==0，调试残留坐标）+ 重复 label（同 layer+
  purpose+net+xy 出现多次）+ drawing-purpose GDS 网络名标签（须忽略，不计入审计））。
- `label_inventory_clean.txt` — 清理**后**的 label dump（仅 vcc/vss/viso 三真实电源
  网，已去重去垃圾，全部 ALIGNED）。
- `rscalc_conventions.md` — RTEXT/RNODE/rscalc 约定（背景知识）。

### inventory 文件格式
每行一条 label：
```
(LAYER "PURPOSE")  "NET"  xy=(X Y)
```
- `LAYER`：金属层名（如 `RDL`）
- `PURPOSE`：`RTEXT` / `RNODE` / `drawing`
- `NET`：网络名（RTEXT/RNODE 不带 `!`，drawing 带 `!`）
- `X Y`：坐标（浮点）
- `#` 开头为注释，空行忽略

## 你要交付（打包成 `outputs/submit.zip`，内含 4 个文件）
1. **`rtext_rnode_audit.py`** — 审计 + 清理工具（纯标准库，可 `python3 rtext_rnode_audit.py ...` 直接跑）。CLI：
   ```
   python3 rtext_rnode_audit.py --inventory <file>
   ```
   退出码：审计完成（无论 ALIGNED/MISALIGNED）一律返回 0；参数/解析错误返回非 0。
2. **`sample_output_unclean.txt`** — 用 `rtext_rnode_audit.py` 跑 `--inventory label_inventory_unclean.txt` 的真实 stdout。
3. **`sample_output_clean.txt`** — 用 `rtext_rnode_audit.py` 跑 `--inventory label_inventory_clean.txt` 的真实 stdout。
4. **`cleanup_report.txt`** — 人读清理报告：列出 per-net 审计（net / RTEXT 数 / RNODE 数 / 所用图层 / verdict）+ 垃圾网络清单 + 重复 label 清单（带 layer/purpose/net/xy）+ 建议删除清单（垃圾 + 重复，带 xy）+ 清理前后对比。

## 输出格式要求（stdout，判分依据）
- 必须出现整体判决关键字 `ALIGNED` 或 `MISALIGNED`。
- 必须给出 per-net 块，每个真实电源网一行，格式形如：
  ```
  net=vcc  RTEXT=2  RNODE=11  layers=RDL  verdict=ALIGNED
  net=test2 RTEXT=2  RNODE=0  layers=RDL  verdict=GARBAGE
  ```
- 必须报告垃圾网络（RTEXT>0 且 RNODE==0）的 net 名（如 `test2`, `edit_test`）。
- 必须报告重复 label 计数（`duplicate_labels: N`）。
- drawing-purpose label **不计入** RTEXT/RNODE 计数，也不计入重复/垃圾（按 purpose 过滤）。

## 约束
- 纯 Python 标准库（`argparse`/`re`/`sys`/`os`/`collections` 等），不引第三方包，
  不调任何 EDA 工具，全本地可跑。
- 必须真正按 `(layer, purpose, net, x, y)` 元组去重（坐标相同才算重复）。
- 必须按 net 分组判定 verdict（不能只数总 RTEXT/RNODE 个数了事；naive 计数器会把
  垃圾网络 `test2`/`edit_test` 的 RTEXT 也算进去，且不查 RNODE==0 → 误报 ALIGNED）。
- drawing-purpose 须按 purpose 过滤排除，不能因为 `vblh!` 带了 `!` 就当成"另一种
  net"参与审计。
- cleanup_report.txt 必须枚举每个 net 的 RTEXT/RNODE 数 + verdict，以及建议删除清单
  的每条 label（带 layer/purpose/net/xy），证明工具真的做了 per-net 审计而非全量计数。
