import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# ── Formatters ────────────────────────────────────────────────────────────────

def format_time(minutes):
    mins = int(minutes)
    secs = round((minutes - mins) * 60)
    return f"{mins}:{secs:02d}"


def format_pace(y, _):
    minutes = int(y)
    seconds = int((y - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


# ── LTHR Estimation ───────────────────────────────────────────────────────────

def estimate_threshold_hr(df):
    """
    Estimate LTHR from hardest sustained efforts.
    Filters: >= 6km, >= 25 min, top 15% HR efforts.
    Returns (top5_df, estimated_lthr) or (None, None).
    """
    candidates = df[
        (df["Distance (km)"] >= 6) &
        (df["Average HR"] >= df["Average HR"].quantile(0.85))
    ].copy()

    candidates["Pace"] = candidates["Time (minutes)"] / candidates["Distance (km)"]
    best = candidates[candidates["Time (minutes)"] >= 25].sort_values("Average HR", ascending=False)

    if best.empty:
        return None, None

    top5 = best.head(5)[["Date", "Distance (km)", "Time (minutes)", "Average HR", "Pace"]].copy()
    top5["Pace"] = top5["Pace"].apply(format_time)
    top5["Time (minutes)"] = top5["Time (minutes)"].apply(format_time)
    top5["Date"] = top5["Date"].dt.strftime("%d %b %Y")
    top5.rename(columns={"Time (minutes)": "Duration"}, inplace=True)

    estimated_lthr = round(best.iloc[0]["Average HR"] * 0.98)
    return top5, estimated_lthr


# ── Training Stress ───────────────────────────────────────────────────────────

def calculate_training_stress(df):
    """
    Calculate daily TSS, CTL (fitness), ATL (fatigue), TSB (form).
    LTHR is derived dynamically from estimate_threshold_hr — not hardcoded.
    """
    df = df.copy().sort_values("Date")

    # Dynamic LTHR — fixes the hardcoded 167 bug
    _, lthr = estimate_threshold_hr(df)
    threshold_hr = lthr if lthr else 167

    df["Duration (hours)"] = df["Time (minutes)"] / 60
    df["IF"] = (df["Average HR"] / threshold_hr).clip(upper=1.2)
    df["TSS"] = df["Duration (hours)"] * (df["IF"] ** 2) * 100
    df["Date"] = df["Date"].dt.normalize()

    daily = df.groupby("Date")["TSS"].sum().reset_index()
    date_range = pd.date_range(daily["Date"].min(), daily["Date"].max(), freq="D")
    daily = daily.set_index("Date").reindex(date_range, fill_value=0).reset_index()
    daily.rename(columns={"index": "Date"}, inplace=True)

    ctl_alpha = 1 - np.exp(-1 / 42)
    atl_alpha = 1 - np.exp(-1 / 7)

    ctl, atl = [], []
    ctl_val, atl_val = 0, 0

    for tss in daily["TSS"]:
        ctl_val = ctl_val + ctl_alpha * (tss - ctl_val)
        atl_val = atl_val + atl_alpha * (tss - atl_val)
        ctl.append(round(ctl_val, 2))
        atl.append(round(atl_val, 2))

    daily["CTL"] = ctl
    daily["ATL"] = atl
    daily["TSB"] = [c - a for c, a in zip(ctl, atl)]

    return daily


def get_ctl_delta(df, days=28):
    """Return CTL change vs N days ago."""
    daily = calculate_training_stress(df)
    if len(daily) < days:
        return None
    current_ctl = daily.iloc[-1]["CTL"]
    past_ctl = daily.iloc[-days]["CTL"]
    return round(current_ctl - past_ctl, 1)


# ── Workloads ─────────────────────────────────────────────────────────────────

def calculate_workloads(df):
    df = df.sort_values("Date")
    acute = df[df["Date"] >= df["Date"].max() - pd.Timedelta(days=7)]["Distance (km)"].sum()
    chronic = df[df["Date"] >= df["Date"].max() - pd.Timedelta(days=28)]["Distance (km)"].sum() / 4
    acwr = acute / chronic if chronic > 0 else 0
    return acute, chronic, acwr


# ── Form Status ───────────────────────────────────────────────────────────────

def get_form_status(df):
    daily = calculate_training_stress(df)
    latest = daily.iloc[-1]
    tsb = latest["TSB"]
    ctl = latest["CTL"]
    atl = latest["ATL"]

    if tsb > 5:
        status, colour = "Fresh", "green"
        advice = "Good time to race or do a hard effort."
    elif tsb > -10:
        status, colour = "Optimal", "amber"
        advice = "Building fitness. Monitor fatigue."
    else:
        status, colour = "Fatigued", "red"
        advice = "High fatigue. Prioritise recovery."

    return {
        "status": status, "colour": colour, "advice": advice,
        "TSB": round(tsb, 1), "CTL": round(ctl, 1), "ATL": round(atl, 1)
    }


# ── Personal Records ──────────────────────────────────────────────────────────

def get_personal_records(df):
    distances = {
        "5K": (4.8, 5.2),
        "10K": (9.8, 10.2),
        "Half Marathon": (20.8, 21.4),
    }
    records = []
    for label, (lo, hi) in distances.items():
        subset = df[(df["Distance (km)"] >= lo) & (df["Distance (km)"] <= hi)]
        if not subset.empty:
            best_row = subset.loc[subset["Time (minutes)"].idxmin()]
            records.append({
                "Distance": label,
                "Best Time": format_time(best_row["Time (minutes)"]),
                "Date": best_row["Date"].strftime("%d %b %Y"),
                "Pace (min/km)": format_time(best_row["Time (minutes)"] / best_row["Distance (km)"]),
                "HR": int(best_row["Average HR"]) if pd.notna(best_row["Average HR"]) else "—"
            })
    return pd.DataFrame(records) if records else None


# ── Race Predictions ──────────────────────────────────────────────────────────

def predict_race_times(df):
    """Riegel formula — projected from recent 8 weeks pace/HR efficiency."""
    df = df.copy().sort_values("Date")
    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]
    df["Efficiency"] = df["Pace"] / df["Average HR"]
    recent = df[df["Date"] >= df["Date"].max() - pd.Timedelta(weeks=8)]

    if recent.empty or recent["Efficiency"].isna().all():
        return None

    avg_efficiency = recent["Efficiency"].mean()
    avg_hr = recent["Average HR"].mean()
    estimated_5k_pace = avg_efficiency * avg_hr

    def riegel(base_time, base_dist, target_dist):
        return base_time * (target_dist / base_dist) ** 1.06

    base_5k_time = estimated_5k_pace * 5
    return {
        "5K": format_time(base_5k_time),
        "10K": format_time(riegel(base_5k_time, 5, 10)),
        "Half Marathon": format_time(riegel(base_5k_time, 5, 21.1)),
    }


def predict_10k_rf(df):
    """Random Forest 10k predictor. Requires 5+ 10k efforts."""
    df = df.copy().sort_values("Date")
    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]
    df["Pace/HR"] = df["Pace"] / df["Average HR"]

    # Fix: date-based rolling window, not row-based
    df = df.set_index("Date")
    df["7d_km"] = df["Distance (km)"].rolling("7d").sum()
    df = df.reset_index()

    tenk = df[df["Distance (km)"].between(9.8, 10.2)].dropna()
    if len(tenk) < 5:
        return None, "Not enough 10K runs (need 5+)."

    X = tenk[["Pace", "Average HR", "Pace/HR", "7d_km"]]
    y = tenk["Time (minutes)"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, model.predict(X_test))

    latest = df.iloc[-1]
    latest_input = pd.DataFrame([{
        "Pace": latest["Pace"],
        "Average HR": latest["Average HR"],
        "Pace/HR": latest["Pace/HR"],
        "7d_km": df["7d_km"].iloc[-1]
    }])
    pred = model.predict(latest_input)[0]

    # PB comparison
    pb_row = tenk.loc[tenk["Time (minutes)"].idxmin()]
    pb_minutes = pb_row["Time (minutes)"]

    return {
        "Predicted Time": format_time(pred),
        "Predicted Minutes": round(pred, 2),
        "MAE (±min)": round(mae, 2),
        "Training Runs": len(tenk),
        "PB": format_time(pb_minutes),
        "PB Minutes": round(pb_minutes, 2),
        "Below PB": pred > pb_minutes,
    }


# ── Charts ────────────────────────────────────────────────────────────────────

def plot_fitness_freshness(df):
    daily = calculate_training_stress(df)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily["Date"], daily["CTL"], label="Fitness (CTL)", color="steelblue", linewidth=2)
    ax.plot(daily["Date"], daily["ATL"], label="Fatigue (ATL)", color="tomato", linewidth=2)
    ax.plot(daily["Date"], daily["TSB"], label="Form (TSB)", color="mediumseagreen", linewidth=1.5, linestyle="--")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle=":")
    ax.fill_between(daily["Date"], daily["TSB"], 0,
                    where=[v >= 0 for v in daily["TSB"]], alpha=0.15, color="mediumseagreen", label="Fresh")
    ax.fill_between(daily["Date"], daily["TSB"], 0,
                    where=[v < 0 for v in daily["TSB"]], alpha=0.15, color="tomato", label="Fatigued")
    ax.set_title("Fitness & Freshness (CTL / ATL / TSB)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Score")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_monthly_distance(df):
    monthly = df.groupby("Month")["Distance (km)"].sum()
    avg = monthly.mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(monthly.index, monthly.values, width=10, color="steelblue", alpha=0.8)
    ax.axhline(avg, linestyle="--", color="tomato", label=f"Avg {avg:.1f} km")
    ax.set_title("Monthly Distance")
    ax.set_xlabel("Month")
    ax.set_ylabel("Distance (km)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_progression(df, lower_bound, upper_bound):
    progression = df[
        (df["Distance (km)"] >= lower_bound) &
        (df["Distance (km)"] < upper_bound)
    ].groupby("Month")["Time (minutes)"].min()

    if progression.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(progression.index, progression.values, marker="o", color="steelblue", label="Best Time")
    for i, t in enumerate(progression.values):
        ax.annotate(format_time(t), (progression.index[i], t),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    avg_time = progression.mean()
    ax.axhline(avg_time, linestyle="--", color="tomato", label=f"Avg: {format_time(avg_time)}")
    ax.set_title(f"Progression {lower_bound:.1f}–{upper_bound:.1f} km")
    ax.set_xlabel("Month")
    ax.set_ylabel("Time (minutes)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    return fig


def plot_pace_vs_hr(df, lower_bound, upper_bound):
    subset = df[
        (df["Distance (km)"] >= lower_bound) &
        (df["Distance (km)"] < upper_bound)
    ]
    if subset.empty:
        return None

    monthly = subset.groupby("Month").agg({
        "Time (minutes)": "sum",
        "Distance (km)": "sum",
        "Average HR": "mean"
    }).reset_index()
    monthly["Pace"] = monthly["Time (minutes)"] / monthly["Distance (km)"]

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(monthly["Month"], monthly["Pace"], marker="o", color="steelblue", label="Pace")
    ax1.set_ylabel("Pace (min/km)")
    ax1.invert_yaxis()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))
    ax2 = ax1.twinx()
    ax2.plot(monthly["Month"], monthly["Average HR"], linestyle="--", marker="s", color="tomato", label="HR")
    ax2.set_ylabel("Average HR")
    ax1.set_title("Pace vs Heart Rate")
    ax1.grid(alpha=0.3)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2)
    plt.tight_layout()
    return fig


def plot_long_run_progression(df):
    """Chart of all Sunday long runs (>= 10km) over time."""
    long_runs = df[df["Distance (km)"] >= 10].copy()
    long_runs = long_runs.sort_values("Date")

    if long_runs.empty:
        return None

    long_runs["Pace"] = long_runs["Time (minutes)"] / long_runs["Distance (km)"]

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.bar(long_runs["Date"], long_runs["Distance (km)"],
            width=3, color="steelblue", alpha=0.6, label="Distance (km)")
    ax1.set_ylabel("Distance (km)")
    ax1.set_xlabel("Date")

    ax2 = ax1.twinx()
    ax2.plot(long_runs["Date"], long_runs["Pace"], marker="o",
             color="tomato", linewidth=1.5, label="Pace (min/km)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))
    ax2.set_ylabel("Pace (min/km)")
    ax2.invert_yaxis()

    ax1.set_title("Long Run Progression (≥ 10km)")
    ax1.grid(axis="y", alpha=0.3)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_pace_zones(df, threshold_pace=None):
    """
    Bar chart of monthly volume split by effort zone.
    Zones based on pace bands relative to threshold pace.
    If threshold_pace not provided, uses 4:25/km as default.
    """
    df = df.copy()
    df["Pace"] = df["Time (minutes)"] / df["Distance (km)"]

    tp = threshold_pace if threshold_pace else 4.417  # 4:25/km in decimal

    def classify(pace):
        if pace <= tp * 0.97:
            return "Hard / Race Pace"
        elif pace <= tp * 1.08:
            return "Moderate / Threshold"
        else:
            return "Easy"

    df["Zone"] = df["Pace"].apply(classify)

    df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").dt.to_timestamp()

    zone_monthly = (
        df.groupby(["Month", "Zone"])["Distance (km)"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )

# Extra safety for Streamlit/Matplotlib
    zone_monthly.index = pd.to_datetime(zone_monthly.index)

    zone_colours = {
        "Easy": "steelblue",
        "Moderate / Threshold": "orange",
        "Hard / Race Pace": "tomato",
    }
    cols = [z for z in ["Easy", "Moderate / Threshold", "Hard / Race Pace"] if z in zone_monthly.columns]
    colours = [zone_colours[c] for c in cols]

    fig, ax = plt.subplots(figsize=(12, 5))
    zone_monthly[cols].plot(kind="bar", stacked=True, ax=ax, color=colours, alpha=0.85)
    ax.set_title("Monthly Volume by Effort Zone")
    ax.set_xlabel("Month")
    ax.set_ylabel("Distance (km)")
    ax.legend(title="Zone")
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig
