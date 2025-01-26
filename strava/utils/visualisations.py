import matplotlib.pyplot as plt

def plot_monthly_distance(df):
    """
    Plot a bar chart for monthly distance.
    """
    # Group by month and sum the distances
    monthly_distance = df.groupby(df["Date"].dt.to_period("M"))["Distance (km)"].sum()

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_distance.index.astype(str), monthly_distance.values, color="blue", width=0.6)
    ax.set_title("Total Monthly Distance", fontsize=16)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    return fig



def plot_weekly_distance(df):
    """
    Plot a bar chart for weekly distance.
    """
    weekly_distance = df.groupby(df["Week"])["Distance (km)"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(weekly_distance.index, weekly_distance.values, color="green", width=5)
    ax.set_title("Total Weekly Distance", fontsize=16)
    ax.set_xlabel("Week", fontsize=12)
    ax.set_ylabel("Distance (km)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    
    return fig