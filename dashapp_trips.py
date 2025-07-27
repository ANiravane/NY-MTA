from data_loader import routes_shapes, stop_times, stops
import data_loader, global_config, utility

import argparse, datetime
import pandas as pd

from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go

def route_fig_base_map(shapes_xy, stops_xy):
    fig = go.Figure()
    color = "#C6C5C1"
    # route_name = global_data['routes'].loc[global_data['routes']['route_id'] == route_id, 'route_long_name'].iloc[0]

    for _, shape_df in shapes_xy.groupby("shape_id"):
        shape_df.sort_values(by = 'shape_pt_sequence', inplace=True)
        # Routes mapped in XY plane - one trace per shape
        fig.add_trace(go.Scatter(
            mode="lines",
            x=shape_df["x"],
            y=shape_df["y"],
            line=dict(width=2, color=color)
        ))

    # Stops encountered on each route
    fig.add_trace(go.Scatter(
        mode="markers",
        x=stops_xy["x"],
        y=stops_xy["y"],
        marker=dict(size=10, color=color)
    ))
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,       
            showticklabels=False, 
            zeroline=False        
        ),
        showlegend = False 
    )

    return fig

selected_routes = ['7', 'M', 'E']
shapes = data_loader.load_parquet(global_config.filepath['shapes'])

shapes_xy = shapes.copy()
filtered_shapes = routes_shapes[((routes_shapes['route_id'].isin(selected_routes))
                                    & (routes_shapes['source'] == 'MTA')) 
                                    | ((routes_shapes['route_id'].isin(selected_routes))
                                    & (routes_shapes['source'] == 'Generated')
                                    & (routes_shapes['existing_shapes'] == False))]
filtered_shapes = filtered_shapes['shape_id']
shapes_xy = shapes_xy[shapes_xy['shape_id'].isin(filtered_shapes)]

shapes_xy[['x', 'y']] = [utility.lonlat_to_xy(lon, lat) for lon, lat in zip(shapes_xy['shape_pt_lon'], shapes_xy['shape_pt_lat'])]
center_x = (shapes_xy['x'].max() - shapes_xy['x']. min()).mean()
center_y = (shapes_xy['y'].max() - shapes_xy['y']. min()).mean()

shapes_xy['x'] = (shapes_xy['x'] - center_x) / 1000
shapes_xy['y'] = (shapes_xy['y'] - center_y) / 1000

# stop_times = stop_times[stop_times['arrival_time'] <= 360]
stop_times = stop_times[stop_times['route_id'].isin(selected_routes)]

stop_times[['x', 'y']] = [utility.lonlat_to_xy(lon, lat) for lon, lat in zip(stop_times['stop_lon'], stop_times['stop_lat'])]

stop_times['x'] = (stop_times['x'] - center_x) / 1000
stop_times['y'] = (stop_times['y'] - center_y) / 1000

stops_xy = stops[stops['stop_id'].isin(stop_times['stop_id'].unique())]
stops_xy[['x', 'y']] = [utility.lonlat_to_xy(lon, lat) for lon, lat in zip(stops_xy['stop_lon'], stops_xy['stop_lat'])]

stops_xy['x'] = (stops_xy['x'] - center_x) / 1000
stops_xy['y'] = (stops_xy['y'] - center_y) / 1000

stop_order = {stop: i+1 for i, stop in enumerate(stop_times['stop_id'].unique())}
x_axis_to_stop = {}
for key, value in stop_order.items():
    x_axis_to_stop[value] = key

route_fig = route_fig_base_map(shapes_xy, stops_xy)
trip_line_fig = go.Figure()

for _, (trip_id, trip_df) in enumerate(stop_times.groupby("trip_id")):
    route_id = trip_df.iloc[0]['route_id']
    color = utility.get_route_colour(route_id)
    trip_df['stop_order_x'] = trip_df["stop_id"].apply(lambda x: stop_order[x])
    stop_range = pd.DataFrame({'stop_order_x': range(trip_df['stop_order_x'].min(), trip_df['stop_order_x'].max() + 1)})
    trip_df = stop_range.merge(trip_df, on='stop_order_x', how='left')
    trip_df['arrival_time_datetime'] = trip_df['arrival_time'].apply(utility.convert_minutes_to_datetime)

    # Trips throughout the day - one trace per trip
    trip_line_fig.add_trace(go.Scatter(
        mode="lines",
        x=trip_df['stop_order_x'],
        y=trip_df["arrival_time_datetime"],
        line=dict(width=1, color=color),
        customdata=trip_df[['stop_id', 'route_id', 'stop_lat', 'stop_lon']],
        name=route_id
    ))

start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0)) # 12:00 AM
end_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59, 59)) # 11:59:59 PM
trip_line_fig.update_layout(
    hovermode='y unified',
    shapes=[], # Initial empty shapes for hover line
    annotations=[],
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=dict(
        autorange=False, # IMPORTANT: Set to False when you manually set 'range'
        range=[end_of_day, start_of_day],
        type='date',           # Set the y-axis type to 'date' for time values
        # autorange='reversed',  # This puts 12 AM (earliest time) at the top
        tickformat='%I:%M %p', # Format ticks to show hour, minute, and AM/PM (e.g., 12:00 AM)
        dtick='H1',            # Set tick interval to 1 hour ('H1' for hourly ticks)
        showgrid=True,         # It's often helpful to show grid lines for time axes
        showticklabels=True,
        zeroline=False
    ),
    showlegend = False 
)

app = Dash(__name__)

app.layout = html.Div([
    # Left Fixed Panel (Map - route_fig)
    html.Div([
        dcc.Graph(id='route_fig', figure=route_fig,
                #   config={'displayModeBar': False},
                  style={
                      'height': '100vh', # The graph itself takes the full height of its fixed parent
                      'width': '100%',   # The graph takes the full width of its fixed parent
                      'backgroundColor': 'white'
                      })
    ], style={
        'position': 'fixed', # This makes the div fixed relative to the viewport
        'top': 0,            # Position it at the top of the viewport
        'left': 0,           # Position it at the left of the viewport
        'height': '100vh',   # Make it take the full viewport height
        'width': '30%',      # Make it take 30% of the viewport width
        'backgroundColor': 'white',
        'borderRight': '1px solid #ddd', # Visual separator
        'overflow': 'hidden',# Prevent any scrolling within the fixed map area itself
        'zIndex': 10         # Ensure it stays on top of other content
    }),

    # Right Scrollable Content Area (Trip Line Graph - trip_line_fig)
    html.Div([
        dcc.Graph(id='trip_line_fig', figure=trip_line_fig, 
                #   config={'displayModeBar': False},
                style={
                    'height': '1800px',
                    # 'height': 'auto',  # Allow the graph to extend vertically as much as needed.
                                  # This is crucial for it to "spill over" and cause the PAGE to scroll.
                })
    ], style={
        'marginLeft': '30%',    # Pushes this content area to the right, past the fixed left panel
        'width': '70%',         # Takes up the remaining 70% of the viewport width
        'paddingLeft': '20px',  # Adds some space between the fixed left panel and the graph
        # 'overflowY': 'auto',  # Removed: The page will now handle the primary scrolling
        'height': 'auto',       # Removed: This div will now expand naturally with its content
        'boxSizing': 'border-box' # Ensures padding is included within the 70% width
    })
], style={
    'width': '100vw',        # Ensure the main container spans the full viewport width
    # 'height': '100vh',     # Removed: Allow the page to grow vertically
    'margin': 0,             # Remove default body margin
    'padding': 0,            # Remove default body padding
    # 'overflow': 'hidden'   # Removed: Allow the page to scroll
})

@app.callback(
    Output('trip_line_fig', 'figure'),
    [Input('trip_line_fig', 'hoverData')],
    [State('trip_line_fig', 'figure')]  
)
def update_fig2_on_hover(hover, fig):
    # fig = go.Figure(current_fig2_figure)
    fig.layout.shapes = []
    fig.layout.annotations = []
    if hover:
        hover_y_plotly_num = hover['points'][0]['y']
        hover_y_dt = datetime.datetime.fromtimestamp(hover_y_plotly_num / 1000)

        # Add a horizontal line shape
        fig.add_shape(
            type="line",
            x0=fig.layout.xaxis.range[0], # Start at the left of the x-axis range
            y0=hover_y_dt,
            x1=fig.layout.xaxis.range[1], # End at the right of the x-axis range
            y1=hover_y_dt,
            line=dict(
                color="blue", # Changed color for horizontal line
                width=2,
                dash="dashdot",
            )
        )

        annotations = []
        for point in hover['points']:
            trace_name = point['data']['name'] # Get the name of the trace (e.g., 'Trip 1', 'Trip 2')
            # point['x'] is the x-coordinate (Value) of the intersection; The y-value is the common hover_y_dt
            stop_id = x_axis_to_stop[point['x']]
            formatted_time = hover_y_dt.strftime('%I:%M %p')

            annotations.append(
                dict(
                    x=stop_id,
                    y=hover_y_dt, # Use the common hovered datetime object for y position
                    xref="x",
                    yref="y",
                    text=f"{trace_name}: Value={stop_id}<br>Time={formatted_time}",
                    showarrow=True,
                    arrowhead=2,
                    ax=20, # Adjust annotation arrow offset
                    ay=-40,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="#c7c7c7",
                    borderwidth=1,
                    borderpad=4,
                    font=dict(size=10, color="#333"),
                )
            )
        fig.layout.annotations = annotations
    return fig

# --- Callback 2: Update fig1 based on fig2's hover ---
@app.callback(
    Output('route_fig', 'figure'),
    [Input('trip_line_fig', 'hoverData')],
    [State('route_fig', 'figure')]  
)
def update_fig1_on_fig2_hover(fig2_hoverData, fig):
    # fig = go.Figure(current_fig1_figure) # 'fig' here is a mutable copy of fig1

    if fig2_hoverData:
        hover_y_plotly_num = fig2_hoverData['points'][0]['y']
        print(hover_y_plotly_num)

        # fig.add_trace(go.Scatter(
        #     mode="markers",
        #     x=stops_xy["x"],
        #     y=stops_xy["y"],
        #     marker=dict(size=10, color=color)
        # ))

    return fig # Return the modified fig (which updates fig1)

parser = argparse.ArgumentParser()
parser.add_argument("--port", default=8050)
args = parser.parse_args()

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(args.port), dev_tools_hot_reload = True)