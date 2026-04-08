"""
Autor: Oscar Vargas Pabon

La idea de separarlo por los puentes viene de 
Separator-based data reduction for signed graph balancing
de Falk Hüffner · Nadja Betzler · Rolf Niedermeier

"""

import sys
import networkx as nx
from corr_clust.local_search import local_correlationClustering as w_lcc
from corr_clust.lp_relax import lp_cluster
from corr_clust.brute import *
from corr_clust.utils import sanitize_cluster, calculate_objective
from corr_clust.treewidth import tree_sizes,weak_corrCl_boundedTreewidth as weak_tree

###################################################################
##### Para encontrar los puentes y poder aplicar la reduccion #####
###################################################################

def tarjan_bridge( G ):
	sys.setrecursionlimit(len(G.nodes)*10)
	bridges=[]; discon=[]; # mi output
	my_time:int = 0;
	min_time = {}; in_time = {}
	def aux_bridge( node, act_comp, dfs_parent ):
		nonlocal my_time, min_time, in_time ## xd, no sabia que habia que hacer esto

		in_time[node] = my_time; min_time[node] = my_time; my_time += 1;
		act_comp.add( node )
		for edge in G.edges(node):
			edge = edge[1];
			if ( edge == dfs_parent ): continue;
			elif ( edge in in_time ):
				## ya lo visitamos
				min_time[node] = min( min_time[node], in_time[edge] );
			else:
				## no lo hemos visitado aun
				neo_comp = aux_bridge( edge, set(), node )
				min_time[node] = min( min_time[node], min_time[edge] )

				if ( min_time[edge] > in_time[node] ):
					# encontramos un puente, gg
					bridges.append( (node, edge) );
					discon.append( neo_comp );
				else:
					act_comp = act_comp.union( neo_comp );
		return act_comp
	for act in G.nodes:
		if ( act not in in_time ):
			lst_comp = aux_bridge( act, set(), None );
			discon.append( lst_comp );
	return bridges, discon;

#################################################################
#### Para unir dos conjuntos separados por un puente( o no ) ####
#################################################################

def weak_join( G, bridge, cluster_a, num_a, cluster_b,num_b ) -> tuple[dict[str,int],int]:
	if ( len(cluster_a) < len(cluster_b) ): 
		# para que cluster_a sea el que tenga menor cantidad de nodos (small to large)
		cluster_a,cluster_b=cluster_b,cluster_a
		num_a,num_b=num_b,num_a
	
	ren:dict[int,int]={};
	if ( bridge!=None ):
		if ( bridge[0] not in cluster_a ):
			bridge = (bridge[1],bridge[0]);
		if ( G.edges[bridge]['weight'] > 0 ): 
			ren[cluster_b[bridge[1]]]=cluster_a[bridge[0]];

	for nd, val in cluster_b.items():
		if ( val not in ren ):
			ren[val] = num_a;
			num_a += 1;
		cluster_a[nd] = ren[val]

	return cluster_a, num_a

def strong_join( G, bridge, cluster_a, num_a, cluster_b, num_b ) -> dict[str,int]:
	# Nota: num_a y num_b no los usamos para nada
	if ( len(cluster_a) < len(cluster_b) ): 
		# para que cluster_a sea el que tenga menor cantidad de nodos (small to large)
		cluster_a,cluster_b=cluster_b,cluster_a
		num_a,num_b=num_b,num_a

	change = 0;
	if ( bridge != None ):
		if ( bridge[0] not in cluster_a ): bridge = (bridge[1],bridge[0]);

		change = 0 if ( G.edge[bridge]['weight'] > 0 ) else 1
	for nd,val in cluster_b.items():
		cluster_a[nd] = val^change
	return cluster_a

###########################################
#### La reduccion en todo su esplendor ####
###########################################

def generic_reduction( G, my_join, my_solve ) -> dict[str,int]:
	dsu_pi:list[int,int] = []; brk_sol:list[dict[str,int],int]=[]; node_dsu:dict[str,int]={};
	def get_root( name ) -> int:
		"""
		Esto es para hacer un 'pseudo-dsu' que me ayude a localizar el cluster de cada nodo
		"""
		res:int=name;
		if ( type(name)==str ): 
			node_dsu[name] = get_root( node_dsu[name] );
			res = node_dsu[name];
		elif ( dsu_pi[name] != name ):
			dsu_pi[name] = get_root( dsu_pi[name] );
			res = dsu_pi[name];
		return res;

	bridges, subG = tarjan_bridge( G ) # computo la respuesta para cada subgrafo
	for i in range(len(subG)):
		dsu_pi.append( i ); brk_sol.append( my_solve( G.subgraph(subG[i]) ) )
		for node in subG[i]: node_dsu[node] = i;

	# uno los clusters en cada puente
	for bridge in bridges:
		u = get_root( bridge[0] ); v = get_root( bridge[1] );
		if ( len(brk_sol[u][0]) < len(brk_sol[v][0]) ): u,v=v,u; # aseguro que 'u' es el que tiene mas nodos
		brk_sol[u] = my_join( G, bridge, brk_sol[u][0], brk_sol[u][1], brk_sol[v][0], brk_sol[v][1] )
		dsu_pi[v] = u;

	agg_cl:dict[str,int]={}; agg_num:int = 0; # agrego sobre todos los componentes conexos del grafo
	for node in G.nodes:
		if ( node not in agg_cl ):
			ind = get_root( node )
			agg_cl, agg_num = my_join( G, None, agg_cl, agg_num, brk_sol[ind][0], brk_sol[ind][1] )
	return sanitize_cluster( G, agg_cl );

################################################
#### Metodos para parametrizar la reduccion ####
################################################

def weak_solve( G ) -> tuple[dict[str,int],int]:
	cl:dict[str,int];
	assert len(G.nodes)<=10 or tree_sizes(G)<13
	if ( len(G.nodes) <= 10 ):
		cl = weak_brute( G );
	elif ( tree_sizes(G) < 13 ):
		cl = weak_tree( G )
	elif ( len(G.nodes) <= 30 ):
		cl = lp_cluster( G )
	else:
		cl = w_lcc( G );
	num = max( cl.values() );
	return cl, num;

def weak_reduction( G ):
	return generic_reduction( G, weak_join, weak_solve )
#def strong_reduction( G ):



def group_analisis():
	G = nx.read_gexf( "..\\maxiAgreement.gexf" )
	br, ds = tarjan_bridge( G );
	cnt = 0
	for group in ds:
		print(len(group))
		cnt += len(group)
	print(cnt,len(G.nodes))

if __name__ == "__main__":
	group_analisis()
