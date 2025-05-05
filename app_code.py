import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("hdx_hapi_returnees_lka.csv")

# Convert date if needed
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# Start Dash app
app = dash.Dash(_name_)
app.title = "Sri Lanka Returnees Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Sri Lanka Returnees Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select District:"),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in sorted(df["district"].dropna().unique())],
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

    total = filtered_df["returnees"].sum()
    latest_date = filtered_df["date"].max()
    latest_returnees = filtered_df[filtered_df["date"] == latest_date]["returnees"].sum()

    summary = f"Total Returnees: {total:,} | Latest Month Returnees: {latest_returnees:,} ({latest_date.date()})"

    # Time-series
    time_fig = px.line(filtered_df, x="date", y="returnees", color="district",
                       title="Returnees Over Time")

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
        map_fig = px.scatter(title="Map data not available")

    return summary, time_fig, map_fig

# Run server
if _name_ == "_main_":
    app.run_server(debug=True)