import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# ---------------------------------
# Data Loading & Preprocessing
# ---------------------------------

# Load the dataset
try:
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
except FileNotFoundError:
    raise FileNotFoundError("The file 'hdx_hapi_returnees_lka.csv' was not found.")

# Standardize column names
df.columns = df.columns.str.strip().str.lower()

# Ensure expected columns exist
required_columns = ['district', 'returnees', 'date']
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Drop rows with missing or invalid dates
df = df.dropna(subset=['date'])

# Ensure 'returnees' column is numeric
df['returnees'] = pd.to_numeric(df['returnees'], errors='coerce').fillna(0)

# Drop rows with missing 'district'
df = df.dropna(subset=['district'])

# Prepare dropdown options
district_options = [{"label": i, "value": i} for i in sorted(df["district"].unique())]

# ---------------------------------
# Dash App Setup
# ---------------------------------

app = dash.Dash(__name__)
app.title = "Sri Lanka Returnees Dashboard"

app.layout = html.Div([
    html.H1("Sri Lanka Returnees Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select District:"),
        dcc.Dropdown(
            options=district_options,
            value=None,
            id="district-dropdown",
            placeholder="Choose a district"
        )
    ], style={'width': '40%', 'margin': 'auto'}),

    html.Br(),

    html.Div(id="summary-stats", style={'textAlign': 'center', 'fontSize': 18}),

    dcc.Graph(id="time-series-graph"),

    dcc.Graph(id="map-graph")
])

# ---------------------------------
# Callbacks
# ---------------------------------

@app.callback(
    [Output("summary-stats", "children"),
     Output("time-series-graph", "figure"),
     Output("map-graph", "figure")],
    [Input("district-dropdown", "value")]
)
def update_dashboard(selected_district):
    filtered_df = df.copy()
    if selected_district:
        filtered_df = filtered_df[filtered_df["district"] == selected_district]

    total = int(filtered_df["returnees"].sum())
    latest_date = filtered_df["date"].max()
    latest_returnees = 0
    if pd.notnull(latest_date):
        latest_returnees = int(filtered_df[filtered_df["date"] == latest_date]["returnees"].sum())

    summary = f"Total Returnees: {total:,} | Latest Month Returnees: {latest_returnees:,} ({latest_date.date() if latest_date else 'N/A'})"

    # Time-series chart
    time_fig = px.line(
        filtered_df,
        x="date",
        y="returnees",
        color="district" if not selected_district else None,
        title="Returnees Over Time"
    )

    # Map
    if {'latitude', 'longitude'}.issubset(df.columns):
        map_fig = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            color="returnees",
            size="returnees",
            hover_name="district",
            mapbox_style="carto-positron",
            title="Geographic Distribution of Returnees"
        )
    else:
        map_fig = px.scatter(title="Map data not available (Missing latitude/longitude columns)")

    return summary, time_fig, map_fig

# ---------------------------------
# Run the App
# ---------------------------------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)



