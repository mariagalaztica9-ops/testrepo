# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get all launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in launch_sites
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Add a pie chart to show launch success counts
    html.Div(
        dcc.Graph(id='success-pie-chart')
    ),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        }
    ),

    # TASK 4: Add a scatter chart to show payload and launch success
    html.Div(
        dcc.Graph(id='success-payload-scatter-chart')
    )
])


# TASK 2: Callback for the launch site dropdown and pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        # Show total successful launches by site
        success_df = spacex_df[spacex_df['class'] == 1]

        fig = px.pie(
            success_df,
            names='Launch Site',
            title='Total Success Launches By Site'
        )

    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        # Show successful versus failed launches
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs. Failed Launches for {entered_site}',
            labels={
                'class': 'Launch Outcome'
            }
        )

        fig.update_traces(
            labels=[
                'Failure' if label == 0 else 'Success'
                for label in fig.data[0].labels
            ]
        )

    return fig


# TASK 4: Callback for launch site and payload slider
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):

    # Filter by payload range
    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Filter by launch site if a specific site is selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Launch Success',
        labels={
            'Payload Mass (kg)': 'Payload Mass (Kg)',
            'class': 'Launch Outcome',
            'Booster Version Category': 'Booster Version'
        }
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)