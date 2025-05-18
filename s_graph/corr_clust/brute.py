"""
Autor: Oscar Vargas Pabon

Estos algo's son brutos
"""

from corr_clust.utils import calculate_objective, sanitize_cluster
def strong_brute( G ) -> dict[str,int]:
	order = list(G.nodes)

	cl:[str,int]={}; 
	for act in order:
		cl[act] = 0;

	best:int=0; bestVal:float = calculate_objective( G, cl );
	for ind in range(1,1<<len(G.nodes)):
		cl = find_cl
		val = calculate_objective(  )

	res = {}
	for ind in range(len(order)):
		res[order[ind]] = 1 if ( (best&(1<<ind))>0 ) else 0
	return res;

def weak_brute( G ) -> dict[str,int]:
	all_nodes=[ act for act in G.nodes ]; stack=[];
	act_cl={};
	def recursive_brute( ind:int ):
		if ( ind == len(G.nodes) ):
			return act_cl.copy(), calculate_objective( G,act_cl );
		stack.append( ind ); act_cl[all_nodes[ind]] = ind;
		best_cl, best_val = recursive_brute( ind+1 );
		stack.pop();
		for name in stack:
			act_cl[all_nodes[ind]] = name;
			cand_cl, cand_val = recursive_brute( ind+1 );
			if ( cand_val > best_val ):
				best_val = cand_val; best_cl = cand_cl;
		return best_cl, best_val
	best_cl, _ = recursive_brute( 0 );
	return sanitize_cluster( G, best_cl )
