import os
from datetime import datetime

import pandas as pd

from .loader import load_dump
from .segmentation import segment, summary_line
from .notice import build_notice

SHOW_COLS = ["loan_no", "name", "mobile", "emi_amount", "missed", "overdue", "outstanding"]


def run(excel_path, out_root, progress=None, log=None):
    """
    Whole job in one call: read dump -> split into buckets -> write notices
    -> save a summary workbook. `progress` and `log` are optional callbacks
    so the UI can show what is happening without the engine knowing about it.
    """
    progress = progress or (lambda done, total: None)
    log = log or print

    log("Reading the dump...")
    df = load_dump(excel_path)
    log(f"{len(df)} rows loaded.")

    early, severe, skipped = segment(df)
    log(summary_line(early, severe, skipped))

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(out_root, f"run_{stamp}")
    total = len(early) + len(severe)
    done = 0
    failed = []

    for stage, frame, folder in (("early", early, "1st_2nd_EMI"), ("severe", severe, "3rd_EMI")):
        target = os.path.join(run_dir, "notices", folder)
        for _, row in frame.iterrows():
            try:
                build_notice(row, stage, target)
            except Exception as e:  # one bad record should not kill the whole batch
                failed.append((row["loan_no"], str(e)))
            done += 1
            if done % 25 == 0 or done == total:
                progress(done, total)

    summary_path = os.path.join(run_dir, "defaulter_summary.xlsx")
    os.makedirs(run_dir, exist_ok=True)
    with pd.ExcelWriter(summary_path, engine="openpyxl") as xl:
        pd.DataFrame({
            "Bucket": ["1st/2nd EMI missed", "3rd EMI missed", "Skipped rows", "Notices failed"],
            "Count": [len(early), len(severe), len(skipped), len(failed)],
        }).to_excel(xl, sheet_name="Overview", index=False)
        early[[c for c in SHOW_COLS if c in early.columns]].to_excel(xl, sheet_name="1st_2nd_EMI", index=False)
        severe[[c for c in SHOW_COLS if c in severe.columns]].to_excel(xl, sheet_name="3rd_EMI", index=False)
        if len(skipped):
            skipped[[c for c in ["loan_no", "name", "reason"] if c in skipped.columns]].to_excel(
                xl, sheet_name="Skipped", index=False)

    if failed:
        log(f"{len(failed)} notices failed, e.g. {failed[0][0]}: {failed[0][1]}")
    log(f"Done. Output saved in: {run_dir}")

    return {"run_dir": run_dir, "early": len(early), "severe": len(severe),
            "skipped": len(skipped), "failed": len(failed)}
