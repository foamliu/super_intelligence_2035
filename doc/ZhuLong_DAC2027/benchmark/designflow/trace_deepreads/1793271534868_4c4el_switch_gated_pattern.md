# Deepread: 1793271534868_4c4el (yzwang @ hfeg0pkn001, mc=90, layout_virtuoso)

## Trace meta
- session: 1793271534868_4c4el, user yzwang, host hfeg0pkn001 (10.129.2.10), mc=90
- 109 msgs, 4 real user_inputs (act mode)
- tools: dbCreateRect:407 + dbCreatePath:60 + dbCreatePolygon:34 + dbCreateLabel:23 + pyAether:4 + ddgetobj:4 + cellview:4
- status: assistant delivered complete artifact (oneOrTwoLayerSpacePass.il.new, 710 lines); no explicit user acceptance after final delivery → B-synthesized

## User task (4 iterative requirements)
- U0 (msg#0): "我在/home/pdk/yzwang/06_AI_workspace/test8放了一个文件叫oneOrTwoLayerSpaceFail.il的pcell脚本，为什么我勾选InsideTouch,OutsideTouch,CUT这三个选项，但没有新的图形生成？"
  → debug: why InsideTouch/OutsideTouch/CUT switches produce no new shapes in Fail.il
- U1 (msg#25): "如果我想把这三个功能加在相同路径下的oneOrTwoLayerSpacePass.il里，应该怎么处理，请帮我在原有的基础上尽量不要做太大的结构性变动，最好是把oneOrTwoLayerSpacePass.il相关的代码复制过去。"
  → add the three switches to Pass.il, minimal structural change, copy from Fail.il
- U2 (msg#71): "脚本改得有问题，当我勾选checkmax的选项时，还是会显示这三个模块的图形，我要求跟Fail的一样，必须在不勾选checkmax的前提下，同时勾选这三个模块的开关，才能显示多出来的图形。同时我还要求这三个模块的开关默认不打开"
  → BUG: shapes show even when CheckMax checked. FIX: gate three switches by `if(!CheckMax then ...)`; switches default OFF (nil)
- U3 (msg#81): "我要求这三个开关显示的图形中不带OPC01_mark1这层。"
  → remove OPC01_mark1 (lppHighlight) layer from the three switch blocks; only obj/obj1 (layer1/layer2) shapes

## Real grounding files (fetched from .75:/home/pdk/yzwang/06_AI_workspace/test8/)
- oneOrTwoLayerSpaceFail.il (1439 lines, 57KB) — source with three switches
- oneOrTwoLayerSpacePass.il (616 lines, 20KB) — original Pass without switches
- oneOrTwoLayerSpacePass.il.new (710 lines, 24KB) — DELIVERED artifact (assistant)

## Pcell structure (from Pass.il.new)
- library="PDK_QA_PCELL", cell="oneOrTwoLayerSpacePass", view="layout"
- pcDefinePCell params: userSpecifyRuleDescription, ruleDescription, Check45dgree, **InsideTouch/OutsideTouch/CUT (boolean nil)**, layer1="V1_drawing", space=0.378, layer1width=0.129, layer1length=0.189, layer2="V1_drawing", layer2width=0.129, layer2length=0.189, Checkarea, CheckExact, **CheckMax (boolean nil)**, recognition="BORD_PERI"
- layer parse: `rexCompile("_"); obj = parseString(rexReplace(layer1, " " 1))` (first-underscore split, same as r211)
- mark layers: lppHighlight=lInfo->highlightLayer (OPC01_mark1), lppBorder=lInfo->borderLayer, lppText=lInfo->textLayer
- step = space*3; basex = space*2; basey = space (initial)

## THE THREE SWITCH BLOCKS (the novel core, lines 456-527 of .new)
Gated by `if(!CheckMax then ... );end not checkmax`:
```
if(!CheckMax then
  if(CUT then
    basex = basex + 1.5*layer1width + 2*layer2width + 2*step; basey = basey
    dbCreateRect(cv obj  list(basex:basey  basex+layer1width:basey+layer1length))            ; layer1 rect
    dbCreateRect(cv obj1 list(basex+0.5*layer1width:basey  basex+0.5*layer1width+layer2width:basey+layer2length))  ; layer2 rect OVERLAP (offset 0.5*w1)
  );cut
  if(OutsideTouch then
    basex = basex + 1.5*layer1width + 2*layer2width + step; basey = basey
    dbCreateRect(cv obj  list(basex:basey  basex+layer1width:basey+layer1length))            ; layer1 rect
    dbCreateRect(cv obj1 list(basex+layer1width:basey  basex+layer1width+layer2width:basey+layer2length))  ; layer2 rect EDGE-TOUCH (at basex+w1)
  );end outside touch
  if(InsideTouch then
    basex = basex + 1.5*layer1width + 2*layer2width + step; basey = basey
    dbCreateRect(cv obj  list(basex:basey  basex+layer1width:basey+layer1length))            ; layer1 rect
    dbCreateRect(cv obj1 list(basex-0.5*layer1width:basey-grid  basex+layer2width+0.5*layer1width:basey+layer2length+layer1length))  ; layer2 STRADDLE (extends left+below+taller)
    ;[pattern12-1]: outside (second pair)
    basex = basex + 1.5*layer1width + 2*layer2width + step; basey = basey
    dbCreateRect(cv obj1 list(basex:basey  basex+layer1width:basey+layer1length))            ; layer2 rect
    dbCreateRect(cv obj  list(basex-0.5*layer1width:basey-grid  basex+layer2width+0.5*layer1width:basey+layer2length+layer1length))  ; layer1 STRADDLE
  );end insise touch
);end not checkmax
```

## Key novel aspects (DISTINCT from r211/r207)
1. **CheckMax negation gate** — three switches suppressed when CheckMax=true (U2 bug+fix: wrap in `if(!CheckMax then ...)`)
2. **Three independent switch-gated patterns** — CUT(overlap, 2 shapes) / OutsideTouch(edge-touch, 2 shapes) / InsideTouch(straddle, 4 shapes: 2 pairs)
3. **Layer filter** — three switch blocks use ONLY obj(layer1)/obj1(layer2), NO lppHighlight/OPC01_mark1 (U3)
4. **Sequential basex progression** — each switch advances basex by 1.5*w1+2*w2+{2*step|step}

## Case plan (B-synthesized, L1-boundary, layout_virtuoso 47→48)
- CID: EDA-Eval-DesignFlow-SwitchGatedSpacePatternGen-001
- Task: SUT writes switch_gated_space_pattern_gen.py, CLI 1 arg <config.json>
- Config: switches{InsideTouch,OutsideTouch,CUT,CheckMax}, layers{layer1,layer2}, params{space,layer1width,layer1length,layer2width,layer2length,grid}, base_offset{basex,basey}
- Logic: step=space*3; gate = !CheckMax; for each switch in [CUT,OutsideTouch,InsideTouch] if switch AND gate: compute shapes (obj=layer1,obj1=layer2), advance basex; NO mark layer
- Output JSON: {config_echo, gate_status, active_switches, inactive_switches[{name,reason}], shapes[{switch,layer,box,pattern_type}], summary{n_shapes,n_active,n_suppressed_checkmax,n_switch_off,has_mark_layer_shapes}}
- Asset A: real V1_drawing, space=0.378, w=0.129, l=0.189, grid=0.001, basex=0.756, basey=0.378, all 3 switches ON, CheckMax=false → 8 shapes (2+2+4)
- Hidden B: reparameterized (layer=M2_drawing/M3_drawing, space=0.5, w=0.2, l=0.3, grid=0.005, different basex/basey, switches mixed: CUT=true/OutsideTouch=false/InsideTouch=true, CheckMax=false → 6 shapes) + CheckMax=true variant (all 3 suppressed)
- B_broken: degenerate (space<=0) → graceful error
- k=16 conditions a–p

## DEBT: 0
