import pandas as pd
import numpy as np


class EcommercePipeline:
    """
    Scalable data processing pipeline for e-commerce transactional data.
    Handles cleaning, transformation, structuring, and SQL-style aggregations.
    """

    def __init__(self, df: pd.DataFrame = None):
        self.raw_df = df
        self.clean_df = None

    # ──────────────────────────────────────────────
    # STEP 1 — Clean & Validate
    # ──────────────────────────────────────────────
    def clean(self) -> "EcommercePipeline":
        df = self.raw_df.copy()

        # Parse dates
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Drop rows with null critical fields
        df.dropna(subset=["order_id", "date", "category", "product", "revenue"], inplace=True)

        # Remove duplicates
        df.drop_duplicates(subset="order_id", keep="first", inplace=True)

        # Remove negative revenue / price
        df = df[(df["unit_price"] > 0) & (df["revenue"] > 0) & (df["quantity"] > 0)]

        # Clip outlier quantities
        df["quantity"] = df["quantity"].clip(upper=100)

        # Standardise string columns
        for col in ["category", "region", "product"]:
            df[col] = df[col].str.strip().str.title()

        # Re-derive time columns
        df["year"]       = df["date"].dt.year
        df["month"]      = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%b %Y")
        df["quarter"]    = df["date"].dt.quarter
        df["week"]       = df["date"].dt.isocalendar().week.astype(int)
        df["day_of_week"]= df["date"].dt.day_name()

        self.clean_df = df.reset_index(drop=True)
        return self

    # ──────────────────────────────────────────────
    # STEP 2 — SQL-style Aggregations
    # ──────────────────────────────────────────────
    def monthly_revenue(self) -> pd.DataFrame:
        """Revenue and order count aggregated by month."""
        df = self.clean_df
        return (
            df.groupby(["year", "month", "month_name"])
            .agg(
                total_revenue=("revenue_net", "sum"),
                total_orders=("order_id", "count"),
                avg_order_value=("revenue_net", "mean"),
                units_sold=("quantity", "sum"),
            )
            .reset_index()
            .sort_values(["year", "month"])
            .assign(
                revenue_growth=lambda x: x["total_revenue"].pct_change() * 100,
                cumulative_revenue=lambda x: x["total_revenue"].cumsum(),
            )
        )

    def category_performance(self) -> pd.DataFrame:
        """Revenue, margin, returns by product category."""
        df = self.clean_df
        return (
            df.groupby("category")
            .agg(
                total_revenue=("revenue_net", "sum"),
                total_orders=("order_id", "count"),
                units_sold=("quantity", "sum"),
                avg_unit_price=("unit_price", "mean"),
                avg_discount=("discount_pct", "mean"),
                return_count=("return_flag", "sum"),
            )
            .reset_index()
            .assign(
                return_rate=lambda x: (x["return_count"] / x["total_orders"] * 100).round(2),
                revenue_share=lambda x: (x["total_revenue"] / x["total_revenue"].sum() * 100).round(2),
            )
            .sort_values("total_revenue", ascending=False)
        )

    def top_products(self, n: int = 10) -> pd.DataFrame:
        """Top N products by net revenue."""
        df = self.clean_df
        return (
            df.groupby(["category", "product"])
            .agg(
                total_revenue=("revenue_net", "sum"),
                total_orders=("order_id", "count"),
                units_sold=("quantity", "sum"),
                avg_price=("unit_price", "mean"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )

    def regional_breakdown(self) -> pd.DataFrame:
        """Revenue and orders by region."""
        df = self.clean_df
        return (
            df.groupby("region")
            .agg(
                total_revenue=("revenue_net", "sum"),
                total_orders=("order_id", "count"),
                avg_order_value=("revenue_net", "mean"),
            )
            .reset_index()
            .assign(revenue_share=lambda x: (x["total_revenue"] / x["total_revenue"].sum() * 100).round(2))
            .sort_values("total_revenue", ascending=False)
        )

    def quarterly_trend(self) -> pd.DataFrame:
        df = self.clean_df
        return (
            df.groupby(["year", "quarter"])
            .agg(
                total_revenue=("revenue_net", "sum"),
                total_orders=("order_id", "count"),
            )
            .reset_index()
            .assign(label=lambda x: "Q" + x["quarter"].astype(str) + " " + x["year"].astype(str))
        )

    def run_all(self) -> dict:
        """Run full pipeline and return all report tables."""
        self.clean()
        return {
            "monthly_revenue":     self.monthly_revenue(),
            "category_performance": self.category_performance(),
            "top_products":        self.top_products(),
            "regional_breakdown":  self.regional_breakdown(),
            "quarterly_trend":     self.quarterly_trend(),
            "clean_data":          self.clean_df,
        }


if __name__ == "__main__":
    from data_generator import generate_dataset
    raw = generate_dataset()
    reports = EcommercePipeline(raw).run_all()
    for name, df in reports.items():
        if name != "clean_data":
            print(f"\n{'='*50}")
            print(f" {name.upper()}")
            print(df.to_string(index=False))
