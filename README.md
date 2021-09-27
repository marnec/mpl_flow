# Requirements

* Python >= 3.6 (There are f strings)
* matpltolib 
* numpy

# Motivation
> There are other libs that you can use to draw flowcharts, why writing your own?

* [PyGraph](https://github.com/jciskey/pygraph#:~:text=Pygraph%20aims%20to%20be%20an,enabling%20maximum%20ease%20of%20use.) and [NetworkX](https://networkx.org/) are great libs for graphs operations, but not so great for flowcharts or computation graphs; 
* [Graphviz](https://graphviz.org/) (and its python declinations) would be ok for these tasks but performs poorly when it comes to customization and control;
* You could use [dot2tex](https://dot2tex.readthedocs.io/en/latest/) but it integrates very poorly with jupyter notebooks and even if you make it work on a local machine it loses compatibility with online services (github markdown rendered for example).
* Even using the graphviz python library you are not accessing the full versatility of the underlying tool. For example you can't have complex typographic styles in the labels and also adding super-/sub-script poses a problem. With this lib you can use LateX.

# Implementation
Matplotlib is an incredibly versatile instrument for graphics in python and I bent it to my will abusing the [Annotation](https://matplotlib.org/stable/tutorials/text/annotations.html) tool far beyond its original purpose of **annotating** plots and repurposing it to **drawing tool**.

Everything in this library is drawn with the [ax.annotate](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.annotate.html) function, especially exploiting the fact that `xycoords` and `textcoords` can be both set to `bbox` instances, which alleviates me from the effort of finding the coordinates from- and to- which the arrows should point.

The rest of the library is just syntactic sugar and quality-of-life functions and parameters.

# Usage
The library focuses on usability: I tried to write the code so that you need to write as little code as possible while maintaining total customization.

## Creating a Flow
A new plot always starts by instantiating the `Flow` class:


```python
f = Flow(ax=None)
f.ax.axis('on')
```




    (0.0, 1.0, 0.0, 1.0)




    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_1_1.png)
    


`Flow()` accepts an [Axes](https://matplotlib.org/stable/api/axes_api.html#matplotlib.axes.Axes) instance or instantiates its own. By default the `Axis` instance has hidden splines and ticks, and its ranges [0,1] on both axes.

## Creating Nodes
You proceed by adding nodes with the `Flow().node()` method: the method takes a `node_id` and a `label` argument that concur to control the display item inside the node:

* If `label != None`, then it is displayed: **labels can contain LaTeX** (FY Graphviz!) 
* If `label == None`, then `node_id` is displayed 
* If also `node_id == None`, a number is displayed. The number increases each time a node is drawn. 


```python
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
ax1, ax2, ax3 = axes
f = Flow(ax=ax1)
f.node(node_id=None, label=None)

f = Flow(ax=ax2)
f.node(node_id='a', label=None)

f = Flow(ax=ax3)
f.node(node_id='a', label='$x^2 + y^2 = 0$');
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_3_0.png)
    


## Traveling and connecting nodes
By creating other nodes they are automatically drawn (they **travel**) to the right of the last node drawn and connected to it by an arrow.

* The default direction can be set with the argument `direction` of the `Flow` instance
* Direction of single nodes can be specified in the `node()` function with the `travel` argument that indicates where the node `travel`s with respect to the `startpoint`
* Nodes can travel without being connected by an arrow: this is achieved by setting `.node(connect=False)`
* Travel directions are like in a **compass**: `n`, `s`, `e`, `w`, `ne`, `se`, `sw`, `nw`. 


The `.node()` methods returns a `Node` instance. Each time a `Node` is drawn, the `ylim` and `xlim` of the `Axes` update to frame and center all the nodes. 


```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
ax1, ax2, ax3 = axes
f = Flow(ax=ax1)
f.node(label='first node')
f.node(label='second node')
f.node(label='third node')
f.node(connect=False)

f = Flow(ax=ax2, direction='ns')
f.node(label='first node')
f.node(label='second node')
f.node(label='third node')
f.node(connect=False)

f = Flow(ax=ax3)
f.node(label='first node')
f.node(label='second node', travel='sw')
f.node(label='third node', travel='se')
f.node(connect=False, travel='ne');
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_5_0.png)
    


## Setting a travel startpoint
Nodes can travel from different `startpoints` than the last node. This is achieved by specifying the `node(startpoint=Node)` argument. A `startpoint` can be:

* a `str`: the `Node.id` of an instantiated `Node`
* a `Node` instance, returned by the `Flow.node()` method


```python
f = Flow()
a, _ = f.node('a')
f.node('b', travel='ne')
f.node('c', travel='se', startpoint=a)
f.node('d', startpoint='b');
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_7_0.png)
    


## Drawing an edge between existing nodes
Edges can be drawn between nodes that have already been defined, using the `Flow.edge()` method, which returns an `Edge` instance


```python
f = Flow()
a, _ = f.node('a')
b, _ = f.node('b', travel='ne')
f.node('c', travel='se', startpoint=a)
f.edge(b, 'c', label='I\'m a label', rotation=90, labelpos=(-1, 0.5))
f.edge('c', 'a', tailport='n', headport='e', arrowprops=dict(connectionstyle='arc3,rad=-0.3'));
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_9_0.png)
    


## Use-cases
### Computational graph
Let's say you want to draw a fairly simple computational graph. At the moment, the best option to draw such a thing would have been to use the graphviz python package.

#### Graphviz
With the python package you ca exploit subragph to have multiple inputs for a single box but you have little more control than that. For example I couldn't find a way to align the square boxes in a single line and the best you can do is playing with the `layout` and hope that one will be good enough for you. Furthermore the superscript are ugly and you have little more mathematical notation that that.


```python
dot = Digraph(node_attr={'fontsize':'9'}, edge_attr={'arrowsize': '0.5', 'fontsize':'9'}, engine='dot')
dot.attr(rankdir='LR', packmode='graph')

with dot.subgraph() as sg:
    sg.attr(rank='same')
    sg.node('x', shape='plaintext', margin='0')
    sg.node('w', label='<W<SUP>[1]</SUP>>', shape='plaintext', margin='0')
    sg.node('b', label='<b<SUP>[1]</SUP>>', shape='plaintext', margin='0')

dot.node('z', shape='rect', label='<Z<SUP>[1]</SUP>  = W<SUP>[1]</SUP> x + b<SUP>[1]</SUP>>', margin='0')
dot.node('h', shape='rect', label='z[2] = W2 a[1] + b[2]', margin='0')
dot.node('y', shape='rect', label='a[2] = g(z[2])', margin='0')
dot.node('l', shape='rect', label='L(a[2], y)', margin='0')

with dot.subgraph() as sg:
    sg.attr(rank='same')
    sg.node('j', label='<W<SUP>[2]</SUP>>', shape='plaintext', margin='0')
    sg.node('k', label='<b<SUP>[2]</SUP>>', shape='plaintext', margin='0')
    sg.node('a', shape='rect', label='a[1] = g(z[1])', margin='0')
    
dot.edges(['xz', 'wz', 'bz', 'za', 'ah', 'hy', 'yl', 'jh', 'kh'])
dot.edge('l', 'y', headport='s', tailport='s', color='red', label='da[2]', fontcolor='red')
dot.edge('y', 'h', headport='s', tailport='s', color='red', label='dz[2]', fontcolor='red')
dot.edge('h', 'k', color='red', label='db[2]', fontcolor='red')
dot.edge('h', 'j', color='red', label='dW[2]', fontcolor='red')
dot
```




    
![svg](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_11_0.svg)
    



#### mpl_flow
With this library you have almost complete control over positioning of boxes and labels and you can access the full power of LateX when it comes to mathematical notation.


```python
fig, ax = plt.subplots(figsize=(10, 2))
f = Flow(ax=ax)
f.node('x', label='$x$')
f.node('W1', label='$W^{[1]}$', travel='s', connect=False)
f.node('b1', label='$b^{[1]}$', travel='s', connect=False)
f.node('Z1', label='$Z^{[1]}=W^{[1]}x+b^{[1]}$', startpoint='x')
f.edge('W1', 'Z1')
f.edge('b1', 'Z1')
f.node('a1', label='$a^{[1]}=g(z^{[1]})$')
f.node('W2', label='$W^{[2]}$', travel='s', connect=False)
f.node('b2', label='$b^{[2]}$', travel='s', connect=False)
f.node('Z2', label='$Z^{[2]}=W^{[2]}x+b^{[2]}$', startpoint='a1')
f.edge('W2', 'Z2')
f.edge('b2', 'Z2')
f.node('a2', label='$a^{[2]}=g(z^{[2]})$', startpoint='Z2')
f.node('L', label='$L(a^{[2]}, y)$')
f.edge('L', 'a2', tailport='s', headport='s', arrowprops=dict(connectionstyle='arc3,rad=0.5', color='r'), c='r', label='$da^{[2]}$')
f.edge('a2', 'Z2', tailport='s', headport='s', arrowprops=dict(connectionstyle='arc3,rad=0.5', color='r'), c='r', label='$dZ^{[2]}$')
f.edge('Z2', 'W2', tailport='s', headport='e', arrowprops=dict(connectionstyle='arc3,rad=0.5', color='r'), c='r', label='$dW^{[2]}$')
f.edge('Z2', 'b2', tailport='s', headport='e', arrowprops=dict(connectionstyle='arc3,rad=0.5', color='r'), c='r', label='$db^{[2]}$');
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_13_0.png)
    


### Increasingly complex examples that would be impossible with other libraries and a nightmare with vanilla matplotlib

#### RNN backpropagation


```python
f = Flow(bbox=dict(boxstyle='square'))

for i in range(6):
    lbl = i if i < 5 else 'T_x'

    if i != 4:
        f.node(f'a{i}', label=f'$a^{{\\langle {lbl} \\rangle}}$', fontsize=13, startpoint=f'a{i-1}')
    else:
        f.node(f'a{i}', label='$\\cdots$', startpoint=f'a{i-1}', fontsize=13, bbox=dict(ec='none'))
    if i != 0:
        f.edge(f'a{i}', f'a{i-1}', arrowprops=dict(connectionstyle='arc3,rad=0.4', ec='r'), headport='se', tailport='sw')
        
    if i >0 and i != 4:
        f.node(f'x{i}', label=f'$x^{{\\langle {lbl} \\rangle}}$', startpoint=f'a{i}', travel='s', fontsize=13, 
               edge_kwargs=dict(arrowprops=dict(arrowstyle='->')), bbox=dict(ec='none'))
        if i == 5:
            lbl = 'T_y'
        f.node(f'y{i}', label=f'$y^{{\\langle {lbl} \\rangle}}$', startpoint=f'a{i}', travel='n', fontsize=13)
        f.node(f'l{i}', label=f'$\\mathcal{{L}}^{{\\langle {lbl} \\rangle}}$', travel='n', fontsize=13)
        f.edge(f'l{i}', f'y{i}', arrowprops=dict(connectionstyle='arc3,rad=0.4', ec='r', shrinkA=4, shrinkB=6), headport='n', tailport='s')
        f.edge(f'y{i}', f'a{i}', arrowprops=dict(connectionstyle='arc3,rad=0.4', ec='r', shrinkA=4, shrinkB=6), headport='n', tailport='s')
        
f.node('l', label='$\\mathcal{L}$', startpoint=f'l5', travel='ne', distance=.5, connect=False)

for i in range(1, 6):
    if i != 4:
        f.edge(f'l{i}', 'l', tailport='n', headport='w', arrowprops=dict(connectionstyle='angle,angleA=0,angleB=90,rad=2'))
        f.edge('l', f'l{i}', tailport='sw', headport='ne', arrowprops=dict(connectionstyle='arc3,rad=-0.05', ec='r'))        
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_16_0.png)
    


#### ResNet architecture


```python
fig, ax = plt.subplots(2, 1, figsize=(14, 6))
ax1, ax2 = ax
dims = [1, 6, 8, 12, 6]
f = [7, 3, 3, 3, 3]
c = [1, 0, 2, 3, 4]
ch = [64, 64, 128, 256, 512]
sc = range(0, 34, 2)

facecolors = sum([[f'C{color}']*dim for color, dim in zip(c, dims)], [])
filters = sum([['${0} \\times {0}$ $\\mathrm{{conv}}$'.format(filt)]*dim for filt, dim in zip(f, dims)], [])
channels = sum([['${}$'.format(c)]*dim for c, dim in zip(ch, dims)], [])
pools = ['$/2$']+['']*6+['$/2$']+['']*7+['$/2$']+['']*11+['$/2$']+['']*5
ax1.set_title('Plain')
ax2.set_title('ResNet')
labels = list(map(lambda l: ', '.join(l), zip(filters, channels, pools)))

f = Flow(ax=ax1)
for i, (c, l) in enumerate(zip(facecolors, labels)):
    f.node(i, label='{:^50}'.format(l.strip(', ')), rotation=90, bbox=dict(boxstyle='square', pad=0.1, fc=c, alpha=.2))
f.node(sum(dims), label='{:^44}'.format('$\\mathrm{FC}$ $1000$'), rotation=90, bbox=dict(boxstyle='square', pad=0.1, fc=c, alpha=.2));

edges = []
f = Flow(ax=ax2)
for i, (c, l) in enumerate(zip(facecolors, labels)):
    _, e = f.node(i, label='{:^50}'.format(l.strip(', ')), rotation=90, bbox=dict(boxstyle='square', pad=0.1, fc=c, alpha=.2))
    if e is not None:
        edges.append(e)
_, e = f.node(sum(dims), label='{:^44}'.format('$\\mathrm{FC}$ $1000$'), rotation=90, bbox=dict(boxstyle='square', pad=0.1, fc=c, alpha=.2))
edges.append(e)

for ii, (i, j) in enumerate(zip(edges[::2], edges[2::2])):
    ls = '--'if ii in [3, 7, 13] else '-'
    f.edge(i, j, arrowprops=dict(connectionstyle='arc,angleA=90,angleB=90,armA=70,armB=70,rad=25', ls=ls))
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_18_0.png)
    


#### U-net architecture


```python
f = Flow(figsize=(12, 6))
vpad=4
hpad=0

nodes = []
fc='C0'
for i in range(27):
    c='k'
    lw=1
    dst=1
    drc='e'
    if i != 1 and i % 3 == 0:
        c='r'
        lw=2
        drc = 's'
        level = -1
        if i >= 15:
            fc='cyan'
            c='lime'
            drc = 'n'
            level = 1
        vpad += level
        dst=1/level
    
    hpad -= level
    nodes.append(f.node(label=' '*hpad+'\n'*3*vpad,  
                        bbox=dict(boxstyle='square', fc=fc, ec='none'),
                        edge_kwargs=dict(arrowprops=dict(ec=c, lw=lw)),
                        travel=drc, distance=0.2, fontsize=5))

    if i >= 15:
        if i % 3 == 0:
            f.edge(nodes[i][0], nodes[((9-(i//3-1))-1)*3-1][0], arrowprops=dict(arrowstyle='->', ec='lightgray', lw=3))
f.node(label='', distance=.12, bbox=dict(boxstyle=None), edge_kwargs=dict(arrowprops=dict(ec='magenta')))
vpad = 0
hpad = 5
for i in range(15, 27, 3):    
    f.node(label=' '*hpad+'\n'*3*vpad, startpoint=i+1, travel='w', distance=0.008*hpad, connect=False,
          bbox=dict(boxstyle='square', ec='none', fc='C0'), fontsize=5)
    hpad -=1 
    vpad +=1

    
plt.scatter([],[],marker=r'$\rightarrow$', label='Conv. ReLU', c='k', s=100) 
plt.scatter([],[],marker=r'$\rightarrow$', label='Skip Connection', c='lightgray', s=100)
plt.scatter([],[],marker=r'$\rightarrow$', label='Conv (1x1)', c='magenta', s=100)
plt.scatter([],[],marker=r'$\downarrow$', label='Max pool', c='r', s=100) 
plt.scatter([],[],marker=r'$\uparrow$', label='Max pool', c='lime', s=100)
plt.legend(loc='lower right');
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_20_0.png)
    


###  Transformer architecture


```python
def multihead(f, startpoint, travel, nid, distance=1, edge_kwargs=dict()):
    a =f.node(f'{nid}.1', label='$\\mathrm{Multi-Head}$\n$\\mathrm{Attention}$',
           startpoint=startpoint, travel=travel, distance=distance,
           bbox=dict(ec='C0'), edge_kwargs=edge_kwargs)
    b =f.node(f'{nid}.2', label='$\\mathrm{Multi-Head}$\n$\\mathrm{Attention}$',
           travel='ne', distance=.03, bbox=dict(ec='C3'), connect=False, zorder=-10)
    c =f.node(f'{nid}.3', label='$\\mathrm{Multi-Head}$\n$\\mathrm{Attention}$',
           travel='ne', distance=.03, bbox=dict(ec='C2'), connect=False, zorder=-20)
    return a,b,c

f = Flow(figsize=(6, 6))
f.node('x', label=r'$x^{\langle 1 \rangle}, \dots , x^{\langle T_x \rangle}$', 
       bbox=dict(ec='none'), fontsize=13)
f.node('peE', label='$+$', bbox=dict(boxstyle='circle'), travel='n', distance=.7)
(_, me),_, _ = multihead(f, 'peE', 'n', 'ME', distance=1,
          edge_kwargs=dict(
              label='$Q, K, V$', labelpos=(5, 0.5)))
f.node('an1', label='$\\mathrm{Add \\ & \\ Norm}$', travel='n', 
       bbox=dict(ec='orange'), startpoint='ME.1', distance=.5,
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-')))
_, ffe = f.node('ffnnE', label='$\\mathrm{Feed \\ Forward}$\n$\\mathrm{Neural\\ Network}$',
       travel='n')
f.node('an2', label='$\\mathrm{Add \\ & \\ Norm}$', travel='n', 
       bbox=dict(ec='orange'), distance=.5,
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-')))
f.node('compound_edge1', label='', distance=.5, travel='n',
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-', shrinkA=0), 
                        headport=(0.5, 0.5)))
f.node('compound_edge2', label='', distance=2, travel='e',
   edge_kwargs=dict(arrowprops=dict(arrowstyle='-', shrinkA=0, shrinkB=0), 
                    headport=(0.5, 0.5), tailport=(0.5, 0.5)))

(_, md1), _, _ = multihead(f, 'compound_edge2', 'se', 'MD2', distance=(1, 1.5), 
          edge_kwargs=dict(
              label='$K, V$', labelpos=(.75, 0.05), 
              tailport=(0.5, 0.5), headport=(0.334, 0), 
              arrowprops=dict( 
                  shrinkB=0,
                  connectionstyle='bar,fraction=-0.2,angle=0')))
_, an3 = f.node('an3', label='$\\mathrm{Add \\ & \\ Norm}$', travel='s', 
       bbox=dict(ec='orange'), distance=1, startpoint='MD2.1',
       edge_kwargs=dict(
           arrowprops=dict(arrowstyle='->'), 
           label='$Q$', labelpos=(2, 0.5)))
(_, md1), _, _ = multihead(f, 'an3', 's', 'MD1', distance=.5,
          edge_kwargs=dict(
              arrowprops=dict(arrowstyle='-')))

_, an4 = f.node('an4', label='$\\mathrm{Add \\ & \\ Norm}$', travel='n', 
       bbox=dict(ec='orange'), distance=.5, startpoint='MD2.1',
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-')))

_, ffd= f.node('ffnnD', label='$\\mathrm{Feed \\ Forward}$\n$\\mathrm{Neural\\ Network}$',
   travel='n', startpoint='an4')
f.node('an5', label='$\\mathrm{Add \\ & \\ Norm}$', travel='n', 
       bbox=dict(ec='orange'), distance=.5, startpoint='ffnnD',
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-')))
f.node('lin', label='$\\mathrm{Linear}$'.center(30), travel='n', distance=.8)
f.node('soft', label='$\\mathrm{Softmax}$'.center(28), travel='n', distance=.4, 
       edge_kwargs=dict(arrowprops=dict(arrowstyle='-')))
f.node('y', label='$\\hat{y}_n$', travel='n', distance=.6, bbox=dict(ec='none'))
f.node('compound_edge1', label='', distance=1, travel='e',
   edge_kwargs=dict(arrowprops=dict(arrowstyle='-', shrinkA=0), 
                    headport=(0.5, 0.5)))
_, pd = f.node('peD', label='$+$', bbox=dict(boxstyle='circle'), travel='s', startpoint='MD1.1', 
       distance=1, edge_kwargs=dict(arrowprops=dict(arrowstyle='->')))
f.node('P', label='$P$'.center(10), distance=1.5, startpoint='peE', 
       edge_kwargs=dict(arrowprops=dict(arrowstyle='->')))
f.edge('P', 'peD', headport='w', tailport='e', 
       arrowprops=dict(connectionstyle='bar,fraction=-0.7,angle=90'))
f.edge('compound_edge1', 'peD', 
       arrowprops=dict(
           arrowstyle='<-', connectionstyle='bar,fraction=0.03,angle=0',
           shrinkA=0, shrinkB=0), 
       headport='s', tailport=(0.5, 0.5))
f.node('encoder', label='  \n\n\n\n', startpoint='x', travel='n', distance=2.5,
       bbox=dict(boxstyle='square', ec='none', fc='gainsboro', pad=5), 
       zorder=-30, connect=False, 
       xlabel='$\\mathrm{Encoder}$', xlabel_xy=(0.15, 1.03))
f.node('encoder', label='   \n\n\n\n\n\n\n\n\n\n', startpoint='MD2.1', distance=.05, travel='n',
   bbox=dict(boxstyle='square', ec='none', fc='gainsboro', pad=5), 
   zorder=-30, connect=False, 
   xlabel='$\\mathrm{Decoder}$', xlabel_xy=(0.15, 1.03))
f.edge(me, 'an1', tailport='w', headport='w', arrowprops=dict(connectionstyle='bar,fraction=-0.2,angle=90'))
f.edge(ffe, 'an2', tailport='w', headport='w', arrowprops=dict(connectionstyle='bar,fraction=-0.2,angle=90'))
f.edge(pd, 'an3', tailport='e', headport='e', arrowprops=dict(connectionstyle='bar,fraction=-0.2,angle=90'))
f.edge(an3, 'an4', tailport=(1, 0.2), headport='e',  
       arrowprops=dict(connectionstyle='bar,fraction=-0.2,angle=90'))
f.edge(ffd, 'an5', tailport=(1, 0.5), headport='e',  
       arrowprops=dict(connectionstyle='bar,fraction=-0.2,angle=90'));
```


    
![png](https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files/README_22_0.png)
    

