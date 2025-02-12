 # Strava Dashboard

A Streamlit-based app to visualise and analyse Strava running data. 

## Features

- **Monthly & Weekly Distances**: Bar charts with average lines for trends.
- **Progression Analysis**: Line graphs for selected distances (e.g., 5K, 10K).
- **Real-Time Data**: Fetches activities directly from the Strava API.

## Setup

### Prerequisites
- **Python** (>= 3.8)
- **Strava API Credentials**: `client_id`, `client_secret`, `refresh_token`.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Deslar457/strava.git
   cd strava

## Create virtual environment
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

## Install dependencies
pip install -r requirements.txt

## Add strava credentials 
client_id = "your_client_id"
client_secret = "your_client_secret"
refresh_token = "your_refresh_token"


## Run the app
streamlit run app.py

## File structure
strava/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── services/               # Strava API integration
├── utils/                  # Data processing and visualization


## Usage
Progression Filter: Use the sidebar to filter by distance (e.g., 5K, 10K).
Visualizations: Explore bar charts for distances and progression graphs.

## License
Licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
Strava API
Streamlit
