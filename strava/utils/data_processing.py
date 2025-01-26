import pandas as pd

def process_activities(activities):
    """
    Process raw Strava activities data into a structured DataFrame.
    """
    # Extract relevant fields
    data = []
    for activity in activities:
        data.append({
            "Date": pd.to_datetime(activity["start_date_local"]),
            "Distance (km)": activity["distance"] / 1000,  # Convert meters to kilometers
            "Time (minutes)": activity["moving_time"] / 60,  # Convert seconds to minutes
            "Average HR": activity.get("average_heartrate", None)  # Handle missing heart rate
        })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Add useful columns
    df["Day"] = df["Date"].dt.day_name()
    df["Month"] = df["Date"].dt.month_name()
    df["Week"] = df["Date"].dt.to_period("W").dt.to_timestamp()

    return df

