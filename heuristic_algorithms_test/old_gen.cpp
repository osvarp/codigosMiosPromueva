/*
 ________
|    ___ |
|  ,',.(`|
| :  `'  |
| :) _  (|
|  `:_)_,|
|________|

Autor: Oscar Vargas Pabon
Fecha: 

*/
#pragma once


#include "model.cpp"
#include<vector>
#include<cassert>
#include<functional>

long long seed=std::chrono::steady_clock::now().time_since_epoch().count();
//long long seed= 1769192308049791000;
std::mt19937 rng( seed );
std::uniform_real_distribution<double> raw_rng_dbl(0,1);
inline double rng_dbl(){return raw_rng_dbl(rng);}
inline int gen(int lim){return (lim+rng()%lim)%lim;};

std::vector<double> gen_opi(int n){
	std::vector<double> res(n);for(double &ac:res)ac=rng_dbl();
	return res;
}

std::vector<Edge<double>> gen_scg(int n,double p,int girth=3){
	// generates a strongly connected component
	assert(n>=girth);
	std::vector<Edge<double>> res;
	for(int i=0;i<n;++i)res.emplace_back(i,i,rng_dbl());//self-edges
	for(int i=0;i<girth;++i)res.emplace_back(i?i-1:girth-1,i,rng_dbl());
	for(int i=girth;i<n;++i){
		int in=rng()%i,out=rng()%i;
		for(int j=0;j<i;++j)if(rng_dbl()<=p||j==in )res.emplace_back(j,i,rng_dbl());
		for(int j=0;j<i;++j)if(rng_dbl()<=p||j==out)res.emplace_back(i,j,rng_dbl());
	} // Now I have to deal with the weights ....
	std::vector<double> norm(n,0);for(Edge<double> &ac:res)norm[ac.v]+=ac.w;
	for(Edge<double> &ac:res)ac.w/=norm[ac.v];
	return res;
}

std::vector<std::vector<double>> gen_mat(int n,double p,int girth=3){
	std::vector<std::vector<double>> mat(n,std::vector<double>(n,0));
	std::vector<Edge<double>> edg=gen_scg(n,p,girth);
	for(const Edge<double> &e:edg)mat[e.u][e.v]=e.w;
	return mat;
}

std::vector<Edge<double>> gen_barabasiAlbert_scg(
	const int n,const int ein,const int eout, const int girth=3){
	// n -> graph size ; ein -> expected in-degree ; eout -> expected out-degree ; girth -> beginning cycle
	assert(n>=girth); std::vector<Edge<double>> res;
	for(int i=0;i<n;++i)res.emplace_back(i,i,rng_dbl());
	for(int i=0;i<girth;++i)res.emplace_back(i?i-1:girth-1,i,rng_dbl());
	
	std::vector<int> deg(n,0);

	std::vector<int> fenw(n+1,0);int f_tot=0;
	
	//std::vector<int> arr(n+1,0);
	auto update=[&](int x,int vl)->void{
		//arr[x]+=vl;
		assert(x>0);for(;x<=n;x+=x&-x)fenw[x]+=vl;
	};
	auto query=[&](int x)->int{
		assert(x>0);
		int rq=0;for(;x;x-=x&-x)rq+=fenw[x];
		return rq;
	};
	auto binlift=[&](int obj)->int{

		//std::cerr << f_tot << "???? here " << obj << std::endl;
		//std::cerr << "[arr]";for(int ac:arr)std::cerr <<' ' << ac; std::cerr << '\n';
		int ind=0,nx,e=1;while(e<=n)e<<=1;
		for(;e;e>>=1){
			nx=ind+e;if(nx<=n&&fenw[nx]<obj){
				obj-=fenw[nx];ind=nx;
			}
		}

		//std::cerr << obj << " asdfa " << ind << std::endl;
		return ind;
	};
	//std::cerr << "xdxd" << std::endl;
	std::vector<bool> us(n,0);
	for(int i=0;i<girth;++i)++f_tot,update(i+1,1);
	for(int i=girth;i<n;++i){
		const int prv=res.size();
		for(int j=0;j<=ein;++j){
			int nd=binlift(gen(f_tot));
			if(us[nd])continue;
			assert(nd<n);
			//std::cerr << nd << " ???? " << i << std::endl;
			res.emplace_back(nd,i,rng_dbl());
			us[nd]=1;
			++f_tot,update(nd+1,1);
		}
		for(int j=prv;j<int(res.size());++j)us[res[j].u]=0;
		const int prv2=res.size();
		for(int j=0;j<=eout;++j){
			int nd=binlift(gen(f_tot));
			if(us[nd])continue;
			assert(nd<n);
			//std::cerr << nd << " ??_? " << i << std::endl;
			res.emplace_back(i,nd,rng_dbl());
			us[nd]=1;
		}f_tot+=res.size()-prv2,update(i+1,res.size()-prv2);
		for(int j=prv2;j<int(res.size());++j)us[res[j].v]=0;
	} // Normalize 
	//std::cerr << "?????" << std::endl;
	std::vector<double> norm(n,0);for(Edge<double> &ac:res)norm[ac.v]+=ac.w;
	for(Edge<double> &ac:res)ac.w/=norm[ac.v];
	return res;
}

#include "graph_metrics.cpp"
std::vector<Edge<double>> gen_barAlb_trans(const int n){
	// https://github.com/Lordrap2002/opinion-model-maude/blob/main/generador.py
	std::vector<Edge<double>> res;while(!strongly_connected(n,res)){
		res.clear();
		//std::cout << "xxdxdxdxxxd" << std::endl;
		std::vector<int> N={0,1},deg(n,1);int tt=0;N.reserve(n);
		for(int x=2;x<n;++x){
			for (int y:N){
				// 
				//if(gen(tt+x+1)<deg[y]){
				if(rng_dbl()<double(deg[y])/double(tt+x+1)){
					//std::cout << "===????"<<std::endl;
					res.emplace_back(y,x,rng_dbl());
					++deg[y];++tt;
				}
				//if(gen(tt+x+1)<deg[x]){
				if(rng_dbl()<double(deg[x])/double(tt+x+1)){
					//std::cout << "===????"<<std::endl;
					res.emplace_back(x,y,rng_dbl());
					++deg[x];++tt;
				}
			}N.push_back(x);
		}
	}
	for(int i=0;i<n;++i)res.emplace_back(i,i,rng_dbl());

	std::vector<double> norm(n,0);for(Edge<double> &ac:res)norm[ac.v]+=ac.w;
	for(Edge<double> &ac:res)ac.w/=norm[ac.v];
	return res;
}