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

#include <bits/stdc++.h>

typedef long long lint;

using namespace std;

#define debug(args...) { string _s = #args; replace(_s.begin(), _s.end(), ',', ' '); stringstream _ss(_s); istream_iterator<string> _it(_ss); raw_debug(_it, args);}
void raw_debug(istream_iterator<string> it) {cerr<<endl;assert(it==it);}
template<typename T, typename... Args>
void raw_debug(istream_iterator<string> it, T a, Args... args) { cerr <<"<"<< *it << "->" << a << "> "; raw_debug(++it, args...); }
#define idebug(v) {cerr<<'['<<#v<<']';for(const auto &el:v)cerr << ' ' << el; cerr << endl;}
#define adebug(ar,n) {cerr<<'['<<#ar<<']';for(int i=0;i<n;++i)cerr << ' ' << ar[i]; cerr << endl;}
template <typename t1,typename t2> ostream &operator<<(ostream &os, const pair<t1,t2> &pr){return os<<"("<<pr.first<<";"<<pr.second<<")";};

#define rep(i,strt,end) for(int i = strt ; i !=int(end) ; (int(strt)<int(end))?++i:--i )
#define rall(vec) vec.rbegin(), vec.rend()
#define all(vec) vec.begin(), vec.end()
#define sz(vec) int(vec.size())
#define eb emplace_back
#define pb push_back
#define pob pop_back
#define pf push_front
#define pof pop_front

mt19937_64 rng_64( chrono::steady_clock::now().time_since_epoch().count() );
constexpr int ilog2( int num ) { return 8*sizeof(int) - __builtin_clz( num ) - 1; }
template<typename tpow> constexpr tpow mpow(tpow x,lint e,tpow m){tpow res=1;while(e){if(e&1ll)res=(res*1ll*x)%m;e>>=1;x=(x*1ll*x)%m;}return res;}

const int template_limit = 1e6;
int a[template_limit], b[template_limit];

void solve() {
	
}

int32_t main(){
	ios_base::sync_with_stdio(false);
    cin.tie(NULL);
	cout << setprecision(12) << fixed;

    int t = 2;
    cin >> t; ++t;
    while ( --t ) {
		solve();
    }
	return 0;
}

