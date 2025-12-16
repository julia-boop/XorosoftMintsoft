import sys
import os
from datetime import datetime, timedelta
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.xorosoft_product_client import XoroSoftProductClient


def main():
    xoro = XoroSoftProductClient()

    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------
    start_cursor = datetime(2025, 12, 15, 23, 59, 59)
    cutoff_date = datetime(2024, 2, 3, 0, 0, 0)
    window = timedelta(hours=12)

    fmt = "%m/%d/%Y %I:%M:%S %p"

    all_items = []

    cursor_max = start_cursor

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------
    while cursor_max > cutoff_date:

        cursor_min = cursor_max - window

        updated_at_max = cursor_max.strftime(fmt)
        updated_at_min = cursor_min.strftime(fmt)

        print("\n=== FETCH WINDOW ===")
        print(f"updated_at_min: {updated_at_min}")
        print(f"updated_at_max: {updated_at_max}")

        items = xoro.get_all_items(
            updated_at_min=updated_at_min,
            updated_at_max=updated_at_max
        )

        print(f"Items fetched: {len(items)}")

        if items:
            all_items.extend(items)

        cursor_max = cursor_min

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------
    if not all_items:
        print("\nNo items fetched at all.")
        return

    print(f"\nTotal items collected: {len(all_items)}")

    df = pd.json_normalize(all_items)

    # OPTIONAL: Deduplicate by Item ID if present
    if "Id" in df.columns:
        df = df.drop_duplicates(subset=["Id"])

    output_dir = os.path.join(ROOT, "exports")
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "xorosoft_items_full.csv")
    xlsx_path = os.path.join(output_dir, "xorosoft_items_full.xlsx")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    print(f"\nSaved CSV  → {csv_path}")
    print(f"Saved XLSX → {xlsx_path}")


if __name__ == "__main__":
    main()
