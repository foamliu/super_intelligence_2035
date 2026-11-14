# 请教信草稿 · DREAM-GAN（ISPD 2023，无 arXiv）

- 收件人：Sung Kyu Lim（Georgia Tech ECE 教授；本文**末位作者**，一作 Yi-Chen Lu）
- 邮箱：`sl186@gatech.edu`（来源：Georgia Tech ECE **院系现行目录页** `https://www.ece.gatech.edu/faculty-staff-directory/sung-kyu-lim` 实测 `HTTP 200` / 57,585 B，页内明文；另课题组页 `limsk.ece.gatech.edu` 仍挂旧地址 `limsung@usc.edu` ⇒ **未采用旧地址**）
- 语言：英文
- 论文：DREAM-GAN: Advancing DREAMPlace towards Commercial-Quality using Generative Adversarial Learning（ISPD 2023，DOI `10.1145/3569052.3572993`，pp. 141–148；**无 arXiv**，`ti:"DREAM-GAN"` 检索 0 entry；OpenAlex 被引 **16**，查询日 2026-11-14）
- 主题：用对抗式「与商用工具布局的相似度」可微损失，把开源 DREAMPlace 的布局质量推向商用 flow
- 问题映射：
  1. 参考布局库很小时相似度损失是否仍成立、先在哪失效 → designflow（造题 / 参考解）
  2. 后布线收益（8.3% 线长 / 7.4% 总功耗）跨 PDK、跨设计的稳健性边界 → harness（指标口径）
  3. 把 DREAMPlace 当 agent 评测的固定基线时该冻结哪些参数 → designflow / zhulong（成本可比）
- 红线：单收件人、不群发、不催、不承诺合作/署名/资助、不透露未公开内部信息、不加第三方。
- 发送前置：正文 `wc -w` ≤200。

## 正文

Subject: DREAM-GAN in hindsight: three questions from a chip-design agent project

Dear Professor Lim,

I am Liu Yang, working on BaiZe-ISEDA2027 (a ~2B domain model for chip design) and ZhuLong-DAC2027 (an EDA agent harness). Your DREAM-GAN paper is the closest published work to a question we keep facing: how to move an open-source placer towards commercial quality when the commercial tool is a black box.

1. The similarity loss is learned from placements in a commercial database. With only a small reference set, does the adversarial signal still help, or does it collapse into copying a few reference layouts? What is the first symptom you would watch for?

2. The post-route gains of 8.3% wirelength and 7.4% total power are strong. How far do they survive across PDKs and design styles, and is there a cheap check that tells us early whether they will transfer?

3. We want to use DREAMPlace as a fixed evaluation baseline for agent-generated placements. Which parameters must be frozen so that two runs are comparable, and which can vary without invalidating the comparison?

Thank you for considering these questions.

Best regards,
Liu Yang
Super Intelligence 2035 / BaiZe-ISEDA2027 / ZhuLong-DAC2027
