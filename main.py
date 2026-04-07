"""
E-Commerce Sales Data Analytics Dashboard
==========================================
Main entry point. Runs the full pipeline:
  1. Generate synthetic transactional data
  2. Clean & transform via EcommercePipeline
  3. Build analytics dashboard (PNG)
  4. Export report CSVs to output/
"""

import os
import pandas as pd
from data_generator import generate_dataset
from pipeline import EcommercePipeline
from dashboard import build_dashboard


def export_reports(reports: dict, out_dir: str = "output/reports"):
    os.makedirs(out_dir, exist_ok=True)
    skip = {"clean_data"}
    for name, df in reports.items():
        if name not in skip:
            path = os.path.join(out_dir, f"{name}.csv")
            df.to_csv(path, index=False)
            print(f"  Exported: {path}")


def print_summary(reports: dict):
    df  = reports["clean_data"]
    mon = reports["monthly_revenue"]

    total_rev  = df["revenue_net"].sum()
    best_month = mon.loc[mon["total_revenue"].idxmax(), "month_name"]
    best_cat   = reports["category_performance"].iloc[0]["category"]
    best_prod  = reports["top_products"].iloc[0]["product"]

    print("\n" + "="*55)
    print("  E-COMMERCE ANALYTICS — PIPELINE SUMMARY")
    print("="*55)
    print(f"  Records processed   : {len(df):,}")
    print(f"  Date range          : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"  Total Net Revenue   : ₹{total_rev:,.2f}")
    print(f"  Average Order Value : ₹{df['revenue_net'].mean():,.2f}")
    print(f"  Total Units Sold    : {df['quantity'].sum():,}")
    print(f"  Return Rate         : {df['return_flag'].mean()*100:.2f}%")
    print(f"  Best Month          : {best_month}")
    print(f"  Top Category        : {best_cat}")
    print(f"  Top Product         : {best_prod}")
    print("="*55)


def main():
    print("[1/4] Generating synthetic e-commerce data...")
    raw_df = generate_dataset(n_rows=5000)

    print("[2/4] Running data pipeline (clean → transform → aggregate)...")
    pipeline = EcommercePipeline(raw_df)
    reports  = pipeline.run_all()

    print("[3/4] Exporting report CSVs...")
    export_reports(reports)

    print("[4/4] Building analytics dashboard...")
    build_dashboard(reports, output_path="output/dashboard.png")

    print_summary(reports)
    print("\nDone! Open output/dashboard.png to view the dashboard.\n")


if __name__ == "__main__":
    main()
