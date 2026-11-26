//####################################################
// Description
//####################################################
// Revision History
//  -v1.0  Lorik Xiao  2026-10-19
//      Initial version
//####################################################
// ============================================================================
// vco_fb_model.v
// VCO 反馈时钟模型 (Behavior, 仿真专用, 不可综合)
//
//   Fvco(code) = vco_base - code * vco_step   [GHz]
//   FBCLK      = Fvco / 400                   [GHz]
//   FBCLK 周期 = 400 / Fvco                    [ns]
//   vco_enable=0 时不振荡 (FBCLK=0)
//   注: vco_base/vco_step 为内部 real 变量, 由 TB 通过层次引用赋值
//       (vco.vco_base = ...; vco.vco_step = ...;)
//       VCS 不支持 real 类型端口 (IPD 冲突 bug), 必须用层次引用传递
//
// 被 model TB (tb_cfreq_ctrl.v) 与 synth TB (tb_cfreq_ctrl_synth.v) 共用。
// ============================================================================

`timescale 1ns/1ps

module vco_fb_model (
    input  [4:0] cap_code,
    input         vco_enable,
    output reg    fbclk
);
    real vco_base;     // GHz (code=0 时 VCO 频率), 由 TB 层次引用赋值
    real vco_step;     // GHz/cap (每档频率递减步进), 由 TB 层次引用赋值
    real vco_freq;     // GHz
    real half_period;  // ns

    // 振荡器: 每个周期即时计算频率 (避免 real 信号敏感列表问题)
    initial fbclk = 1'b0;
    always begin
        vco_freq = vco_base - cap_code * vco_step;
        if (vco_freq < 0.01) vco_freq = 0.01;      // 下限保护
        half_period = (400.0 / vco_freq) / 2.0;    // ns (Fvco[GHz] -> FBCLK=Fvco/400)
        if (vco_enable && half_period > 0.1) begin
            #(half_period) fbclk = ~fbclk;
        end else begin
            #(20) fbclk = 1'b0;
        end
    end

endmodule

