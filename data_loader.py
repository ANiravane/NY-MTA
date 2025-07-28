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
        data_dict[year] = load_parquet(os.path.join(global_config.aggr_rs_dir, f"hourly_ridership_{year}.parquet"))
    return data_dict

import global_config
hourly_ridership = load_mta_hourly_dataset()
stations = load_parquet(global_config.filepath['stations'])
stops = load_parquet(global_config.filepath['stops'])
routes = load_parquet(global_config.filepath['routes'])
routes_shapes = load_parquet(global_config.filepath['routes_shapes'])
shape_geometry = load_parquet(global_config.filepath['shape_geometry'])
shapes_trips = load_parquet(global_config.filepath['shapes_trips'])
trip_stop_times = load_parquet(global_config.filepath['trip_stop_times'])


# network implementation
# import networkx as nx

# nx_MTA_graph = nx.DiGraph()

# for stop in stops['stop_id'].tolist():
#     nx_MTA_graph.add_edge(stop, type = 'stop')

# for station in stations['station_complex_id'].tolist():
#     nx_MTA_graph.add_edge(station, type = 'station')

# for route in routes['route_id'].tolist():
#     nx_MTA_graph.add_edge(route, type = 'route')

# for shape in routes_shapes['shap_id'].tolist():
#     nx_MTA_graph.add_edge(station, type = 'station')

# for shape_id, route_id in zip(routes_shapes['shape_id'], routes_shapes['route_id']):
#     nx_MTA_graph.add_edge(shape_id, route_id, relationship = 'belongs_to')
#     nx_MTA_graph.add_edge(route_id, shape_id, relationship = 'follows')
 

# def get_required_key(graph, source_node, target_type, max_depth=4, singular=True):
#     visited = set()
#     to_visit = [(source_node, 0)]
#     result = []

#     while to_visit:
#         current, depth = to_visit.pop()
#         if depth > max_depth:
#             continue
#         if current in visited:
#             continue
#         visited.add(current)

#         if graph.nodes[current].get("type") == target_type and depth > 0:
#                 if singular:
#                     return current.
#             result.append(current)

#         for neighbor in graph.successors(current):
#             to_visit.append((neighbor, depth + 1))
    


#     return result
