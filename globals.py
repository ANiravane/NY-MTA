import os
from pyproj import Transformer

# Variables
years = [2024, 2023]
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
theme_colors = {2024: "firebrick", 2023: "darkslateblue", 2022: "darkgoldenrod", 2021: "darkseagreen", 2020: "darkorchid"}
base_dir = os.getcwd()
aggr_data_dir = os.path.join(base_dir, "Aggregated_ridership/")
gtfs_data_dir = os.path.join(base_dir, "GTFS Subway/")
metadata_data_dir = os.path.join(base_dir, "MTA Metadata/")