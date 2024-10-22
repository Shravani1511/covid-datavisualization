import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

# Sample JSON data simulating COVID-19 data
covid_data_json = '''
{
    "data": [
        {"country": "United States", "date": "2020-03-01", "total_cases": 100, "new_cases": 20, "total_deaths": 5, "total_recoveries": 10, "population": 331000000},
        {"country": "United States", "date": "2020-04-01", "total_cases": 10000, "new_cases": 500, "total_deaths": 200, "total_recoveries": 5000, "population": 331000000},
        {"country": "United States", "date": "2020-05-01", "total_cases": 50000, "new_cases": 3000, "total_deaths": 1000, "total_recoveries": 25000, "population": 331000000},
        {"country": "India", "date": "2020-03-01", "total_cases": 50, "new_cases": 10, "total_deaths": 2, "total_recoveries": 5, "population": 1380000000},
        {"country": "India", "date": "2020-04-01", "total_cases": 5000, "new_cases": 250, "total_deaths": 100, "total_recoveries": 2500, "population": 1380000000},
        {"country": "India", "date": "2020-05-01", "total_cases": 30000, "new_cases": 1500, "total_deaths": 600, "total_recoveries": 15000, "population": 1380000000}
    ]
}
'''

# Load the JSON data
covid_data = json.loads(covid_data_json)
df = pd.DataFrame(covid_data['data'])
df['date'] = pd.to_datetime(df['date'])

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("COVID-19 Dashboard with Multiple Charts", style={'textAlign': 'center'}),

    # Dropdown to select country
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in df['country'].unique()],
        value='United States',
        style={'width': '50%', 'margin': '0 auto'}
    ),

    # Line chart for case progression over time
    dcc.Graph(id='cases-line-chart'),

    # Bar chart for death vs recovery rates
    dcc.Graph(id='death-recovery-bar-chart'),

    # Choropleth map for total cases by country
    dcc.Graph(id='choropleth-map'),

    # Heatmap for case density
    dcc.Graph(id='cases-heatmap'),

    # Additional chart (e.g., Pie chart for active vs recovered cases)
    dcc.Graph(id='active-recovered-pie-chart')
])

# Callback for updating line chart
@app.callback(
    Output('cases-line-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_cases_line_chart(selected_country):
    filtered_data = df[df['country'] == selected_country]
    
    fig = px.line(filtered_data, x='date', y='total_cases', title=f'COVID-19 Case Progression in {selected_country}')
    return fig

# Callback for bar chart (death vs recovery rates)
@app.callback(
    Output('death-recovery-bar-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_death_recovery_bar_chart(selected_country):
    filtered_data = df[df['country'] == selected_country]
    
    fig = go.Figure(data=[
        go.Bar(name='Total Deaths', x=filtered_data['date'], y=filtered_data['total_deaths']),
        go.Bar(name='Total Recoveries', x=filtered_data['date'], y=filtered_data['total_recoveries'])
    ])
    
    fig.update_layout(barmode='group', title=f'Death vs Recovery Rates in {selected_country}')
    return fig

# Callback for Choropleth map
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_choropleth_map(selected_country):
    latest_data = df.groupby('country').max().reset_index()
    
    fig = px.choropleth(latest_data, locations='country', locationmode='country names',
                        color='total_cases', hover_name='country',
                        title='Total COVID-19 Cases by Country',
                        color_continuous_scale='Blues')
    return fig

# Callback for heatmap (case density)
@app.callback(
    Output('cases-heatmap', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_cases_heatmap(selected_country):
    heatmap_data = df[df['country'] == selected_country]
    heatmap_data['new_case_rate'] = heatmap_data['new_cases'] / heatmap_data['population'] * 1000000
    
    fig = px.density_heatmap(heatmap_data, x='date', y='new_case_rate', title=f'Case Density in {selected_country}')
    return fig

# Callback for Pie chart (active vs recovered cases)
@app.callback(
    Output('active-recovered-pie-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_active_recovered_pie_chart(selected_country):
    latest_data = df[df['country'] == selected_country].iloc[-1]
    active_cases = latest_data['total_cases'] - (latest_data['total_recoveries'] + latest_data['total_deaths'])
    recovered_cases = latest_data['total_recoveries']
    
    fig = go.Figure(data=[go.Pie(labels=['Active Cases', 'Recovered Cases'], 
                                 values=[active_cases, recovered_cases])])
    
    fig.update_layout(title=f'Active vs Recovered Cases in {selected_country}')
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True,port=8051)
