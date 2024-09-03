import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pickle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

file = open('map_list/list_g', 'rb')
G = pickle.load(file)
file.close()

class Node:
    def __init__(self, id_, x, y):
        self.id = id_
        self.coords = [x, y]
        self.outgoings = []

node_dict = {}
for node_id in G.nodes:
    x, y = G.nodes[node_id]['x'], G.nodes[node_id]['y']
    node_dict[node_id] = Node(node_id, x, y)

for u, v, _ in G.edges(data=True):
    node_dict[u].outgoings.append(node_dict[v])

