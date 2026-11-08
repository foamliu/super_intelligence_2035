# trace_deepread: 1794133519350_pchuf (harrywu @ hfeg0pkn002) — ClampPwrStateExtract-001

**扫描来源**：11-05 重扫令 11-08 cron 盲区直扫。`eda_trace_20261108.log` mtime Nov 8 00:00（cron 已停在此）。本轮通过 `find /home/*/.cline/data/sessions/ -newermt '2026-11-08 00:00:00'` 直扫 hfeg0pkn001/002/003/004/005 五台，发现 ~22 个 cron 盲区新会话。`ssh pkn002 cat pchuf.json | python3 rscan.py` spice 计分 → pchuf spice=1005 tools=275 uturns=21（hfhds201 本地 15 新会话 + pkn001/004/005 均为 wrong-shard 或低 spice）。

**会话概况**：582 msgs，2.1MB。用户 harrywu（DDR6 DSCQA 验证工程师）。
- **U#0（任务说明轮，A-faithful ✓）**逐字：
  > /proj/dscqa/V0/agentdir/harrywu/simulation/pwrup_issue/psf/理解该路径下的所有文件，并对Cell : DecEn_PwrUpLock进行功耗分析，需要在SecEn=1/0两种情况下的静态功耗分析，这里主要分析MP4和MN4造成的静态功耗，需要修改testbench，加入电流分析以及meas脚本，仿真自己提交，我只需要结果
  
  提出需求，无根因、无修复方向 → 符合 A-档选轮规则。
- U#105 corner=TT/1.025v/98c + 换正常 power 文件（补充约束，入 hint 不入 prompt）
- U#155 给出网表片段 + "XMMN4 网表中栅极写成 net5 疑似笔误"（指出根因 → 不入 prompt）
- U#177+ 转向 FSDB 波形/平台设计工作（wrong-phase，不入 prompt）

**金标准（assistant msg #104/#154/#176，用户接受）**：
- 电路结构：`SecEn --XI92(invGSx2)--> DecEnN(net3, ~SecEn) --XI61(invLVx8)--> DecEn(net5, SecEn)`；`PwrOn3 --XI8(invLx1)--> PwrOn3F`。
- 钳位管对：**XMMP4（PMOS, gate=PwrOn3, drain=DecEnN, source=vcc!）** + **XMMN4（NMOS, gate=PwrOn3F, drain=DecEn, source=vss!）**。
- 正常态（上电完成 PwrOn3=VCC, PwrOn3F=0）：PMOS Vgs≈0 → OFF；NMOS Vgs≈0 → OFF。两管只剩亚阈值/栅漏电 = 静态功耗来源。
- SecEn=1：net3≈0, net5≈VCC，两管跨满 Vds → I_MP4=40.04nA, I_MN4=65.81nA。
- SecEn=0：net3≈VCC, net5≈0，两管 Vds≈0 → I_MP4=0.156pA, I_MN4=0.181pA。
- 实测波形（finesim-fsdb-reader fscript）确认 pwron3=1.025V("1"), pwron3f≈0("0") 恒定 → 两管门端稳定关断偏置。

**可复用子流**：从 SPICE 网表识别电源钳位管对（PMOS+NMOS 互补门对，由 power-up inverter 产生互补信号），定位输入信号→钳位 PMOS 漏(=互补)→钳位 NMOS 漏(=同相) 的反相链，判定正常态两管 OFF 偏置（PMOS 门=VCC, NMOS 门=GND）。

**关键 trap**：
- decoy inverter XIbuf（输出 DecEnBuf 不接钳位管，不能误识为反相链一环）
- decoy MOS XMPD/XMND（门端可能重叠 power-up 信号但类型错或漏端不在反相链上 → 必须用「门对互补 + 漏端在反相链 + 类型对应」三重判据排除）
- 隐藏 B 重命名所有信号/subckt/实例/模型 + 重塑 w/l/nf + 翻转 decoy PMOS 门（PONB）测试区分能力

**case id**：EDA-Eval-DesignFlow-ClampPwrStateExtract-001（spice_sim, A-faithful, L1, k=15）
