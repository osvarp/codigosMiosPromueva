import sys
import networkx as nx
from corr_clust.local_search import local_correlationClustering as lcc # local_correlation_clustering
from corr_clust.local_search import local_search
from corr_clust.bridge_reduction import weak_reduction as br_cc
from corr_clust.utils import calculate_objective
from corr_clust.lp_relax import lp_cluster
from corr_clust.treewidth import weak_corrCl_boundedTreewidth as corrcl_tw

def multicut_int( fname:str, max_time:float=10 ):
	G = nx.read_gexf( fname )
	#cluster = lcc(G, max_time )
	#cluster = br_cc( G )
	#cluster = lp_cluster( G )
	cluster = corrcl_tw( G )
	for act, cl, in cluster.items():
		G.nodes[act]["mnc_partition"] = cl
	nx.write_gexf(G, fname )
	print( "termina con ", calculate_objective( G, cluster ) )
from corr_clust.treewidth import strong_corrCl_boundedTreewidth as str_corrcl_tw

def strong_int(fname:str):
	G = nx.read_gexf( fname )
	cluster = str_corrcl_tw( G )
	for act, cl, in cluster.items():
		G.nodes[act]["mxc_partition"] = cl
	nx.write_gexf(G, fname )
	print( "termina con ", calculate_objective( G, cluster ) )

def manual_refinement( fname:str, strt:str, max_time:float=10 ):
	G = nx.read_gexf( fname );
	cluster = {}; cl_num = 0;
	for act in G.nodes:
		cluster[act] = G.nodes[act]['mnc_partition'];
		cl_num = max( cl_num, cluster[act] );

	s=[strt]; vis:set[str]={strt}; init_cl = cluster[strt];
	while ( len(s) > 0 ):
		act = s.pop();
		cluster[act]=cl_num;
		for edge in G.edges(act):
			if ( edge[1] not in vis and cluster[edge[1]]==init_cl and G.edges[edge]['weight']>=0 ):
				s.append(edge[1]); vis.add( edge[1] );
	cluster = local_search( G, cluster, max_time )
	for act, cl, in cluster.items():
		G.nodes[act]["mnc_partition"] = cl
	nx.write_gexf(G, fname )
	print( "termina con ", calculate_objective( G, cluster ) )


if __name__=="__main__":
	#nombre = 'CathyJuvinao (0.05)'
	nombre = 'VaneDeCol (0.12)'
	strong_int(sys.argv[1]);
	#manual_refinement( sys.argv[1], nombre,float(sys.argv[2]) if (len(sys.argv)>=3) else 10 )
	multicut_int( sys.argv[1], float(sys.argv[2]) if (len(sys.argv)>=3) else 10 )
