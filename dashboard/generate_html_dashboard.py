# /home/pingh/Brazilian-E-Commerce-Public-Dataset-by-Olist/dashboard/generate_html_dashboard.py

import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. Paths & data loading
# ------------------------------------------------------------------------------

BASE_DIR = Path("/home/pingh/Brazilian-E-Commerce-Public-Dataset-by-Olist")
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_PATH = DASHBOARD_DIR / "fact_orders_with_sentiment.csv"
OUTPUT_HTML = DASHBOARD_DIR / "olist_ml_business_dashboard.html"

print(f"📂 Loading data from: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# Make sure timestamp is datetime
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

# ------------------------------------------------------------------------------
# 2. KPI metrics (for CEO-style tiles)
# ------------------------------------------------------------------------------

total_revenue = float(df["payment_value"].sum())
total_orders = int(df["order_id"].nunique())
avg_order_value = float(df["payment_value"].mean())
avg_freight = float(df["freight_value"].mean())
avg_review = float(df["review_score"].mean())

sent_counts = df["sentiment_label"].value_counts()
sent_pct = (sent_counts / sent_counts.sum() * 100).round(1)

pct_positive = float(sent_pct.get("positive", 0.0))
pct_neutral = float(sent_pct.get("neutral", 0.0))
pct_negative = float(sent_pct.get("negative", 0.0))

# If you want to hard-code ML metrics from your XGBoost notebook:
XGB_RMSE = 9.36
XGB_MAE = 3.90
XGB_R2 = 0.6334

# ------------------------------------------------------------------------------
# 3. Build Plotly figures (Tableau-style layout)
# ------------------------------------------------------------------------------

# 3.1 Revenue trend
monthly = (
    df.groupby("year_month")
    .agg(
        revenue=("payment_value", "sum"),
        orders=("order_id", "nunique"),
    )
    .reset_index()
)

fig_revenue = px.line(
    monthly,
    x="year_month",
    y="revenue",
    title="Monthly Revenue Trend",
    labels={"year_month": "Month", "revenue": "Revenue (BRL)"},
)
fig_revenue.update_layout(margin=dict(l=40, r=20, t=60, b=40), height=400)

# 3.2 Sentiment share over time
sent_time = (
    df.groupby(["year_month", "sentiment_label"])
    .size()
    .reset_index(name="count")
)
sent_time["share"] = sent_time.groupby("year_month")["count"].transform(
    lambda x: x / x.sum()
)

fig_sentiment_time = px.area(
    sent_time,
    x="year_month",
    y="share",
    color="sentiment_label",
    title="Sentiment Share Over Time",
    labels={"year_month": "Month", "share": "Share of Reviews"},
)
fig_sentiment_time.update_layout(
    yaxis_tickformat=".0%",
    margin=dict(l=40, r=20, t=60, b=40),
    height=400,
)

# 3.3 Revenue by state (top 10)
state_rev = (
    df.groupby("customer_state")
    .agg(revenue=("payment_value", "sum"))
    .reset_index()
    .sort_values("revenue", ascending=False)
    .head(10)
)

fig_state_rev = px.bar(
    state_rev,
    x="customer_state",
    y="revenue",
    title="Top 10 States by Revenue",
    labels={"customer_state": "State", "revenue": "Revenue (BRL)"},
)
fig_state_rev.update_layout(margin=dict(l=40, r=20, t=60, b=40), height=400)

# 3.4 Freight vs review score (box plot)
fig_freight_review = px.box(
    df,
    x="review_score",
    y="freight_value",
    points="outliers",
    title="Freight Cost vs Review Score",
    labels={"review_score": "Review Score", "freight_value": "Freight (BRL)"},
)
fig_freight_review.update_layout(margin=dict(l=40, r=20, t=60, b=40), height=400)

# Convert figures to HTML snippets (no full HTML, no JS duplication)
fig_revenue_html = pio.to_html(fig_revenue, include_plotlyjs=False, full_html=False)
fig_sentiment_time_html = pio.to_html(
    fig_sentiment_time, include_plotlyjs=False, full_html=False
)
fig_state_rev_html = pio.to_html(fig_state_rev, include_plotlyjs=False, full_html=False)
fig_freight_review_html = pio.to_html(
    fig_freight_review, include_plotlyjs=False, full_html=False
)

# ------------------------------------------------------------------------------
# 4. HTML template (Tableau-like dark layout with tiles + 2x2 grid)
# ------------------------------------------------------------------------------

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Brazilian E-Commerce – ML & Business Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
    }}

    .page {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 24px 40px 24px;
    }}

    h1 {{
      margin: 0 0 4px 0;
      font-size: 28px;
      font-weight: 600;
    }}

    .subtitle {{
      font-size: 14px;
      color: #9ca3af;
      margin-bottom: 20px;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: #020617;
      border-radius: 14px;
      padding: 14px 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      border: 1px solid #1f2937;
    }}

    .kpi-label {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #9ca3af;
      margin-bottom: 8px;
    }}

    .kpi-value {{
      font-size: 22px;
      font-weight: 600;
      margin-bottom: 4px;
    }}

    .kpi-sub {{
      font-size: 12px;
      color: #6b7280;
    }}

    .grid-2x2 {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      grid-auto-rows: minmax(0, 1fr);
      gap: 20px;
    }}

    .panel {{
      background: #020617;
      border-radius: 14px;
      padding: 12px;
      border: 1px solid #1f2937;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }}

    .panel-title {{
      font-size: 13px;
      font-weight: 500;
      margin: 0 0 4px 4px;
      color: #e5e7eb;
    }}

    .panel-subtitle {{
      font-size: 11px;
      color: #9ca3af;
      margin: 0 0 8px 4px;
    }}

    @media (max-width: 1024px) {{
      .kpi-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .grid-2x2 {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Brazilian E-Commerce – ML & Business Dashboard</h1>
    <div class="subtitle">
      End-to-end pipeline: Kaggle → Meltano → BigQuery → dbt → GX → XGBoost → HTML
    </div>

    <!-- KPI row -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">R$ {total_revenue:,.0f}</div>
        <div class="kpi-sub">Across {total_orders:,} unique orders</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">R$ {avg_order_value:,.2f}</div>
        <div class="kpi-sub">Avg freight: R$ {avg_freight:,.2f}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Customer Sentiment</div>
        <div class="kpi-value">{pct_positive:.1f}% 👍</div>
        <div class="kpi-sub">
          Neutral: {pct_neutral:.1f}% · Negative: {pct_negative:.1f}%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">ML Model (XGBoost freight)</div>
        <div class="kpi-value">R² = {XGB_R2:.3f}</div>
        <div class="kpi-sub">RMSE: {XGB_RMSE:.2f} · MAE: {XGB_MAE:.2f}</div>
      </div>
    </div>

    <!-- 2x2 grid of charts -->
    <div class="grid-2x2">
      <div class="panel">
        <p class="panel-title">Revenue & Orders Over Time</p>
        <p class="panel-subtitle">Seasonality and growth pattern by month</p>
        {fig_revenue_html}
      </div>
      <div class="panel">
        <p class="panel-title">Sentiment Share Over Time</p>
        <p class="panel-subtitle">How positive / negative feedback evolves</p>
        {fig_sentiment_time_html}
      </div>
      <div class="panel">
        <p class="panel-title">Top 10 States by Revenue</p>
        <p class="panel-subtitle">Where most GMV is generated</p>
        {fig_state_rev_html}
      </div>
      <div class="panel">
        <p class="panel-title">Freight Cost vs Review Score</p>
        <p class="panel-subtitle">Higher freight tends to correlate with lower satisfaction</p>
        {fig_freight_review_html}
      </div>
    </div>
  </div>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# 5. Write out HTML
# ------------------------------------------------------------------------------

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_HTML.write_text(html_template, encoding="utf-8")

print(f"✅ Dashboard written to: {OUTPUT_HTML}")
