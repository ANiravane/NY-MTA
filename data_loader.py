import pandas as pd
from functools import lru_cache
import os

@lru_cache(maxsize=None)
def load_parquet(filepath = "./MTA Metadata/gtfs_routes.parquet"):
    return pd.read_parquet(filepath)

@lru_cache(maxsize=None)
def load_mta_hourly_dataset():
    data_dict = {}
    for year in global_config.years:
        data_dict[year] = load_parquet(os.path.join(global_config.aggr_data_dir, f"hourly_per_station_{year}.parquet"))
    return data_dict

import global_config
mta_hourly_ridership = load_mta_hourly_dataset()
station_complex_hierarchy = load_parquet(global_config.filepath['station_complex_hierarchy'])
stop_times = load_parquet(global_config.filepath['stop_times'])
stops = load_parquet(global_config.filepath['stops'])
shapes = load_parquet(global_config.filepath['shapes'])
routes = load_parquet(global_config.filepath['routes'])
routes_shapes = load_parquet(global_config.filepath['routes_shapes'])
trips = load_parquet(global_config.filepath['trips'])
stop_to_station = load_parquet(global_config.filepath['stop_to_station'])