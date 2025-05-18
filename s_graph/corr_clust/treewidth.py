"""
Autor: Oscar Vargas Pabon
"""
import networkx as nx
from corr_clust.utils import sanitize_cluster

############################################################################
############################# precomputations ##############################
############################################################################

def precompute_tree( G, T, tnd, pi=None, strong:bool=True ):
	free_nd=[]; taken_nd = [];
	for nd in tnd:
		######################################### small improvement on (weak) case
		if ( G.nodes[nd]['cl'] == -1 ): free_nd.append((-G.degree(nd), nd));
		else: taken_nd.append(nd);
	free_nd.sort()
	for i in range(len(free_nd)): free_nd[i] = free_nd[i][1]
	

	T.nodes[tnd]['ord_nd'] = free_nd+taken_nd
	ord_nd = T.nodes[tnd]['ord_nd']
	inv_nd = { ord_nd[i]:i for i in range(len(ord_nd)) }

	def precompute_plausible_group():
		vis = {}; grp = {};
		for i in range(len(free_nd)):

			nd = ord_nd[i];
			if ( nd not in vis ):
				vis[nd] = i; s = [nd]; grp[i] = set();
				while ( len(s) > 0 ):
					nd = s.pop();
					if ( nd in tnd ): grp[i].add(nd);

					for e in G.neighbors(nd):
						if ( e not in vis and G.edges[nd,e]['weight']>0 ):
							if ( G.nodes[e]['cl'] == -1 ):
								s.append(e); vis[e] = i;
							else: grp[i].add( e );
							# only nodes in tnd can have edges to filled ones
		pl_grp={}; i_grp=0;
		for _,g in grp.items():
			for nd in g: pl_grp[nd]=i_grp;
			i_grp += 1;
		T.nodes[tnd]['plausible_group'] = (pl_grp,i_grp)

	if ( not strong ):
		precompute_plausible_group()

	for nd in free_nd: G.nodes[nd]['cl']=0; # to avoid overcounting free nodes
	

	
	def precompute_submsk(e):
		submsk = 0
		for nd in e:
			if ( nd in inv_nd ):
				#assert nd in tnd
				submsk |= 1<<inv_nd[nd]
		T.nodes[e]['submsk'] = submsk;
	def precompute_lsubmsk(e):
		lsubmsk=[]
		for nd in tnd:
			if (nd not in e ):
				lsubmsk.append( nd )
		T.nodes[e]['lsubmsk']=tuple(lsubmsk)
	for e in T.neighbors(tnd):
		if ( e != pi ):
			precompute_tree( G, T, e, tnd, strong=strong )
			if ( strong ):
				precompute_submsk(e)
			else:
				precompute_lsubmsk(e)
	for nd in free_nd: G.nodes[nd]['cl'] = -1; # to free this nodes
	#print(len(free_nd),"__",len(tnd))

############################################################################
################################ (strong) ##################################
############################################################################

def strong_dp( G, T, tnd, mem, msk=0, pi=None ):
	## tnd -> tree-node ; pi -> parent in the tree

	if ( (tnd,msk) not in mem ):
		ord_nd=T.nodes[tnd]['ord_nd']
		free_i = 0;
		while ( free_i < len(ord_nd) and G.nodes[ord_nd[free_i]]['cl']==-1 ):
			G.nodes[ord_nd[free_i]]['cl']=0;
			free_i += 1;
		inv_nd = { ord_nd[i]:i for i in range(len(ord_nd)) }
		
		def calculate_incost():
			## calcula el coste de las aristas no previamente sumadas
			in_cost = 0;
			for i in range(free_i):
				nd = ord_nd[i]
				for e in G.neighbors(nd):
					if ( e in inv_nd and inv_nd[nd] < inv_nd[e] ):
						if ( G.nodes[nd]['cl'] == G.nodes[e]['cl'] ):
							in_cost += G.edges[nd,e]['weight']
						else:
							in_cost -= G.edges[nd,e]['weight']
			return in_cost
		init_cost = calculate_incost()
		upper_msk=0; #la parte que no esta libre para modificar
		for i in range(free_i,len(ord_nd)):
			upper_msk |= G.nodes[ord_nd[i]]['cl']<<i

		case_arr = [ 0 for _ in range( free_i )]
		best_msk = -1; best_val = float("-inf");
		for lower_msk in range(1<<free_i):
			case_msk = lower_msk|upper_msk; #la mascara completa del caso
			case_cst = init_cost
			#case_cst = calculate_incost()
			for e in T.neighbors(tnd):
				if ( e !=pi ):
					case_cst += strong_dp( G, T, e, mem, msk=case_msk&T.nodes[e]['submsk'], pi=tnd )[0]
			
			if ( best_val < case_cst ):
				best_val = case_cst; best_msk = case_msk;
			#### modificando el arreglo para dar espacio al nuevo caso
			if ( lower_msk==(1<<free_i-1) ): continue; # este es un edge-case
			lim_i = 0; case_arr[0] += 1;
			while ( lim_i < free_i and case_arr[lim_i] == 2 ):
				case_arr[lim_i] = 0; case_arr[lim_i+1] += 1;
				lim_i += 1;
			for j in range(lim_i+1): G.nodes[ord_nd[j]]['cl'] = case_arr[j]
			for j in range(lim_i+1):
				nd = ord_nd[j]
				for e in G.neighbors(nd):
					if ( e in inv_nd and lim_i < inv_nd[e] ):
						if ( G.nodes[e]['cl'] == G.nodes[nd]['cl'] ):
							init_cost += 2*G.edges[nd,e]['weight']
						else:
							init_cost -= 2*G.edges[nd,e]['weight']
		for i in range(free_i): G.nodes[ord_nd[i]]['cl'] = -1;
		mem[tnd,msk] = best_val,best_msk;
	return mem[tnd,msk];
def strong_rebuild( G,T, tnd, mem, cl, msk=0, pi=None ):
	assert (tnd,msk) in mem, "Error: no se cumplio esta condicion"

	ord_nd=T.nodes[tnd]['ord_nd']
	_,neo_msk=mem[tnd,msk]
	i = 0;
	while ( i < len(ord_nd) and ord_nd[i] not in cl ):
		cl[ord_nd[i]] = neo_msk&1;
		neo_msk >>= 1;
		i += 1
	_,neo_msk=mem[tnd,msk]
	for e in T.neighbors(tnd):
		if ( e !=pi ):
			strong_rebuild( G, T, e, mem, cl, msk=neo_msk&T.nodes[e]['submsk'], pi=tnd )

def strong_corrCl_boundedTreewidth( G ):
	mem = {}; cl = {};
	tw,T = nx.approximation.treewidth_min_degree(G)
	#tw,T = nx.approximation.treewidth_min_fill_in(G)
	assert tw < 15, "Error: considero tw(%d) muy grande."%(tw);

	for nd in G.nodes: G.nodes[nd]['cl'] = -1;

	strt = list(T.nodes)[0]
	#strt = min(list(T.nodes));
	precompute_tree( G, T, strt )

	cst,msk = strong_dp( G, T, strt, mem )
	print(cst,'=',cst*2,msk)
	
	strong_rebuild( G, T, strt, mem, cl )
	return cl;

############################################################################
################################# (weak) ###################################
############################################################################

def unpack_weak(G,T,tnd):
	ord_nd = T.nodes[tnd]['ord_nd']
	inv_nd = {ord_nd[i]:i for i in range(len(ord_nd))}

	free_i = 0;
	while ( free_i < len(ord_nd) and G.nodes[ord_nd[free_i]]['cl'] == -1 ):
		free_i += 1;

	am_cl=-1;
	for i in range(free_i,len(ord_nd)):am_cl=max(am_cl,G.nodes[ord_nd[i]]['cl']);
	am_cl += 1;

	ren_cl = { am_cl+ind:ind for ind in range(free_i) }; 
	for i in range(free_i,len(ord_nd)):
		cl_val = G.nodes[ord_nd[i]]['cl']
		if ( cl_val not in ren_cl ):ren_cl[cl_val] = len(ren_cl);

	jmp = [1]
	for _ in range(len(tnd)): jmp.append(jmp[-1]*(len(tnd)+1))

	return ord_nd,inv_nd,free_i,am_cl,ren_cl,jmp

def weak_dp( G, T, tnd, mem,msk=0, pi=None ):
	if ( (tnd,msk) not in mem ):
		ord_nd,inv_nd,free_i,am_cl,ren_cl,jmp = unpack_weak(G,T,tnd)
		i_msk=0;
		for i in range(free_i,len(ord_nd)):
			i_msk += ren_cl[G.nodes[ord_nd[i]]['cl']]*jmp[i]
		
		pl_grp,i_grp=T.nodes[tnd]['plausible_group']
			
		plaus=[set() for _ in range(i_grp)]
		for i in range(free_i,len(ord_nd)):
			nd = ord_nd[i]
			if ( nd in pl_grp ): plaus[pl_grp[nd]].add( G.nodes[nd]['cl'] );

		def node_contrib( nd ) -> tuple[dict[int,float],float]:
			contrib:dict[int,float] = {}; tot:float=0;
			for e in G.neighbors(nd):
				if ( G.nodes[e]['cl'] != -1 ):
					#print("Edge",nd,e,G.nodes[e]['cl'])
					cl = G.nodes[e]['cl']
					if ( cl not in contrib ): contrib[cl] = 0;
					contrib[cl] += G.edges[nd,e]['weight'];
					tot += G.edges[nd,e]['weight'];
			#print(contrib)
			return contrib,tot;
		best_msk = None; best_val=float("-inf");
		def enumerate_partitions( ind:int, act_val:float,i_msk:int, l_msk:list=[] ):
			nonlocal am_cl, T, G, mem, tnd, pi, best_val,best_msk,free_i
			if ( ind >= free_i ):
				for e in T.neighbors(tnd):
					if ( e != pi ):
						e_msk=i_msk;
						for nd in T.nodes[e]['lsubmsk']:
							nd_ind=inv_nd[nd]
							e_msk-= ren_cl[G.nodes[nd]['cl']]*jmp[nd_ind]
						#e_msk = tuple([G.nodes[nd]['cl'] for nd in ord_nd])
						act_val += weak_dp( G, T, e, mem,msk=e_msk, pi=tnd )[0]
				if ( act_val > best_val ):
					best_val=act_val; best_msk=tuple(map(lambda x: ren_cl[x], l_msk));
			else:
				nd = ord_nd[ind]
				contrib,tot=node_contrib(nd)
				act_val = act_val-tot

				cl = am_cl+ind
				G.nodes[nd]['cl'] = cl;
				plaus[pl_grp[nd]].add(cl); l_msk.append(cl);
				enumerate_partitions( ind+1,act_val,i_msk+ind*jmp[ind], l_msk)
				plaus[pl_grp[nd]].remove(cl); l_msk.pop();
				for cl in plaus[pl_grp[nd]]:
					if ( cl not in contrib ): contrib[cl] = 0;
					G.nodes[nd]['cl'] = cl
					l_msk.append( cl );
					enumerate_partitions(ind+1,act_val+2*contrib[cl],i_msk+ren_cl[cl]*jmp[ind],l_msk)
					l_msk.pop();
				G.nodes[nd]['cl'] = -1;
		enumerate_partitions(0,0,i_msk)
		mem[tnd,msk]=(best_val,best_msk)
	return mem[tnd,msk]
def weak_rebuild( G, T, tnd, mem, cl, pi=None,msk=0 ):
	ord_nd,inv_nd,free_i,am_cl,ren_cl,jmp = unpack_weak(G,T,tnd)

	_,neo_msk = mem[tnd,msk]
	
	inv_cl=[-1 for _ in range(len(ren_cl))];
	for key,val in ren_cl.items(): inv_cl[val]=key;
	
	for i in range(free_i):
		nd = ord_nd[i]
		cl[nd] = inv_cl[neo_msk[i]]
		G.nodes[nd]['cl']=cl[nd]

	i_msk=0;
	for i in range(len(ord_nd)):
		i_msk += ren_cl[G.nodes[ord_nd[i]]['cl']]*jmp[i]
	
	for e in T.neighbors(tnd):
		if ( e != pi ):
			e_msk=i_msk;
			for nd in T.nodes[e]['lsubmsk']:
				nd_ind=inv_nd[nd]
				e_msk-= ren_cl[G.nodes[nd]['cl']]*jmp[nd_ind]
			weak_rebuild( G, T, e, mem, cl, pi=tnd, msk=e_msk )

def weak_corrCl_boundedTreewidth( G ):
	mem = {}; cl = {};
	tw1,T1 = nx.approximation.treewidth_min_degree(G)
	tw2,T2 = nx.approximation.treewidth_min_fill_in(G)
	if ( tw1 > tw2 ): tw,T=tw2,T2;
	else: tw,T=tw1,T1;

	assert tw < 15, "Error: considero tw(%d) muy grande."%(tw);
	#print("lo hago con tw",tw)
	for nd in G.nodes: G.nodes[nd]['cl'] = -1;

	strt = list(T.nodes)[0]
	#print(strt)
	#strt = min(list(T.nodes));
	precompute_tree( G, T, strt, strong=False )

	cst,msk = weak_dp( G, T, strt, mem )
	print(cst,'=',cst*2,msk)
	
	weak_rebuild( G, T, strt, mem, cl )
	cl = sanitize_cluster(G,cl)
	for nd in G.nodes: G.nodes[nd]['cl'] = -1;
	return cl;
def tree_sizes(G):
	tw1,T1 = nx.approximation.treewidth_min_degree(G)
	tw2,T2 = nx.approximation.treewidth_min_fill_in(G)
	return min(tw1,tw2)

if __name__=="__main__":
	G = nx.Graph()
	G.add_node(1); G.add_node(2); G.add_node(3); G.add_node(4);
	G.add_edge(1,2,weight=-1); G.add_edge( 3,4,weight=1 )
	G.add_edge(1,3,weight=1); G.add_edge(2,3,weight=-1);
	cl = strong_corrCl_boundedTreewidth(G)
	print(cl)