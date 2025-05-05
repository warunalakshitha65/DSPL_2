import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load CSV (adjust filename if needed)
try:
    df = pd.read_csv("hdx_hapi_returnees_lka.csv")
except Exception as e:
    print("Error loading CSV:", e)
    df = pd.DataFrame({'Example Category': ['A', 'B', 'C'], 'Value': [10, 20, 30]})

# Rename columns to be safe
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Create a simple bar chart using first 2 columns
try:
    x_col = df.columns[0]
    y_col = df.columns[1]
    fig = px.bar(df, x=x_col, y=y_col, title=f'{y_col.capitalize()} by {x_col.capitalize()}')
except Exception as e:
    print("Error creating chart:", e)
    fig = px.bar(title="Could not create chart. Check CSV column names.")

# Start Dash app
app = dash.Dash(__name__)
app.title = "Simple Dashboard"

app.layout = html.Div([
    html.H1("CSV Dashboard", style={'textAlign': 'center'}),
    dcc.Graph(figure=fig)
])

if __name__ == '_main_':
    app.run_server(debug=True)


