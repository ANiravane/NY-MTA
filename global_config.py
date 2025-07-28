import os, sys

# Variables
years = [2024]
trips_port = 8050
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
theme_colors = {2024: "firebrick", 2023: "darkslateblue", 2022: "darkgoldenrod", 2021: "darkseagreen", 2020: "darkorchid"}
base_dir = os.getcwd()
src_hourly_rs_dir = os.path.join(base_dir, "SRC_Hourly_Ridership/")
src_od_estimate_dir = os.path.join(base_dir, "SRC_OD_Ridership_Estimate/")
src_gtfs_data_dir = os.path.join(base_dir, "SRC_GTFS_Subway/")
src_trains_delayed_dir = os.path.join(base_dir, "SRC_Trains_Delayed/")
aggr_rs_dir = os.path.join(base_dir, "Aggregated_Ridership/")
metadata_dir = os.path.join(base_dir, "MTA_Metadata/")

filepath = {
    'stations': os.path.join(metadata_dir, 'stations.parquet'),
    'stops' : os.path.join(metadata_dir, "stops.parquet"),
    'routes' : os.path.join(metadata_dir, "routes.parquet"),
    'routes_shapes' : os.path.join(metadata_dir, "routes_shapes.parquet"),
    'shape_geometry' : os.path.join(metadata_dir, "shape_geometry.parquet"),
    'shapes_trips' : os.path.join(metadata_dir, "shapes_trips.parquet"),
    'trip_stop_times' : os.path.join(metadata_dir, "trip_stop_times.parquet")
}

days_of_week = {
    "Full Week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Weekend": ["Saturday", "Sunday"],
    "Weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
}

# from data_loader import mta_hourly_ridership
# stations = sorted(mta_hourly_ridership[years[0]]["station_complex_id"].unique())