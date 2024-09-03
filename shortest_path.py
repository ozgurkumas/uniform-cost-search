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

def calcCost(A: Node, B: Node):
    dist = ((A.coords[0] - B.coords[0])**2 + (A.coords[1] - B.coords[1])**2)**0.5
    return dist

def find_shortest_path(startState, goalState):
    class PriorityQueue:
        def __init__(self):
            self.queue = []

        def enqueue(self, list_):
            self.queue.append(list_)

        def dequeue(self, index):
            self.queue.pop(index)

        def peek(self):
            index = 0
            i = len(self.queue) - 1
            min_cost = self.queue[-1][1]
            while i >= 0:
                if self.queue[i][1] <= min_cost:
                    min_cost = self.queue[i][1]
                    index = i
                i -= 1
            return index

    prioQueue = PriorityQueue()
    visitedList = []
    parent = {}

    prioQueue.enqueue([startState, 0])
    parent[startState] = None

    while True:
        index = prioQueue.peek()
        currentState = prioQueue.queue[index][0]

        if currentState == goalState:
            break
        else:
            if currentState not in visitedList:
                for outgoing in currentState.outgoings:
                    if outgoing not in visitedList:
                        prioQueue.enqueue([outgoing, calcCost(currentState, outgoing) + prioQueue.queue[index][1]])
                        parent[outgoing] = currentState
                visitedList.append(currentState)
            prioQueue.dequeue(index)

    listPathNodes = []
    currentNode = goalState
    while currentNode is not None:
        listPathNodes.append(currentNode)
        currentNode = parent[currentNode]

    listPathNodes.reverse()
    return [node.id for node in listPathNodes]


selected_nodes = []
def on_click(event):
    if event.button == 1 and event.inaxes is not None:
        x_click, y_click = event.xdata, event.ydata
        closest_node = ox.distance.nearest_nodes(G, x_click, y_click)
        selected_nodes.append(closest_node)

        x = G.nodes[closest_node]["x"]
        y = G.nodes[closest_node]["y"]
        ax.scatter(x, y, s=100, c="r", alpha=0.5, edgecolor="none")

        if len(selected_nodes) == 2:
            startNode = selected_nodes[0]
            goalNode = selected_nodes[1]

            startState = node_dict[startNode]
            goalState = node_dict[goalNode]

            route = find_shortest_path(startState, goalState)

            ax.clear()

            ox.plot_graph(G, node_size=10, edge_linewidth=1, ax=ax, show=False, close=False)

            ox.plot_graph_route(G, route, route_color='g', route_linewidth=4, node_size=10, bgcolor='white', ax=ax, show=False)

            x = (G.nodes[startNode]["x"], G.nodes[goalNode]["x"])
            y = (G.nodes[startNode]["y"], G.nodes[goalNode]["y"])
            ax.scatter(x, y, s=100, c="r", alpha=0.5, edgecolor="none") 

            canvas.draw()

            selected_nodes.clear()
        
        canvas.draw()




