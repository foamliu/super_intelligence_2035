# trace deepread — 1795001214198_w8iq4 (joeyl @ hfeg0pkn002 = 10.129.2.11)

- mc=246, 159 msgs (94 user / 65 assistant), agent=lead, 574924B
- domain: spice_sim (DDR4 V0 FineSim 仿真, ulvt 管 Vth 降阈)
- scanned via eda_flow open_session → ssh 10.129.2.11 → scp messages.json

## 用户真实意图（按时间线）
1. **msg 0**: 给 `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/simulation/Bias/hspiceD/schematic/netlist/netlist` 加 `vth=-0.2v`，用 `/home/joeyl/ulvt_delvto/` 工具
2. **msg 21**: "我更新了netlist，请再替换一次，原本数据直接替换即可，无需备份"
3. **msg 30**: "这次vth只-0.1,原本数据直接替换即可，无需备份"
4. **msg 42**: 把 `CML_C2C` netlist 也替换，vth-0.2
5. **msg 56**: "我又抽了一次这个netlist，请照原样替换"
6. **msg 64**: `Solo_Divider` netlist，"只需要给出替换后的path即可，vth依然-0.2"
7. **msg 77**: "这次请帮忙替换WCKTop_netlist"
8. **msg 89** 🔴 **关键纠正**: "发现个非常关键的问题，对pmos，Vth应该+0.2!麻烦重新替换" — PMOS Vth 本身负值，降 |Vth| 要 +delvto；NMOS 才 -delvto。agent 在 msg 92 连续 6 次 editor 改 `reduce_vth.py` + 2 次 `config.cfg` 加 `delvto_by_model = pulvt_ckt:+0.2, nulvt_ckt:-0.2`，并新建 `verify_model_delvto.py`
9. **msg 112**: "麻烦把solo divider的vth的数值改到0.05"
10. **msg 124/132**: 重抽 Solo_Divider netlist 再替换
11. **msg 140**: `Divider_and_C2C` netlist，vth0.05
12. **msg 151**: "请再替换一次"

## agent 工具链
- `list_allowed_files` / `read_files` 读 `AI_USAGE.md` + `config.cfg` + `reduce_vth.py` + netlist
- `editor` 写 `copy_netlist.py`（拷源 netlist 到 work）+ `verify_netlist.py`/`verify_model_delvto.py`（验证）+ 改 `config.cfg`/`reduce_vth.py`
- `run_approved_command` (profile=python-runner) 跑 `copy_netlist.py` → `reduce_vth.py` → `verify_model_delvto.py`
- 多模块迭代：Bias → CML_C2C → Solo_Divider → WCKTop → Divider_and_C2C

## reduce_vth.py 核心逻辑（trace-verbatim, 11868B, scp 取回）
- `DELVTO_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])(_delvto\s*=\s*)[^\s$]+")` — token 精确（`(?<![A-Za-z0-9_])` 防 `xxx_delvto` 误匹配）
- `find_unquoted_comment`: 找行内 `$` / `//`（跳过引号内）
- `append_token`: _delvto 追加到物理行末，有注释插注释前
- `statement_model`: 扫语句各物理行 code 部分找模型 token
- `apply_delvto`: 已有 _delvto= → 替换值（情况1）；否则追加到末行（情况2）= 幂等
- `process_netlist`: 按 `+` 续行分组语句，`require_x_prefix` 只处理 X 行，跳过 `*`/`//` 注释行，按 `delvto_by_model` 查模型对应正负号
- 输出: `<原名>_delvto<值>.sp`（非原地）/ 原地改写留 `.bak`

## 本 case 抽取
- case_id: EDA-Eval-DesignFlow-DelvtoNetlistMod-001
- domain=spice_sim, layer=L1 (纯 Python 文本处理无 EDA 二进制), track=faithful, tier=B
- 交付: `apply_delvto.py` 参数化（argparse: --netlist/--delvto/--models/--delvto-by-model/--outdir）
- check 14 断言 a-n，真跑 candidate 在 hidden B (pulvt_rfv/nulvt_rfv, delvto -0.15, PMOS+0.15/NMOS-0.15)
- ref 14/14 PASS, 5 neg 全 FAIL NEG_RC=5/5
