import matplotlib.pyplot as plt

def plot_monthly_distance(df):
    """
    Plot a bar chart for total monthly distance with an average line.
    """
    monthly_distance = df.groupby(df["Date"].dt.to_period("M"))["Distance (km)"].sum()
    avg_monthly_distance = monthly_distance.mean()  # Calculate the average

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_distance.index.astype(str), monthly_distance.values, color="blue", width=0.6, label="Monthly Distance")
    ax.axhline(avg_monthly_distance, color="red", linestyle="--", linewidth=2, label=f"Avg: {avg_monthly_distance:.2f} km")
    ax.set_title("Total Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    return fig

def plot_weekly_distance(df):
    """
    Plot a bar chart for total weekly distance with an average line.
    """
    weekly_distance = df.groupby(df["Week"])["Distance (km)"].sum()
    avg_weekly_distance = weekly_distance.mean()  # Calculate the average

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="green", width=5, label="Weekly Distance")
    ax.axhline(avg_weekly_distance, color="red", linestyle="--", linewidth=2, label=f"Avg: {avg_weekly_distance:.2f} km")
    ax.set_title("Total Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    return fig

def plot_progression(df, distance_min, distance_max):
    """
    Plot a progression graph for activities within a specified distance range.
    """
    filtered_df = df[(df["Distance (km)"] >= distance_min) & (df["Distance (km)"] <= distance_max)]
    filtered_df = filtered_df.sort_values("Date")

    if filtered_df.empty:
        return None

    avg_time = filtered_df["Time (minutes)"].mean()  # Calculate the average time

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(filtered_df["Date"], filtered_df["Time (minutes)"], marker="o", linestyle="-", color="blue", label="Progression")
    ax.axhline(avg_time, color="red", linestyle="--", linewidth=2, label=f"Avg: {avg_time:.2f} min")
    ax.set_title(f"Progression for {distance_min}K to {distance_max}K", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Time (minutes)", fontsize=12)
    ax.legend()
    ax.grid(alpha=0.7)
    return fig
