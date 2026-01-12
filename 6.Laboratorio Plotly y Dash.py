# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Obtener lista de sitios de lanzamiento únicos para el dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}]
launch_site_options += [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=launch_site_options,
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True,
        style={'width': '80%', 'margin': '0 auto'}
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i} Kg' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Filtrar solo lanzamientos exitosos (clase = 1)
        success_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            success_df, 
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        # Filtrar por sitio específico
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            site_df,
            names='class',
            title=f'Success vs Failed Launches for {selected_site}',
            labels={'0': 'Failed', '1': 'Success'}
        )
    return fig

# TASK 4: Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # Filtrar por rango de payload
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Filtrar por sitio si no es 'ALL'
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Crear gráfico de dispersión
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success',
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        hover_data=['Launch Site', 'Payload Mass (kg)']
    )
    
    # Mejorar la visualización del eje Y
    fig.update_yaxes(
        ticktext=['Failed', 'Success'],
        tickvals=[0, 1]
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)