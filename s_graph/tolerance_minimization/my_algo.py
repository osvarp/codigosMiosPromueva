"""
Autor: Oscar Vargas Pabon
Fecha: 15/04/2025

trivial solutions
tl >= max_{u,v\\in V}\\{|st_u-st_v|\\}
tl <= min{u,v\\in V}\\{|st_u-st_v\\}

I could actually output the ranges of tl where it generates these balanced graphs


Observe i'm actually using self._sz over the amount of edges, while self._set works
	in time relative to the amount of vertices
"""
import networkx as nx

class DSU:
	def __init__(self, G):
		self._pi = { i:i for i in G.nodes }
		self._esz = { i:G.degree(i) for i in G.nodes }
		self._sz = { i:1 for i in G.nodes }
		self._set = { i:{i} for i in G.nodes }
	def parent( self, nd ):
		if ( self._pi[nd] != nd ):
			self._pi[nd] = self.parent( self._pi[nd] )
		return self._pi[nd]
	def sz( self, nd ):
		return self._sz[self.parent(nd)]
	def esz( self, nd ):
		return self._esz[self.parent(nd)]
	def set( self, nd ):
		return self._set[self.parent(nd)]
	def join( self, u, v ):
		u = self.parent( u ); v = self.parent( v );
		if ( u != v ):
			if ( self._sz[u] > self._sz[v] ): u,v=v,u
			self._pi[u] = v;
			self._sz[v] += self._sz[u]
			self._esz[v] += self._esz[u]

			self._set[v].update( self._set[u] )
			self._set[u] = set()

def normalize_res( raw:list[tuple] ) -> list[tuple]:
	"""
	Transforma an answer with potentially repeated ranges into completely meaningfull ones
	[..,(a,b),(b,c),...,] -> [..,(a,c),..]
	"""
	res = []
	prv = raw[0][0]
	for i in range(1,len(raw)):
		print( raw[i][0] , raw[i-1][1] )
		if ( raw[i][0] != raw[i-1][1] ):
			print("entro")
			res.append((prv,raw[i-1][1]))
			prv = raw[i][0]
	res.append((prv,raw[-1][1]))
	return res

def min_tol( G ):
	all_edges=[]
	for u,v in G.edges():
		all_edges.append((abs(G.nodes[u]['stance']-G.nodes[v]['stance']),u,v))
	all_edges.sort()
	
	res = [(0,all_edges[0][0])]
	dsu = DSU(G)
	tl = all_edges[0][0]
	for delta,u,v in all_edges:
		if( delta >= tl ):
			res.append((tl,delta))
			tl = delta
		if ( dsu.parent(u) != dsu.parent(v) ):
			# I have to join them, potentially adding new bad edges
			if ( dsu.esz(u) > dsu.esz(v) ):u,v=v,u;
			for nd in dsu.set(u):
				for e in G.neighbors(nd):
					if ( dsu.parent(e) == dsu.parent(v) ):
						tl = max( tl, abs(G.nodes[nd]['stance']-G.nodes[e]['stance']) )
			dsu.join(u,v)
	res.append((tl,1))
	res = normalize_res( res )
	return res

if __name__ == "__main__":
	G = nx.read_gexf("..\\sparseAgreement0_2.gexf")
	rr = min_tol(G)
	print(rr)
	re = [(0,0.9),(0.9,1)]
	#print(normalize_res(re))
