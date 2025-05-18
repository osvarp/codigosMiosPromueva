"""
Autor: Oscar Vargas Pabon
Fecha: 10/04/2025

Trying stuff with an lp relaxation
"""
import networkx as nx
import pulp
from heapq import heappop, heappush
import math
from corr_clust.local_search import local_search

# 0 -> mismo grupo ; 1 -> grupos distintos

def lp_relax( G ):
  problem = pulp.LpProblem( "exec", pulp.LpMinimize )
  all_nodes = list(G.nodes)
  all_var = []
  for i1 in range(len(all_nodes)):
    a1 = all_nodes[i1]
    for i2 in range(i1+1,len(all_nodes)):
      a2 = all_nodes[i2]
      all_var.append( (a1,a2) )
  x = pulp.LpVariable.dicts( "x", all_var, lowBound=0,upBound=1,cat="Continuous" )
  # objective function
  problem += pulp.lpSum([ -G.edges[e]['weight']*(1-x[e]) if (G.edges[e]['weight']<0) else G.edges[e]['weight']*x[e] for e in G.edges])
  for i1 in range(len(all_nodes)):
    a1 = all_nodes[i1]
    for i2 in range(i1+1,len(all_nodes)):
      a2 = all_nodes[i2]
      for i3 in range(i2+1,len(all_nodes)):
        a3 = all_nodes[i3]
        problem += x[a1,a2]+x[a2,a3] >= x[a1,a3]
        problem += x[a1,a2]+x[a1,a3] >= x[a2,a3]
        problem += x[a1,a3]+x[a2,a3] >= x[a1,a2]
  solver = pulp.PULP_CBC_CMD(msg=0,mip=True)
  #### el otro no sirve
  #solver = pulp.COIN_CMD(path="C:\\Users\\oscar\\Local\\ponti\\promueva\\testing_measures\\coin_or_clp\\bin\\Clp.exe")
  
  
  resp = problem.solve(solver)
  #print(pulp.LpStatus[problem.status])
  X = {}
  for e in all_var:
    ee = (min(e[0],e[1]),max(e[0],e[1]))
    X[ee] = x[e].value()
  
  return X

def cut(G, S):
  res = 0
  for v in S:
    for e in G.neighbors(v):
      if ( e not in S):
        res += max(0,G.edges[v,e]['weight'])
  return res
def vol(G, S, X):
  res = 0
  for v in S:
    for e in G.neighbors(v):
      ee = (min(v,e),max(v,e))
      res += max(0,G.edges[v,e]['weight']*X[ee])
  return res

def round( G, X, Cc=2.01 ):
  cl:dict[str,int] = {}; cl_am=0;
  def aux_round( u ):
    r = 0
    pq = [(0,u)]
    vis = {act:10 for act in G.nodes}
    vis[u] = 0;
    ss =set()
    while ( len(pq) > 0 ):
      dst,v = heappop(pq)
      if ( dst > vis[v] ): continue
      if ( dst <= r or cut(G, ss) > Cc*math.log(len(G.nodes)+1)*vol(G,ss,X) ):
        cl[v] = cl_am
        ss.add(v)
        r = dst
        for e in G.neighbors(v):
          ee = (min(v,e),max(v,e))
          if ( vis[e] > X[ee] ):
            vis[e] = X[ee]
            heappush(pq, (vis[e],e))
      else:
        pq = []

  for u in G.nodes:
    if ( u not in cl ):
      aux_round(u)
      cl_am += 1;
  return cl

def lp_cluster( G ):
  X = lp_relax( G )
  print([act for act in X.values()])
  inter_cl = round( G, X )
  cl = local_search( G, inter_cl )
  return cl


def test0():
  G = nx.Graph()
  G.add_nodes_from([0,1,2])
  G.add_edges_from([(0,1),(0,2),(1,2)], weight=1)
  G.edges[0,1]['weight'] = -1
  cl = lp_cluster(G)
  print(cl)
def test1():
  G = nx.Graph()
  G.add_nodes_from([0,1,2,3,4])
  G.add_edges_from([(0,1),(0,2),(2,3),(3,4),(1,2),(3,1),(4,1)], weight=1)
  #G.edges[(2,3)]['weight'] = -1
  G.edges[(1,2)]['weight'] = -1
  G.edges[(1,3)]['weight'] = -1
  G.edges[(1,4)]['weight'] = -1
  cl = lp_cluster(G)
  print(cl)
if __name__ == "__main__":
  test1()
  pass