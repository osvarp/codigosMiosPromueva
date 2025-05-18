"""
Autor: Oscar Vargas Pabon
  _
_|?|_
(-_-)
"""
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import sys

def plotG( fname:str ) -> None:
	G = nx.read_gexf( fname )
	
	communities = [set() for _ in range(2)]
	for node in G.nodes:
		communities[max(G.nodes[node]["partition"],0)].add( node )

	supergraph = nx.cycle_graph(len(communities))
	superpos = nx.spring_layout(G, scale=50, seed=429)
	# Use the "supernode" positions as the center of each node cluster
	centers = list(superpos.values())
	pos = {}
	for center, comm in zip(centers, communities):
		pos.update(nx.spring_layout(nx.subgraph(G, comm), center=center, seed=1430))

	# Nodes colored by cluster
	for nodes, clr in zip(communities, ("tab:blue", "tab:orange", "tab:green")):
		nx.draw_networkx_nodes(G, pos=pos, nodelist=nodes, node_color=clr, node_size=100)
	nx.draw_networkx_edges(G, pos=pos)

	plt.tight_layout()
	plt.show()

def histogram(fname):
	G = nx.read_gexf( fname )
	allDif = []
	for edge in G.edges:
		allDif.append( G.edges[edge]["weight"] )

	n_bins=10 #https://matplotlib.org/stable/gallery/statistics/hist.html
	fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)

	# We can set the number of bins with the *bins* keyword argument.
	axs.hist(allDif, bins=n_bins)

	plt.show()

def stance_to_weight( st1:float, st2:float, tol:float=0.5 ) -> float:
	# (1-delta 0.05) [0,1] [-1,1]
	#return (1-abs(st1-st2)) *2 -1;
	delta = abs(st1-st2);
	if ( delta <= tol ):
		res = (tol-delta)* (1/tol)
		assert( 0 <= res and res <= 1 );
	else:
		res = -(delta-tol)* (1/(1-tol))
		assert( -1 <= res and res <= 0 );
	return res;

def make_graph( fname, tol ):

	G = nx.read_gexf( fname )
	for act in G.nodes:
		G.nodes[act]['original_degree'] = len(G.edges(act))

	for edge in G.edges:
		st1 = G.nodes[edge[0]]["stance"]; st2 = G.nodes[edge[1]]["stance"];
		G.edges[edge]["weight"] = stance_to_weight( st1,st2, tol )

	miniSet = set(); maxiSet=set()
	for c in nx.connected_components(G):
		if ( len(c) > 6 and len(c) < 10):
			miniSet.update( c )
		elif ( len(c) >= 10):
			maxiSet=c
	#Gmini = G.subgraph(miniSet).copy()
	Gmaxi = G.subgraph(maxiSet).copy()

	#nx.write_gexf(Gmini, "miniAgreement.gexf")
	nx.write_gexf(Gmaxi, "sparseAgreement0_"+str(int(tol*10))+".gexf")

def make_clique( fname, tol ) :
	G=nx.read_gexf( fname );
	for act in G.nodes:
		G.nodes[act]['original_degree'] = len(G.edges(act))

	for a in G.nodes:
		st1 = G.nodes[a]['stance']
		for b in G.nodes:
			st2 = G.nodes[b]['stance']
			if ( not G.has_edge(a,b) ):
				G.add_edge( a, b )
			G.edges[a,b]["weight"] = stance_to_weight( st1, st2, tol )
	nx.write_gexf( G, "cliqueAgreement"+str(tol)+".gexf" );


if __name__ == "__main__":
	"""i=0;
				while ( i <= 1 ):
					print(i,"->",stance_to_weight(0,i,0.2))
					i += 0.05"""

	assert(len(sys.argv)>=1)
	fname:str = sys.argv[1];
	op:str = sys.argv[2] if (len(sys.argv)>=3) else "make";
	tol:float = float(sys.argv[3]) if (len(sys.argv)>=4) else 0.5;
	if ( op == "make" ):
		make_graph( fname, tol )
	elif( op == "clique"):
		make_clique( fname, tol )
	elif( op == "hist" ):
		histogram( fname )
	elif (op=="plot"):
		plotG(fname)
