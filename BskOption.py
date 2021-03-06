import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

### Basket Control Variate ####

### parameters ###

coefs = np.array([[0.3,0.5,0.20],[0.29,0.15,0.25],[0.21,0.23,0.2]])
spots = [100,100,100]
weights = [1/3,1/3,1/3]
nSim = 10000

T = 0.5
r = 0.25
K=100

def means_of(x):
    return [np.mean(x[:i]) for i in range(len(x))]

def std_of(x):
    return [np.std(x[:i])/np.sqrt(i+1) for i in range(len(x))]

def N(x):
    return norm.cdf(x)

def vols(coefs): #Vols matrix for the bsk
    variances = [np.sum((coefs**2)[i]) for i in range(np.shape(coefs)[0])]
    return np.array([np.sqrt(variances[i]) for i in range(len(variances))])

def covars(coefs): #Covar matrix of end multidim. BM Sample
    
    d = np.shape(coefs)[0]
    v = vols(coefs)
    temp = np.zeros([d,d])
    
    for i in range(d):
        for j in range(d):
            temp[i,j] = np.dot(coefs[i],coefs[j])/(v[i]*v[j])
    return temp

def BMSample(coefs,T):
    
    d = np.shape(coefs)[0]
    chol = np.linalg.cholesky(covars(coefs)*T)
    norm = np.random.normal(0,1,d)
    
    return np.dot(chol,norm)

def GBMSample(spots,coefs,r,T):
    BM = BMSample(coefs,T)
    v = vols(coefs)
    return [spots[i]*np.exp((r-0.5*v[i]**2)*T + v[i]*BM[i]) for i in range(len(spots))]
    

def BskSample(spots,weights,coefs,r,T,K):
    wEnds = np.dot(GBMSample(spots,coefs,r,T),weights)
    return np.exp(-r*T)*max(wEnds - K,0)

def BskMCRegular(spots,weights,coefs,r,T,K,nSim):
    x = [BskSample(spots,weights,coefs,r,T,K) for i in range(nSim)]
    return np.mean(x)


    
def A(spots,weights): # mult constant in the lognormal version
    return np.dot(spots,weights)

def bsk_mu(spots,weights,coefs,r,T): # gaussian mean of geom. basket
    vol = vols(coefs)
    C = A(spots,weights)
    x = [weights[i]*spots[i]*(r-0.5*(vol[i]**2)) for i in range(len(weights))]
    return (T/C)*np.sum(x)

def bsk_var(spots,weights,coefs,T) : # gaussian variance of geom. basket
    
    vol = vols(coefs)
    cov = covars(coefs)
    
    C = A(spots,weights)**2
    d = len(spots)
    
    tab = np.zeros([d,d])
    for i in range(d):
        for j in range(d):
            tab[i,j] = (T/C)*weights[i]*weights[j]*spots[i]*spots[j]*cov[i,j]

    return np.sum(tab)

def BskGeomSample(spots,weights,coefs,r,T,K):
    path = GBMSample(spots,coefs,r,T)
    C = A(spots,weights)
    endsGeom = C*np.exp((1/C)* np.sum([weights[i]*spots[i]*np.log(path[i]/spots[i]) for i in range(len(spots))]))
    return np.exp(-r*T)*max(endsGeom-K,0)

def BskGeomRegular(spots,weights,coefs,r,T,K,nSim):
    x = [BskGeomSample(spots,weights,coefs,r,T,K) for i in range(nSim)]
    return np.mean(x)

        
def BskArithGeomSample(spots,weights,coefs,r,T,K): #Generates both arith/geom samples from same path
    
    path = GBMSample(spots,coefs,r,T)
    C = A(spots,weights)
    endsArith = np.dot(path,weights)
    endsGeom = C*np.exp((1/C)* np.sum([weights[i]*spots[i]*np.log(path[i]/spots[i]) for i in range(len(spots))]))
    
    callArith = np.exp(-r*T)*max(endsArith-K,0)
    callGeom = np.exp(-r*T)*max(endsGeom-K,0)
    
    return [callArith,callGeom]

def BskGeomTheoretical(spots,weights,coefs,r,T,K):
    
    v = bsk_var(spots,weights,coefs,T)
    m = bsk_mu(spots,weights,coefs,r,T)
    C = A(spots,weights)
    m_exp = C*np.exp(m+0.5*v)
    
    d_1 = (1/np.sqrt(v))*(np.log(m_exp/K) + 0.5*v)
    d_2 = (1/np.sqrt(v))*(np.log(m_exp/K) - 0.5*v)

    print("v ={} m = {} C = {} m_exp = {} d_1 = {} d_2 = {}".format(v,m,C,m_exp,d_1,d_2))

    return np.exp(-r*T)*(m_exp*N(d_1) - K*N(d_2))
    
    
def BskCVMC(spots,weights,coefs,r,T,K,nSim):
    temp = []
    th = BskGeomRegular(spots,weights,coefs,r,T,K,25000)
    for i in range(nSim):
        mc = BskArithGeomSample(spots,weights,coefs,r,T,K)
        mc = mc[0] - mc[1] + th
        temp += [mc]
    return [means_of(temp),std_of(temp)]


def BskMC(spots,weights,coefs,r,T,K,nSim):
    temp = [BskSample(spots,weights,coefs,r,T,K) for i in range(nSim)]
    return [means_of(temp), std_of(temp)]



coefs = np.array([[0.3,0.5,0.20],[0.29,0.15,0.25],[0.21,0.23,0.2]])
spots = [100,100,100]
weights = [1/3,1/3,1/3]
nSim = 10000

##T = 0.5
##r = 0.25
##K=85
##
##a = BskCVMC(spots,weights,coefs,r,T,K,nSim)
##b = BskMC(spots,weights,coefs,r,T,K,nSim)
##
##plt.plot(a[0],dashes=[1,1],label="ControlVariate BskMC")
##plt.plot(b[0],label="BskMCRegular BskMC")
##plt.legend()
##plt.show()




