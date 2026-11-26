# EmXlsModel -- LDDB2.0 EM Excel workbook reader/model

Deliverable for `EDA-Eval-DesignFlow-EmXlsModel-001`.

## What it does

`em_xls_model.py` parses the electromigration (EM) model/rules workbook
`LDDB2.0_EM_File.xls/.xlsx` using only the Python 3 standard library
(`zipfile` + `xml.etree.ElementTree`).  It turns every worksheet into a Python
class and every data row into a `<SheetName>Row` class whose attributes mirror
the worksheet header cells.

## Why no pandas / xlrd / openpyxl

The EDA runtime has no third-party Excel parser installed, so the model is
implemented on the standard library only.  It reads OOXML `.xlsx` directly and
also tolerates SpreadsheetML-2003 XML spreadsheets.  For legacy binary `.xls`
(BIFF) it raises a clear message asking to re-save as `.xlsx` (or, if `xlrd`
happens to be installed, it uses it automatically).

## Usage

    from em_xls_model import EmXlsModel

    wb = EmXlsModel("LDDB2.0_EM_File.xlsx")
    print(wb.sheet_names)          # ['EmTemp', ...]

    s = wb["EmTemp"]               # or wb.EmTemp, or wb.sheet(0)
    for row in s:                  # EmTempRow (subclass of Row)
        print(row.as_dict())

## Model / classes

* `EmXlsModel` -- the workbook reader/model.
* `Sheet` -- base class for one worksheet; subclasses are generated per sheet
  (e.g. `EmTemp`, `EmRule`, ...) and registered on the module at parse time.
* `Row` -- base class for one data row; `EmTempRow` is the documented example.
* `sheet_classes` / `row_classes` -- OrderedDict registries mapping the actual
  sheet name to its generated class.

Each `Row`:

* exposes header columns as attributes (CamelCase and exact identifier-safe
  names),
* supports `row[col]`, `row[header]`, `row.get(header)`, `row.as_dict()`,
* keeps values in native type (int/float/bool/str/None).

Each `Sheet`:

* iterable (`for row in sheet`), indexable (`sheet[i]`),
* exposes `.headers`, `.rows`, `.column(name)`, `.as_dicts()`.

## Files

* `em_xls_model.py`  -- the module (self-contained).
* `README.md`        -- this file.
* `submit.zip`       -- archive of the two files above.

## Packaging

To produce `submit.zip` (archive of the two files above):

    cd outputs && zip -j submit.zip em_xls_model.py README.md

## Running the demo

    python em_xls_model.py LDDB2.0_EM_File.xlsx EmTemp