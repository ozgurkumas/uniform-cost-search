import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pickle

G = ox.graph_from_place("Manhattan, New York, USA", network_type='drive')
G = ox.utils_graph.get_largest_component(G, strongly=True)

with open('file.pkl', 'wb') as file: 
    pickle.dump(G, file)
