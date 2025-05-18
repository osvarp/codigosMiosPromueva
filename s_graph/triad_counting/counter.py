"""
Autor: Oscar Vargas Pabon

"""

import networkx as nx
from itertools import combinations

def sgn( num:float ):
	if ( num<0 ): res = -1;
	elif (num>0 ): res = 1;
	else: res = 0;
	return res;

def triad_counter( G ):
	"""
	Para cada triada del grafo, guarda la triada segun la cantidad de aristas positivas
	que se generan en su distribucion.

	Parameters
	----------
	G : Grafo de networkx

	Returns
	-------
	list[list[tuple]] : donde en triadDistr[i] esta la lista de triadas
						con i aristas positivas
	"""
	triadDistr = [[] for _ in range(4)]
	for u,v,k in combinations(G.nodes):
		if ( (u,v) not in G.edges or (v,k) not in G.edges or (k,u) not in G.edges ): continue;
		cnt = max(0,sgn(G.edges[u,v]['weight']))
		cnt += max(0,sgn(G.edges[v,k]['weight']))
		cnt += max(0,sgn(G.edges[k,u]['weight']))
		assert(cnt>=0 and cnt < 4)
		triadDistr[cnt].append((u,v,k))
	return triadDistr

if __name__ == "__main__":
	filename="XXXXXXXX"
	G = nx.read_gephi(filename)
	trd = triad_counter( G )
	