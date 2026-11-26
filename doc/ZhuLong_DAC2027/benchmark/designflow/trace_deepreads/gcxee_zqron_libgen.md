# deepread — 1794969925980_gcxee (clarawu @ hfeg0pkn005, mc=72, spice_sim)

## 用户真实意图（trace verbatim）
clarawu 做 DDR4 ZQ 校准 Ron characterization（FineSim/HSPICE）。8 条 user 消息演化：
- U[0]-U[3] how-to：`.inc` 相对路径调不到文件 / `.temp` DC 扫描 / 温度作参数（Q&A，trace-faithful 上下文）
- U[4]-U[7] 主线交付：写 Python 脚本读 `wv_Ron_<proc>/Ron_<proc>#<n>.md0` + `stimulus_Ron_<proc>.sp`，
  生成 `zqcode_75pvt.sp` 的 `.lib ZQCODE_<PVT>...endl` 块
  - U[6] 要求大写 `ZQCODE_` + zqpu/zqpd 参数（agent 在 idx=70 把 `zqcode_`→`ZQCODE_`）
  - U[7] 要求每块含 corner 元信息：`.lib 'model.sp' top_tt` / `.lib 'model_thick.sp' tt_vodka` /
    `.temp 60` / `.param VVDD=0.82` / `.param VVDDQ=0.6`（agent 在 idx=80-83 加 parse_pvt + MODEL_SP/THICK）

## 关键数据结构（trace verbatim）
- `.md0` 列：`index zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpu_50 rpd_50 temper alter#`
- PVT label：`TT_60C_0P82V_0P6V` → proc=TT / temp=60 / vdd=0.82 / vddq=0.60（M40C→-40，0PxxV→0.xx）
- best-row：rpu_50/rpd_50 **各自独立**选最接近 TARGET=230 的行 → 取该行 zq5..0（pu/pd 可不同行不同码，
  trace idx=41 实证：rpu50=230.590 zqpu=011111 | rpd50=230.860 zqpd=001011）
- PVT 列表来源：`stimulus_Ron_<proc>.sp` 中有序 `* PVT: <label>` 注释，`alter#` 1-based 映射
- 输出块：`.lib ZQCODE_<PVT>` + model `.lib` + `.temp` + `VVDD`/`VVDDQ` + `zqpu5..0`/`zqpd5..0` + `.endl`

## 合成（r879 已落地 → EDA-Eval-DesignFlow-ZqRonLibGen-001）
- reframe：harness-for-teeth（Q&A + one-off script → produce 参数化 `zq_ron_libgen.py`）
- asset A：process=tt，4 PVT（TT_M40C/25C/60C/130C × vdd/vddq），target=230，rpu/rpd 值 verbatim 自 trace
- hidden B：process=ss，4 PVT（SS_*，不同 temp/vdd/vddq），target=215，zq 码全不同 → anti-hardcode-A
- check.py：13 断言，独立重算 best-row zq 位比对 + anti-hardcode-A + determinism
- 自验：REF PASS（13/13），5 neg 全 FAIL（NEG_RC=5/5）
- layer=L1（纯 python 文本解析，无 EDA 二进制）
