#!/usr/bin/env python3
"""em_xls_model.py -- dependency-free object model for the LDDB2.0 EM
(Excel) workbook ("EmXlsModel" deliverable).

Reads an .xlsx workbook using only the Python 3 standard library
(zipfile + xml.etree.ElementTree).  Every worksheet becomes a Python class
and every data row becomes a "<SheetName>Row" class whose attributes mirror
the header cells.  No pandas/xlrd/openpyxl is required.

    from em_xls_model import EmXlsModel
    wb = EmXlsModel("LDDB2.0_EM_File.xlsx")
    print(wb.sheet_names)          # -> ['EmTemp', ...]
    for row in wb["EmTemp"]:       # EmTempRow objects
        print(row.as_dict())

Conventions:
* one class per worksheet; the name is normalised to CamelCase (so "EmTemp"
  yields "EmTemp" / "EmTempRow", both registered on this module at parse time).
* the first non-empty row is the header row.
* values keep their native Excel type (int/float/bool/str/None).
* a Row exposes each column by its exact identifier-safe header name and by
  its CamelCase name, plus index/dict access for schema-agnostic code.

Inputs:
* .xlsx (OOXML zip) -- full support via the standard library.
* SpreadsheetML-2003 "XML spreadsheet" (.xls that is really XML) -- supported.
* binary .xls (BIFF) -- needs xlrd; a clear message is raised if unavailable.
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import OrderedDict

__all__ = ["EmXlsModel", "Sheet", "Row", "EmTemp", "EmTempRow",
           "sheet_classes", "row_classes"]

_MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_SS_NS = "urn:schemas-microsoft-com:office:spreadsheet"

sheet_classes = OrderedDict()
row_classes = OrderedDict()


def _tag(local):
    return "{%s}%s" % (_MAIN_NS, local)


def _localname(tag):
    return tag.rsplit("}", 1)[-1]


def _identifier(raw):
    if raw is None:
        return ""
    s = re.sub(r"[^0-9A-Za-z_]+", "_", str(raw).strip())
    if s and s[0].isdigit():
        s = "_" + s
    return s


def _camel(raw):
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    toks = re.split(r"[^0-9A-Za-z]+", s)
    name = "".join((t[0].upper() + t[1:]) for t in toks if t)
    if name and name[0].isdigit():
        name = "_" + name
    return name


def _number(text):
    if text is None:
        return None
    s = str(text).strip()
    if s == "":
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return int(f) if f.is_integer() else f


def _column_index(ref):
    letters = ""
    for ch in (ref or ""):
        if ch.isalpha():
            letters += ch
        else:
            break
    col = 0
    for ch in letters.upper():
        col = col * 26 + (ord(ch) - 64)
    return col - 1


def _inline_text(is_el):
    if is_el is None:
        return None
    return "".join(t.text for t in is_el.iter(_tag("t")) if t.text)


def _shared_strings(path):
    strings = []
    with zipfile.ZipFile(path) as zf:
        cands = [n for n in zf.namelist() if n.endswith("sharedStrings.xml")]
        if not cands:
            return strings
        root = ET.fromstring(zf.read(cands[0]))
        for si in root.findall(_tag("si")):
            strings.append("".join(t.text for t in si.iter(_tag("t")) if t.text))
    return strings


def _findall_local(parent, local):
    return [el for el in parent if _localname(el.tag) == local]


class Row(object):
    """One data row; attributes mirror the worksheet header cells."""

    def __init__(self, headers, values):
        self._headers = list(headers)
        self._values = list(values)
        self._dict = OrderedDict(zip(self._headers, self._values))
        seen = set()
        for h, v in zip(self._headers, self._values):
            ident = _identifier(h)
            if ident and ident not in _ROW_RESERVED and ident not in seen:
                seen.add(ident)
                setattr(self, ident, v)
            camel = _camel(h)
            if camel and camel not in _ROW_RESERVED and camel not in seen:
                seen.add(camel)
                setattr(self, camel, v)

    @property
    def headers(self):
        return list(self._headers)

    @property
    def values(self):
        return list(self._values)

    def get(self, header, default=None):
        key = str(header)
        ident = _identifier(key)
        camel = _camel(key)
        for k, v in zip(self._headers, self._values):
            if _identifier(k) == ident or _camel(k) == camel:
                return v
        return default

    def as_dict(self):
        return OrderedDict(self._dict)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        ident = _identifier(str(key))
        for k, v in self._dict.items():
            if k == key or _identifier(k) == ident:
                return v
        raise KeyError(key)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        body = ", ".join("%s=%r" % (k, v) for k, v in self._dict.items())
        return "%s(%s)" % (type(self).__name__, body)


_ROW_RESERVED = frozenset(dir(Row))


class Sheet(object):
    """Ordered collection of Row objects with shared headers."""

    _row_cls = Row

    def __init__(self, name, headers, rows, row_cls=None):
        self.name = name
        self.headers = list(headers)
        self.rows = list(rows)
        if row_cls is not None:
            self._row_cls = row_cls

    def column(self, header):
        return [r.get(header) for r in self.rows]

    def as_dicts(self):
        return [r.as_dict() for r in self.rows]

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __repr__(self):
        return "%s(name=%r, rows=%d)" % (type(self).__name__, self.name, len(self.rows))


class EmTempRow(Row):
    """Row of the documented EmTemp worksheet (EM temperature model)."""


class EmTemp(Sheet):
    """The documented EmTemp worksheet of the LDDB2.0 EM workbook."""

    _row_cls = EmTempRow


def _build_classes(sheet_name):
    name = _camel(sheet_name) or str(sheet_name)
    row_name = name + "Row"
    sheet_cls = globals().get(name)
    row_cls = globals().get(row_name)
    if not (isinstance(sheet_cls, type) and issubclass(sheet_cls, Sheet)):
        if not (isinstance(row_cls, type) and issubclass(row_cls, Row)):
            row_cls = type(str(row_name), (Row,), {"__module__": __name__})
        sheet_cls = type(str(name), (Sheet,), {"__module__": __name__, "_row_cls": row_cls})
    else:
        row_cls = getattr(sheet_cls, "_row_cls", None)
        if not (isinstance(row_cls, type) and issubclass(row_cls, Row)):
            row_cls = type(str(row_name), (Row,), {"__module__": __name__})
            sheet_cls._row_cls = row_cls
    globals().setdefault(name, sheet_cls)
    globals().setdefault(row_name, row_cls)
    sheet_classes[sheet_name] = sheet_cls
    row_classes[sheet_name] = row_cls
    return sheet_cls, row_cls


class EmXlsModel(object):
    """Schema-agnostic reader/model for the LDDB2.0 EM workbook."""

    def __init__(self, path, header_row=1, skip_empty_rows=True):
        self.path = os.path.abspath(str(path))
        self.header_row = header_row
        self.skip_empty_rows = skip_empty_rows
        self.sheets = OrderedDict()
        self._parse()
        self._bind()

    @property
    def sheet_names(self):
        return list(self.sheets.keys())

    @property
    def sheet_list(self):
        return list(self.sheets.values())

    def sheet(self, key):
        if isinstance(key, int):
            return self.sheet_list[key]
        return self.sheets[str(key)]

    def __getitem__(self, key):
        return self.sheet(key)

    def __getattr__(self, name):
        sheets = self.__dict__.get("sheets")
        if sheets and name in sheets:
            return sheets[name]
        if sheets:
            for k, v in sheets.items():
                if _camel(k) == name:
                    return v
        raise AttributeError(name)

    def __len__(self):
        return len(self.sheets)

    def __iter__(self):
        return iter(self.sheet_list)

    def to_dict(self):
        return OrderedDict((k, v.as_dicts()) for k, v in self.sheets.items())

    def _bind(self):
        for sh in self.sheet_list:
            nm = _camel(sh.name)
            if nm and nm not in self.__dict__:
                self.__dict__[nm] = sh

    def _parse(self):
        with open(self.path, "rb") as fh:
            head = fh.read(8)
        if head[:2] == b"PK":
            self._parse_xlsx()
        elif head.lstrip()[:5] in (b"<?xml", b"<Work", b"<work"):
            self._parse_xml_spreadsheet()
        elif head[:8] == bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]):
            self._parse_biff()
        else:
            raise ValueError("Unrecognised Excel file format: %s" % self.path)

    def _parse_biff(self):
        try:
            import xlrd
        except ImportError:
            raise ImportError(
                "Legacy binary .xls (BIFF) needs the xlrd package, which is "
                "unavailable. Re-save as .xlsx and open it with EmXlsModel.")

    def _parse_xlsx(self):
        shared = _shared_strings(self.path)
        with zipfile.ZipFile(self.path) as zf:
            names = set(zf.namelist())
            wb_rel = next((n for n in names if n.endswith("workbook.xml")), None)
            if wb_rel is None:
                raise ValueError("workbook.xml not found in %s" % self.path)
            rel_path = (os.path.dirname(wb_rel) + "/_rels/" +
                        os.path.basename(wb_rel) + ".rels").strip("/")
            id_to_target = {}
            try:
                rels = ET.fromstring(zf.read(rel_path))
                for rel in rels.findall("{%s}Relationship" % _PKG_REL_NS):
                    rid, tgt = rel.get("Id"), rel.get("Target")
                    if rid and tgt:
                        id_to_target[rid] = tgt
            except KeyError:
                pass
            wb_root = ET.fromstring(zf.read(wb_rel))
            base = os.path.dirname(wb_rel)
            for s in wb_root.iter(_tag("sheet")):
                name = s.get("name")
                rid = s.get("{%s}id" % _DOC_REL_NS)
                target = id_to_target.get(rid)
                if not name or not target:
                    continue
                path_in_zip = self._resolve_target(names, base, target)
                if path_in_zip is None:
                    continue
                grid = self._parse_sheet_zip(zf, path_in_zip, shared)
                self._add_sheet(name, grid)

    @staticmethod
    def _resolve_target(names, base, target):
        base = base.strip("/")
        cands = [target.lstrip("/")]
        if base:
            cands.append(base + "/" + target.lstrip("/"))
        for c in cands:
            for x in (os.path.normpath(c).replace(os.sep, "/"), c):
                if x in names:
                    return x
        tail = os.path.basename(target)
        for n in names:
            if n.endswith("/" + tail) or n == tail:
                return n
        return None

    def _parse_sheet_zip(self, zf, path_in_zip, shared):
        root = ET.fromstring(zf.read(path_in_zip))
        grid = {}
        for row in root.iter(_tag("row")):
            if not row.get("r"):
                continue
            ri = int(row.get("r")) - 1
            for c in row.iter(_tag("c")):
                ci = _column_index(c.get("r"))
                t = c.get("t")
                v_el = c.find(_tag("v"))
                v = v_el.text if v_el is not None else None
                value = self._cell_value(c, t, v, shared)
                if value is not None:
                    grid[(ri, ci)] = value
        return grid

    @staticmethod
    def _cell_value(c, t, v, shared):
        if t == "s":
            try:
                idx = int(v)
                return shared[idx] if 0 <= idx < len(shared) else v
            except (TypeError, ValueError):
                return v
        if t == "inlineStr":
            return _inline_text(c.find(_tag("is")))
        if t == "b":
            return v in ("1", "true", "True", "TRUE") if v is not None else False
        if t == "n":
            return _number(v)
        if t in ("str", "e"):
            return v
        if t == "d":
            return v
        is_el = c.find(_tag("is"))
        if is_el is not None:
            return _inline_text(is_el)
        return _number(v)


def _parse_xml_spreadsheet(self):
        root = ET.parse(self.path).getroot()
        for ws in root.iter():
            if _localname(ws.tag) != "Worksheet":
                continue
            name = next((v for k, v in ws.attrib.items() if _localname(k) == "Name"), "Sheet")
            table = next((el for el in ws if _localname(el.tag) == "Table"), None)
            grid = {}
            if table is not None:
                for ri, row_el in enumerate(table):
                    if _localname(row_el.tag) != "Row":
                        continue
                    ci = 0
                    for cell in row_el:
                        if _localname(cell.tag) != "Cell":
                            continue
                        idx = cell.get("{%s}Index" % _SS_NS) or cell.get("Index")
                        if idx:
                            ci = int(idx) - 1
                        data = next((d for d in cell if _localname(d.tag) == "Data"), None)
                        if data is None:
                            ci += 1
                            continue
                        txt = "".join(data.itertext())
                        ttype = data.get("{%s}Type" % _SS_NS) or data.get("Type")
                        value = _number(txt) if ttype == "Number" else txt
                        if value is not None and value != "":
                            grid[(ri, ci)] = value
                        ci += 1
            self._add_sheet(name, grid)

    def _add_sheet(self, name, grid):
        if not grid:
            self._make(name, [], [])
            return
        rows_idx = sorted(set(r for r, c in grid))
        cols_idx = sorted(set(c for r, c in grid))
        min_c, max_c = cols_idx[0], cols_idx[-1]
        hdr = self.header_row
        if not hdr:
            hdr_idx = rows_idx[0]
        else:
            later = [r for r in rows_idx if r >= hdr - 1]
            hdr_idx = later[0] if later else rows_idx[0]
        headers = [grid.get((hdr_idx, c)) for c in range(min_c, max_c + 1)]
        while headers and headers[-1] is None:
            headers.pop()
            max_c -= 1
        rows_data = []
        for r in rows_idx:
            if r <= hdr_idx:
                continue
            vals = [grid.get((r, c)) for c in range(min_c, max_c + 1)]
            if self.skip_empty_rows and all(v is None for v in vals):
                continue
            rows_data.append(vals)
        self._make(name, headers, rows_data)

    def _make(self, name, headers, rows_data):
        sheet_cls, row_cls = _build_classes(name)
        row_objs = [row_cls(headers, rd) for rd in rows_data]
        self.sheets[name] = sheet_cls(name, headers, row_objs, row_cls=row_cls)


def main(argv=None):
    import sys as _sys
    argv = _sys.argv[1:] if argv is None else argv
    if not argv:
        _sys.stderr.write("usage: python em_xls_model.py <workbook.xlsx> [sheet]\n")
        return 2
    wb = EmXlsModel(argv[0])
    print("sheets: %s" % wb.sheet_names)
    for name in wb.sheet_names:
        sh = wb[name]
        print("  %s -> %d rows; headers=%r" % (type(sh).__name__, len(sh), sh.headers))
    if len(argv) > 1:
        for r in wb[argv[1]]:
            print(r.as_dict())
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())