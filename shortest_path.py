import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pickle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

file = open('map_list/list_g', 'rb')
G = pickle.load(file)
file.close()
