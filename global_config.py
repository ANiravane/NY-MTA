import os, sys

# Variables
years = [2024, 2023]
trips_port = 8050
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
theme_colors = {2024: "firebrick", 2023: "darkslateblue", 2022: "darkgoldenrod", 2021: "darkseagreen", 2020: "darkorchid"}
base_dir = os.getcwd()
aggr_data_dir = os.path.join(base_dir, "Aggregated_ridership/")
gtfs_data_dir = os.path.join(base_dir, "GTFS Subway/")
metadata_data_dir = os.path.join(base_dir, "MTA Metadata/")

filepath = {
    'station_complex_hierarchy' : os.path.join(metadata_data_dir, f'station_complex_hierarchy.parquet'),
    'stop_times' : os.path.join(metadata_data_dir, "gtfs_stop_times.parquet"),
    'stops' : os.path.join(metadata_data_dir, "gtfs_stops.parquet"),
    'shapes' : os.path.join(metadata_data_dir, "gtfs_shapes.parquet"),
    'routes' : os.path.join(metadata_data_dir, "gtfs_routes.parquet"),
    'routes_shapes' : os.path.join(metadata_data_dir, "gtfs_routes_shapes.parquet"),
    'stop_to_station' : os.path.join(metadata_data_dir, "gtfs_stop_closest_station.parquet"),
    'trips' : os.path.join(metadata_data_dir, "gtfs_trips.parquet")
}

days_of_week = {
    "Full Week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Weekend": ["Saturday", "Sunday"],
    "Weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
}

# from data_loader import mta_hourly_ridership
# stations = sorted(mta_hourly_ridership[years[0]]["station_complex_id"].unique())