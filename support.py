from scipy.integrate import quad
from scipy.optimize import root_scalar

##### OTIMIZAÇÃO DE TRANSIÇÃO DE AFILAMENTO #####

# Valores quaisquer para otimização, "O resultado terá as mesmas porcentagens"
#w_bt=2.3
#w_cr=0.5372
#w_ct=0.63
#w_baf=0.2

'''
a_e= (w_bt/2)                                                 # Semi-eixos da elipse
b_e= (w_cr/2)-(w_cr/4)
b_e2= (w_cr/2)+(w_cr/4)
'''

def elip_le(x, w_bt, w_cr):
    # w_bt e w_cr em metros, envergadura completa

    a_e= (w_bt/2)                                                 # Semi-eixos da elipse
    b_e= (w_cr/2)-(w_cr/4)
    return (w_cr*(3/4))+(b_e**2-(b_e**2/a_e**2)*x**2)**0.5

def elip_te(x, w_bt, w_cr):
    # w_bt e w_cr em metros, envergadura completa

    a_e= (w_bt/2)                                                 # Semi-eixos da elipse
    b_e2= (w_cr/2)+(w_cr/4)
    return (w_cr*(3/4))-(b_e2**2-(b_e2**2/a_e**2)*x**2)**0.5

def elip_c(x, w_bt, w_cr):
    # Corda da parte elíptica
    # w_bt e w_cr em metros, envergadura completa

    return elip_le(x, w_bt, w_cr)-elip_te(x, w_bt, w_cr)

def reta_le(x,w_cr):
    # w_cr em metros

    return w_cr+x*0

def reta_te(x):
    return 0+x*0

def reta_c(x,w_cr):
    # Corda da parte reta, w_cr em metros

    return reta_le(x,w_cr)-reta_te(x)

def trap_le(x,w_ct,w_baf,w_bt,w_cr):
    # Coordenadas do bordo de ataque da parte trapezoidal
    # Medidas em metros, envergaduras completas

    return (w_cr+(w_cr/4-((w_ct)/4))/(w_bt/2-w_baf/2)*w_baf/2)-(w_cr/4-(w_ct/4))/(w_bt/2-w_baf/2)*x

def trap_te(x,w_ct,w_baf, w_bt, w_cr):
    # Coordenadas do bordo de fuga da parte trapezoidal
    # Medidas em metros, envergaduras completas

    return -((3*(w_cr/4-(w_ct/4)))/(w_bt/2-w_baf/2))*w_baf/2+(3*(w_cr/4-(w_ct/4)))/(w_bt/2-w_baf/2)*x

def trap_c(x,w_bt, w_cr, w_ct,w_baf):
    # Corda da parte trapezoidal, medidas em metros e envergaduras completas

    return trap_le(x,w_ct,w_baf,w_bt,w_cr) - trap_te(x,w_ct,w_baf, w_bt, w_cr)

def s_elip(x, w_bt, w_cr):
    # Área da parte elíptica, medidas em metros e envergaduras completas

    s_2, s_res= quad(elip_c, 0, w_bt/2, args=(w_bt, w_cr), limit= 100)

    return 2*s_2

def s_mist(x, w_bt, w_cr, w_ct, w_baf):
    # Área da asa mista, medidas em metros e envergaduras completas

    s_ret_2,s_ret_res= quad(reta_c,0,w_baf/2, args=(w_cr), limit= 100)
    s_trap_2,s_trap_res= quad(trap_c,w_baf/2,w_bt/2, args=(w_bt, w_cr, w_ct,w_baf), limit= 100)

    return 2*(s_ret_2 + s_trap_2)

def var(x, w_ct, w_bt, w_cr, w_baf):

    if x <= w_baf/2:
        var= elip_c(x, w_bt, w_cr)-reta_c(x, w_cr)

    else:
        var= elip_c(x, w_bt, w_cr)-trap_c(x, w_bt, w_cr, w_ct, w_baf)

    return var

def err_af(x, w_ct, w_bt, w_cr, w_baf):

    erro, erro_res= quad(var, 0, w_bt/2, args=(w_ct, w_bt, w_cr, w_baf), limit= 100)

    return erro

def w_baf_tgt(w_baf, w_ct,w_bt, w_cr):

    x=0
    w_baf_tgt= err_af(x, w_ct, w_bt, w_cr, w_baf)

    return w_baf_tgt

def w_baf_opt(w_ct, w_bt, w_cr, w_baf=0):

    opt_w_baf= root_scalar(w_baf_tgt, args= (w_ct, w_bt, w_cr), method='bisect', bracket=[0.03,1.5], xtol= 0.0001)

    return opt_w_baf.root

##### CÁLCULO DA CORDA MÉDIA AERODINÂMICA #####

def mac_int1(x, w_cr):

    res1= reta_c(x, w_cr) **2

    return res1

def mac_int2(x, w_bt, w_cr, w_ct, w_baf):

    res2= trap_c(x, w_bt, w_cr, w_ct, w_baf) **2

    return res2

def s_mist(x, w_bt, w_cr, w_ct, w_baf):
    # Área da asa mista, medidas em metros e envergaduras completas

    s_ret_2,s_ret_res= quad(reta_c,0,w_baf/2, args=(w_cr), limit= 100)
    s_trap_2,s_trap_res= quad(trap_c,w_baf/2,w_bt/2, args=(w_bt, w_cr, w_ct,w_baf), limit= 100)

    return 2*(s_ret_2 + s_trap_2)

def mac(x, w_bt, w_baf, w_cr, w_ct):

    #Todos os inputs em valores absolutos
    s_ref= s_mist(x, w_bt, w_cr, w_ct, w_baf)

    int_reta,mac_int1_res= quad(mac_int1,0,w_baf/2, args= (w_cr), limit= 100)
    int_trap,mac_int2_res= quad(mac_int2,w_baf/2,w_bt/2, args=(w_bt, w_cr, w_ct, w_baf), limit= 100)

    return (2/s_ref) * (int_reta+int_trap)

##### RESTRIÇÕES DE 2024 #####

def restric(b,p,n=2):

    """Calcula o valor da restrição física dada uma envergadura "b", uma potência "p" e um número de superfícies sustentadoras "n" com função longitudinal"""

    r = p*b**(0.1529+0.1233*max(n,2))

    return r

def minimize_restric(b,p,n=2):

    min_r= restric(b,p,n)-981.8

    return min_r

def find_wb_restric(b, p ,n=2):

    b_max= root_scalar(minimize_restric, args= (p, n), method='bisect', bracket=[1.0,3.5])

    return b_max.root


##### TESTES #####

if __name__ == '__main__':

    print(w_baf_opt(0.1584, 2.59745, 0.528))
    print(mac(0, 2.52767524, 0.9691546630859376, 0.566, 0.172))