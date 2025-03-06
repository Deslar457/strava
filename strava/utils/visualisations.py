import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def plot_progression(df, lower_bound, upper_bound):
    """Generate a line graph for progression of a specific distance range."""
    progression = df[
        (df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)
    ].groupby("Month")["Time (minutes)"].min()

    if not progression.empty:
        def format_time(minutes):
            mins = int(minutes)
            secs = round((minutes - mins) * 60)
            return f"{mins}:{secs:02d}"

        formatted_times = [format_time(t) for t in progression.values]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(progression.index, progression.values, marker="o", color="blue", label="Best Time")

        # Annotate each point with MM:SS format
        for i, txt in enumerate(formatted_times):
            ax.annotate(txt, (progression.index[i], progression.iloc[i]), 
                        textcoords="offset points", xytext=(0, 5), ha="center")

        avg_time = progression.mean()
        ax.axhline(avg_time, color="red", linestyle="--", label=f"Avg: {format_time(avg_time)}")
        
        ax.set_title(f"Progression for {lower_bound:.1f}-{upper_bound:.1f} km", fontsize=16)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Time (minutes)", fontsize=12)
        ax.legend()
        ax.grid(alpha=0.5)
        return fig
    return None


def plot_monthly_distance(df):
    """Generate a bar chart for monthly distance with average distance label."""
    monthly_distance = df.groupby("Month")["Distance (km)"].sum()
    avg_distance = monthly_distance.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(monthly_distance.index, monthly_distance.values, color="skyblue", width=20, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    ax.set_title("Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig


def plot_weekly_distance(df):
    """Generate a bar chart for weekly distance with average distance label."""
    weekly_distance = df.groupby("Week")["Distance (km)"].sum()
    avg_distance = weekly_distance.mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="lightgreen", width=7, edgecolor="black")
    ax.axhline(avg_distance, color="red", linestyle="--", label=f"Avg Distance: {avg_distance:.2f} km")

    ax.set_title("Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    return fig

def format_pace(y, _):
    """Convert decimal minutes to mm:ss format for plotting."""
    minutes = int(y)
    seconds = int((y - minutes) * 60)
    return f"{minutes}:{seconds:02d}"

def plot_pace_vs_hr(df, lower_bound, upper_bound):
    """Plot Pace vs. Heart Rate for a selected distance range each month."""
    filtered_df = df[
        (df["Distance (km)"] >= lower_bound) & (df["Distance (km)"] < upper_bound)
    ]

    if not filtered_df.empty:
        monthly_data = filtered_df.groupby("Month").agg({
            "Time (minutes)": "sum",
            "Distance (km)": "sum",
            "Average HR": "mean"
        }).reset_index()

        # Calculate pace in minutes per km
        monthly_data["Pace (min/km)"] = monthly_data["Time (minutes)"] / monthly_data["Distance (km)"]

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Line chart for Pace
        ax1.set_xlabel("Month", fontsize=12)
        ax1.set_ylabel("Pace (min/km)", color="blue", fontsize=12)
        ax1.plot(monthly_data["Month"], monthly_data["Pace (min/km)"], marker="o", color="blue", label="Pace")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.invert_yaxis()  # Faster times at the top

        # Convert y-axis labels to mm:ss format
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_pace))

        # Second y-axis for Heart Rate
        ax2 = ax1.twinx()
        ax2.set_ylabel("Avg HR (bpm)", color="red", fontsize=12)
        ax2.plot(monthly_data["Month"], monthly_data["Average HR"], marker="s", color="red", linestyle="--", label="Heart Rate")
        ax2.tick_params(axis="y", labelcolor="red")

        ax1.set_title(f"Pace vs. Heart Rate for {lower_bound}K - {upper_bound}K", fontsize=16)
        ax1.grid(alpha=0.5)
        fig.tight_layout()
        plt.show()
        return fig
    return None


def calculate_workloads(df):
    """Calculate acute (7-day), chronic (28-day), and ACWR."""
    df = df.sort_values("Date")
    acute_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=7))]["Distance (km)"].sum()
    chronic_workload = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=28))]["Distance (km)"].sum() / 4
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0
    return acute_workload, chronic_workload, acwr



def plot_weekly_rolling_distance(df, window=4):
    """Plot a rolling average of weekly distance."""
    
    # Ensure Date column is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Group by week (sum distance per week)
    df["Week"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_data = df.groupby("Week")["Distance (km)"].sum().reset_index()

    # Compute rolling average
    weekly_data["Rolling Avg (km)"] = weekly_data["Distance (km)"].rolling(window=window, min_periods=1).mean()

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weekly_data["Week"], weekly_data["Distance (km)"], marker="o", linestyle="-", label="Weekly Distance")
    ax.plot(weekly_data["Week"], weekly_data["Rolling Avg (km)"], marker="s", linestyle="--", color="red", label=f"{window}-Week Rolling Avg")
    
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.set_title(f"Weekly Distance with {window}-Week Rolling Average", fontsize=16)
    ax.legend()
    ax.grid(alpha=0.5)
    plt.show()
    return fig


    

def plot_hr_vs_pace_correlation(df):
    """Plot correlation between heart rate and pace, only for sessions between 3:00-6:00 min/km."""

    # Ensure time and distance are in the correct units
    df = df.copy()  # Avoid modifying the original DataFrame
    df["Pace (min/km)"] = df["Time (minutes)"] / df["Distance (km)"]

    # Filter data to only include paces between 3:00 and 6:00 min/km
    df_filtered = df[(df["Pace (min/km)"] >= 3.0) & (df["Pace (min/km)"] <= 6.0)]

    if df_filtered.empty:
        return None  # If no data remains, return nothing

    # Compute correlation coefficient (r-value)
    correlation = df_filtered["Pace (min/km)"].corr(df_filtered["Average HR"])

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_filtered, x="Pace (min/km)", y="Average HR", alpha=0.6, ax=ax)

    # Regression line
    sns.regplot(data=df_filtered, x="Pace (min/km)", y="Average HR", scatter=False, ax=ax, color="red", line_kws={"alpha": 0.7})

    # Add correlation value on the chart
    ax.text(5.5, df_filtered["Average HR"].max(), f"r = {correlation:.2f}", fontsize=12, color="black", ha="right")

    ax.set_xlabel("Pace (min/km)", fontsize=12)
    ax.set_ylabel("Average Heart Rate (bpm)", fontsize=12)
    ax.set_title("Heart Rate vs. Pace (Filtered: 3:00 - 6:00 min/km)", fontsize=14)
    ax.grid(alpha=0.3)
    
    return fig
