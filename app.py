import global_config, data_loader, utility
from data_loader import hourly_ridership, stations, routes, routes_shapes, shape_geometry

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit.components.v1 import html as st_html

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

import os, subprocess, sys, time, atexit

st.set_page_config(page_title="MTA Dashboard", layout="wide")
    
@st.cache_data
def render_routes(selected_routes = None, show_gen_shapes = False):

    fig = go.Figure()

    if not selected_routes:
        selected_routes = routes['route_id'].unique()

    for route_id in selected_routes:
        color = utility.get_route_colour(route_id)
        route_long_name = routes.loc[routes['route_id'] == route_id, 'route_long_name'].iloc[0]

        filtered_shapes = routes_shapes[(routes_shapes['route_id'] == route_id)
                                        & (routes_shapes['shape_for_map'])]['shape_id'].unique()
        
        filtered_shape_geometry = shape_geometry[shape_geometry['shape_id'].isin(filtered_shapes)]
        for shape_idx, (shape_id, shape_df) in enumerate(filtered_shape_geometry.groupby("shape_id")):
            shape_df.sort_values(by = 'shape_pt_sequence', inplace=True)
            fig.add_trace(go.Scattermap(
                mode="lines",
                lon=shape_df["shape_pt_lon"],
                lat=shape_df["shape_pt_lat"],
                line=dict(width=4, color=color), 
                name=f"{route_id} {route_long_name}" if shape_idx == 0 else None,  # only show legend once
                legendgroup=route_id,       # group shapes of the same route
                showlegend=(shape_idx == 0)
            ))

    fig.add_trace(go.Scattermap(
        mode='markers+text',
        lon=stations["longitude"],
        lat=stations["latitude"],
        marker = go.scattermap.Marker(
            size = 14,
            color = 'black'
        ),
        text = stations['station_complex_id'],
        textfont=dict(size=14, color='black'),
        textposition='top center',
        hovertext=stations['station_complex'],
        hoverinfo='text',
        name='Stations'
    ))


    fig.update_layout(
        mapbox_style="carto-positron",  # or "open-street-map", "white-bg", etc.
        mapbox=dict(
            center=dict(lat=stations['latitude'].mean(), lon=stations['longitude'].mean()),  # Set a center if needed
            zoom=10
        ),
        height=800,  # Increase height
        width=1200,  # Optional: for wide layouts
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            title="Routes",
            orientation="v",            # or "h" for horizontal
            x=0.01,                     # from 0 (left) to 1 (right)
            y=0.99,                     # from 0 (bottom) to 1 (top)
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",  # optional background
            bordercolor="black",
            borderwidth=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------- PAGE NAVIGATION -------------------- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Through the day", "Overview", "Temporal", "Spatial", "Fare Types"])

# -------------------- THROUGH THE DAY -------------------- #
if page == "Through the day":
    # def _spawn_dash():
    #     dash_cmd = [sys.executable, 'dashapp_trips.py']
    #     proc = subprocess.Popen(dash_cmd, env = os.environ)
    #     time.sleep(1.0)
    #     return proc

    # def ensure_fresh_dash():
    #     old = st.session_state.get('_dash_trips_proc')
    #     if old and old.poll() is None:
    #         old.kill()
    #     new = _spawn_dash()
    #     st.session_state['_dash_trips_proc'] = new 
    #     atexit.register(new.kill)

    # ensure_fresh_dash()
    
    st.title("Through the Day")
    st_html(
        f'<iframe src="http://localhost:{global_config.trips_port}" style="border:none;width:100%;height:600px;" scrolling="auto"></iframe>',
        height=620,
    )

    
# -------------------- OVERVIEW PAGE -------------------- #
elif page == "Overview":
    st.title("📊 Overview")

    # -------------------- SHARED MASTER FILTER -------------------- #
    st.sidebar.title("Ranking Criteria")
    select_n = st.sidebar.number_input("Select N", min_value=1, max_value=10, value=5, step=1)

    ranking_criteria = st.sidebar.selectbox('Show me top N stations ranked by', options = 
                                    ['Total Ridership in 2024', 'YoY Growth', 'Day of week', 'Time of Day'])
    
    if ranking_criteria == 'Total Ridership in 2024':
        top_n_stations = hourly_ridership[2024].groupby('station_complex_id')['ridership'].sum().nlargest(select_n).index.tolist()
        st.dataframe(stations[stations['station_complex_id'].isin(top_n_stations)])
        selected_stn_data = {}
        remng_stn_data = {}
        for year in global_config.years:
            selected_stn_data[year] = hourly_ridership[year][hourly_ridership[year]['station_complex_id'].isin(top_n_stations)]
            remng_stn_data[year] = hourly_ridership[year][~hourly_ridership[year]['station_complex_id'].isin(top_n_stations)]
            
            
        with st.expander("🎯 Ridership Supported", expanded=True):
            
            fig = go.Figure()
            
            st.write('Comparing over the past 12 months')

            sel_agg_data = selected_stn_data[2024].groupby(
                    ['date'], as_index=False
                ).agg({
                    'ridership': 'sum',
                    'dayofyear': 'first',
                    'date': 'first'
                })

            rem_agg_data = remng_stn_data[2024].groupby(
                    ['date'], as_index=False
                ).agg({
                    'ridership': 'sum',
                    'dayofyear': 'first',
                    'date': 'first'
                })

            fig.add_trace(go.Scatter(
                x=sel_agg_data['dayofyear'],
                y=sel_agg_data['ridership'],
                mode='lines+markers',
                name=f'Top {select_n}',
                line=dict(color='blue', width=2),
                marker=dict(size=4),
                text = pd.to_datetime(sel_agg_data['date']).dt.strftime('%b %d') + f', 2024 (' + pd.to_datetime(sel_agg_data['date']).dt.strftime('%a') + ')<br>Ridership : ' + sel_agg_data['ridership'].apply(lambda x: f'{x/1e6:.2f}M'),  
                hovertemplate=("%{text}<extra></extra>")
            ))

            fig.add_trace(go.Scatter(
                x=rem_agg_data['dayofyear'],
                y=rem_agg_data['ridership'],
                mode='lines+markers',
                name=f'Remaining',
                line=dict(color='red', width=2),
                marker=dict(size=4),
                text = pd.to_datetime(rem_agg_data['date']).dt.strftime('%b %d') + f', 2024 (' + pd.to_datetime(rem_agg_data['date']).dt.strftime('%a') + ')<br>Ridership : ' + rem_agg_data['ridership'].apply(lambda x: f'{x/1e6:.2f}M'),  
                hovertemplate=("%{text}<extra></extra>")
            ))

            fig.update_layout(
                title='Daily MTA Ridership: Year-over-Year Comparison',
                xaxis_title='Day of Year',
                yaxis_title='Total Ridership',
                xaxis=dict(
                    tickmode='array',
                    tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                ),
                yaxis=dict(
                    tickformat=',.1s' 
                ),
                hovermode='x unified',
                template='plotly_white',
                legend=dict(bgcolor='rgba(255,255,255,0.7)', bordercolor='black', borderwidth=1)
            )

            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("🎯 Total Ridership Over the Years", expanded=True):
            
            fig = go.Figure()

            for year in global_config.years:
                fig.add_trace(go.Scatter(
                    x=selected_stn_data[year]['dayofyear'],
                    y=selected_stn_data[year]['ridership'],
                    mode='lines+markers',
                    name=f'{year}',
                    line=dict(color=global_config.theme_colors[year], width=2),
                    marker=dict(size=4),
                    text = pd.to_datetime(selected_stn_data[year]['date']).dt.strftime('%b %d') + f', {year} (' + pd.to_datetime(selected_stn_data[year]['date']).dt.strftime('%a') + ')<br>Ridership : ' + selected_stn_data[year]['ridership'].apply(lambda x: f'{x/1e6:.2f}M'),  
                    hovertemplate=("%{text}<extra></extra>")
                ))

            fig.update_layout(
                title='Daily MTA Ridership: Year-over-Year Comparison',
                xaxis_title='Day of Year',
                yaxis_title='Total Ridership',
                xaxis=dict(
                    tickmode='array',
                    tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                ),
                yaxis=dict(
                    tickformat=',.1s' 
                ),
                hovermode='x unified',
                template='plotly_white',
                legend=dict(bgcolor='rgba(255,255,255,0.7)', bordercolor='black', borderwidth=1)
            )

            st.plotly_chart(fig, use_container_width=True)

    elif ranking_criteria == 'YoY Growth':
        stacked_data = hourly_ridership[2024].copy()
        stacked_data['year'] = 2024
        hourly_ridership[2024]['day_num'] = hourly_ridership[2024]['dayofyear']
        max_day_num = hourly_ridership[2024]['day_num'].max()
        for year in global_config.years[1:]:
            hourly_ridership[year]['year'] = year
            hourly_ridership[year]['day_num'] = hourly_ridership[year]['dayofyear'] + max_day_num
            stacked_data = pd.concat([stacked_data, hourly_ridership[year]], axis=0, ignore_index=True)
        stacked_data['ridership'] = stacked_data['ridership'].drop_duplicates(inplace=True)

        stacked_data = stacked_data.groupby(['station_complex_id', 'day_num']).agg({
            'ridership': 'sum'
            # 'transfers': 'sum'
            }).reset_index()
        results = []

        for station_id, group in stacked_data.groupby('station_complex_id'):
            # Sort by timestamp
            group = group.sort_values('day_num')
            
            # Encode time as ordinal (e.g. hour number from start)
            group['time_idx'] = np.arange(len(group))
            
            # Fit linear regression: time_idx → ridership
            X = group['time_idx'].values.reshape(-1, 1)
            y = group['ridership'].values

            if len(X) > 1:
                model = LinearRegression().fit(X, y)
                slope = model.coef_[0]
                results.append({
                    'station_complex_id': station_id,
                    'slope': slope
                })

        trend_df = pd.DataFrame(results)

        growth_criteria = st.sidebar.selectbox('YoY Growth', options = 
                                ['Positive', 'Negative', 'Consistent'])
        if growth_criteria == "Positive":
            top_n_stations = trend_df['slope'].nlargest(select_n).index.tolist()
        elif growth_criteria == "Negative":
            top_n_stations = trend_df['slope'].nsmallest(select_n).index.tolist()
        elif growth_criteria == "Consistent":
            top_n_stations = trend_df['slope'].abs().nsmallest(select_n).index.tolist()
        st.dataframe(stations[stations['station_complex_id'].isin(top_n_stations)])


    elif ranking_criteria == 'Day of week':
        selected_dow = st.sidebar.selectbox("Time of Week", options =
                                            global_config.days_of_week.keys())
        selected_days = global_config.days_of_week[selected_dow]
        df = hourly_ridership[2024][hourly_ridership[2024]['day_of_week'].isin(selected_days)]
        month_range = st.sidebar.slider("Select Time Range (Jan - Dec 2024)", 1, 12, (9, 12), key="month_range")

        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df = df[(df["month"] >= month_range[0]) & (df["month"] <= month_range[1])]


        df = df.groupby(['station_complex_id', 'date']).agg({
            'ridership' : 'sum',
            'day_of_week' : 'first'
        }).reset_index()
        df = df.groupby(['station_complex_id', 'day_of_week']).agg({
            'ridership' : 'mean'
        }).reset_index()
        df = df.groupby(['station_complex_id']).agg({
            'ridership' : 'mean'
        }).reset_index()
        

        top_n_stations = df['station_complex_id'].nlargest(select_n).index.tolist()
        st.dataframe(stations[stations['station_complex_id'].isin(top_n_stations)])

    elif ranking_criteria == 'Time of Day':

        df = data_loader.load_parquet()
        hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (6, 20), key="hour_range")
        df_local = df[(df["hour"] >= hour_range[0]) & (df["hour"] <= hour_range[1])]

        top_n_stations = hourly_ridership[2024].groupby('station_complex_id')['ridership'].sum().nlargest(select_n).index.tolist()
        st.dataframe(stations[stations['station_complex_id'].isin(top_n_stations)])
    

# -------------------- TEMPORAL PAGE -------------------- #
elif page == "Temporal":
    st.title("⏱️ Temporal Patterns")

    with st.expander("Hourly Distribution Across All Stations", expanded=True):
        df = data_loader.load_parquet()
        hour_range = st.slider("Select Hour Range", 0, 23, (6, 20), key="temporal_hour")
        df_local = df[(df["hour"] >= hour_range[0]) & (df["hour"] <= hour_range[1])]

        fig = px.box(
            df_local,
            x="hour",
            y="avg_hourly_riders",
            color="day_of_week",
            title="Hourly Ridership Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- SPATIAL PAGE -------------------- #
elif page == "Spatial":
    st.title("🗺️ Station-Level Map")

    st.sidebar.header("Map Filters")
    selected_routes = st.sidebar.multiselect(
        "Select Subway Line(s)",
        options=routes['route_id'].unique(),
        default=routes['route_id'].unique()
    )
    
    render_routes(selected_routes)

# -------------------- FARE TYPES PAGE -------------------- #
elif page == "Fare Types":
    st.title("🎟️ Fare Type Comparison")

    with st.expander("Comparison by Fare Type", expanded=True):
        df = data_loader.load_parquet()
        hour = st.slider("Select Hour", 0, 23, 9, key="fare_hour")
        df_local = df[df["hour"] == hour]

        fig = px.pie(
            df_local,
            names="fare_class_category",
            values="avg_hourly_riders",
            title=f"Fare Class Share at Hour {hour}"
        )
        st.plotly_chart(fig, use_container_width=True)
