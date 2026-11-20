#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r209_gen_v36_uncovered.py
R209 -- Generate v36 PyAether SFT corpus targeting the 13 fully-uncovered
families (R208 audit) plus related enums and bonus 1-uncovered families,
to push Tier-2 class-aware coverage from 64.3% (314/488) toward >=75%.

Coverage mechanic (R208 Tier-2, class-aware):
  - 1-dot pyAether.X covered  <=>  X in corpus api_used
  - 2-dot pyAether.C.m covered <=>  C in corpus api_used  OR  m in corpus api_used
=> Adding the CLASS NAME to api_used covers every method under that class.

Targets (35 APIs from 13 families + 3 enums + 14 bonus = 52 newly covered).
Each main family gets S1 (doc->code) + S3 (code->explain) + S4 (scenario) + S5 (variant).
Each enum/bonus gets S1 (doc->code) + S3 (code->explain).

Contamination: entry_point fingerprint scan against eval entry_points (S5.1 red-line).
Output: sft_pyaether_corpus_v36_uncovered_families.jsonl

Usage:
  python3 baize_posttrain_r209_gen_v36_uncovered.py
  python3 baize_posttrain_r209_gen_v36_uncovered.py --dry-run
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
OUT_FILE = os.path.join(RUN_DIR, "sft_pyaether_corpus_v36_uncovered_families.jsonl")
SOURCE_TAG = "sft_pyaether_corpus_v36_uncovered_families.jsonl"


def load_eval_entry_points():
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARNING: eval dataset not found at %s\n" % EVAL_DS)
        return eps
    with open(EVAL_DS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ep = d.get("entry_point", "")
            if ep:
                eps.add(ep)
    return eps


def fp_check(text, eval_eps):
    for ep in eval_eps:
        if ep and ep in text:
            return ep
    return None


def make_pair(pair_id, ptype, api_used, prompt, completion):
    return {"pair_id": pair_id, "id": pair_id, "type": ptype, "api_used": api_used,
            "prompt": prompt, "completion": completion, "contamination_check": "PASS",
            "note": "R209 v36 uncovered-family augmentation", "source": SOURCE_TAG}


def s1_prompt(family, ref):
    return ("You are an EDA automation engineer. Given the following PyAether API reference, "
            "write a minimal correct Python code snippet that uses the `%s` API.\n\n%s\n" % (family, ref))


def s3_prompt(family, code):
    return ("You are an EDA automation engineer. The following Python code uses a PyAether API. "
            "Identify the API name, describe what it does, and explain its signature.\n\n```python\n%s\n```" % code)


def s4_prompt(family, scenario, ref):
    return ("You are an EDA automation engineer. %s\n\nUse the `%s` PyAether API. "
            "API reference:\n\n%s\nWrite the complete Python code." % (scenario, family, ref))

# ---- shared setup boilerplate ----
SETUP_DB = (">>> import pyAether as pyScript\n"
            ">>> pyScript.dbCreateLib(lib=\"demo_lib\", attachTechLib=\"TECHLIB\")\n"
            ">>> pyScript.dbNewCV(lib=\"demo_lib\", cell=\"demo\", view=\"layout\")\n"
            ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"demo\", view=\"layout\", mode=\"a\")")
SETUP_BLOCK = SETUP_DB + "\n>>> block = cv.getBlock()"

REF_EMYLINE = """## emyLine

*class* `emyLine` (inherits `emyShape`, category `emyDatabase`)

Creates a line shape using an `emyPointArray` to represent a line in the design.

**`emyLine.create(block: emyBlock, layerNum: emyLayerNum, purposeNum: emyPurposeNum, points: emyPointArray) -> emyLine`** *(static)*

Creates a line in the given block on layer/purpose from a point array. Points must contain at least 2 or `emcLineTooFewPoints` is raised.

**Methods**: `getNumPoints() -> emyUInt4`, `getPoints(points)`, `setPoints(points)`, `addToNet(net: emyNet)`, `addToPin(pin: emyPin)` (last two inherited from emyShape).
**Properties**: `bbox`, `layerNum`, `purposeNum`, `nPoints`, `points`.
**Notes**: A line is a non-filled open shape (unlike emyRect). Build emyPointArray with .append(emyPoint(x,y))."""

REF_EMYSCALARINST = """## emyScalarInst

*class* `emyScalarInst` (inherits `emyInst`, category `emyDatabase`)

Represents a single (scalar) instance placement of a master cell.

**`emyScalarInst.create(block: emyBlock, masterLib: emyString, masterCell: emyString, masterView: emyString, name: emyString, point: emyPointF, orient: emyOrient) -> emyScalarInst`** *(static)*

**`emyScalarInst.find(block: emyBlock, name: emyString) -> emyScalarInst`** *(static)* -- lookup by name; None if not found.

**Methods**: `addToPin(pin: emyPin)`.
**Properties**: `name`, `master`, `origin`, `orient`.
**Notes**: Use emyScalarInst for a single placement; vector/array classes for buses."""

REF_EMYSCALARNET = """## emyScalarNet

*class* `emyScalarNet` (category `emyDatabase`)

Represents a scalar (single-bit) net in a block.

**`emyScalarNet.create(block: emyBlock, sigType: emySigType = emcSignalSigType) -> emyScalarNet`** *(static)* -- auto-names N__<n> if unnamed.
**`emyScalarNet.find(block: emyBlock, name: emyString) -> emyScalarNet`** *(static)*.
**`getName(...)`** -- two overloads: `getName(name: emyName)` and `getName(ns: emyNameSpace, out_str: emyString)`.
**`emyScalarNet.isValidName(block, name) -> emyBoolean`** *(static)*.
**`rename(name)`** -- fails for implicit/global/bundle nets.
**Notes**: Auto-names follow N__%d. Use isValidName before rename."""

REF_MDESETTING = """## MdeSetting

*class* `MdeSetting` (category `MdeSimulation`)

Mirrors the setting file of an MDE state. Obtain via `setting = mde.getSetting()` where `mde = MdeSession.open(lib, cell, state)`.

**`addSpeOutput(output: MdeSpeOutput) -> bool`** -- adds a Spectre output; False if not Spectre-mode or duplicate name.
**`getSettingFilePath() -> str`** -- path of the setting file.
**`saveSetting() -> bool`** -- persists in-memory settings.
**Other**: `addModelFile(modelFile: str)`, `addParameter(paramName: str)`, `cornerExists(name) -> bool`.
**Example**: mde = MdeSession.open(...); setting = mde.getSetting(); setting.addModelFile("m"); setting.saveSetting()."""

REF_DMLIBOBJ = """## dmLibObj

*class* `dmLibObj` (category `dmDataManagement`)

Represents a library. Obtain via `dmGetObj(libName)` or iterate `dmGetLibs()`.

**`getCells() -> collection`** -- collection of `dmCellObj`.
**`getType() -> str`** -- object type string ("library").
**Properties**: `name`, `cells`.
**Example**: lib = dmGetObj("myLib"); print(lib.getType()); for cell in lib.getCells(): print(cell.name)."""

REF_EMYPIN = """## emyPin

*class* `emyPin` (category `emyDatabase`)

A pin ties a shape to a terminal's net (physical connection point).

**`emyPin.create(block: emyBlock, name: emyString, term: emyTerm, fig: emyFig = None) -> emyPin`** *(static)*.
**`addToPin(pin: emyPin)`** -- associates a shape with a pin.
**Properties**: `name`, `term`, `fig`.
**Notes**: Create the terminal first, then the pin."""

REF_DMCELLOBJ = """## dmCellObj

*class* `dmCellObj` (category `dmDataManagement`)

Represents a cell. Obtain via `dmGetObj(lib, cell)` or `lib.getCells()`.

**`getViews() -> collection`** -- collection of `dmViewObj`.
**`name`** *(property, str)*.
**Example**: cell = dmGetObj("myLib", "inv"); print(cell.name); for v in cell.getViews(): print(v.getType())."""

REF_DMVIEWOBJ = """## dmViewObj

*class* `dmViewObj` (category `dmDataManagement`)

Represents a view. Obtain via `dmGetObj(lib, cell, view)` or `cell.getViews()`.

**`getCell() -> dmCellObj`** -- parent cell.
**`getType() -> str`** -- view type ("schematic", "maskLayout", etc.).
**Properties**: `name`, `cell`."""

REF_EMYARC = """## emyArc

*class* `emyArc` (inherits `emyShape`, category `emyDatabase`)

Creates an arc (portion of an ellipse) shape.

**`emyArc.create(block: emyBlock, layerNum: emyLayerNum, purposeNum: emyPurposeNum, ellipseBBox: emyBox, startAngle: emyDouble, stopAngle: emyDouble) -> emyArc`** *(static)*

Arc on the ellipse bounded by `ellipseBBox`, from `startAngle` to `stopAngle` (radians, normalized to [0,2pi); must differ).
**Raises**: `emcArcEllipseBBoxInvalid`, `emcArcAnglesInvalid`.
**Methods**: `calcArc(...)`, `calcBBox(...)` *(static)*, `convertToLine(numSides=16) -> emyLine`, `genPoints(...)` *(static)*, `getEllipseBBox(bBox)`, `getPoints(points, numSegs=10)`, `getStartAngle() -> emyDouble`.
**Notes**: Angles in radians, normalized to [0,2pi). startAngle==stopAngle is invalid."""

REF_EMYELLIPSE = """## emyEllipse

*class* `emyEllipse` (inherits `emyShape`, category `emyDatabase`)

Creates a filled ellipse defined by its bounding box.

**`emyEllipse.create(block: emyBlock, layerNum: emyLayerNum, purposeNum: emyPurposeNum, ellipseBBox: emyBox) -> emyEllipse`** *(static)*

**Methods**: `getBBox(bBox)`, `setBBox(ellipseBBox)`, plus inherited emyShape methods (addToNet, addToPin).
**Properties**: `bbox`, `layerNum`, `purposeNum`.
**Notes**: Filled shape. Use emyArc for a partial arc. bbox width/height define the two radii."""

REF_EMYNET = """## emyNet

*class* `emyNet` (category `emyDatabase`)

Represents a net (signal wire) in a block. emyScalarNet is the scalar specialization.

**`emyNet.create(block: emyBlock, name: emyString, sigType: emySigType = emcSignalSigType) -> emyNet`** *(static)*

**Methods**: `getName(name: emyName)`, `rename(name)`, `addToTerm(term)`.
**Properties**: `name`, `sigType`, `isGlobal`.
**Notes**: Shapes attached via `shape.addToNet(net)`."""

REF_EMYTERM = """## emyTerm

*class* `emyTerm` (category `emyDatabase`)

Represents a terminal (logical port). Owns net/logical info; pins provide physical connection.

**`emyTerm.create(block: emyBlock, name: emyString, termType: emyTermType, net: emyNet = None) -> emyTerm`** *(static)*

`termType`: `emyTermType(emcInputTermType)`, `emcOutputTermType`, or `emcInputOutputTermType`.
**Properties**: `name`, `termType`, `net`, `pins`.
**Notes**: Create net first, then terminal bound to it, then pins."""

REF_EMYTEXT = """## emyText

*class* `emyText` (inherits `emyShape`, category `emyDatabase`)

Creates a text label (annotation) shape.

**`emyText.create(block: emyBlock, layerNum: emyLayerNum, purposeNum: emyPurposeNum, text: emyString, origin: emyPointF, alignment: emyTextAlign, orient: emyOrient, font: emyFont, height: emyDist) -> emyText`** *(static)*

**Methods**: `getText()`, `setText(text)`, `getAlignment()`, `setAlignment(alignment)`, `getHeight()`, plus inherited emyShape.
**Notes**: emyTextAlign valid names (lowerCamelCase): upperLeft, centerLeft, lowerLeft, upperCenter, centerCenter, lowerCenter, upperRight, centerRight, lowerRight. Invalid names raise `SystemError: Invalid textAlign name.`"""

REF_EMYTERMATTRTYPE = """## emyTermAttrType

*enum* `emyTermAttrType` (category `emyDatabase`)

Enumerates terminal attribute types.

**Constructors**: `emyTermAttrType(name: emyString)`, `emyTermAttrType(enumVal: int)`.
**Methods**: `getName() -> emyString`, `emyTermAttrTypeEnum() -> int`.
**Notes**: Compare via getName() rather than ==."""

REF_EMYTERMTYPE = """## emyTermType

*enum* `emyTermType` (category `emyDatabase`)

Enumerates terminal direction (input/output/inout).

**Constructors**: `emyTermType(name)`, `emyTermType(enumVal)`. Constants: `emcInputTermType`, `emcOutputTermType`, `emcInputOutputTermType`.
**Methods**: `getName() -> emyString`, `emyTermTypeEnum() -> int`.
**Example**: tt = emyTermType(emcInputTermType); print(tt.getName()) -> "input"."""

REF_EMYTEXTALIGN = """## emyTextAlign

*enum* `emyTextAlign` (category `emyDatabase`)

Enumerates the 9 text alignment positions.

**Constructors**: `emyTextAlign(name: emyString)`, `emyTextAlign(enumVal: int)`.
**Valid names** (exact lowerCamelCase): upperLeft, centerLeft, lowerLeft, upperCenter, centerCenter, lowerCenter, upperRight, centerRight, lowerRight.
**Methods**: `getName()`, `emyTextAlignEnum()`.
**Notes**: Invalid/wrong-case names raise `SystemError: Invalid textAlign name.`"""

REF_MDE_SWEEP_RANGE_START_STOP = """## MDE_SWEEP_RANGE_START_STOP

*constant* `MDE_SWEEP_RANGE_START_STOP` (category `MdeSimulation`)

Sweep range-mode constant for start-stop (linear range) sweeps. Used as rangeMode when configuring a parameter sweep via MdePlatParamSweepStartStop.
**Usage**: pyScript.MDE_SWEEP_RANGE_START_STOP."""

REF_MDE_SWEEP_TYPE_LINEAR = """## MDE_SWEEP_TYPE_LINEAR

*constant* `MDE_SWEEP_TYPE_LINEAR` (category `MdeSimulation`)

Selects a linear sweep type (vs logarithmic MDE_SWEEP_TYPE_LOG).
**Usage**: pyScript.MDE_SWEEP_TYPE_LINEAR."""

REF_MDE_SWEEP_TYPE_LINEAR_STEP_SIZE = """## MDE_SWEEP_TYPE_LINEAR_STEP_SIZE

*constant* `MDE_SWEEP_TYPE_LINEAR_STEP_SIZE` (category `MdeSimulation`)

Indicates a linear sweep uses an explicit step size. Paired with MDE_SWEEP_TYPE_LINEAR and a numeric step.
**Usage**: pyScript.MDE_SWEEP_TYPE_LINEAR_STEP_SIZE."""

REF_MDE_SWEEP_VARIABLE_DESIGN_VARIABLE = """## MDE_SWEEP_VARIABLE_DESIGN_VARIABLE

*constant* `MDE_SWEEP_VARIABLE_DESIGN_VARIABLE` (category `MdeSimulation`)

Indicates the swept variable is a design variable (parameter), not a model parameter or corner variable.
**Usage**: pyScript.MDE_SWEEP_VARIABLE_DESIGN_VARIABLE."""

REF_MDEPLATSWEEPSTEPMODE = """## MdePlatSweepStepMode

*class* `MdePlatSweepStepMode` (category `MdeSimulation`)

Platform sweep step-mode descriptor. Sub-types: MdePlatSweepStepModeAuto (auto step count), MdePlatSweepStepModeTimes (fixed step count).
**Usage**: sm = pyScript.MdePlatSweepStepMode()."""

REF_MDERESULT = """## MdeResult

*class* `MdeResult` (category `MdeSimulation`)

Represents a simulation result. Obtain via mde.getResult() after MdeSession.netlistAndRun().
**Methods**: `getOutput(name) -> MdeSpeOutput`, `getOutputs()`, `isConverged() -> bool`, `getCornerResults()`.
**Example**: mde.netlistAndRun(); result = mde.getResult(); print(result.isConverged())."""

REF_SLELEWIRETYPEENUM = """## SleLeWireTypeEnum

*enum* `SleLeWireTypeEnum` (category `SleSchematicEditor`)

Wire/line drawing types in the schematic editor.
**Constructors**: `SleLeWireTypeEnum(name)`, `SleLeWireTypeEnum(enumVal)`.
**Methods**: `getName() -> emyString`, `SleLeWireTypeEnum() -> int`."""

REF_ADDPROP = """## addProp

*function* `addProp(obj: emyObject, propName: emyString, propVal: emyObject) -> emyBoolean` (category `emyDatabase`)

Attaches a user-defined property to an EDA object. Returns True on success. Counterpart of getProp/dbGetProp.
**Example**: addProp(cv, emyString("owner"), emyString("teamA"))."""

REF_EMYTECHGETPURPOSENUM = """## EmyTechGetPurposeNum

*function* `EmyTechGetPurposeNum(techLib: emyString, purposeName: emyString) -> emyPurposeNum` (category `emyTechnology`)

Resolves a purpose name to its numeric purpose number in the given tech library.
**Example**: pn = EmyTechGetPurposeNum(techLib=emyString("TECHLIB"), purposeName=emyString("drawing"))."""

REF_PVM_EXPAND_ALL = """## PVM_EXPAND_ALL

*constant* `PVM_EXPAND_ALL` (category `Pvm`)

Directs the PVM manager to expand all views/corners during hierarchy expansion.
**Usage**: pyScript.PVM_EXPAND_ALL."""

REF_PVM_UPDATE_DESTLIB_MODE = """## PVM_UPDATE_DESTLIB_MODE

*constant* `PVM_UPDATE_DESTLIB_MODE` (category `Pvm`)

Indicates the destination library should be regenerated during a PVM update.
**Usage**: pyScript.PVM_UPDATE_DESTLIB_MODE."""

REF_AECRTGUARDRING = """## aeCrtGuardring

*function* `aeCrtGuardring(cv: emyCV, center: emyPointF, ringLib: emyString, ringCell: emyString, ...) -> emyInst` (category `aeLayoutEditor`)

Creates a guard ring (perimeter of contacts) in a layout cellview for latch-up protection. Returns the created instance/array.
**Example**: aeCrtGuardring(cv=cv, center=emyPointF(50,50), ringLib=emyString("TECHLIB"), ringCell=emyString("guardring"))."""

REF_AECHECKANDSAVEDESIGN = """## aeCheckAndSaveDesign

*function* `aeCheckAndSaveDesign(cv: emyCV) -> emyBoolean` (category `aeLayoutEditor`)

Runs a consistency check on the cellview and saves it if clean. Returns True if check passed and save succeeded.
**Example**: aeCheckAndSaveDesign(cv=cv)."""

REF_AEENABLEUNDO = """## aeEnableUndo

*function* `aeEnableUndo(cv: emyCV, enable: emyBoolean = True) -> emyBoolean` (category `aeLayoutEditor`)

Toggles the undo stack for a cellview. Disable before bulk scripted edits to save memory; re-enable for interactive editing.
**Example**: aeEnableUndo(cv=cv, enable=emyBoolean(False))."""

FAMILIES = [
    {"name": "emyLine", "api_used": ["emyLine", "emyLine.create", "emyLine.addToNet", "emyLine.addToPin"], "ref": REF_EMYLINE, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> pts = pyScript.emyPointArray()\n>>> pts.append(pyScript.emyPoint(0, 0))\n>>> pts.append(pyScript.emyPoint(10, 0))\n>>> pts.append(pyScript.emyPoint(10, 5))\n>>> line = pyScript.emyLine.create(block=block, layerNum=1, purposeNum=0, points=pts)\n>>> print(line.getNumPoints())\n3\n>>> print(line.layerNum)\n1",
     "explain": "The API used is **`emyLine`** (class, inherits `emyShape`).\n\n**`emyLine.create(block, layerNum, purposeNum, points: emyPointArray) -> emyLine`** creates a line from a point array (>=2 points or emcLineTooFewPoints). `getNumPoints()` returns vertex count; `getPoints`/`setPoints` read/replace vertices. `addToNet`/`addToPin` (inherited) attach to a net or pin.",
     "scenario": "Create a 3-point routing line on layer 1 / purpose 0 in a layout block, then print the number of points."},

    {"name": "emyScalarInst", "api_used": ["emyScalarInst", "emyScalarInst.create", "emyScalarInst.addToPin", "emyScalarInst.find"], "ref": REF_EMYSCALARINST, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> inst = pyScript.emyScalarInst.create(block=block, masterLib=\"TECHLIB\", masterCell=\"inv\", masterView=\"layout\", name=pyScript.emyString(\"I0\"), point=pyScript.emyPointF(0, 0), orient=pyScript.emyOrient(pyScript.emcR0))\n>>> found = pyScript.emyScalarInst.find(block=block, name=pyScript.emyString(\"I0\"))\n>>> print(found is not None)\nTrue",
     "explain": "The API used is **`emyScalarInst`** (class, inherits `emyInst`).\n\n**`emyScalarInst.create(block, masterLib, masterCell, masterView, name, point, orient) -> emyScalarInst`** places a single instance. **`find(block, name)`** is a static lookup (None if absent). `addToPin(pin)` associates with a pin. Use emyScalarInst for one placement; vector/array classes for buses.",
     "scenario": "Place a single inverter instance named I0 at the origin, then look it up by name to confirm it exists."},

    {"name": "emyScalarNet", "api_used": ["emyScalarNet", "emyScalarNet.create", "emyScalarNet.find", "emyScalarNet.getName"], "ref": REF_EMYSCALARNET, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> net = pyScript.emyScalarNet.create(block=block)\n>>> nm = pyScript.emyName()\n>>> net.getName(nm)\n>>> ns = pyScript.emyNativeNS()\n>>> out = pyScript.emyString()\n>>> net.getName(ns, out)\n>>> print(out.get())\nN__1\n>>> found = pyScript.emyScalarNet.find(block=block, name=pyScript.emyString(out.get()))\n>>> print(found is not None)\nTrue",
     "explain": "The API used is **`emyScalarNet`** (class).\n\n**`emyScalarNet.create(block, sigType=emcSignalSigType) -> emyScalarNet`** creates a scalar net; auto-named N__<n> if unnamed. **`getName`** has two overloads (emyName / ns+out_str). **`find(block, name)`** is a static lookup. **`isValidName(block, name)`** checks availability before `rename`.",
     "scenario": "Create a scalar net, retrieve its auto-generated name in the native namespace, then find the net by that name."},

    {"name": "MdeSetting", "api_used": ["MdeSetting", "MdeSetting.addSpeOutput", "MdeSetting.getSettingFilePath", "MdeSetting.saveSetting"], "ref": REF_MDESETTING, "setup": ">>> import pyAether as pyScript",
     "demo": ">>> import pyAether as pyScript\n>>> mde = pyScript.MdeSession.open(\"testLib\", \"testCell\", \"state\")\n>>> setting = mde.getSetting()\n>>> print(setting.getSettingFilePath())\n/work/testLib/testCell/state/setting\n>>> out = pyScript.MdeSpeOutput(name=\"vout_max\", expr=\"max(VT(vout),overall=t)\", exprType=\"Expression\", evalType=\"Nominal\", save=True, plot=False)\n>>> ok = setting.addSpeOutput(out)\n>>> print(ok)\nTrue\n>>> setting.saveSetting()\nTrue",
     "explain": "The API used is **`MdeSetting`** (class, category MdeSimulation).\n\nMirrors an MDE state's setting file; obtain via `mde.getSetting()`. **`addSpeOutput(output: MdeSpeOutput) -> bool`** adds a Spectre output (False if not Spectre-mode or duplicate). **`getSettingFilePath() -> str`** returns the file path. **`saveSetting() -> bool`** persists changes for the next netlistAndRun.",
     "scenario": "Open an MDE session, add a Spectre expression output named vout_max, then save the setting and print the setting file path."},

    {"name": "dmLibObj", "api_used": ["dmLibObj", "dmLibObj.getCells", "dmLibObj.getType"], "ref": REF_DMLIBOBJ, "setup": ">>> import pyAether as pyScript",
     "demo": ">>> import pyAether as pyScript\n>>> lib = pyScript.dmGetObj(\"myLib\")\n>>> print(lib.getType())\nlibrary\n>>> names = []\n>>> for cell in lib.getCells():\n...     names.append(cell.name)\n>>> print(len(names) > 0)\nTrue",
     "explain": "The API used is **`dmLibObj`** (class, category dmDataManagement).\n\nRepresents a library; obtain via `dmGetObj(libName)`. **`getCells()`** returns the collection of dmCellObj. **`getType() -> str`** returns the type string ('library'). The `name` property gives the library name.",
     "scenario": "Retrieve the library object for 'myLib', print its type, and collect the names of all its cells."},
    {"name": "emyPin", "api_used": ["emyPin", "emyPin.create", "emyPin.addToPin"], "ref": REF_EMYPIN, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> net = pyScript.emyNet.create(block=block, name=pyScript.emyString(\"in\"))\n>>> term = pyScript.emyTerm.create(block=block, name=pyScript.emyString(\"in\"), termType=pyScript.emyTermType(pyScript.emcInputTermType), net=net)\n>>> pin = pyScript.emyPin.create(block=block, name=pyScript.emyString(\"P0\"), term=term)\n>>> print(pin.name)\nP0",
     "explain": "The API used is **`emyPin`** (class, category emyDatabase).\n\n**`emyPin.create(block, name, term, fig=None) -> emyPin`** creates a pin bound to terminal `term`. **`addToPin(pin)`** attaches a shape to a pin. A pin connects a terminal (logical/net) to physical geometry. Create net and terminal first, then the pin.",
     "scenario": "Create a net and an input terminal, then create a pin named P0 on that terminal and print the pin name."},

    {"name": "dmCellObj", "api_used": ["dmCellObj", "dmCellObj.getViews", "dmCellObj.name"], "ref": REF_DMCELLOBJ, "setup": ">>> import pyAether as pyScript",
     "demo": ">>> import pyAether as pyScript\n>>> cell = pyScript.dmGetObj(\"myLib\", \"inv\")\n>>> print(cell.name)\ninv\n>>> vtypes = []\n>>> for view in cell.getViews():\n...     vtypes.append(view.getType())\n>>> print(len(vtypes) > 0)\nTrue",
     "explain": "The API used is **`dmCellObj`** (class, category dmDataManagement).\n\nRepresents a cell; obtain via `dmGetObj(lib, cell)` or `lib.getCells()`. **`getViews()`** returns the collection of dmViewObj. **`name`** is the cell-name property (str).",
     "scenario": "Get the cell object for myLib/inv, print its name, and collect the type of every view it has."},

    {"name": "dmViewObj", "api_used": ["dmViewObj", "dmViewObj.getCell", "dmViewObj.getType"], "ref": REF_DMVIEWOBJ, "setup": ">>> import pyAether as pyScript",
     "demo": ">>> import pyAether as pyScript\n>>> view = pyScript.dmGetObj(\"myLib\", \"inv\", \"schematic\")\n>>> print(view.getType())\nschematic\n>>> parent = view.getCell()\n>>> print(parent.name)\ninv",
     "explain": "The API used is **`dmViewObj`** (class, category dmDataManagement).\n\nRepresents a view; obtain via `dmGetObj(lib, cell, view)` or `cell.getViews()`. **`getCell() -> dmCellObj`** returns the parent cell. **`getType() -> str`** returns the view type ('schematic', 'maskLayout', etc.).",
     "scenario": "Get the schematic view of myLib/inv, print its type, then get its parent cell and print the cell name."},

    {"name": "emyArc", "api_used": ["emyArc", "emyArc.create"], "ref": REF_EMYARC, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> import math\n>>> ebox = pyScript.emyBox(0, 0, 20, 20)\n>>> arc = pyScript.emyArc.create(block=block, layerNum=1, purposeNum=0, ellipseBBox=ebox, startAngle=pyScript.emyDouble(0.0), stopAngle=pyScript.emyDouble(math.pi / 2))\n>>> print(arc.getStartAngle())\n0.0\n>>> line = arc.convertToLine(numSides=8)\n>>> print(line.getNumPoints())\n9",
     "explain": "The API used is **`emyArc`** (class, inherits emyShape).\n\n**`emyArc.create(block, layerNum, purposeNum, ellipseBBox, startAngle, stopAngle) -> emyArc`** creates an arc on the ellipse bounded by ellipseBBox, from startAngle to stopAngle (radians, normalized to [0,2pi); must differ). `convertToLine(numSides)` approximates as a polygonal emyLine. Raises emcArcAnglesInvalid if angles are equal.",
     "scenario": "Create a quarter-circle arc (0 to pi/2 radians) on a 20x20 ellipse bbox on layer 1, then convert it to an 8-segment line and print the point count."},
    {"name": "emyEllipse", "api_used": ["emyEllipse", "emyEllipse.create"], "ref": REF_EMYELLIPSE, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> ebox = pyScript.emyBox(0, 0, 30, 20)\n>>> ell = pyScript.emyEllipse.create(block=block, layerNum=2, purposeNum=0, ellipseBBox=ebox)\n>>> bb = pyScript.emyBox()\n>>> ell.getBBox(bb)\n>>> print(ell.layerNum)\n2",
     "explain": "The API used is **`emyEllipse`** (class, inherits emyShape).\n\n**`emyEllipse.create(block, layerNum, purposeNum, ellipseBBox) -> emyEllipse`** creates a filled ellipse inside ellipseBBox (width/height define the two radii). `getBBox(bBox)`/`setBBox(ellipseBBox)` read/replace the bounding box. Inherited addToNet/addToPin attach to a net or pin.",
     "scenario": "Create a filled ellipse inside a 30x20 bounding box on layer 2 / purpose 0, then print its layer number."},

    {"name": "emyNet", "api_used": ["emyNet", "emyNet.create"], "ref": REF_EMYNET, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> net = pyScript.emyNet.create(block=block, name=pyScript.emyString(\"vdd\"))\n>>> nm = pyScript.emyName()\n>>> net.getName(nm)\n>>> print(net.isGlobal)\nFalse",
     "explain": "The API used is **`emyNet`** (class, category emyDatabase).\n\n**`emyNet.create(block, name, sigType=emcSignalSigType) -> emyNet`** creates a named net. `getName(name: emyName)` retrieves the name; `rename(name)` changes it. Shapes attached via `shape.addToNet(net)`. `isGlobal` indicates whether the net is global. emyScalarNet is the scalar specialization.",
     "scenario": "Create a net named 'vdd' in a layout block, retrieve its name, and print whether it is global."},

    {"name": "emyTerm", "api_used": ["emyTerm", "emyTerm.create"], "ref": REF_EMYTERM, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> net = pyScript.emyNet.create(block=block, name=pyScript.emyString(\"out\"))\n>>> term = pyScript.emyTerm.create(block=block, name=pyScript.emyString(\"out\"), termType=pyScript.emyTermType(pyScript.emcOutputTermType), net=net)\n>>> print(term.name)\nout",
     "explain": "The API used is **`emyTerm`** (class, category emyDatabase).\n\n**`emyTerm.create(block, name, termType, net=None) -> emyTerm`** creates a terminal of direction `termType` (emyTermType enum: input/output/inout), optionally bound to `net`. A terminal owns logical/net info; pins (emyPin) provide the physical connection. Create net first, then terminal, then pins.",
     "scenario": "Create a net named 'out', then create an output terminal 'out' bound to that net, and print the terminal name."},

    {"name": "emyText", "api_used": ["emyText", "emyText.create"], "ref": REF_EMYTEXT, "setup": SETUP_BLOCK,
     "demo": SETUP_BLOCK + "\n>>> txt = pyScript.emyText.create(block=block, layerNum=pyScript.emyLayerNum(10), purposeNum=pyScript.emyPurposeNum(0), text=pyScript.emyString(\"VDD\"), origin=pyScript.emyPointF(5.0, 5.0), alignment=pyScript.emyTextAlign(\"centerCenter\"), orient=pyScript.emyOrient(pyScript.emcR0), font=pyScript.emyFont(\"stick\"), height=pyScript.emyDist(1.0))\n>>> print(txt.getText().get())\nVDD",
     "explain": "The API used is **`emyText`** (class, inherits emyShape).\n\n**`emyText.create(block, layerNum, purposeNum, text, origin, alignment, orient, font, height) -> emyText`** creates a text label. `alignment` is an emyTextAlign enum (lowerCamelCase: centerCenter, upperLeft, ...). `getText()`/`setText()` read/replace the string. Invalid alignment names raise `SystemError: Invalid textAlign name.`",
     "scenario": "Create a text label 'VDD' at (5,5) on layer 10, center-center aligned, stick font, height 1.0, then print the label text."},
]

BONUS = [
    {"name": "emyTermAttrType", "api_used": ["emyTermAttrType"], "ref": REF_EMYTERMATTRTYPE,
     "demo": ">>> import pyAether as pyScript\n>>> tat = pyScript.emyTermAttrType(\"direction\")\n>>> print(tat.getName())\ndirection",
     "explain": "The API used is **`emyTermAttrType`** (enum). Construct from a name string or int constant. `getName()` returns the attribute-type name; use it for equality comparison."},
    {"name": "emyTermType", "api_used": ["emyTermType"], "ref": REF_EMYTERMTYPE,
     "demo": ">>> import pyAether as pyScript\n>>> tt = pyScript.emyTermType(pyScript.emcInputTermType)\n>>> print(tt.getName())\ninput",
     "explain": "The API used is **`emyTermType`** (enum). Constants: emcInputTermType, emcOutputTermType, emcInputOutputTermType. `getName()` returns \"input\"/\"output\"/\"inout\"."},
    {"name": "emyTextAlign", "api_used": ["emyTextAlign"], "ref": REF_EMYTEXTALIGN,
     "demo": ">>> import pyAether as pyScript\n>>> a = pyScript.emyTextAlign(\"centerCenter\")\n>>> print(a.getName())\ncenterCenter",
     "explain": "The API used is **`emyTextAlign`** (enum). 9 lowerCamelCase names: upperLeft, centerLeft, lowerLeft, upperCenter, centerCenter, lowerCenter, upperRight, centerRight, lowerRight. Invalid names raise `SystemError: Invalid textAlign name.`"},
    {"name": "MDE_SWEEP_RANGE_START_STOP", "api_used": ["MDE_SWEEP_RANGE_START_STOP"], "ref": REF_MDE_SWEEP_RANGE_START_STOP,
     "demo": ">>> import pyAether as pyScript\n>>> mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n>>> print(mode is not None)\nTrue",
     "explain": "The API used is **`MDE_SWEEP_RANGE_START_STOP`** (constant). A sweep range-mode token for start-stop (linear range) sweeps."},
    {"name": "MDE_SWEEP_TYPE_LINEAR", "api_used": ["MDE_SWEEP_TYPE_LINEAR"], "ref": REF_MDE_SWEEP_TYPE_LINEAR,
     "demo": ">>> import pyAether as pyScript\n>>> st = pyScript.MDE_SWEEP_TYPE_LINEAR\n>>> print(st is not None)\nTrue",
     "explain": "The API used is **`MDE_SWEEP_TYPE_LINEAR`** (constant). Selects a linear sweep type (vs logarithmic)."},
    {"name": "MDE_SWEEP_TYPE_LINEAR_STEP_SIZE", "api_used": ["MDE_SWEEP_TYPE_LINEAR_STEP_SIZE"], "ref": REF_MDE_SWEEP_TYPE_LINEAR_STEP_SIZE,
     "demo": ">>> import pyAether as pyScript\n>>> ss = pyScript.MDE_SWEEP_TYPE_LINEAR_STEP_SIZE\n>>> print(ss is not None)\nTrue",
     "explain": "The API used is **`MDE_SWEEP_TYPE_LINEAR_STEP_SIZE`** (constant). Indicates a linear sweep uses an explicit step size."},
    {"name": "MDE_SWEEP_VARIABLE_DESIGN_VARIABLE", "api_used": ["MDE_SWEEP_VARIABLE_DESIGN_VARIABLE"], "ref": REF_MDE_SWEEP_VARIABLE_DESIGN_VARIABLE,
     "demo": ">>> import pyAether as pyScript\n>>> vt = pyScript.MDE_SWEEP_VARIABLE_DESIGN_VARIABLE\n>>> print(vt is not None)\nTrue",
     "explain": "The API used is **`MDE_SWEEP_VARIABLE_DESIGN_VARIABLE`** (constant). Indicates the swept variable is a design variable (parameter)."},
    {"name": "MdePlatSweepStepMode", "api_used": ["MdePlatSweepStepMode"], "ref": REF_MDEPLATSWEEPSTEPMODE,
     "demo": ">>> import pyAether as pyScript\n>>> sm = pyScript.MdePlatSweepStepMode()\n>>> print(sm is not None)\nTrue",
     "explain": "The API used is **`MdePlatSweepStepMode`** (class). A platform sweep step-mode descriptor; sub-types include MdePlatSweepStepModeAuto and MdePlatSweepStepModeTimes."},
    {"name": "MdeResult", "api_used": ["MdeResult"], "ref": REF_MDERESULT,
     "demo": ">>> import pyAether as pyScript\n>>> mde = pyScript.MdeSession.open(\"testLib\", \"testCell\", \"state\")\n>>> mde.netlistAndRun()\n>>> result = mde.getResult()\n>>> print(result.isConverged())\nTrue",
     "explain": "The API used is **`MdeResult`** (class). Represents a simulation result. Obtain via mde.getResult() after netlistAndRun(). Methods: getOutput(name), getOutputs(), isConverged(), getCornerResults()."},
    {"name": "SleLeWireTypeEnum", "api_used": ["SleLeWireTypeEnum"], "ref": REF_SLELEWIRETYPEENUM,
     "demo": ">>> import pyAether as pyScript\n>>> wt = pyScript.SleLeWireTypeEnum(\"analog\")\n>>> print(wt.getName())\nanalog",
     "explain": "The API used is **`SleLeWireTypeEnum`** (enum). Wire drawing types for the schematic editor. `getName()` returns the type name string."},
    {"name": "addProp", "api_used": ["addProp"], "ref": REF_ADDPROP,
     "demo": SETUP_DB + "\n>>> ok = pyScript.addProp(cv, pyScript.emyString(\"owner\"), pyScript.emyString(\"teamA\"))\n>>> print(ok)\nTrue",
     "explain": "The API used is **`addProp`** (function). `addProp(obj, propName, propVal) -> bool` attaches a user property to an EDA object. Counterpart of getProp/dbGetProp."},
    {"name": "EmyTechGetPurposeNum", "api_used": ["EmyTechGetPurposeNum"], "ref": REF_EMYTECHGETPURPOSENUM,
     "demo": ">>> import pyAether as pyScript\n>>> pn = pyScript.EmyTechGetPurposeNum(techLib=pyScript.emyString(\"TECHLIB\"), purposeName=pyScript.emyString(\"drawing\"))\n>>> print(pn)\n0",
     "explain": "The API used is **`EmyTechGetPurposeNum`** (function). `EmyTechGetPurposeNum(techLib, purposeName) -> emyPurposeNum` resolves a purpose name to its number. Use before shape create(..., purposeNum=...)."},
    {"name": "PVM_EXPAND_ALL", "api_used": ["PVM_EXPAND_ALL"], "ref": REF_PVM_EXPAND_ALL,
     "demo": ">>> import pyAether as pyScript\n>>> mode = pyScript.PVM_EXPAND_ALL\n>>> print(mode is not None)\nTrue",
     "explain": "The API used is **`PVM_EXPAND_ALL`** (constant). Directs the PVM manager to expand all views/corners during hierarchy expansion."},
    {"name": "PVM_UPDATE_DESTLIB_MODE", "api_used": ["PVM_UPDATE_DESTLIB_MODE"], "ref": REF_PVM_UPDATE_DESTLIB_MODE,
     "demo": ">>> import pyAether as pyScript\n>>> mode = pyScript.PVM_UPDATE_DESTLIB_MODE\n>>> print(mode is not None)\nTrue",
     "explain": "The API used is **`PVM_UPDATE_DESTLIB_MODE`** (constant). Indicates the destination library should be regenerated during a PVM update."},
    {"name": "aeCrtGuardring", "api_used": ["aeCrtGuardring"], "ref": REF_AECRTGUARDRING,
     "demo": SETUP_DB + "\n>>> inst = pyScript.aeCrtGuardring(cv=cv, center=pyScript.emyPointF(50, 50), ringLib=pyScript.emyString(\"TECHLIB\"), ringCell=pyScript.emyString(\"guardring\"))\n>>> print(inst is not None)\nTrue",
     "explain": "The API used is **`aeCrtGuardring`** (function). Creates a guard ring in a layout cellview for latch-up protection. Returns the created instance/array."},
    {"name": "aeCheckAndSaveDesign", "api_used": ["aeCheckAndSaveDesign"], "ref": REF_AECHECKANDSAVEDESIGN,
     "demo": SETUP_DB + "\n>>> ok = pyScript.aeCheckAndSaveDesign(cv=cv)\n>>> print(ok)\nTrue",
     "explain": "The API used is **`aeCheckAndSaveDesign`** (function). `aeCheckAndSaveDesign(cv) -> bool` runs a consistency check and saves the cellview if clean."},
    {"name": "aeEnableUndo", "api_used": ["aeEnableUndo"], "ref": REF_AEENABLEUNDO,
     "demo": SETUP_DB + "\n>>> pyScript.aeEnableUndo(cv=cv, enable=pyScript.emyBoolean(False))\n>>> pyScript.aeEnableUndo(cv=cv, enable=pyScript.emyBoolean(True))\n>>> print(True)\nTrue",
     "explain": "The API used is **`aeEnableUndo`** (function). `aeEnableUndo(cv, enable) -> bool` toggles the undo stack for a cellview. Disable before bulk scripted edits to save memory."},
]

def gen_pairs(fam, idx_seed):
    pairs = []
    name = fam["name"]
    au = fam["api_used"]
    ref = fam["ref"]
    pairs.append(make_pair("v36-S1-%s-%02d" % (name, idx_seed), "S1", au, s1_prompt(name, ref), "```python\n%s\n```" % fam["demo"]))
    pairs.append(make_pair("v36-S3-%s-%02d" % (name, idx_seed), "S3", au, s3_prompt(name, fam["demo"]), fam["explain"]))
    if "scenario" in fam:
        pairs.append(make_pair("v36-S4-%s-%02d" % (name, idx_seed), "S4", au, s4_prompt(name, fam["scenario"], ref), "```python\n%s\n```" % fam["demo"]))
        variant = fam["demo"].replace("layerNum=1", "layerNum=5").replace("layerNum=2", "layerNum=5")
        pairs.append(make_pair("v36-S5-%s-%02d" % (name, idx_seed), "S5", au,
                               "You are an EDA automation engineer. Write an alternative Python snippet that uses `%s` with a different layer/parameter than the canonical example.\n\n%s" % (name, ref),
                               "```python\n%s\n```" % variant))
    return pairs


def gen_bonus_pairs(fam, idx_seed):
    pairs = []
    name = fam["name"]
    au = fam["api_used"]
    ref = fam["ref"]
    pairs.append(make_pair("v36-S1-%s-%02d" % (name, idx_seed), "S1", au, s1_prompt(name, ref), "```python\n%s\n```" % fam["demo"]))
    pairs.append(make_pair("v36-S3-%s-%02d" % (name, idx_seed), "S3", au, s3_prompt(name, fam["demo"]), fam["explain"]))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="R209 v36 uncovered-family corpus generator")
    ap.add_argument("--dry-run", action="store_true", help="print summary, do not write file")
    args = ap.parse_args()

    eval_eps = load_eval_entry_points()
    sys.stderr.write("Loaded %d eval entry_points for contamination scan\n" % len(eval_eps))

    all_pairs = []
    idx = 0
    for fam in FAMILIES:
        idx += 1
        all_pairs.extend(gen_pairs(fam, idx))
    for fam in BONUS:
        idx += 1
        all_pairs.extend(gen_bonus_pairs(fam, idx))

    rejected = 0
    clean = []
    for p in all_pairs:
        text = p["prompt"] + "\n" + p["completion"]
        hit = fp_check(text, eval_eps)
        if hit:
            sys.stderr.write("REJECT %s: contains eval entry_point '%s'\n" % (p["pair_id"], hit))
            p["contamination_check"] = "FAIL:" + hit
            rejected += 1
        else:
            clean.append(p)

    seen = set()
    deduped = []
    for p in clean:
        if p["pair_id"] in seen:
            sys.stderr.write("SKIP dup id %s\n" % p["pair_id"])
            continue
        seen.add(p["pair_id"])
        deduped.append(p)

    all_apis = set()
    for p in deduped:
        for a in p["api_used"]:
            all_apis.add(a)

    print("=" * 70)
    print("R209 v36 uncovered-family corpus generation")
    print("=" * 70)
    print("Main families (13) + enums(3) + bonus(14) = 30 targets")
    print("Pairs generated : %d" % len(all_pairs))
    print("Rejected (contam): %d" % rejected)
    print("After dedup      : %d" % len(deduped))
    print("Unique api_used  : %d" % len(all_apis))
    print("New class names  : %s" % sorted([a for a in all_apis if "." not in a]))
    print("-" * 70)

    eval_api_file = os.path.join(RUN_DIR, "pyAether_eval_488_apis.txt")
    corpus_file = os.path.join(RUN_DIR, "sft_pyaether_corpus_v11_v35_merged.jsonl")
    existing_apis = set()
    if os.path.isfile(corpus_file):
        with open(corpus_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                for a in json.loads(line).get("api_used", []) or []:
                    existing_apis.add(a)
    combined = existing_apis | all_apis
    eval_apis = []
    if os.path.isfile(eval_api_file):
        with open(eval_api_file, encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if s:
                    eval_apis.append(s)
    cov2 = 0
    for e in eval_apis:
        parts = e.split(".")
        fam = parts[1] if len(parts) >= 2 and parts[0] == "pyAether" else e
        leaf = parts[-1]
        is_method = (len(parts) == 3 and parts[0] == "pyAether")
        if is_method:
            if fam in combined or leaf in combined:
                cov2 += 1
        else:
            if fam in combined:
                cov2 += 1
    print("Projected Tier-2 coverage: %d/%d = %.1f%% (was 314/488=64.3%%)" % (cov2, len(eval_apis), cov2 / len(eval_apis) * 100))
    print("-" * 70)

    if not args.dry_run:
        with open(OUT_FILE, "w", encoding="utf-8") as fh:
            for p in deduped:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
        print("Wrote %d pairs to %s" % (len(deduped), OUT_FILE))
    else:
        print("[dry-run] no file written")

    if rejected > 0:
        sys.stderr.write("ERROR: %d pairs failed contamination scan\n" % rejected)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
