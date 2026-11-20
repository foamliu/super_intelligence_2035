# 经典论文请教信 · DREAMPlace（DAC 2019，无 arXiv）

- 收件人：**David Z. Pan**（The University of Texas at Austin, ECE；DREAMPlace 通讯/末位作者）
- 邮箱：**dpan@ece.utexas.edu**（来源：本人现行主页 `https://users.ece.utexas.edu/~dpan/` 实测 `HTTP 200` / 55,267 B，页内明文 `dpan at ece.utexas.edu` ⇒ 按页面规则还原；**未用论文 PDF 里的旧地址**）
- 发送时间：2026-11-14 06:1x CST（第 35 封）
- 语言：英文（作者非中文姓名、机构为美国 UT Austin）
- 正文：`research/mail/2026-11-14-classic-dreamplace-dac19.txt`
- 词数：发送前 `wc -w` 实测（见发送记录）

## 主题

Question on DREAMPlace's >30x speedup and its use inside agent loops

## 正文（四段式 · 与 BaiZe / ZhuLong 的对应）

1. 自我介绍（《超级智能2035》+ BaiZe-ISEDA2027 / ZhuLong-DAC2027，署名 Liu Yang / Foam）
2. 为什么读：把解析式布局改写成 PyTorch 上的可微程序 = 我们要的「可验证环境」；>30×（vs RePlAce，全局布局、质量不降）是我们引用最多的数字
3. 三个具体问题（均能回填研发决策）：
   - Q1（designflow · L4 工具链保真度）：macro 密集设计上，>30× 里线长/密度 kernel 与优化器各占多少？缩预算时该保留哪个旋钮？
   - Q2（zhulong · rollout 成本）：布局被放进「多次 rollout 的 agent 循环」时，哪个廉价设置（迭代数 / 目标密度 / 提前停）最保序？我们打算预注册一个保真度判据。
   - Q3（designflow · 判分可验证性）：可微松弛在 legalization / detailed placement 哪里失效，质量差距多大？
4. 致谢 + 签名

## 红线自查

- 🚫 未承诺合作 / 署名 / 资助；🚫 未透露未公开内部信息；🚫 未夸大；🚫 未加第三方收件人
- 同作者 ≤1 封（David Z. Pan 首次）；同论文 ≤1 封；UT Austin 当日第 1 封
