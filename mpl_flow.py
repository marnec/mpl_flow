import matplotlib.pyplot as plt
import numpy as np

class Flow():
    node_counter = 1
    edge_counter = 1
    compass = {
        'e': np.array((1, .5)),
        'w': np.array((0, .5)),
        's': np.array((.5, 0)),
        'n': np.array((.5, 1)),
        'ne': np.array((1, 1)),
        'nw': np.array((0, 1)),
        'se': np.array((1, 0)),
        'sw': np.array((0, 0))}
    
    def __init__(self, fig=None, ax=None, direction='we', arrowprops=None, bbox=None, 
        figsize=None, distance=1, fontsize=None, pad_axis=.01):
        self.nodes = {}
        self.edges = {}
        self.direction = direction
        self.fig = fig
        self.ax = ax 
        self.init_plot(figsize)
        self.distance = distance
        self.arrowprops = self.init_style(dict(arrowstyle="<-"), arrowprops)
        self.bbox = self.init_style(dict(boxstyle="round", fc="w", facecolor='w'), bbox)
        self.global_kwargs=dict(fontsize=fontsize)
        self.pad_axis = pad_axis
    
    @staticmethod
    def roundout(a):
        return np.trunc(a + np.copysign(.5, a))
    
    @staticmethod
    def init_style(style, custom):
        if custom is not None:
            style = {**style, **custom}
        return style
    
    def init_plot(self, figsize=None):
        if not self.fig and not self.ax and figsize:
            self.fig, self.ax = plt.subplots(figsize=figsize)
        else:
            if not self.fig:
                self.fig = plt.gcf()
            if not self.ax:
                self.ax = plt.gca()


        self.start_point = (0, 0.5)
#         self.ax.set_aspect('equal')
        self.ax.axis('off')
        
    def update_boundaries(self):
        coords = np.array([n.annotation.xyann for n in self.nodes.values()])
        
        xlim, ylim = np.vstack([coords.min(axis=0), coords.max(axis=0)]).T
        self.ax.set_xlim(*(xlim+[-self.pad_axis, self.pad_axis]))
        self.ax.set_ylim(*(ylim+[-self.pad_axis, self.pad_axis]))

    
    def node(self, node_id=None, label=None, travel=None, startpoint=None, 
        arrowprops=None, bbox=None, connect=True, distance=None, xlabel=None, xlabel_xy=(0, -.5), edge_kwargs=dict(), **kwargs):
        
        if isinstance(startpoint, (str, int)):
            startpoint = self.nodes.get(startpoint)
            
        if startpoint is None:
            if not self.nodes:
                startpoint = self.start_point
            else:
                startpoint = max([n for n in self.nodes.values()], key=lambda node: node.n)          

        kwargs = {**self.global_kwargs, **kwargs}
        edge_kwargs = {**self.global_kwargs, **edge_kwargs}
        node = Node(self, self.node_counter, node_id, label)
        self.node_counter += 1  
        
        self.nodes[node.id] = node
        
        node.draw(travel, startpoint, arrowprops, bbox, connect, distance, xlabel, xlabel_xy, **kwargs)
        self.update_boundaries()

        edge = None
        if connect is True and isinstance(startpoint, Node):
            eid = edge_kwargs.pop('eid', None)
            elabel = edge_kwargs.pop('label', None)
            edge = self.edge(startpoint, node, eid, elabel, **edge_kwargs)
            self.edges[edge.id] = edge
        return node, edge
    
    def edge(self, a, b, edge_id=None, label=None, tailport=None, headport=None,  arrowprops=None, **kwargs):
        kwargs = {**self.global_kwargs, **kwargs}
        edge = Edge(self, a, b, self.edge_counter, edge_id, label)
        self.edge_counter += 1
        self.edges[edge.id] = edge
        edge.draw(tailport, headport, arrowprops, **kwargs)
        return edge


class Node():
    def __init__(self, masterflow, n, nid=None, label=None):
        self.flow = masterflow
        self.n = n
        self.id = nid if nid is not None else n
        self.label = label if label is not None else self.id
        self.annotation = None
        self.length = .1
    
    def displacement(self, start, direction, distance):
        if isinstance(distance, (tuple, list)):
            distance + np.array(distance)

        return np.array(start) + Flow.roundout(Flow.compass[direction] -.5)* self.length * distance
        
    def draw(self, travel=None, startpoint=None, arrowprops=None, 
        bbox=None, connect=True, distance=None, xlabel=None, xlabel_xy=(0, -.5), **kwargs):
        distance = distance if distance is not None else self.flow.distance
        travel = travel if travel is not None else self.flow.direction[-1]
        arrowprops = dict() if arrowprops is None else arrowprops
        bbox = dict() if bbox is None else bbox
        
            
        if isinstance(startpoint, tuple):
            ann = self.flow.ax.annotate(self.label, xy=startpoint, xycoords="data", 
                                   va="center", ha="center", 
                                   bbox={**self.flow.bbox, **bbox}, **kwargs)
        
        elif isinstance(startpoint, Node):
            ann = self.flow.ax.annotate(self.label, 
                              Flow.compass[travel], xycoords=startpoint.annotation.get_bbox_patch(),
                              xytext=self.displacement(startpoint.annotation.xyann, travel, distance), textcoords="data",
                              va='center', ha='center', **kwargs,
                              bbox={**self.flow.bbox, **bbox})

        if xlabel and ann.get_bbox_patch():
            # TODO: use compass for xytext and add +- .2 to go outside
            self.flow.ax.annotate(xlabel, xy=(.5, .5), xytext=xlabel_xy, xycoords=ann.get_bbox_patch(), 
                va='center', ha='center')

        self.annotation = ann
        return ann
    
    def node(self, **kwargs):
        return self.flow.node(**kwargs)

    
class Edge():
    def __init__(self, masterflow, a, b, n, eid, label):
        self.flow = masterflow
        self.a = masterflow.nodes[a] if isinstance(a, (str, int)) else a
        self.b = masterflow.nodes[b] if isinstance(b, (str, int)) else b
        self.n = n
        self.id = eid if eid is not None else n
        self.label = label
        self.annotation = None
    
    def get_ports(self, a, b):
        tailport, headport = '', ''
        ax, ay = a.annotation.xyann # it is took for granted that I'm interested in the Text box instead of ArrowPatch
        bx, by = b.annotation.xyann # this needs to be accounted for if I want arrows pointing to other arrows
        
        # TODO: I can't find a way to get the position of an arrowPatch

        if ay - by > 0.001:
            tailport += 's'
            headport += 'n'
        elif ay - by < -0.001:
            tailport += 'n'
            headport += 's'
        if ax - bx > 0.001:
            tailport += 'w'
            headport += 'e'
        if ax - bx < -0.001:
            tailport += 'e'
            headport += 'w'

        if not tailport:
            tailport = 'n'
        if not headport:
            headport = 'n'
        return tailport, headport
    
    @staticmethod
    def get_inclination(ax, ay, bx, by):
        return (by-ay)/(bx-ax+0.0001)

    @staticmethod
    def sigmoid(x):
        return 1 /(1+np.e**-x)
    
    def draw(self, tailport=None, headport=None, arrowprops=None, fontcolor='k', labelpos=None, va='center', ha='center', **kwargs):
        m = self.get_inclination(*self.a.annotation.xyann, *self.b.annotation.xyann)
        tp, hp = self.get_ports(self.a, self.b)
        
        if tailport is None:
            tailport = tp
        if isinstance(tailport, str):
            tailport = Flow.compass[tailport]
        
        if headport is None:
            headport = hp
        if isinstance(headport, str):
            headport = Flow.compass[headport]

        # TODO: invert tailport and headport if the direction of the arrow is reversed
        
        arrowprops = dict() if arrowprops is None else arrowprops
        textcoords = self.b.annotation.get_bbox_patch() if isinstance(self.b, Node) else self.b.annotation.arrow_patch
        xycoords = self.a.annotation.get_bbox_patch() if isinstance(self.a, Node) else self.a.annotation.arrow_patch
        
        con = self.flow.ax.annotate(None, xy=tailport, xytext=headport, 
                               textcoords=textcoords, xycoords=xycoords, 
                               arrowprops={**self.flow.arrowprops, **arrowprops}, **kwargs)
        if self.label:
            if labelpos is None:
                x = .5
                y = self.sigmoid(-m/2) if m != 0 else 1.2
            else:
                x, y = labelpos

            self.flow.ax.annotate(self.label, xy=(0, 0), xytext=(x, y), xycoords=con.arrow_patch, 
                             va=va, ha=ha, color=fontcolor, **kwargs)
        self.annotation = con
        return con

