"""
Autor: Oscar Vargas Pabon

Nota: calculate_objective esta contando cada arista en ambas direcciones
"""

def calculate_objective( G, cluster:dict[str,int] ) -> float:
	res:float = 0;
	for act in G.nodes:
		for edge in G.edges( act ):
			if ( cluster[edge[0]] == cluster[edge[1]] ):
				res += G.edges[edge]['weight']
			else:
				res -= G.edges[edge]['weight']
	return res;
def calculate_cut( G, cluster:dict[str,int] ) -> float:
	res:float = 0;
	for act in G.nodes:
		for edge in G.edges( act ):
			if ( cluster[edge[0]] != cluster[edge[1]] ):
				res -= G.edges[edge]['weight']
	return res/2; # porque estamos contando cada arista en ambas direcciones

def sanitize_cluster( G, cluster:dict[str,int] ) -> dict[str,int]:
	san_cluster = {}; cluster_num:int = 0;
	for node in G.nodes:
		if ( node not in san_cluster ):
			s = [node]; san_cluster[node] = cluster_num;
			while ( len(s) > 0 ):
				act = s.pop();
				for edge in G.edges(act):
					if ( cluster[edge[1]] == cluster[edge[0]] and edge[1] not in san_cluster ):
						san_cluster[edge[1]] = cluster_num
						s.append( edge[1] );
			cluster_num += 1;
	return san_cluster;