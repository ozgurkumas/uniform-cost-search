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


def zoom(event):
    base_scale = 1.1
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata

    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        scale_factor = 1

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
    ax.set_ylim([ydata - new_height * (1 - rely)])

    canvas.draw()

start_drag_x = None
start_drag_y = None

def on_right_press(event):
    global start_drag_x, start_drag_y
    start_drag_x = event.xdata
    start_drag_y = event.ydata

def on_right_drag(event):
    if event.button == 3 and event.inaxes is not None:
        if start_drag_x is None or start_drag_y is None:
            return

        try:
            dx = start_drag_x - event.xdata
            dy = start_drag_y - event.ydata

            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            ax.set_xlim([cur_xlim[0] + dx, cur_xlim[1] + dx])
            ax.set_ylim([cur_ylim[0] + dy, cur_ylim[1] + dy])
        except Exception as e:
            pass

        canvas.draw()

def on_right_release(event):
    global start_drag_x, start_drag_y
    start_drag_x = None
    start_drag_y = None

root = tk.Tk()
root.wm_title("Map Visualization")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=1)

def plot_map():
    global ax, canvas

    panel_width = 1200
    panel_height = 600

    fig, ax = ox.plot_graph(
        G, 
        node_size=10, 
        edge_linewidth=1, 
        show=False, 
        close=False,
        figsize=(panel_width/100, panel_height/100),
        dpi=600 
    )

    frame.config(width=panel_width, height=panel_height)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    canvas.mpl_connect('button_press_event', on_click)
    canvas.mpl_connect('scroll_event', zoom)
    canvas.mpl_connect('button_press_event', on_right_press)
    canvas.mpl_connect('motion_notify_event', on_right_drag)
    canvas.mpl_connect('button_release_event', on_right_release)

plot_button = tk.Button(root, text="Plot Map", command=plot_map)
plot_button.pack(side=tk.BOTTOM)

tk.mainloop()
