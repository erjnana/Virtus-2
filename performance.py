from scipy import *
from scipy.integrate import quad
from scipy.optimize import root_scalar
from math import *
import matplotlib.pyplot as plt
import numpy as np

'''
Módulo que inclui todos os cálculos de desempenho necessários à otimização do modelo
'''
#pot = 600 #adicionado (não conseguimos identificar se a variável "pot" era exclusiva dessa parte do código ou se tem outra origem)
c_pista= 55
h_decol= 0.7

def alt(p, t):
    
    alti= (288.15/0.0065)*(1-((p/1013.25)/((t+273.15)/288.15))**0.234959)
    return alti
    
def rho(p, t):
    #alti=1500
    alti= alt(p,t)
    rho= 1.2250177777777773-0.00011760273526795266*alti+4.359717577108174e-9*(alti)**2-9.65009064952006e-14*alti**3
    return rho

def tracd(p, t, v, pot):

    #tracd= ((28.709955+0.07366009766*v-0.03187744135*v**2-0.0013809470336*v**3+7.82035332027e-5*v**4-1.160949504525e-6*v**5)*(rho(p,t)/rho(p=1013.25, t=15)))*(pot/712.15)

    trac600= (45.384+0.6374625901805*v-0.39434159385213*v**2+0.028296433071339*v**3-0.00068805475237905*v**4)*(rho(p,t)/rho(p=1013.25, t=15))
    
    trac650= (40.691396530109+0.6374625901805*v-0.39434159385213*v**2+0.028296433071339*v**3-0.00068805475237905*v**4)*(rho(p,t)/rho(p=1013.25, t=15))

    #trac700= (42.305389981987+0.026804040121956*v-0.20140472951687*v**2+0.013246483129662*v**3-0.00034284828105358*v**4)*(rho(p,t)/rho(p=1013.25, t=15))

    #trac750= (46.024270393988-0.42344371921103*v-0.21442574712369*v**2+0.016855206083626*v**3-0.00043684083730426*v**4)*(rho(p,t)/rho(p=1013.25, t=15))

    #if pot >= 650 and pot <=700:
        #tracd= (trac650*(700-pot) + trac700*(pot-650))/50

    #if pot >= 700 and pot <=750:
        #tracd= (trac700*(750-pot) + trac750*(pot-700))/50
    
    if pot >= 600 and pot <= 650:
        tracd= (trac600*(650-pot) + trac650*(pot-600))/50
    
    return tracd

def tracr(cld ,cdd , m):        
    #Calcula tração requerida

    tracr= m*9.81*(cdd/cld)
    return tracr

def q(p, t, v):
    #Calcula pressão dinâmica
    dens= rho(p,t)
    q= (dens*v**2)/2
    return q

def lift(p, t, v, s, cl):
    #Calcula sustentação
    qp= q(p, t, v)
    lift= qp*s*cl
    return lift

def drag(p, t, v, s, cd):
    #Calcula arrasto
    qp= q(p, t, v)
    drag= qp*s*cd
    return drag

def v_estol(p, t, m, s, clmax, g=9.81):
    #Calcula velocidade de estol
    dens= rho(p,t)
    v_estol= sqrt(abs((2*m*g)/(dens*s*clmax)))
    return v_estol 

def fric(p, t, m, s, clc, clmax, v, g= 9.81, mu= 0.03):
    #Calcula força de atrito no solo
    if v <= 1.2*v_estol(p, t, m, s, clmax, g=9.81):
        lift_c= lift(p, t, v, s, clc)
        fric= mu*(m*g-lift_c)
    
    else:
        fric= 0
    
    return fric

def acel_dec(p, t, v, m, s, clc, clmax, cdc, pot, g= 9.81, mu= 0.03):
    #Calcula aceleração na decolagem
    tracdisp= tracd(p,t,v,pot)
    atrito= fric(p, t, m, s, clc, clmax, v, g= 9.81, mu= 0.03)
    dragc= drag(p, t, v, s, cdc)

    acel_dec= (tracdisp-dragc-atrito)/m

    return acel_dec

def f_d_sol(v, p, t, m, s, clc, clmax, cdc, pot, g= 9.81, mu= 0.03):
    #Calcula a função para integração da distância de solo
    f= v/acel_dec(p, t, v, m, s, clc, clmax, cdc, pot, g, mu)
    return f

def d_sol(p, t, v, m, s, clc, clmax, cdc, pot, g= 9.81, mu= 0.03):
    #Calcula distância de solo
    v_est= v_estol(p, t, m, s, clmax, g)
    v_decol= 1.2*v_est

    d_sol, d_sol_res= quad(f_d_sol, 0, v_decol, args=(p, t, m, s, clc, clmax, cdc, pot, g, mu), limit= 100)

    return d_sol

def d_rot(p, t, m, s, clmax, g= 9.81):
    #Calcula distância de rotação
    v_est= v_estol(p, t, m, s, clmax, g)
    d_rot= 1.2*v_est/3

    return d_rot

def r_trans(p, t, m, s, clmax, g= 9.81, n= 1.2):
    #Calcula raio de transição
    v_est= v_estol(p, t, m, s, clmax, g)
    r_trans= (1.15*v_est)**2/(g*(n-1))

    return r_trans

def g_cl(p, t, m, s, clmax, cdt, pot, g=9.81):
    #Calcula ângulo onde a transição termina 
    v_est= v_estol(p, t, m, s, clmax, g)
    tracdisp= tracd(p, t, v_est,pot)
    drag_t= drag(p, t, v_est, s, cdt)

    g_cl= (tracdisp-drag_t)/(m*g) #em rad

    return g_cl

def h_trans(p, t, m, s, clmax, cdt, pot, g= 9.81, n= 1.2):
    #Calcula altura de transição
    r_t= r_trans(p, t, m, s, clmax, g, n)
    g_cl_rad= g_cl(p, t, m, s, clmax, cdt, pot, g)

    ht= r_t*(1-cos(g_cl_rad))

    return ht

def f_g_tr(gamma, p, t, m, s, clmax, g= 9.81, n= 1.2):
    #Cálculo da função para encontrar o ângulo de transição
    r_t= r_trans(p, t, m, s, clmax, g, n)

    f= h_decol- (r_t*(1-cos(gamma)))

    return f

def g_tr(gamma, p, t, m, s, clmax, g= 9.81, n= 1.2):
    #Calcula ângulo de transição
    g_tr= root_scalar(f_g_tr, args= (p, t, m, s, clmax, g, n), method='bisect', bracket=[0,pi/4])
    
    if g_tr.flag == 'converged':
        result = g_tr.root #em radianos
    else:
        print('g_tr não convergiu, continuando assim mesmo')
        result = g_tr.root

    return result
    
def d_trans(p, t, m, s, clmax, cdt, pot, g= 9.81, n= 1.2, gamma=0):
    #Calcula distância de transição
    h_t= h_trans(p, t, m, s, clmax, cdt, pot, g, n)
    r_t= r_trans(p, t, m, s, clmax, g, n)

    if h_t < h_decol:
        gamma_cl= g_cl(p, t, m, s, clmax, cdt, pot, g)

        d_t= r_t*sin(gamma_cl)
    
    else:
        gamma_tr= g_tr(gamma, p, t, m, s, clmax, g, n)

        d_t= r_t*sin(gamma_tr)

    return d_t

def d_sub(p, t, m, s, clmax, cdt, pot, g= 9.81, n= 1.2 ):
    #Calcula distância de subida
    h_t= h_trans(p, t, m, s, clmax, cdt, pot, g, n)
    gamma_cl= g_cl(p, t, m, s, clmax, cdt, pot, g)

    if h_t < h_decol:

        d_sub= (h_decol-h_t)/tan(gamma_cl)

    else:
        d_sub= 0

    return d_sub

def d_decol(p, t, v, m, s, clc, clmax, cdc, cdt, pot, g= 9.81, mu= 0.03, n= 1.2, gamma= 0):
    #Calcula distância total de decolagem
    dist_solo= d_sol(p, t, v, m, s, clc, clmax, cdc, pot, g, mu)

    dist_rot= d_rot(p, t, m, s, clmax, g)

    dist_trans= d_trans(p, t, m, s, clmax, cdt, pot, g, n, gamma)

    dist_sub= d_sub(p, t, m, s, clmax, cdt, pot, g, n)

    dist_decol= dist_solo + dist_rot + dist_trans + dist_sub

    return dist_decol

def f_mtow(m, p, t, v, s, clc, clmax, cdc, cdt, pot, g= 9.81, mu= 0.03, n= 1.2, gamma= 0):
    #Cálculo da função para encontrar o MTOW
    f= c_pista - d_decol(p, t, v, m, s, clc, clmax, cdc, cdt, pot, g, mu, n, gamma)

    return f

def mtow(p, t, v, m, s, clc, clmax, cdc, cdt, pot, g= 9.81, mu= 0.03, n= 1.2, gamma= 0):
    #Calcula MTOW
    #Usa método de bisecção para encontrar raiz da função f_mtow
    f_low = f_mtow(5, p, t, v, s, clc, clmax, cdc, cdt, pot, g, mu, n, gamma)
    f_high = f_mtow(20, p, t, v, s, clc, clmax, cdc, cdt, pot, g, mu, n, gamma)

    #if f_low * f_high < 0:
    mtow = root_scalar(f_mtow, args= (p, t, v, s, clc, clmax, cdc, cdt, pot, g, mu, n, gamma), method='bisect', bracket=[5,30])
    result = mtow.root
    # elif f_low > 0 and f_high > 0:
    #     # Can take off with more mass, return max
    #     result = 20
    # elif f_low < 0 and f_high < 0:
    #     # Can't take off even with min mass, return 0
    #     result = 0
    # else:
    #     # Edge case, return midpoint or something
    #     result = 12.5

    return result


#def mtow():






if __name__ == '__main__':
    print(alt(905,25))
    print(rho(1013,26))
    print(tracd(1013,26,8,601))
    #print(v_estol(10,1013,26,0.8,2.04,9.81))
    #print(d_sol(1013,26,10,10,0.8,1.2,2.04,0.2))
    #print(g_tr(0,1013,26,10,0.8,2.04,9.81,1.2))
    #print(d_trans(1013, 26, 10, 0.8, 2.04, 0.2))
    #print(d_sub(1013, 26, 10, 0.8, 2.04, 0.2))
    #print(d_decol(1013, 26, 10, 10.6, 0.8, 1.2, 2.04, 0.2, 0.3))
    print(mtow(1013, 26, 10, 20, 0.8, 1.2, 2.04, 0.2, 0.3, 601))

