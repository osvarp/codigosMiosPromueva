"""
Autor: Oscar Vargas Pabon

jugando con la medida
"""
import matplotlib.pyplot as plt

alpha, k = 1.5978, 1

def assertForAll( dist:list[float], cond ) -> None:
	for el in dist:
		assert cond(el), "Invalid value on distribution.";

def ERmeasure( y:list[float], pi:list[float] ) -> float:
	"""
	La medida de polarizacion Esteban-Ray
	"""
	assert len(y) == len(pi), "Input not a distribution.";
	assertForAll( pi, lambda x: x >= 0 );

	measure = 0;
	for i in range(len(y)):
		for j in range(len(y)):
			measure += pow( pi[i], 1+alpha ) * pi[j] * abs(y[i]-y[j]);
	measure *= k;
	return measure;

def checkingFirstAxiom( p:float, q:float, midPoint:float, delta:float, precision:int )->list[float]:
	ERoutput=[0 for _ in range(precision)]
	for act in range(precision):
		effectiveDistance = (act+1)* delta/precision;
		y = [ 0, midPoint-effectiveDistance, midPoint+effectiveDistance ];
		#print(y[1:])
		pi = [ p, q, q ];
		ERoutput[act] = ERmeasure( y, pi );
	joined = ERmeasure( [0,midPoint],[p, 2*q] )
	#print( "unidos2 ", ERmeasure( [0, midPoint,midPoint], [p,q,q] ) )
	print( "polarizacion puntos unidos: ", joined, "\nPolarizacion puntos separados: ", ERoutput[-1] );
	if( joined==ERoutput[-1] ) : cad = '='
	elif( joined > ERoutput[-1] ) : cad= '>'
	elif( joined < ERoutput[-1]) : cad ='<'
	print( "puntos unidos ", cad, " puntos separados" );
	return ERoutput
def plotFirstAxiom( mu:float, midPoint, epsilon:float, pr:int ):
	res = checkingFirstAxiom( 1/mu, 1, midPoint, epsilon, pr );
	plt.plot( [(i+1)*epsilon/pr for i in range(pr) ] ,res );
	plt.xlabel( "variacion en distancia entre masas q" );
	plt.ylabel("Resultado ER");
	plt.show();
def checkingSecondAxiom( p:float, q:float, r:float, x:float,y:float, precision:int ) -> list[float] :
	ERoutput = [0 for _ in range(precision)];
	for act in range(precision):
		effectiveDistance = (act+1)* (y-x)/precision;
		ym = [ 0, x+effectiveDistance, y];
		pi = [p, q, r];
		ERoutput[act] = ERmeasure( ym, pi );
	return ERoutput;
def plotSecondAxiom( p, q, r, x, y, pr ):
	res = checkingSecondAxiom( p, q, r, x, y, pr );
	plt.plot( [(i+1)*(y-x)/pr for i in range(pr) ] ,res );
	plt.xlabel( "variacion en distancia de q a r" );
	plt.ylabel("Resultado ER");
	plt.show();

def checkingThirdAxiom( p:float, q:float, dist:float, precision:int )->list[float]:
	ERoutput = [0 for _ in range(precision)];
	for act in range(precision):
		delta = ( (act+1) * q/precision ) /2;
		y = [ 0, dist, dist*2];
		pi = [ p+delta, q-2*delta, p+delta ];
		ERoutput[act] = ERmeasure( y, pi );
	return ERoutput;
def plotThirdAxiom( p, q, dist, pr ):
	res = checkingThirdAxiom( p, q, dist, pr );
	minima,maxima=[],[]
	for ind in range( 1, pr-1 ):
		if ( res[ind] > res[ind-1] and res[ind] > res[ind+1] ):
			maxima.append(ind);
		elif( res[ind] < res[ind-1] and res[ind] < res[ind+1] ):
			minima.append(ind);
	#print(minima,maxima)
	
	xAxis = [ (i+1)*q/pr for  i in range(pr)];
	fig, ax = plt.subplots()
	ax.plot( xAxis, res )
	for act in minima:
		ax.plot(xAxis[act],res[act], 'x', color="green", markeredgewidth=2)
	for act in maxima:
		ax.plot( xAxis[act],res[act], 'x', color="red", markeredgewidth=2 );

	plt.xlabel("Variacion en masa q");
	plt.ylabel("Resultado ER");
	plt.show()

allPr=100000
#plotFirstAxiom( mu=1/10, midPoint=10, epsilon=1, pr=allPr )
#plotSecondAxiom( p=10, q=2, r=8, x=0, y=100, pr=allPr )
#plotThirdAxiom( p=10, q=100, dist=5, pr=allPr )

"""
El primer axioma siempre tiende a generar una recta, que cambia cuando se acerca mucho al valor deseado
Al igual el segundo.
El tercero genera minimos y maximos locales cuando alpha := 1.5978. Creo que este alpha supera la cota dada.
"""

def descubriendoLaCotaEnAlpha():
	LB,UB = 0.36,0.4
	xAxis, yAxis =[(UB-LB)/(i+1)+LB for i in range(allPr)], [(UB-LB)/(i+1)+LB for i in range(allPr)]
	f = lambda z,alph: (1+alph)*( z-pow(z,alph)/2-pow(z,1+alph) )-1/2
	f2 = lambda z : f(z,1.5978)
	yAxis = list( map(f2, yAxis ) );
	plt.plot( xAxis,yAxis );
	print(max(yAxis))
	plt.show()
#descubriendoLaCotaEnAlpha()