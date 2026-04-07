import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Global theme ──────────────────────────────────────────────────────────────
BG       = "#0F1117"
PANEL    = "#1A1D27"
ACCENT   = "#4F8EF7"
GREEN    = "#2ECC71"
ORANGE   = "#F39C12"
RED      = "#E74C3C"
PURPLE   = "#9B59B6"
TEAL     = "#1ABC9C"
TEXT     = "#E8E8F0"
SUBTEXT  = "#8888AA"
PALETTE  = [ACCENT, GREEN, ORANGE, PURPLE, TEAL, RED, "#F1C40F"]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    PANEL,
    "axes.edgecolor":    "#2A2D3A",
    "axes.labelcolor":   TEXT,
    "axes.titlecolor":   TEXT,
    "xtick.color":       SUBTEXT,
    "ytick.color":       SUBTEXT,
    "text.color":        TEXT,
    "grid.color":        "#2A2D3A",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "legend.facecolor":  PANEL,
    "legend.edgecolor":  "#2A2D3A",
    "font.family":       "DejaVu Sans",
    "font.size":         10,
})


def fmt_inr(x, pos=None):
    """Format numbers as ₹ with K/L/Cr suffixes."""
    if x >= 1e7:
        return f"₹{x/1e7:.1f}Cr"
    if x >= 1e5:
        return f"₹{x/1e5:.1f}L"
    if x >= 1e3:
        return f"₹{x/1e3:.0f}K"
    return f"₹{x:.0f}"


def _ax_spine_off(ax):
    for sp in ax.spines.values():
        sp.set_visible(False)


# ── Individual charts ─────────────────────────────────────────────────────────

def plot_revenue_trend(ax, monthly: pd.DataFrame):
    x = range(len(monthly))
    rev = monthly["total_revenue"].values

    ax.fill_between(x, rev, alpha=0.15, color=ACCENT)
    ax.plot(x, rev, color=ACCENT, linewidth=2.5, zorder=3)

    # growth annotations on select months
    for i, (r, g) in enumerate(zip(rev, monthly["revenue_growth"].fillna(0))):
        if i % 4 == 0:
            color = GREEN if g >= 0 else RED
            ax.annotate(f"{g:+.1f}%", (i, r), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=7, color=color, fontweight="bold")

    tick_step = max(1, len(monthly) // 8)
    ax.set_xticks(list(x)[::tick_step])
    ax.set_xticklabels(monthly["month_name"].iloc[::tick_step], rotation=30, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_title("Monthly Revenue Trend", fontweight="bold", fontsize=12, pad=10)
    ax.set_ylabel("Net Revenue")
    ax.grid(axis="y", alpha=0.4)
    _ax_spine_off(ax)


def plot_cumulative_revenue(ax, monthly: pd.DataFrame):
    x = range(len(monthly))
    cum = monthly["cumulative_revenue"].values
    ax.fill_between(x, cum, alpha=0.2, color=GREEN)
    ax.plot(x, cum, color=GREEN, linewidth=2.5)

    tick_step = max(1, len(monthly) // 8)
    ax.set_xticks(list(x)[::tick_step])
    ax.set_xticklabels(monthly["month_name"].iloc[::tick_step], rotation=30, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_title("Cumulative Revenue", fontweight="bold", fontsize=12, pad=10)
    ax.set_ylabel("Cumulative Net Revenue")
    ax.grid(axis="y", alpha=0.4)
    _ax_spine_off(ax)


def plot_category_revenue(ax, cat: pd.DataFrame):
    bars = ax.barh(cat["category"], cat["total_revenue"], color=PALETTE[:len(cat)],
                   edgecolor="none", height=0.6)
    for bar, val, share in zip(bars, cat["total_revenue"], cat["revenue_share"]):
        ax.text(bar.get_width() + bar.get_width() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{fmt_inr(val)}  ({share:.1f}%)", va="center", fontsize=8, color=TEXT)
    ax.set_xlim(0, cat["total_revenue"].max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_title("Revenue by Category", fontweight="bold", fontsize=12, pad=10)
    ax.set_xlabel("Net Revenue")
    ax.grid(axis="x", alpha=0.3)
    _ax_spine_off(ax)


def plot_top_products(ax, prod: pd.DataFrame):
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(prod))]
    bars = ax.barh(prod["product"], prod["total_revenue"], color=colors, edgecolor="none", height=0.6)
    for bar, val in zip(bars, prod["total_revenue"]):
        ax.text(bar.get_width() + bar.get_width() * 0.01, bar.get_y() + bar.get_height() / 2,
                fmt_inr(val), va="center", fontsize=8, color=TEXT)
    ax.set_xlim(0, prod["total_revenue"].max() * 1.18)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_title("Top 10 Products by Revenue", fontweight="bold", fontsize=12, pad=10)
    ax.set_xlabel("Net Revenue")
    ax.grid(axis="x", alpha=0.3)
    _ax_spine_off(ax)


def plot_category_orders(ax, cat: pd.DataFrame):
    wedges, texts, autotexts = ax.pie(
        cat["total_orders"],
        labels=cat["category"],
        autopct="%1.1f%%",
        colors=PALETTE[:len(cat)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=2),
        pctdistance=0.75,
    )
    for t in texts:
        t.set_fontsize(8)
        t.set_color(TEXT)
    for at in autotexts:
        at.set_fontsize(7)
        at.set_color(BG)
        at.set_fontweight("bold")
    ax.set_title("Order Share by Category", fontweight="bold", fontsize=12, pad=10)


def plot_return_rate(ax, cat: pd.DataFrame):
    bar_colors = [RED if r > 10 else ORANGE if r > 7 else GREEN for r in cat["return_rate"]]
    bars = ax.bar(cat["category"], cat["return_rate"], color=bar_colors, edgecolor="none", width=0.55)
    for bar, val in zip(bars, cat["return_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.1f}%", ha="center", fontsize=8, color=TEXT, fontweight="bold")
    ax.axhline(cat["return_rate"].mean(), color=ORANGE, linewidth=1.5, linestyle="--", label="Avg")
    ax.set_ylim(0, cat["return_rate"].max() * 1.3)
    ax.set_ylabel("Return Rate (%)")
    ax.set_title("Return Rate by Category", fontweight="bold", fontsize=12, pad=10)
    ax.set_xticklabels(cat["category"], rotation=20, ha="right", fontsize=8)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    _ax_spine_off(ax)


def plot_quarterly(ax, quarterly: pd.DataFrame):
    x = range(len(quarterly))
    bars = ax.bar(x, quarterly["total_revenue"], color=PALETTE[:len(quarterly)],
                  edgecolor="none", width=0.6)
    for bar, val in zip(bars, quarterly["total_revenue"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_height() * 0.01,
                fmt_inr(val), ha="center", fontsize=8, color=TEXT, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(quarterly["label"], rotation=20, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
    ax.set_title("Quarterly Revenue Breakdown", fontweight="bold", fontsize=12, pad=10)
    ax.set_ylabel("Net Revenue")
    ax.grid(axis="y", alpha=0.3)
    _ax_spine_off(ax)


# ── KPI summary bar ───────────────────────────────────────────────────────────

def draw_kpi_bar(fig, reports: dict):
    df   = reports["clean_data"]
    mon  = reports["monthly_revenue"]

    kpis = [
        ("Total Revenue",    fmt_inr(df["revenue_net"].sum()),       ACCENT),
        ("Total Orders",     f"{len(df):,}",                          GREEN),
        ("Avg Order Value",  fmt_inr(df["revenue_net"].mean()),       ORANGE),
        ("Best Month",       mon.loc[mon['total_revenue'].idxmax(), 'month_name'], PURPLE),
        ("Total Units Sold", f"{df['quantity'].sum():,}",             TEAL),
        ("Avg Return Rate",  f"{(df['return_flag'].mean()*100):.1f}%", RED),
    ]

    n = len(kpis)
    for i, (label, value, color) in enumerate(kpis):
        x0 = i / n
        ax = fig.add_axes([x0 + 0.005, 0.93, 1 / n - 0.010, 0.065])
        ax.set_facecolor(PANEL)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.02, 0.05), 0.96, 0.90,
            boxstyle="round,pad=0.02",
            facecolor=PANEL, edgecolor=color, linewidth=1.5,
        ))
        ax.text(0.5, 0.68, value, ha="center", va="center",
                fontsize=13, fontweight="bold", color=color)
        ax.text(0.5, 0.25, label, ha="center", va="center",
                fontsize=8, color=SUBTEXT)


# ── Main build function ───────────────────────────────────────────────────────

def build_dashboard(reports: dict, output_path: str = "output/dashboard.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig = plt.figure(figsize=(22, 17), facecolor=BG)
    fig.suptitle(
        "E-Commerce Sales Analytics Dashboard",
        y=0.98, fontsize=22, fontweight="bold", color=TEXT, va="top"
    )

    draw_kpi_bar(fig, reports)

    gs = fig.add_gridspec(3, 3, left=0.05, right=0.97,
                          top=0.91, bottom=0.04,
                          hspace=0.45, wspace=0.32)

    axes = {
        "trend":    fig.add_subplot(gs[0, :2]),
        "cumul":    fig.add_subplot(gs[0, 2]),
        "cat_rev":  fig.add_subplot(gs[1, :2]),
        "cat_ord":  fig.add_subplot(gs[1, 2]),
        "top_prod": fig.add_subplot(gs[2, :2]),
        "ret_rate": fig.add_subplot(gs[2, 2]),
    }

    plot_revenue_trend(axes["trend"],    reports["monthly_revenue"])
    plot_cumulative_revenue(axes["cumul"], reports["monthly_revenue"])
    plot_category_revenue(axes["cat_rev"], reports["category_performance"])
    plot_category_orders(axes["cat_ord"],  reports["category_performance"])
    plot_top_products(axes["top_prod"],    reports["top_products"])
    plot_return_rate(axes["ret_rate"],     reports["category_performance"])

    fig.text(0.97, 0.01, "E-Commerce Analytics Dashboard | Built with Python & Pandas",
             ha="right", fontsize=7, color=SUBTEXT, style="italic")

    plt.savefig(output_path, dpi=160, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"Dashboard saved → {output_path}")


if __name__ == "__main__":
    from data_generator import generate_dataset
    from pipeline import EcommercePipeline
    raw = generate_dataset()
    reports = EcommercePipeline(raw).run_all()
    build_dashboard(reports)
