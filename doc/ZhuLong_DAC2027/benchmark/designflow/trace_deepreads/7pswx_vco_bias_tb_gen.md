# Deepread: 1794883500039_7pswx (wnyu@hfeg0plg002 · spice_sim)

**Session**: 1794883500039_7pswx.messages.json (1.9MB, 633 msgs)
**User**: wnyu @ hfeg0plg002 (10.129.2.11)
**Model**: deepseek-v4-flash
**mc**: 353 | **domain**: spice_sim | **shard**: B

## Real Task

为 VCO_BIAS 模块（环形 VCO 的两级串联片上 LDO：PMOS LDO→VDDAI，NMOS LDO→VRING，隔离 VRING 与系统 VDD）搭建可在 finesim 下跑 0.94V 的 testbench，并完成 1.8V→0.94V 迁移分析。

## Key Artifacts (agent produced)

1. **build_vcobias_tb.py** (268行, 8599B): 主 TB 生成脚本
   - 从 flat schematic netlist 提取 XNM/XPM 器件行
   - 包装成 `.subckt VCO_BIAS`（11 端口）
   - 生成 3 个 TB deck + 3 个 PVT corner + run.sh
2. **VCO_BIAS_subckt.sp**: 17 器件（XNM0-9, XPM0-9），全 nlvt_ckpt/plvt_ckpt
3. **TB_0p94_dc.sp**: .op + .dc VCTRL sweep → VRING/VDDAI transfer
4. **TB_0p94_load.sp**: .dc IRING sweep → VRING dropout
5. **TB_0p94_psrr_tran.sp**: .ac PSRR + .tran load-step
6. **pvt_0p94_tt/ss/ff.sp**: .lib top_tt/ss/ff + pre_simu, VVDD=0.94
7. **run.sh**: finesim runner, 3 corners × 3 TBs

## Iterative Design Changes (later in trace)

用户多轮迭代换管子类型尝试抬压 VRING 到 0.6-0.8V:
- orig (nlvt_ckpt) → nb → nulvt (XNM7/XNM9 换 nulvt_ckpt) → native (nna08_ckpt, Vth=0)
- 减 Vth 0.2V, 调 multi
- 每轮生成变体 TB deck: VCO_BIAS_nulvt.sp, VCO_BIAS_native.sp, etc.

## Case Design

- **case_id**: EDA-Eval-DesignFlow-VcoBiasTbGen-001
- **domain**: spice_sim | **layer**: L1 | **track**: faithful | **tier**: B
- **deliverable**: build_vcobias_tb.py (parameterized, --netlist/--outdir)
- **A (visible)**: vco_bias_netlist.txt (17 nlvt/plvt 器件行, spmt=10e-6, net47)
- **B (hidden)**: 变体网表 (XNM7/XNM9=nulvt_ckpt, spmt=1e-6, net47→netmir, 4 个 multi 不同)
- **check**: 12 断言组, 36 个 _assert 调用, 真跑脚本在 B 上校验生成结构
  - 关键牙: B 器件特征 (nulvt_ckpt/netmir/spmt=1e-6/multi=384) 必须出现在 subckt, A 特征 (multi=512/spmt=10e-6) 不得出现 → 防 hardcoded-A
- **§4.9**: 5 neg (empty/printf/hardcoded_A/core_deleted/nosim) 全 FAIL, ref PASS
