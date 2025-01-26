import requests

def refresh_access_token(refresh_token, client_id, client_secret):
    """
    Refresh the access token using Strava's OAuth endpoint.
    """
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json().get('access_token')

def fetch_activities(access_token, after_timestamp):
    """
    Fetch activities for the authorized user after a specific timestamp.
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    activities = []
    page = 1

    while True:
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers=headers,
            params={'after': after_timestamp, 'page': page, 'per_page': 200}
        )
        if response.status_code != 200 or not response.json():
            break

        activities.extend(response.json())
        page += 1

    return activities

