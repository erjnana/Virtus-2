'''
Módulo que inclui todos os cálculos e verificações de estabilidade estática da aeronave para adequação do modelo aos critérios estabelecidos
'''
# Restrições:
# Est. Longitudinal
vht_min= 0.3; vht_max= 0.6 #alterado
cm0_min= 0
cma_max= 0
a_trim_min= 2; a_trim_max= 6 #mantido
me_min= 0.05; me_max= 0.15       # Essa margem estática é normalizada com relação à corda da raíz (alterado)
#Est. Ddirecional
vvt_min= 0.02; vvt_max=0.05 #alterado
cnb_min= 0

def check_interval(value,min,max):

    if value >= min and value <= max:
        return True
    
    else:
        return False

def check_min(value,min):

    if value > min:
        return True
    
    else:
        return False
    
def check_max(value,max):

    if value < max:
        return True
    
    else:
        return False

def me(x_np, x_cg, mac):   # x_cg aqui não é porcentagem, mas sim a posição do cg

    me= (x_np - x_cg)/mac

    return me

def long_stab_check(vht, cm0, cma, a_trim, x_np, x_cg, w_cr):

    m_est= me(x_np, x_cg, w_cr)

    check_vht= check_interval(vht, vht_min, vht_max)
    check_cm0= check_min(cm0, cm0_min)
    check_cma= check_max(cma, cma_max)
    check_a_trim= check_interval(a_trim, a_trim_min, a_trim_max)
    check_me= check_interval(m_est, me_min, me_max)

    return check_vht and check_cm0 and check_cma and check_a_trim and check_me

def dir_stab_check(vvt, cnb):

    check_vvt= check_min(vvt,vvt_min)
    check_cnb= check_min(cnb,cnb_min)

    return check_vvt and check_cnb

def stab_check(vht, cm0, cma, a_trim, x_np, x_cg, w_cr, vvt, cnb):

    return long_stab_check(vht, cm0, cma, a_trim, x_np, x_cg, w_cr) and dir_stab_check(vvt, cnb)
