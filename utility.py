from data_loader import routes
import global_config

import streamlit as st
import pandas as pd
import datetime

@st.cache_data 
def first_monday(year):
    dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-01-07')
    monday = dates[dates.weekday == 0][0]
    return monday.date()

@st.cache_data
def lonlat_to_xy(lon, lat):
    x, y = global_config.transformer.transform(lon, lat)
    return x, y

colour_map = {
    rid: f"#{hex}" 
    for rid, hex in zip(routes.route_id, routes.route_color)
    if pd.notna(hex)
}

@st.cache_data
def get_route_colour(route_id: str, default="#9E9E9E") -> str:
    return colour_map.get(route_id, default)
# Use GS as Default 

@st.cache_data
def convert_minutes_to_datetime(minutes_since_midnight):
    if pd.isna(minutes_since_midnight): # Handle potential NaN values
        return None
    reference_date = datetime.date.today() # Or any fixed date, e.g., datetime.date(2000, 1, 1)
    hours = int(minutes_since_midnight // 60)
    minutes = int(minutes_since_midnight % 60)
    # Ensure hours don't exceed 23 (for values > 1439 minutes, which is 23:59)
    # This handles cases where minutes_since_midnight might be > 1439 (e.g., 25 hours)
    hours = hours % 24
    return datetime.datetime.combine(reference_date, datetime.time(hour=hours, minute=minutes))

def get_parent_value(child_col, child_val, parent_col, table):
    return table[table[child_col] == child_val][parent_col].iloc[0]