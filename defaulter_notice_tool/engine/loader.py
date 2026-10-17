import re
import pandas as pd

from . import config


class DumpError(Exception):
    """Raised when the Excel dump is not something we can work with."""


def _clean(header):
    # "Loan  Account No." -> "loan account no"
    return re.sub(r"[^a-z0-9 _]", "", str(header).lower()).strip()


def _map_columns(df):
    cleaned = {col: _clean(col) for col in df.columns}
    mapping = {}
    for internal, aliases in config.COLUMN_ALIASES.items():
        for original, c in cleaned.items():
            if c in aliases:
                mapping[original] = internal
                break
    return mapping


def load_dump(path, sheet=0):
    """Read the Excel dump and return a dataframe with our standard column names."""
    try:
        raw = pd.read_excel(path, sheet_name=sheet, dtype={"Mobile": str})
    except FileNotFoundError:
        raise DumpError(f"Could not find the file:\n{path}")
    except Exception as e:
        raise DumpError(f"Excel file could not be read ({e})")

    if raw.empty:
        raise DumpError("The sheet is empty.")

    mapping = _map_columns(raw)
    df = raw.rename(columns=mapping)

    missing = [c for c in config.REQUIRED if c not in df.columns]
    if missing:
        raise DumpError(
            "These columns were not found in the dump: " + ", ".join(missing)
            + "\n\nCheck COLUMN_ALIASES in engine/config.py if your header is named differently."
        )

    # drop fully blank rows and rows with no loan number (usually total rows at the bottom)
    df = df.dropna(how="all")
    df = df[df["loan_no"].notna()].copy()
    df["loan_no"] = df["loan_no"].astype(str).str.strip()

    for col in ("emi_amount", "overdue", "outstanding", "emis_missed"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)
