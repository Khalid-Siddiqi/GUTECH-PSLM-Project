"""Convert the HIES 2024-25 Stata files into readable CSV files.

Usage (from the repository root):
    python "HIES 2024_2025/stata_to_csv.py"

What it does, for every .dta file in "Stata data/":
  * Replaces coded answers with their text labels (e.g. s1aq03: 1 -> "male").
  * Item-code columns (itc, code, ind_code) keep the number AND get a
    "<column>_label" column with the item name, because analyses filter on the codes.
  * ID columns (prcode, hhno, hhcode, idc, ino) and amounts stay as numbers.
  * Whole numbers stored as decimals are written without ".0"; "NULL" text becomes empty.
  * Adds hhcode (= prcode*1000 + hhno) to files that lack it.
  * Writes "_codebook.csv": every column of every file with its description and codes.

Fixes applied to the original labels (documented in _codebook.csv):
  * province / region use one standard label set everywhere. Sec_04e_decisionmaking.dta
    has region labels reversed (1 = urban) although its values follow 1 = rural, 2 = urban.
  * FIES q1-q8 use the questionnaire's codes: 98 = don't know, 99 = refused
    (the .dta labels say the opposite and q6-q8 had no labels for 98/99).
"""
import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Stata data")
OUT = os.path.join(HERE, "CSV data")

KEEP_CODE = {"itc", "code", "ind_code"}
ID_COLS = {"prcode", "hhno", "hhcode", "idc", "ino"}
PROVINCE = {1: "kp", 2: "punjab", 3: "sindh", 4: "balochistan", 6: "islamabad", 7: "gb", 8: "aj&k"}
REGION = {1: "rural", 2: "urban"}
FIES = {1: "yes", 2: "no", 98: "don't know", 99: "refused"}


def clean(text):
    return str(text).replace("\x85", "...").replace("\x92", "'").strip()


def labels_for(file_name, column, label_name, value_labels):
    """Return ({code: text}, note) for a column."""
    if column == "province":
        return PROVINCE, "standard province labels"
    if column == "region":
        return REGION, "standard region labels"
    if file_name == "sec_05m4_fies" and column in {f"q{i}" for i in range(1, 9)}:
        return FIES, "98/99 codes taken from the questionnaire"
    if label_name in value_labels:
        return {int(k): clean(v) for k, v in value_labels[label_name].items()}, ""
    return {}, ""


def to_int_if_whole(series):
    if series.dtype.kind == "f" and series.notna().any() and (series.dropna() % 1 == 0).all():
        return series.astype("Int64")
    return series


def convert(path, codebook):
    name = os.path.splitext(os.path.basename(path))[0]
    with pd.io.stata.StataReader(path) as reader:
        df = reader.read(convert_categoricals=False)
        descriptions = reader.variable_labels()
        value_labels = reader.value_labels()
        label_name_of = dict(zip(reader._varlist, reader._lbllist))

    out = pd.DataFrame(index=df.index)
    if "hhcode" not in df.columns and {"prcode", "hhno"} <= set(df.columns):
        out["hhcode"] = (df["prcode"].astype("int64") * 1000 + df["hhno"].astype("int64")).astype("Int64")
        codebook.append({"file": name, "column": "hhcode",
                         "description": "household ID = prcode*1000 + hhno (added during conversion)",
                         "value_labels": "", "note": "added"})

    for col in df.columns:
        s = df[col]
        if col == "hhcode":
            s = s.round().astype("Int64")
        elif s.dtype == object:
            s = s.str.strip().replace({"NULL": pd.NA, "": pd.NA})
        else:
            s = to_int_if_whole(s)

        mapping, note = labels_for(name, col, label_name_of.get(col) or "", value_labels)
        if mapping and col not in ID_COLS and s.dtype != object:
            text = s.map(lambda v: mapping.get(int(v), v) if pd.notna(v) and float(v) % 1 == 0 else v)
            if col in KEEP_CODE:
                out[col] = s
                out[col + "_label"] = text
            else:
                out[col] = text
        else:
            out[col] = s

        codebook.append({
            "file": name,
            "column": col,
            "description": clean(descriptions.get(col, "")),
            "value_labels": "; ".join(f"{k} = {v}" for k, v in mapping.items()),
            "note": note,
        })

    csv_path = os.path.join(OUT, name + ".csv")
    out.to_csv(csv_path, index=False, encoding="utf-8-sig")  # BOM so Excel reads UTF-8
    print(f"{name}: {len(out):,} rows x {out.shape[1]} columns, {os.path.getsize(csv_path) / 1e6:.1f} MB", flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    codebook = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.dta")), key=str.lower):
        convert(path, codebook)
    pd.DataFrame(codebook).to_csv(os.path.join(OUT, "_codebook.csv"), index=False, encoding="utf-8-sig")
    print(f"_codebook.csv: {len(codebook)} columns described")


if __name__ == "__main__":
    main()
