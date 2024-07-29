"""
Autor: Oscar Vargas Pabon

Este es nomas un programa de jugete que hize para probar NetworkX
Este resuelve el grafo 'bipartito' con relaciones de amistad.

m[u][v] = 1 si son amigos
m[u][v] = -1 si son enemigos
de lo contrario es 0 (no hay arista)
"""

import networkx as nx
import matplotlib.pyplot as plt


def buildGraph( mat:list[list[int]], val:list[int] ):
	"""
	Construye un grafo de NetworkX a partir de una matriz de adyacencia.
	Solo se van a considerar aristas con peso en 'val'

	Parameters
	----------
	mat : grafo representado en matriz de adyacencia
	val : valores de las aristas a considerar

	Returns
	-------
	Grafo de NetworkX
	"""
	G = nx.Graph()
	dim = len(mat);
	for act in range(dim):
		G.add_node(act);
	for row in range(dim):
		for col in range(dim):
			if ( mat[row][col] in val ):
				G.add_edge( row, col );
	return G;

def preprocess( adjM:list[list[int]] ):
	"""
	Construye un grafo condensado que ya no tendrá aristas de amistad

	Parameters
	----------
	adjM : grafo en representacion matriz de adyacencia

	Returns
	-------
	GDense : grafo condensado
	condensedNode : lista en donde condensedNode[node] tiene el nombre del vertice en GDense que 
					lo representa
	"""
	dim = len(adjM);
	Gplus = buildGraph( adjM, [1] );

	GDense=nx.Graph();
	condensedNode=[-1 for _ in range(dim)];
	ind = 0;
	for c in nx.connected_components(Gplus):
		GDense.add_node( ind, color=-1 );
		for node in Gplus.subgraph(c):
			condensedNode[node] = ind;
			for edge in range(dim):
				if ( adjM[node][edge]==-1 and condensedNode[edge]!=-1 ):
					GDense.add_edge( ind, condensedNode[edge] );
		ind += 1;
	return GDense,condensedNode;

def bipartiteColoring( G ) -> bool:
	"""
	Parameters
	----------
	G : un grafo de NetworkX

	Returns
	-------
	posible : toma valor 'True' si el grafo G es bipartito, 'False' de lo contrario
	G.nodes[node]['color'] : retorna el color que le asigno ( 1 o 0 );
	"""
	#print(len(G.nodes))
	def recursiveColoring(node):
		res = True;
		for edge in G[node]:
			if ( G.nodes[edge]['color'] == G.nodes[node]['color'] ):
				res = False;
			elif ( G.nodes[edge]['color']==-1 ):
				G.nodes[edge]['color'] = G.nodes[node]['color']^1;
				res = res and recursiveColoring( edge );
		return res;
	posible = True;
	for node in range(len(G.nodes)):
		if ( G.nodes[node]['color'] == -1 ):
			G.nodes[node]['color']=0;
			posible = posible and recursiveColoring( node );
	return posible;

m=[
[0,1,0,-1,-1],
[1,0,0,-1,-1],
[0,0,0,1,0],
[-1,-1,1,0,1],
[-1,-1,0,1,0],
]


G, mapping = preprocess(m)
posible = bipartiteColoring( G );

lbl={}
dim = len(m);
for node in range(dim):
	lbl[node] = G.nodes[mapping[node]]['color'];

GFull = buildGraph( m, [1,-1] );
edgeColor=[]
for u,v in GFull.edges():
	color = 1 if m[u][v]==1 else 0;
	edgeColor.append( color );

# el label va a ser el color del nodo, no el nombre
nx.draw( GFull, with_labels=True, labels=lbl,edge_color=edgeColor );
plt.show();


