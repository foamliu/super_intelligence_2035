# BaiZe 论文源文件结构（2026-10-31 重写后）

> 本目录只放**被 `main.tex` include 的章节**。历史版本已移入 `deprecated/`，不再参与编译。

## 1. 章节与文件一一对应

| 节 | 文件 | 内容 | 状态 |
|:--|:--|:--|:--|
| Abstract | `0_abstract.tex` | ZhuLong 锚点 + 两个目标 + 主张 A/B/C + 状态说明 | 已重写 |
| §1 | `1_intro.tex` | 两个痛点、三条可证伪主张、4 条贡献、定位句 | 已重写 |
| §2 | `2_related_work.tex` | 四条相关工作线 + **§2.5 与 ZhuLong 的关系** | 已增强 |
| §3 | `3_architecture.tex` | 五阶段、O(1) 会话状态公式、**T3 协议 / T4 token 档 / T5 harness 清单** | 已重写 |
| §4 | `4_llm_pretrain.tex` | 语言预训练（**已完成**，2.94T/700k/iter 30,660/loss 2.151） | 事实已核校 |
| §5 | `5_llm_posttrain.tex` | 后训练 + **RQ1–RQ4 / T6–T10** + 领域适配（原 §8 并入） | 已重写 |
| §6 | `6_vision_encoder.tex` | 多模态：编码器（**已完成**）+ 对齐 + **RQ5–RQ7 / T11–T14** + 波形 | 已重写 |
| §7 | `7_serving_economics.tex` | **服务经济账（新增）**：成本公式 + **T15** + 成本-精度平面 | 全新 |
| §8 | `8_error_analysis.tex` | **错误分析（新增）**：**T16**，四类失败模式与 ZhuLong 并表 | 全新 |
| §9 | `9_discussion.tex` | **讨论与局限（新增）**：什么会证明本文错了 + 四条局限 | 全新 |
| §10 | `10_conclusion.tex` | 结论 + 主张 A/B/C 的检验状态 | 已重写 |
| 附录 A | `A1_experiment_plan.tex` | 实验规划/预算 + claim→RQ→表索引 + 六页裁切方案 | 全新 |

## 2. 为什么会有「重复编号」的历史文件

原稿是 **9 个文件**（0–9）。按用户提供的《BaiZe 论文改写任务说明 v1.2》重构为 **10 节 + 附录**，
原 `7_mllm` / `8_domain_rl` / `9_conclusion` 三章的内容被拆分并入新章节，文件名编号随即与新节号错位：

| 旧文件 | 去向 |
|:--|:--|
| `7_mllm.tex`（原 §7 多模态对齐） | 内容并入 **§6.2 对齐协议**（`6_vision_encoder.tex`） |
| `8_domain_rl.tex`（原 §8 半导体领域适配） | 内容并入 **§5.7**（`5_llm_posttrain.tex`） |
| `9_conclusion.tex`（原 §9 结论） | 被 **§10**（`10_conclusion.tex`）取代 |

三者已 `git mv` 到 `deprecated/`，**不参与编译**，仅留作历史对照。

## 3. 编译

```bash
cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

当前实测：**11 页 / ERR=0 / UNDEF=0 / Overfull=0**。

## 4. 编码约定（重要）

所有 `.tex` 必须是 **UTF-8 with BOM**，否则中文 Windows 编辑器会按 GBK 解码，`% 中文：` 双语注释显示为乱码。
提交前自检：

```bash
python scripts/check_tex_encoding.py        # 0 problem(s) 才算过
python scripts/check_tex_encoding.py --fix  # 自动补 BOM / 末尾换行
```
