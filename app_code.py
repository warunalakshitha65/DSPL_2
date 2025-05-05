import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

# Load the CSV
df = pd.read_csv('hdx_hapi_returnees_lka.csv')

# Check and clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Example expected columns: district, returnees, month
# If "month" is a date column, convert it
if 'month' in df.columns:
    try:
        df['month'] = pd.to_datetime(df['month'])
    except:
        pass

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Returnees Dashboard - Sri Lanka"

# Main layout
app.layout = html.Div([
    html.H1("Sri Lanka Returnees Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select District:"),
        dcc.Dropdown(
            id='district-dropdown',
            options=[{'label': d, 'value': d} for d in df['district'].dropna().unique()],
            value=df['district'].dropna().unique()[0]
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Br(),

    html.Div([
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='time-series')
    ])
])


# Callbacks to update charts
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('time-series', 'figure')],
    [Input('district-dropdown', 'value')]
)
def update_charts(selected_district):
    filtered_df = df[df['district'] == selected_district]

    # Bar chart: Total returnees by sub-district or other category if available
    if 'ds_division' in filtered_df.columns:
        bar_fig = px.bar(
            filtered_df,
            x='ds_division',
            y='returnees',
            title=f"Returnees by DS Division in {selected_district}",
            labels={'returnees': 'Number of Returnees', 'ds_division': 'DS Division'}
        )
    else:
        bar_fig = px.bar(
            filtered_df,
            x='month',
            y='returnees',
            title=f"Returnees Over Time in {selected_district}"
        )

    # Time series chart
    if 'month' in filtered_df.columns:
        time_fig = px.line(
            filtered_df.sort_values('month'),
            x='month',
            y='returnees',
            title=f"Monthly Returnees Trend in {selected_district}",
            markers=True
        )
    else:
        time_fig = px.scatter(title="Time data not available")

    return bar_fig, time_fig


# Run the app
if _name_ == '_main_':
    app.run_server(debug=True)





