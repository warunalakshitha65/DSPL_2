import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("hdx_hapi_returnees_lka.csv")

# Convert date column if it exists
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# Standardize column names (helps avoid KeyErrors due to spacing/casing)
df.columns = df.columns.str.strip().str.lower()

# Confirm 'district' column exists
if "district" in df.columns:
    district_options = [{"label": i, "value": i} for i in sorted(df["district"].dropna().unique())]
else:
    district_options = []
    print("Column 'district' not found in the DataFrame.")

# Start Dash app
app = dash.Dash(__name__)
app.title = "Sri Lanka Returnees Dashboard"

# Layout
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

# Callbacks
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

    total = filtered_df["returnees"].sum() if "returnees" in df.columns else 0
    latest_date = filtered_df["date"].max() if "date" in df.columns else None
    latest_returnees = 0
    if latest_date is not None:
        latest_returnees = filtered_df[filtered_df["date"] == latest_date]["returnees"].sum()

    summary = f"Total Returnees: {total:,} | Latest Month Returnees: {latest_returnees:,} ({latest_date.date() if latest_date else 'N/A'})"

    # Time-series
    if "date" in df.columns and "returnees" in df.columns:
        time_fig = px.line(filtered_df, x="date", y="returnees", color="district",
                           title="Returnees Over Time")
    else:
        time_fig = px.scatter(title="Time-series data not available")

    # Map
    if {'latitude', 'longitude'}.issubset(df.columns):
        map_fig = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            color="returnees" if "returnees" in df.columns else None,
            size="returnees" if "returnees" in df.columns else None,
            hover_name="district" if "district" in df.columns else None,
            mapbox_style="carto-positron",
            title="Geographic Distribution of Returnees"
        )
    else:
        map_fig = px.scatter(title="Map data not available")

    return summary, time_fig, map_fig

# Run server
if __name__ == "__main__":
    # Change from app.run_server() to app.run() as per Dash 2.x and later
    app.run(debug=True, use_reloader=False)


