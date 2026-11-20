# fyfm9 — ShmooCfgParser deepread

**session**: `1792630397654_fyfm9.messages.json` · yanxvwei @ hfeg0pkn002 (10.129.2.11)
**mtime**: 2026-10-30 · 245 msgs / ~1.05 MB · cron 11-10 log: 54 hspice / 45 pyAether / 18 netlist / 13 schematic
**source**: 11-05 重扫令 → cron 11-10 log diff 8 un-ledgered spice-dominated，held 5 备选 peek 全 5 → fyfm9 CLEAN (其余 4 = 2 FIFO dup of z7n9b / 1 near-dup of v5icx / 1 diagnostic)。

## 对话流（13 user 轮，2D Shmoo 流程 cxmtGen2DShmooFromWv.pl）
- U#0 「cxmtGen2DShmooFromWv.pl 支持 MRcode（扫描 vref 电阻串 code MRCode<6:0>），cfg 文件该怎么写」—— 咨询
- U#12 「写使用文档，结合代码介绍 cfg 每个参数含义 + MRcode 作用」→ assistant 产出 `cxmtGen2DShmooFromWv_Usage.md`（**完整 cfg 格式规格**，见下）
- U#20 「/proj/.../13_digital_eye_withVrefDQ/ excel 中间为什么空，不要猜测找根因」—— 诊断
- U#71 「2dshmoo/wv_2dshmoo/ 咋生成 excel」
- U#73 「单独写个脚本，将 cxmtGen2DShmooFromWv.pl 画成 IO_2D_Shmoo.xlsx」→ `gen2DShmoo_from_txt.py`（get_shmoo_info + get_golden_value + 排序/cell）
- U#97 gen2DShmoo_from_txt.py traceback (get_golden_value)
- U#127 「wv_shmoo.txt 得到的 excel 中间 -30ps~-60ps 没数据，找根因」
- U#145 「写一个脚本用于读取 tr0 生成 wv_shmoo.txt」→ `tr0_to_wvshmoo.py`（驱动 wv Tcl 抽 tr0）
- **U#185 「使其能够输入 shmoocfg 文件」** ← 本 case 选轮（提需求未给根因/修复 → A-合规；作 B-synthesized 交付）
- U#221 tr0_to_wvshmoo.py --cfg shmoo1.cfg 报错（信号名 dini<0>/dqsampn not found）
- U#239 「加 -MRCode 反而把列按字符串排，不对，为什么」
- U#241/U#243 MRcode 补齐时机 / 全流程哪部分起作用

## 选轮裁定
- U#185 = 纯提需求「使其能够输入 shmoocfg 文件」（feature-add，未给根因/修复）→ A-faithful 合格 ✓。
- 取 B-synthesized 口径：把 assistant 给 tr0_to_wvshmoo.py 增加的 `read_cfg()`（msg #204）重构成**通用的 shmoo.cfg 解析函数** `parse_shmoo_cfg(cfg_text)->dict`，契约对齐 Perl `getInfoFromCfgFile`，使隐藏 B（不同信号/位宽/引号/缺省项）可判分 + 反硬编码。

## 金标准 = read_cfg()（msg #204，editor new_text on _tr0_new.py）
```python
def _strip_quotes(s):
    s = s.strip()
    while (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    return s

def read_cfg(cfg_path):
    info = {}; signal_list = []
    with open(cfg_path) as f:
        for ln in f:
            line = ln.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            key, _, val = line.partition("=")
            key = key.strip(); val = _strip_quotes(val)
            if key.lower() == "signal":
                v = val.replace(",", ":").replace(" ", "")
                if v: signal_list.append(v)
            else:
                info[key.lower()] = val
    return {"signals": signal_list, "wave_pattern": info.get("wave_path"),
            "vth": info.get("a2d_vth"), "edge": info.get("clk_edge"),
            "start_time": info.get("start_time"), "toggle_start": info.get("toggle_start"),
            "toggle_count": info.get("toggle_count"), "glitch_th": info.get("glitch_th")}
```
关键口径：① `#`/空行/无`=`行跳过 ② Signal 逗号→冒号 + 去全部空格，多行顺序保留 ③ 其它 key 小写、值剥成对引号 ④ 只返回 8 个契约键，Timing/Voltage 进 info 但不返回 ⑤ 可选键缺省 None。

## 真实 cfg（资产）
- A = `shmoo.cfg`（real, msg #26）：Signal dini/dinq/dinib/dinqb → ...dqsampn；Wave_Path 单引号 `*100ps.tr0`；A2D_Vth=0.5125；CLK_Edge=f；Start_Time=2n；Toggle_Start=1；Toggle_Count=20；无 Glitch_Th；Timing=0ps/Voltage=0110101（须丢弃）。
- B1 = `shmoo1.cfg`（real, msg #26）：信号带 `<0>` + xi0<0>...；Wave_Path 单引号 `*ps.tr0`。
- B2 = synthesized：双引号 Wave_Path、3 域 Signal `data_a,clk_a,ref_a`、缺 Toggle_*/Glitch_Th、噪声无`=`行、Timing/Voltage 在场。

## case
EDA-Eval-DesignFlow-ShmooCfgParser-001（characterization / B-synthesized / L1 / k=21）
- check.py 21 断言（a..r + load）：zip/可调用/B1 dict/signals(4 str)/signals 精确匹配/wave_pattern 单引号剥/vth/edge 原始/start_time 原始/toggle_start+count/glitch_th None/不含 timing-voltage/恰 8 键/B2 signals(3 域 ref)/B2 wave_pattern 双引号剥/B2 标量/B2 缺省全 None/反硬编码 signal 不泄漏/反硬编码 glob 不泄漏/3 次幂等/噪声 cfg 空。
- format-aware 结构化比较（dict/list 相等，非文本相似）—— 落实 research 日报 11-09 designflow 建议 ①（格式感知等价比较）。
- 自验：ref PASS 21/21 + 3neg(stub/always_example/core_deleted)全 FAIL NEG_RC=0 + §4.9 三假全 FAIL + check_sha256=90ea2a86…。
