# a583c_xrxiong_netlist_portclean.md — round #495 deepread

## trace
- sid: 1793770593617_a583c
- user: xrxiong · host: hfeg0plg74 (10.129.8.112) · mc=129
- keywords: verilog:664;netlist:350;drc:303;aether:102;schematic:55;lvs:13;cmos:13;lib.defs:12
- file: /home/xrxiong/.cline/data/sessions/1793770593617_a583c/1793770593617_a583c.messages.json (188906 bytes)
- schema: {version, agent:"lead", sessionId, messages:[{id,role,content:[{type:text|thinking|tool_use|tool_result}]}]}
- 114 msgs / 26 user / 23 tool_use

## conversation flow
1. U#1-2: 改 tbconfig (tbarchetecture ddr5→ddr6) — sed via shell-runner (editor blocked by writableRoot policy=/home/xrxiong)
2. U#3: 「修改 tbconfig, 提取 drcoa 项目 lib=drcoa_digital cell=C_APCtrl 的网表」→ sed 改 blockcellname R_RowCtrl→C_APCtrl + netlistversion=V0_C_APCtrl_..., cd DLUT && ./bin/vsim_aether 后台跑
3. vsim_aether → emy2verilog 导出 31 子模块网表到 netlist/V0_C_APCtrl_CST11月04日.星期三/ (emy.log: "Exporting design drcoa_digital/C_APCtrl/schematic ... 100% 0 errors 0 warnings 13.21s")
4. U#4: 「为什么目录名乱码?不要使用中文」→ netlistversion 含中文月/日/星期三, 建议 ASCII timestamp
5. U#5: 「阅读 clean_netlist.py」→ 助手读到完整源码(tool_result), 总结 5 步清洗逻辑

## clean_netlist.py 源码 (从 msg 118 tool_result 提取, 完整)
```python
#!/usr/bin/env python3
"""Remove power/gnd/bias ports from Verilog netlist.
Ports removed: .vbn .vbp .vcc .vss .vdbias
               .inh_vss .inh_vcc .inh_vbp .inh_vbn .inh_vdbias
Also removes inout declarations and module port list entries.
Functional uses (e.g. .A(inh_vss)) are replaced with constants.
"""
import re, sys

def clean(input_file, output_file=None):
    with open(input_file, 'r') as f:
        text = f.read()
    if output_file is None:
        output_file = input_file.rsplit('.', 1)[0] + '.v'
    inh = ['inh_vdbias', 'inh_vbp', 'inh_vbn', 'inh_vcc', 'inh_vss']
    std = ['vdbias', 'vbp', 'vbn', 'vcc', 'vss']
    ports = inh + std
    # 1. Remove power port connections from instances
    for p in ports:
        text = re.sub(r'\.' + p + r'\([^)]*\)\s*,\s*', '', text)
        text = re.sub(r',\s*\.' + p + r'\([^)]*\)', '', text)
        text = re.sub(r'\.' + p + r'\([^)]*\)(\s*\))', r'\1', text)
    # 2. Replace functional power signal refs with constants
    text = re.sub(r'\(inh_vss\)', "(1'b0)", text)
    text = re.sub(r'\(inh_vcc\)', "(1'b1)", text)
    text = re.sub(r'\(inh_vbp\)', "(1'b0)", text)
    text = re.sub(r'\(inh_vbn\)', "(1'b0)", text)
    text = re.sub(r'\(inh_vdbias\)', "(1'b0)", text)
    # 3. Remove inout declarations
    for p in inh:
        text = re.sub(r'^[ \t]*inout[ \t]+' + p + r'[ \t]*;[ \t]*\n', '', text, flags=re.MULTILINE)
    # 4. Remove from module port lists
    for p in inh:
        text = re.sub(r'\b' + p + r'\b', '', text)
    # 5. Cleanup commas
    text = re.sub(r'(,\s*){2,}', ',', text)
    text = re.sub(r',\s*\)', ')', text)
    text = re.sub(r'\(\s*,', '(', text)
    # 6. Cleanup whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    with open(output_file, 'w') as f:
        f.write(text)
    print('Done ->', output_file)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 clean_netlist.py <input.v> [output.v]')
        sys.exit(1)
    clean(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
```

## verdict
CLEAN single-produce: clean_netlist.py 是确定性 5 步 regex 端口清洗器, 自包含可复刻。vsim_aether/emy2verilog 需整 EDA toolchain + drcoa 私有库不可复刻 → 取 clean_netlist.py 为可复刻产物。B-grade synthesized: 可见 A dirty_netlist_A.v(C_APCtrl) vs 隐藏 B dirty_netlist_B.v(C_DPCtrl, 全不相交名), 端口名驱动通用化 + 隐藏 B 反硬编码。

## 交付
- case_id: EDA-Eval-DesignFlow-NetlistPortClean-001
- D.jsonl 304→305, ledger_D a583c claim+mark case, k=14 (a-n), L2, schematic_netlist
- ref PASS 14/14 + 5 fakes FAIL NEG_RC=0
