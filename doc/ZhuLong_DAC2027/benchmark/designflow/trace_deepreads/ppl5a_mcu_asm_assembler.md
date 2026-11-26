# trace_deepreads/ppl5a_mcu_asm_assembler.md

**session**: 1788772817371_ppl5a · user harrys · host hfeg0pkn002 (10.129.2.11) · mc557
**agent**: lead · 247 msgs / 126 user (mostly tool_result) / 1.02 MB
**scanned keywords**: rtl:723;assembler:648;verilog:123;synopsys:38;analog:12;systemverilog:10;cadence:5;dc_shell:3
**ledger history**: parked r148 (2026-11-06) as "kw-mention only, analog/netlist, unfit shard-A L2" — **misjudgment** (shallow survey, no deep-read). Deep-read confirms clean digital/RTL produce-task. Reopened r418.

## User prompt (single, U#0)
`<user_input mode="act">base mcu document achievement this mcu until run  sucess until pass and show pass waveform in simvision</user_input>`

**A-faithful check**: user gives NO root cause, only "make the MCU pass and show waveform in simvision" → A-faithful ✓ (vague goal, agent must figure out what's broken).

## What the agent did (tool mix: run_commands×83, editor×26, read_files×15)
Iterative MCU bring-up on `/home/harrys/Desktop/digital_rtl_design/`:
1. **asm_assembler.py** (118 lines, pure stdlib) — two-pass assembler for a custom 16-bit MCU ISA:
   - 16 opcodes (ADD/SUB/AND/OR/XOR/MOV/LDI/LD/ST/BEQ/BNE/JMP/CALL/RET/PUSH/POP)
   - 8 registers (R0-R7), encoding [15:12]=op [11:9]=rd [8:6]=rs [5:3]=rt [2:0]=lo
   - pseudo ADDI/SUBI, labels, ORG, comments (// ;), Verilog $readmemh hex output
   - iterated ~12 editor edits over the session
2. **test_blink.asm** (73 lines) — GPIO blink + ALU self-test + mem test + countdown loop
3. **test_blink_updated.asm** (10 lines) — minimal blink
4. **mcu_cpu_core.sv** — RTL core (edited 3×)
5. ran simvia run_commands until pass + simvision waveform

## ISA (extracted from asm_assembler.py docstring + impl)
- 16-bit word, 4-bit opcode, 3-bit fields rd/rs/rt
- R-type: op|rd|rs|rt|000 ; LDI: op|rd|imm8 ; LD/ST: op|rd|rs|off6
- BEQ/BNE: op|000|rs|off6 (PC-relative signed 6-bit, compare Rs==0)
- JMP/CALL: op|addr12 ; RET: op|0 ; PUSH: op|000|reg|000 ; POP: op|reg|000|000
- ADDI/SUBI pseudo → ADD/SUB with imm3 in rt field

## Deliverable candidate
**asm_assembler.py** = clean produce-task (pure stdlib, offline-verifiable: parse .asm → emit hex, check by independent re-encoding). Perfect B档 synthesized material.

## B档 synthesis plan (McuAsmGen-001, digital L1 spec-driven code generator, k=15)
- **A (visible)**: isa_spec.md (encoding table) + example.asm (cleaned test_blink, 2-operand BNE form)
- **B (hidden, cross-input guard)**:
  - factorial.asm — CALL/RET/PUSH/POP/BEQ (absent in A) + forward+backward branches + ADDI -1
  - edge.asm — mid-file ORG 0x010 gap (0000 padding) + AND/OR/XOR/SUB/MOV/LD mix + label-on-same-line
- **deliverable**: mcu_asm.py (pure stdlib two-pass assembler)
- **check.py**: independent oracle (regex-tokenize + binary-concatenation word build, structurally ≠ reference's split+shift-or); 15 conditions (a-o) covering each instruction class + ORG padding + format
- **negatives**: naive_empty / print_only / core_removed (BEQ/BNE offset removed → only k fails, surgical) / hardcoded_A (emits A's 33-word hex → fails B's different word count, cross-input guard)
- **self-verify**: ref PASS 15/15; 4 neg FAIL; §4.9(a)(b)(c) FAIL; core_removed surgical (only k)

## Notes
- test_blink.asm original uses 3-operand `BNE R4, R0, COUNTDOWN` but the assembler's BNE impl is 2-operand (`BNE Rs, label`). The cleaned A example.asm normalizes to 2-operand form for ISA consistency (B档 synthesized — spec cleaned, scenario/ISA from trace).
- /home/harrys/Desktop/digital_rtl_design reachable on hfeg0pkn002 (scp'd asm_assembler.py + .asm files for reference).
