"""
Modulo dedicado a estimar as propriedades de massa e inercia de cada protótipo

Configuração atual 24/02/2024 - Fuselagem e tailboom de placas, elementos integrados à asa.
"""

# Dados de densidade das estruturas do avião

dens_w= 1.3025                  #kg/m2 - Considerando Asa + Longarina (Jacurutu usado como exemplo)
#dens_fus= 0.700                 #kg/m2 - Considerando DivinyCell com 2 camadas de carbono em cada lado e com alívios - Exemplo Jacurutu 
dens_boom= 0.237                #kg/m - Considerando um tubo de carbono de 40mm de diâmetro e 2mm de parede
dens_stab= 0.555                #kg/m2 - Valor médio entre densidade do EH e densidade do EV
dens_canard= 0.208              #kg/m2 - Valor da densidade do EH do jacurutu (sem profundor e servos)
 
# Dados de massa dos componentes principais em kg

m_batt= 0.600                     # kg - Bateria + componentes elétricos
m_motor= 0.530                   # kg- Motor + hélice
m_tdp= 0.250                     # kg - TDP + Rodas e rolamentos
m_beq= 0.230                     # kg - Garfo de aço + Rodas e Rolamentos + Mancais e rolamentos do mecanismo

#noctua:
# dens_w= 0.812                    #kg/m2 - Considerando Asa + Longarina (Noctua usado como exemplo)
dens_fus= 2.35                   #kg/m2 - Considerando DivinyCell com 2 camadas de carbono em cada lado
# dens_boom= 0.15                 #kg/m - Considerando um tubo de carbono de 40mm de diâmetro e 3mm de parede
# dens_stab= 0.63775               #kg/m2 - Valor médio entre densidade do EH e densidade do EV
 
# # Dados de massa dos componentes principais em kg

# m_batt= 0.500                     # kg - Bateria + componentes elétricos
# m_motor= 0.500                   # kg- Motor + hélice
# m_tdp= 0.740                     # kg - TDP + Rodas e rolamentos
# m_beq= 0.220                     # kg - Garfo de aço + Rodas e Rolamentos + Mancais e rolamentos do mecanismo

# Dados geométricos fixados

def total_m(w_s, eh_s, ev_s, cn_s, fus_h, fus_l, l_boom):

    m_w = dens_w * w_s
    m_fus = 2 * dens_fus * fus_h * fus_l 
    m_boom = dens_boom * l_boom
    m_eh = dens_stab * eh_s
    m_ev = dens_stab * ev_s
    m_cn = dens_canard * cn_s  # Massa do Canard

    m_total = (m_w + m_fus + m_boom + m_eh + m_ev + m_cn) + (m_batt + m_motor + m_tdp + m_beq)

    return m_total

def cg(w_s, w_z, w_cr, eh_s, eh_x, eh_z, eh_cr, ev_s, ev_x, ev_z, ev_cr, cn_s, cn_x, cn_z, cn_cr, fus_z, fus_h, fus_l, l_boom, motor_x, motor_z):

    m_w = dens_w * w_s
    m_fus = 2 * dens_fus * fus_h * fus_l 
    m_boom = dens_boom * l_boom
    m_eh = dens_stab * eh_s
    m_ev = dens_stab * ev_s
    m_cn = dens_canard * cn_s # Massa do Canard

    # --- Posições X e Z já definidas anteriormente (mantidas) ---
    fus_x = fus_l * 0.10
    boom_x = l_boom * 0.33 + fus_l * 0.35 
    batt_x = fus_l * 0.00 
    tdp_x = fus_l * 0.30 
    beq_x = -fus_l * 0.2 
    
    fus_z_cg = fus_z + 0.5 * fus_h 
    boom_z = fus_z_cg * 0.67 + eh_z * 0.33
    batt_z = fus_z_cg - 0.25 * fus_h 
    tdp_z = fus_z_cg - 0.75 * fus_h 
    beq_z = fus_z_cg - 0.5 * fus_h 

    # --- Contribuição de cada componente (X) ---
    cx_w = m_w * (w_cr / 3)
    cx_eh = m_eh * (eh_x + eh_cr / 3)
    cx_ev = m_ev * (ev_x + ev_cr / 3)
    cx_cn = m_cn * (cn_x + cn_cr / 3) # Contribuição Canard X
    cx_fus = m_fus * fus_x
    cx_boom = m_boom * boom_x
    cx_batt = m_batt * batt_x
    cx_motor = m_motor * motor_x
    cx_tdp = m_tdp * tdp_x
    cx_beq = m_beq * beq_x

    # --- Contribuição de cada componente (Z) ---
    cz_w = m_w * w_z
    cz_eh = m_eh * eh_z
    cz_ev = m_ev * ev_z
    cz_cn = m_cn * cn_z # Contribuição Canard Z
    cz_fus = m_fus * fus_z_cg
    cz_boom = m_boom * boom_z
    cz_batt = m_batt * batt_z
    cz_motor = m_motor * motor_z
    cz_tdp = m_tdp * tdp_z
    cz_beq = m_beq * beq_z

    # Massa Total (chamada com cn_s)
    mt = total_m(w_s, eh_s, ev_s, cn_s, fus_h, fus_l, l_boom)

    # Cálculo Final do CG
    x_cg = (cx_w + cx_eh + cx_ev + cx_cn + cx_fus + cx_boom + cx_batt + cx_motor + cx_tdp + cx_beq) / mt
    z_cg = (cz_w + cz_eh + cz_ev + cz_cn + cz_fus + cz_boom + cz_batt + cz_motor + cz_tdp + cz_beq) / mt

    return [x_cg, z_cg]





