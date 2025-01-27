import pandas as pd

def process_activities(data):
    """Process raw Strava activities into a clean DataFrame."""
    df = pd.DataFrame(data)
    df = df[['start_date', 'distance', 'moving_time', 'average_heartrate']]
    df.rename(columns={
        'start_date': 'Date',
        'distance': 'Distance (meters)',
        'moving_time': 'Time (seconds)',
        'average_heartrate': 'Average HR'
    }, inplace=True)

    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Drop timezone
    df['Distance (km)'] = df['Distance (meters)'] / 1000
    df['Time (minutes)'] = df['Time (seconds)'] / 60
    df['Week'] = df['Date'].dt.to_period('W').dt.to_timestamp()
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    df.sort_values('Date', inplace=True)
    return df
