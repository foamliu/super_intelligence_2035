# trace_deepread: 1792552971568_dnkz8 (johnl @ hfeg0plg99) — T_IsmTop StarRCXT RCC 体偏置修复

- **trace**: session 1792552971568_dnkz8, user johnl, host hfeg0plg99, mc=99, 148 msgs (77 user / 71 assistant), 679KB messages.json, model deepseek-v4-flash, 状态 failed (stale_session_reconciler, exit 1). 时间 2026-10-21 03:22~05:22 UTC.
- **domain**: pnr_signoff (StarRCXT/Calibre LVS RCC 抽取). shard A.
- **用户原话 (msg #0)**: "/proj/drcoa/V0/ver/pex/johnl/T_IsmTop 这个文件夹抽IsmRCC失败了 说是I37底层没map vbn 到vss vbp 到vcc 要改cdl你改下记得 对所有目录下到文件的修改都要比较修改前后确保合适修改没问题 修改并完成RCC抽取 你别想太多 就这一个cell连线可能需要修改一下 最后完成RCC"
  - 注意：此轮用户已给出根因+修复方案 → 不符 A 档规则②（提出需求轮），归 **B 档 synthesized**。
- **工具链**: Calibre LVS (calibre 2020.1_36 aoi_cal) + StarRCXT/StarXtract (starrc 2020.09-SP5-4)，LSF bsub (queue star)，runlpe wrapper，emy2netlist 2025.09.sp1.hf6 生成 CDL。lpe.config mode=RCC。
- **根因定位 (assistant 深读)**:
  - CDL `T_IsmTop.cdl` (177153B, 3575 行, emy2netlist 输出)。顶层 `.SUBCKT T_IsmTop ... vbn! vbp! vcc! vdbias! vss!` (line 3058) — vbn!/vbp! 是体偏置 body-bias 端口。
  - buf 族子电路签名 `A Y vbn! vbp! vcc! vss!`：bufLx4 (line 543)、bufLx16 (line 2444)。
  - 实例 XI37 (line 3249): `XI37 JudgeN<8> JudgeN_buff vbn! vbp! vcc! vss! / bufLx4` ← 错（bulk 端接在 vbn!/vbp! 上，没映射到 vss!/vcc!）。
  - 其余 buf 实例已正确接 vss!/vcc! (如 XI378 `... vss! vcc! vcc! vss! / bufLx4`)。
  - 备份 `T_IsmTop.cdl.bak_vbnfix` 的 vbn 计数 681 / vbp 515，当前 .cdl 680 / 514（各多 1）→ 印证修复=把 XI37 的 vbn!→vss!、vbp!→vcc!（仅一行）。CDL 修复其实已被前次尝试应用。
  - RCC 产物 `T_IsmTop.spf.TYP_98_RCC` mtime 8/25（早于 CDL 修复 10/21）→ 需用修好的 CDL 重抽。
- **assistant 后续 (重抽 RCC)**: 写 run_pipeline.sh / launch_rcc.sh / bsub_job.sh，遇环境问题连环排查：
  ① calibre 报 "VCO=aok. Software tree is for VCO=aoi"（本机 VCO 检测与 aoi_cal 树不匹配）；
  ② nohup 直跑 Permission denied → 改 `nohup bash`；
  ③ StarXtract 本机跑 8 worker FAILED（缺 CCI_DB，因 calibre -query 失败）；
  ④ 转 bsub 提交计算节点，第一 job 秒退（LD_LIBRARY_PATH 泄漏 eda-agent lib，GLIBC_2.18 not found on compute node）；
  ⑤ sanitized env 重提 job 264223 DONE，但 StarXtract 缺 libtbb.so.2 → 在 bsub_job.sh 显式 `export LD_LIBRARY_PATH=/apps/synopsys/SRB/starrc.../lib/shlib`；
  ⑥ 提 job 264930，poll3 时被 SIGKILL（stale_session_reconciler 终结）。**session 最终 failed，RCC 未确认完成**。
- **可验证的核心 (本 case 取材点)**: CDL 体偏置修复是确定性、可独立判分的子任务 —— 交付 `fix_cdl.py`（通用 bufLx* bulk 端 vbn!→vss!/vbp!→vcc! 重映射器）+ 修复后的 A CDL + unified diff。RCC 实跑（L3）依赖计算节点环境/许可，过于脆弱，不纳入判分；脚本可由 fix_cdl.py 衍生。
- **金标准**: trace 中已应用的修复（XI37 vbn!/vbp!→vss!/vcc!，单行，备份计数印证）。断言只对事实（实例 bulk 端取值、单行改动、.SUBCKT 定义不动、计数差=1、幂等、跨输入守卫），不对措辞。
- **合成资产**: A=T_IsmTop.cdl（按真实结构裁剪，含 XI37 错接 + 其余正确实例 + bufLx4/bufLx16 定义）；隐藏 B=T_DacTop.cdl（顶层 T_DacTop，错接实例 XI52 of bufLx16，网名 DacCtrl<3>/DacCtrl_b，工艺 cxmt10G4_LP TYP_125 0.90V）——跨输入守卫击破硬编 XI37/bufLx4/JudgeN<8>。
- **判分**: check.py 14 条 a-n 独立断言，subprocess 在 B 上重跑候选 fix_cdl.py。ref PASS 14/14，3 negatives + §4.9 三假（空壳/只print/删核心）全 FAIL。🧾 k_rationale=k_check=14 ≥8 ✓。
- **case_id**: EDA-Eval-DesignFlow-CdlVbnBulkRemap-001 (A.jsonl 第 49 行). L2. track synthesized.
