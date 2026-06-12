"""
Energy Consumption Anomaly Detector
=====================================
Detects fraudulent or tampered electricity meters by analyzing
consumption patterns and flagging statistical anomalies.

Author  : Aditya Kumar
College : NIT Manipur | Electrical Engineering
Inspired by internship work at South Bihar Power Distribution Company Ltd. (SBPDCL)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── CONFIG ──────────────────────────────────────────────────────────────────
DATA_FILE   = "consumption_data.csv"
OUTPUT_DIR  = "output"
Z_THRESHOLD = 2.0   # Flag reading if it deviates more than 2 std devs from mean
DROP_THRESH = 0.50  # Also flag if a reading drops >50% compared to personal average
# ────────────────────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(filepath):
    """Load and validate the consumption CSV."""
    df = pd.read_csv(filepath)
    required_cols = {"connection_id", "consumer_name", "month", "units_consumed"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")
    print(f"✔  Loaded {len(df)} records for {df['connection_id'].nunique()} connections.\n")
    return df


def detect_anomalies(df):
    """
    For each connection, compute mean & std of units consumed.
    Flag a reading as anomalous if:
      - Its Z-score exceeds Z_THRESHOLD  (unusual spike or drop), OR
      - It drops more than DROP_THRESH % below the connection's average (tampering signal)
    """
    results = []

    for conn_id, group in df.groupby("connection_id"):
        consumer = group["consumer_name"].iloc[0]
        mean_units = group["units_consumed"].mean()
        std_units  = group["units_consumed"].std()

        for _, row in group.iterrows():
            z_score = (row["units_consumed"] - mean_units) / std_units if std_units > 0 else 0
            drop_pct = (mean_units - row["units_consumed"]) / mean_units if mean_units > 0 else 0

            is_anomaly = abs(z_score) > Z_THRESHOLD or drop_pct > DROP_THRESH

            # Determine anomaly type
            if is_anomaly:
                if drop_pct > DROP_THRESH:
                    anomaly_type = "Suspected Tampering (Sudden Drop)"
                elif row["units_consumed"] > mean_units:
                    anomaly_type = "Unusual Spike"
                else:
                    anomaly_type = "Unusual Drop"
            else:
                anomaly_type = "Normal"

            results.append({
                "connection_id"  : conn_id,
                "consumer_name"  : consumer,
                "month"          : row["month"],
                "units_consumed" : row["units_consumed"],
                "avg_consumption": round(mean_units, 1),
                "z_score"        : round(z_score, 2),
                "is_anomaly"     : is_anomaly,
                "anomaly_type"   : anomaly_type
            })

    return pd.DataFrame(results)


def print_report(result_df):
    """Print a clean summary of flagged connections to the terminal."""
    flagged = result_df[result_df["is_anomaly"]]

    print("=" * 60)
    print("         ANOMALY DETECTION REPORT")
    print("=" * 60)
    print(f"Total records analyzed : {len(result_df)}")
    print(f"Anomalies detected     : {len(flagged)}")
    print(f"Connections flagged    : {flagged['connection_id'].nunique()}")
    print("=" * 60)

    if flagged.empty:
        print("No anomalies found.")
        return

    for _, row in flagged.iterrows():
        print(f"\n⚠  {row['connection_id']} | {row['consumer_name']}")
        print(f"   Month           : {row['month']}")
        print(f"   Units Consumed  : {row['units_consumed']}  (Avg: {row['avg_consumption']})")
        print(f"   Z-Score         : {row['z_score']}")
        print(f"   Flag Reason     : {row['anomaly_type']}")

    print("\n" + "=" * 60)


def plot_all_connections(df, result_df):
    """
    Plot consumption trend for every connection.
    Anomalous readings are marked with red dots.
    Saves one combined figure to the output folder.
    """
    conn_ids   = df["connection_id"].unique()
    n          = len(conn_ids)
    cols       = 2
    rows       = (n + 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 3.5))
    fig.suptitle("Electricity Consumption Analysis — All Connections",
                 fontsize=14, fontweight="bold", y=1.01)
    axes = axes.flatten()

    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for i, conn_id in enumerate(conn_ids):
        ax        = axes[i]
        conn_data = result_df[result_df["connection_id"] == conn_id].copy()

        # Sort by month order
        conn_data["month_num"] = conn_data["month"].apply(
            lambda m: months_order.index(m) if m in months_order else 99
        )
        conn_data = conn_data.sort_values("month_num")

        normal   = conn_data[~conn_data["is_anomaly"]]
        anomalou = conn_data[conn_data["is_anomaly"]]
        avg      = conn_data["avg_consumption"].iloc[0]

        ax.plot(conn_data["month"], conn_data["units_consumed"],
                color="#1F4E79", linewidth=2, marker="o", markersize=5, zorder=2)
        ax.scatter(anomalou["month"], anomalou["units_consumed"],
                   color="red", s=100, zorder=3, label="Anomaly")
        ax.axhline(avg, color="orange", linestyle="--", linewidth=1.2, label=f"Avg: {avg}")

        consumer = conn_data["consumer_name"].iloc[0]
        ax.set_title(f"{conn_id} — {consumer}", fontsize=10, fontweight="bold")
        ax.set_xlabel("Month", fontsize=8)
        ax.set_ylabel("Units (kWh)", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # Shade anomaly points
        for _, row in anomalou.iterrows():
            ax.annotate("⚠ Flag", xy=(row["month"], row["units_consumed"]),
                        xytext=(0, 12), textcoords="offset points",
                        fontsize=7, color="red", ha="center")

    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "consumption_analysis.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n✔  Chart saved → {out_path}")
    plt.show()


def plot_anomaly_summary(result_df):
    """Bar chart showing flagged vs normal readings per connection."""
    summary = result_df.groupby(["connection_id", "is_anomaly"]).size().unstack(fill_value=0)
    summary.columns = ["Normal", "Anomaly"] if False in summary.columns else summary.columns

    # Rename columns safely
    col_map = {False: "Normal", True: "Anomaly"}
    summary = summary.rename(columns=col_map)
    if "Normal"  not in summary.columns: summary["Normal"]  = 0
    if "Anomaly" not in summary.columns: summary["Anomaly"] = 0

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(summary))
    ax.bar(x - 0.2, summary["Normal"],  0.4, label="Normal",  color="#1F4E79")
    ax.bar(x + 0.2, summary["Anomaly"], 0.4, label="Anomaly", color="#C0392B")
    ax.set_xticks(x)
    ax.set_xticklabels(summary.index, rotation=45, ha="right")
    ax.set_title("Flagged vs Normal Readings per Connection", fontweight="bold")
    ax.set_ylabel("Number of Readings")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "anomaly_summary.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"✔  Summary chart saved → {out_path}")
    plt.show()


def save_report_csv(result_df):
    """Save the full flagged report as CSV for further review."""
    flagged  = result_df[result_df["is_anomaly"]]
    out_path = os.path.join(OUTPUT_DIR, "flagged_connections.csv")
    flagged.to_csv(out_path, index=False)
    print(f"✔  Flagged records saved → {out_path}")


# ── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df         = load_data(DATA_FILE)
    result_df  = detect_anomalies(df)

    print_report(result_df)
    save_report_csv(result_df)
    plot_all_connections(df, result_df)
    plot_anomaly_summary(result_df)

    print("\n✅  Analysis complete. Check the 'output/' folder for results.")
