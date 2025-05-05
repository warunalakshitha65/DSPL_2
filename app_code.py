import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load the CSV
df = pd.read_csv('hdx_hapi_returnees_lka.csv')

# Initialize Dash app
app = dash.Dash(_name_)
app.title = "Returnees Dashboard"

# Create a sample chart (edit according to actual columns)
fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="Sample Chart")

# Layout of dashboard
app.layout = html.Div(children=[
    html.H1("Returnees Dashboard", style={'textAlign': 'center'}),
    html.Div(children="Interactive visualization of returnees data."),
    dcc.Graph(figure=fig)
])

# Run the server
if _name_ == '_main_':
    app.run_server(debug=True)
    


