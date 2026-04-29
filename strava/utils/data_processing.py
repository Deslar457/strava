import pandas as pd


def format_time(minutes):
    mins = int(minutes)
    secs = round((minutes - mins) * 60)
    return f"{mins}:{secs:02d}"


def process_activities(data):
    df = pd.DataFrame(data)
    df = df[['start_date', 'distance', 'moving_time', 'average_heartrate']]
    df.rename(columns={
        'start_date': 'Date',
        'distance': 'Distance (meters)',
        'moving_time': 'Time (seconds)',
        'average_heartrate': 'Average HR'
    }, inplace=True)

    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    df['Distance (km)'] = df['Distance (meters)'] / 1000
    df['Time (minutes)'] = df['Time (seconds)'] / 60
    df['Formatted Time'] = df['Time (minutes)'].apply(format_time)
    df['Week'] = df['Date'].dt.to_period('W').dt.to_timestamp()
    df['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df