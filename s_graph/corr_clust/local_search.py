"""
Autor: Oscar Vargas Pabon

Bounding and Comparing Methods for Correlation Clustering Beyond ILP
Micha Elsner and Warren Schudy

Aqui estan los greedy ahi expuestos

La 'local_search' tambien es la descrita en 
	A partitioning approach to structural balance
	Patrick Doreian a,*, Andrej Mrvar b
"""

import networkx as nx
import time, random
from collections import deque
from corr_clust.utils import calculate_objective, sanitize_cluster

###############################################################################################
#################################### Greedy methods ###########################################
###############################################################################################

def VOTE_quality(G, node:int, cluster_ind:int, cluster:dict[str,int]) -> float :
	res:float = 0;
	for edge in G.edges( node ):
		if ( edge[1] in cluster ):
			if ( cluster[edge[1]] == cluster_ind ):
				res += G.edges[edge]['weight'];
			else:
				res -= G.edges[edge]['weight']
	return res;

def FIRST_quality( G, node:int, cluster_ind:int, cluster:dict[str,int], frst_order:dict[str,int] ) -> float :
	res:int = -1;
	for edge in G.edges( node ):
		if ( edge[1] in cluster and cluster[edge[1]] == cluster_ind ):
			if ( G.edges[edge]['weight'] > 0 ):
				res = max( res, frst_order[edge[1]] )
	return res;

def BEST_quality( G, node:int, cluster_ind:int, cluster:dict[str,int] ) -> float :
	res:int = -1;
	for edge in G.edges( node ):
		if ( edge[1] in cluster and cluster[edge[1]] == cluster_ind ):
			res = max( res, G.edges[edge]['weight'] )
	return res;

def calc_PIVOT_heur( G, permutation:list[str] ) -> dict[str,int]:
	cluster={}; cluster_num:int = 0;
	for act in permutation:
		if ( act not in cluster ):
			cluster[act] = cluster_num; cluster_num += 1;
			for edge in G.edges(act):
				if ( edge[1] not in cluster and G.edges[edge]['weight'] > 0 ):
					cluster[edge[1]] = cluster[act]
	return cluster;

def paper_greedy( G,permutation:list[str] ) -> dict[str,int]:
	cluster = {"VOTE":{},"FIRST":{},"BEST":{}}; cluster_num = {"VOTE":0,"FIRST":0,"BEST":0};

	frst_order = {}; iteration:int=0; # FIRST
	for act in permutation:
		besto:int={"VOTE":cluster_num["VOTE"],"FIRST":cluster_num["FIRST"],"BEST":cluster_num["BEST"]};
		bestVal:int={"VOTE":0,"FIRST":0,"BEST":0};
		for cl in range(max(cluster_num.values())):
			val = {"VOTE":VOTE_quality( G, act, cl, cluster ),
			"FIRST":FIRST_quality( G, act, cl, cluster, frst_order),
			"BEST":BEST_quality( G, act, cl, cluster )
			}
			for ky in cluster.keys():
				if ( bestVal[ky] < val[ky] ):
					besto[ky] = cl; bestVal[ky] = val[ky];
		for ky in cluster.keys():
			cluster[ky][act] = besto[ky];
			if ( cluster_num[ky] == besto[ky] ): cluster_num[ky] += 1;

		frst_order[act] = iteration; iteration += 1; # FIRST
	# retorno el mejor de las heuristicas
	cluster["PIVOT"] = calc_PIVOT_heur( G, permutation );
	best_cluster = "NULL"; best_value:float = float("-inf");
	for ky in cluster.keys():
		val = calculate_objective( G, cluster[ky] )
		#print(ky,val)
		if ( best_value < val ): 
			best_cluster = ky;
			best_value = val;
	return cluster[best_cluster]

############################################################################################
######################################### Baseline #########################################
############################################################################################

def baseline_cluster( G ) -> dict[str,int]:
	cl_df = {}; cl_eq={}; cnt=0;
	for act in G.nodes:
		cl_df[act] = cnt;
		cnt += 1;
		cl_eq[act] = 0;
	res = cl_df if calculate_objective(G,cl_df) > calculate_objective(G,cl_eq) else cl_eq
	return res;
def all_positive_cluster(G) -> dict[str,int]:
	vis = set(); cl={}; cl_num=0;
	for act in G.nodes:
		if ( act not in vis ):
			s = [act]; vis.add(act);
			while ( len(s) > 0 ):
				act = s.pop(); cl[act] = cl_num;
				for edge in G.edges(act):
					if ( edge[1] not in vis and G.edges[edge]['weight']>=0 ):
						vis.add( edge[1] ); s.append( edge[1] );
			cl_num += 1;
	return cl;

############################################################################################
####################################### Local Search #######################################
############################################################################################



def local_search( G, cluster:dict[str,int], time_limit:float=10 ) -> dict[str,int]:
	cluster_num = 0;
	for val in cluster.values():
		cluster_num = max( cluster_num, val+1 );
	allNodes = [ act for act in G.nodes ];

	#print("init: ", calculate_objective(G,cluster))

	start_time = time.time()
	
	touched = {};q = deque();
	for act in G.nodes:
		touched[act] = True;
		q.append( act );
	
	while ( len(q) > 0 and ( time.time()-start_time) < time_limit ):
		act = q.popleft();
		touched[act] = False;

		deg:int = 0; in_consideration = {cluster_num:0,cluster[act]:0};
		for edge in G.edges(act):
			deg += G.edges[edge]['weight'];
			if ( cluster[edge[1]] not in in_consideration ): in_consideration[cluster[edge[1]]]=0;
			in_consideration[cluster[edge[1]]] += G.edges[edge]['weight'];

		besto:int = cluster_num; bestVal:float = -deg;
		for num,val in in_consideration.items():
			val = 2*val - deg
			if ( bestVal < val or ( bestVal == val and num == cluster[act] ) ): 
				besto=num; bestVal = val;
		if ( besto != cluster[act] ):
			for edge in G.edges(act):
				if ( not touched[edge[1]]  ):
					touched[edge[1]] = True;
					q.append( edge[1] );
			cluster[act] = besto;
			if ( besto == cluster_num ): cluster_num += 1;

	cluster = sanitize_cluster( G, cluster )
	#print(len(q),"_",calculate_objective(G,cluster))
	if ( len(q) == 1 ): print(q)
	return cluster;

def positive_refinement( G, cluster ):
	neo_cluster={}; cl_num = 0;
	for act in G.nodes:
		if ( act not in neo_cluster ):
			s = [act]; neo_cluster[act] = cl_num;
			while ( len(s) > 0 ):
				act = s.pop(); neo_cluster[act] = cl_num;
				for edge in G.edges(act):
					if ( edge[1] not in neo_cluster and cluster[edge[1]]==cluster[act] and G.edges[edge]['weight']>=0 ):
						s.append( edge[1] ); neo_cluster[edge[1]]= cl_num;
			cl_num += 1;
	return neo_cluster;


############################################################################################
####################################### Corrl #######################################
############################################################################################

def get_init_cluster( G, rep:int=10 ) -> dict[str,int]:
	return baseline_cluster( G )
	allNodes=[ act for act in G.nodes ]
	c1 = paper_greedy( G, allNodes )
	for i in range(rep):
		random.shuffle( allNodes );

		ctmp = paper_greedy( G, allNodes )
		if ( calculate_objective(G,c1) < calculate_objective(G,ctmp) ):c1 = ctmp;

	#res = c1
	c2 = baseline_cluster( G )
	c3 = all_positive_cluster( G );
	c2 = c2 if calculate_objective(G,c2) > calculate_objective(G,c3) else c3;
	res = c1 if calculate_objective(G,c1) > calculate_objective(G,c2) else c2;
	return res;

def local_correlationClustering( G, time_limit:float=10 ):
	
	init_cluster = get_init_cluster( G );
	#tmp = calculate_objective( G, init_cluster )
	#print("comienza")#
	inter_cluster = local_search( G, init_cluster, time_limit=time_limit )
	inter_cluster = positive_refinement( G, inter_cluster );
	cluster  = local_search( G, inter_cluster, time_limit=time_limit )
	#tmp1 = calculate_objective( G, cluster)
	#assert( tmp <= tmp1+1e-8)
	return cluster;

if __name__ == "__main__":
	G = nx.Graph()
	G.add_nodes_from([i for i in range(4)] )
	G.add_edges_from( [(0,1,{"weight":1}),(1,2,{"weight":-1}),(2,3,{"weight":1}),(3,0,{"weight":-1})] )
	cl = correlationClustering( G )
	print(cl)