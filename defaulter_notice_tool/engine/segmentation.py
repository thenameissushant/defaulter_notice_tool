import numpy as np
import pandas as pd

from . import config


def count_missed_emis(df):
    """
    Use the 'EMIs missed' column if the dump has it. If not, work it out
    from overdue / EMI amount (rounded up, because a part-payment still
    leaves that EMI unpaid).
    """
    if "emis_missed" in df.columns and df["emis_missed"].notna().any():
        return df["emis_missed"].fillna(0).astype(int)

    if "overdue" not in df.columns:
        raise ValueError(
            "Dump has neither an 'EMIs missed' column nor an 'Overdue amount' column, "
            "so I can't tell who has defaulted."
        )

    emi = df["emi_amount"].replace(0, np.nan)
    return np.ceil(df["overdue"].fillna(0) / emi).fillna(0).astype(int)


def segment(df):
    """
    Returns (early_stage, severe_stage, skipped).

    early_stage  - missed 1st or 2nd EMI
    severe_stage - missed 3rd EMI (or more)
    skipped      - rows we couldn't classify, with a reason, so nothing disappears silently
    """
    df = df.copy()
    df["missed"] = count_missed_emis(df)

    bad_emi = df["emi_amount"].isna() | (df["emi_amount"] <= 0)
    skipped = df[bad_emi].copy()
    skipped["reason"] = "EMI amount missing or zero"
    df = df[~bad_emi]

    early = df[(df["missed"] >= 1) & (df["missed"] <= config.EARLY_STAGE_MAX)].copy()
    severe = df[df["missed"] >= config.SEVERE_STAGE_MIN].copy()

    return early, severe, skipped.reset_index(drop=True)


def summary_line(early, severe, skipped):
    total = len(early) + len(severe)
    return (f"{total} defaulters found: {len(early)} in 1st/2nd EMI bucket, "
            f"{len(severe)} in 3rd EMI bucket, {len(skipped)} rows skipped.")
