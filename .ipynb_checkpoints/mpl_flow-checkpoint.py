import matplotlib.pyplot as plt
import numpy as np

class Flow():
    node_counter = 1
    compass = {
        'e': np.array((1, .5)),
        'w': np.array((0, .5)),
        's': np.array((.5, 0)),
        'n': np.array((.5, 1)),
        'ne': np.array((1, 1)),
        'nw': np.array((0, 1)),
        'se': np.array((1, 0)),
        'sw': np.array((0, 0))}
    
    def __init__(self, ax=None, direction='we', arrowprops=None, bbox=None, distance=1):
        self.elems = {}
        self.direction = direction
        self.ax = ax 
        self.init_plot()
        self.distance = distance
        self.arrowprops = self.init_style(dict(arrowstyle="<-"), arrowprops)
        self.bbox = self.init_style(dict(boxstyle="round", fc="w"), bbox)
    
    @staticmethod
    def roundout(a):
        return np.trunc(a + np.copysign(.5, a))
    
    @staticmethod
    def init_style(style, custom):
        if custom is not None:
            style = {**style, **custom}
        return style
    
    def init_plot(self):
        self.ax = self.ax if self.ax is not None else plt.gca()
        self.start_point = (0, 0.5)
#         self.ax.set_aspect('equal')
        self.ax.axis('off')
        
    def update_boundaries(self):
        coords = np.array([n.annotation.xyann for n in self.elems.values()])
        
        xlim, ylim = np.vstack([coords.min(axis=0), coords.max(axis=0)]).T
        self.ax.set_xlim(*(xlim+[-.01, .01]))
        self.ax.set_ylim(*(ylim+[-.01, .01]))
    
    def node(self, node_id=None, label=None, travel=None, startpoint=None, edgelabel=None, 
             arrowprops=None, bbox=None, connect=True, distance=None, **kwargs):

        if isinstance(startpoint, str):
            startpoint = self.elems.get(startpoint)
            
        if startpoint is None:
            if not self.elems:
                startpoint = self.start_point
            else:
                startpoint = max([n for n in self.elems.values()], key=lambda node: node.n)          

        node = Node(self, node_id, self.node_counter, label)
        self.node_counter += 1  
        
        self.elems[node.id] = node
        
        node.draw(travel, startpoint, edgelabel, arrowprops, bbox, connect, distance, **kwargs)
        self.update_boundaries()
        return node
    
    def edge(self, a, b, tailport=None, headport=None, arrowprops=None, edgelabel=None, **kwargs):
        edge = Edge(self, a, b)
        edge.draw(tailport, headport, arrowprops, edgelabel, **kwargs)


class Node():
    def __init__(self, masterflow, nid, n, label):
        self.flow = masterflow
        self.n = n
        self.id = nid if nid is not None else n
        self.label = label if label is not None else self.id
        self.annotation = None
        self.length = .1
    
    def displacement(self, start, direction, distance):
        return np.array(start) + Flow.roundout(Flow.compass[direction] -.5)* self.length * distance
        
    def draw(self, travel, startpoint, edgelabel, arrowprops, bbox, connect, distance, **kwargs):
        distance = distance if distance is not None else self.flow.distance
        travel = travel if travel is not None else self.flow.direction[-1]
        arrowprops = dict() if arrowprops is None else arrowprops
        bbox = dict() if bbox is None else bbox
        
        
        if isinstance(startpoint, tuple):
            ann = self.flow.ax.annotate(self.label, xy=startpoint, xycoords="data", 
                                   va="center", ha="center", 
                                   bbox={**self.flow.bbox, **bbox})
            
        elif isinstance(startpoint, Node):
            ann = self.flow.ax.annotate(self.label, 
                              Flow.compass[travel], xycoords=startpoint.annotation.get_bbox_patch(),
                              xytext=self.displacement(startpoint.annotation.xyann, travel, distance), textcoords="data",
                              va='center', ha='center', **kwargs,
                              bbox={**self.flow.bbox, **bbox},                         
                              arrowprops={**self.flow.arrowprops, **arrowprops} if connect is True else None)

        if edgelabel and ann.arrow_patch:
            self.flow.ax.annotate(edgelabel, xy=(.5, .5), xytext=(.5, 2), xycoords=ann.arrow_patch,
                        va='center', ha='center')

        self.annotation = ann
    
    def node(self, **kwargs):
        return self.flow.node(**kwargs)

    
class Edge():
    def __init__(self, masterflow, a, b):
        self.flow = masterflow
        self.annotation = None
        self.a = masterflow.elems[a].annotation if isinstance(a, str) else a.annotation
        self.b = masterflow.elems[b].annotation if isinstance(b, str) else b.annotation
    
    @staticmethod
    def get_ports(a, b):
        tailport, headport = '', ''
        ax, ay = a.xyann # it is took for granted that I'm interested in the Text box instead of ArrowPatch
        bx, by = b.xyann # this needs to be accounted for if I want arrows pointing to other arrows
        
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
        return tailport, headport
    
    def draw(self, tailport=None, headport=None, arrowprops=None, edgelabel=None, **kwargs):
        tp, hp = Edge.get_ports(self.a, self.b)
        tailport = tp if tailport is None else tailport
        headport = hp if headport is None else headport
        arrowprops = dict() if arrowprops is None else arrowprops
        
        con = self.flow.ax.annotate(None, xy=Flow.compass[tailport], xytext=Flow.compass[headport], 
                               textcoords=self.b.get_bbox_patch(), xycoords=self.a.get_bbox_patch(), 
                               arrowprops={**self.flow.arrowprops, **arrowprops}, **kwargs)
        if edgelabel:
            self.flow.ax.annotate(edgelabel, xy=(0, 0), xytext=(.5, .5), xycoords=con.arrow_patch, 
                             va='center', ha='center', **kwargs)
        self.annotation = con
        return con

