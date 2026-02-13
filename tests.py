from prototype import *
from simulator import *
from performance import *
from airfoil_loader import *
import matplotlib.pyplot as plt
import time

"""
Este arquivo contém alguns testes que foram úteis para debugging durante o desenvolvimento do código.
"""
# Aviao 1: Primeiro após trocas para perfis de 2024
# aviao1= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_c= 0.2794223867605712, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502,pot= 680.0, ge= False)
# aviao1_ge= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_c= 0.2794223867605712, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502,pot= 680.0, ge= True)
# aviao2= Prototype ( w_cr= 0.5699220096512, w_ct= 0.33, w_z= 0.18, w_inc= -0.6927216185942724, eh_b= 1.1455366975233654, eh_c= 0.2832457949890901, eh_inc= 0.11748405385738692, ev_b= 0.2330642307232967, eh_x= 1.038698074462542, eh_z= 0.25, motor_x= -0.19707875106896672,pot= 680.0, ge= False)
# aviao2_ge= Prototype ( w_cr= 0.5699220096512, w_ct= 0.33, w_z= 0.18, w_inc= -0.6927216185942724, eh_b= 1.1455366975233654, eh_c= 0.2832457949890901, eh_inc= 0.11748405385738692, ev_b= 0.2330642307232967, eh_x= 1.038698074462542, eh_z= 0.25, motor_x= -0.19707875106896672,pot= 680.0, ge= True)

# print('Peso vazio:', aviao1.pv, 
#       'X_cg:',aviao1.x_cg, 
#       'Z_cg:',aviao1.z_cg)

# print('Comprimento do boom:', aviao1.boom_l)


# simulation1= Simulator(aviao1,aviao1_ge)

# simulation1.scorer()

#simulation1.run_a()
#simulation1.run_a_fus(19)
#simulation1.run_stall()
#simulation1.run_ge()
#print('CL=',simulation1.cl)
#print('CD=',simulation1.cd)
#print('CLmax=', simulation1.clmax)
#print('CL_GE=',simulation1.cl_ge)
#print('CD_GE=',simulation1.cd_ge)

# alpha_cases=[]

# for a in range(0,25):
#     a_case= Case(name='a'+str(a), alpha=a, X_cg= aviao1.x_cg, Z_cg= aviao1.z_cg)
#     alpha_cases.append(a_case)


# a0 = Case(name='a0', alpha=30, X_cg= aviao1.x_cg, Z_cg= aviao1.z_cg)
# a_trim = Case(name='a10', alpha=0, X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg,  elevator=Parameter(name='elevator', constraint='Cm', value=0))
# beta= Case(name='dutch_roll', beta=5, bank=5, X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg)
# #trimmed = Case(name='Trimmed', alpha=10, elevator=Parameter(name='elevator', constraint='Cm', value=0.0))
# aviao1.show_geometry()

# trimmed= Case(name='trimmed', X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg, alpha=Parameter(name='a', constraint='Cm',value=0.0))

# session=Session(geometry=aviao1.geometry,cases=[a0])

# session._run_analysis


# results= session.get_results()

# with open('./logs/out8.json', 'w') as f:
#         f.write(json.dumps(results))
# #time.sleep(1000)

# #mass= mtow(simulation1.p, simulation1.t, simulation1.v, simulation1.prototype.m, simulation1.prototype.s, simulation1.cl_ge[0], simulation1.clmax, simulation1.cd_ge[0], simulation1.cd[0], g= 9.81, mu= 0.03, n= 1.2, gamma= 0)
# #print(mass)


# '''
# fig, ax = plt.subplots(figsize=(10,6))
# x = np.linspace(0,20, 200)
# y= np.zeros(200)
# for e in range(len(x)):
#     i= x[e]
#     y[e]= f_d_sol(i, simulation1.p, simulation1.t, simulation1.prototype.m, simulation1.prototype.s, simulation1.cl_ge[0], simulation1.clmax, simulation1.cd_ge[0])
# ax.plot(x, y, 'r-', linewidth=2, alpha=0.6) 
# plt.grid()
# ax.set_xlabel('v') 
# ax.set_ylabel('distsol')
# #ax.set_xticks(np.arange(0, 21, 5))
# #ax.set_yticks(np.arange(0, 2.5, 0.2))
# plt.axhline(color='k', lw=0.8)
# plt.axvline(color='k', lw=0.8)
# ax.set_title('dist_sol x v')
# plt.show()
# '''

# aviao1= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_bt= 3.5, w_baf=0.8, w_ci=0.8, w_wo=0.0,w_d=1, eh_cr=0.27, eh_ct=0.9, ev_ct=0.9, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502, ge= False)
# aviao1_ge= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_bt= 3.5, w_baf=0.8, w_ci=0.8, w_wo=0.0,w_d=1, eh_cr=0.27, eh_ct=0.9, ev_ct=0.9, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502, ge= True)
# aviao1.print_geometry_info()
# simulation1= Simulator(aviao1,aviao1_ge)
# simulation1.run_a()
# simulation1.scorer()
# simulation1.print_coeffs()

# Selecionar um perfil de cada categoria para usar nos testes
# if airfoils_database_asa:
#     af_root = list(airfoils_database_asa.values())[0]
#     af_tip = list(airfoils_database_asa.values())[0]
# else:
#     raise ValueError("Nenhum perfil de asa foi carregado")

# if airfoils_database_eh:
#     af_eh = list(airfoils_database_eh.values())[0]
# else:
#     raise ValueError("Nenhum perfil de EH foi carregado")

# if airfoils_database_ev:
#     af_ev = list(airfoils_database_ev.values())[0]
# else:
#     raise ValueError("Nenhum perfil de EV foi carregado")

root_af = 'MIN1112'
tip_af = 'eppler421'       
eh_af = 'NACA0012'
ev_af = 'NACA0012'
cn_af = 'NACA0012'

dados_root = {'name': 'MIN1112', 'cl_max': 2.39, 'alpha_cl_max': 12.0, 'dat_path': 'airfoils\\assymmetric\\MIN1112\\geometry.dat'}
dados_tip = {'name': 'eppler421', 'cl_max': 1.8, 'alpha_cl_max': 11.0, 'dat_path': 'airfoils\\assymmetric\\eppler421\\geometry.dat'}
dados_eh = {'name': 'NACA0012', 'cl_max': 1.2, 'alpha_cl_max': 15.0, 'dat_path': 'airfoils\\symmetric\\NACA0012\\geometry.dat'}
dados_ev = {'name': 'NACA0012', 'cl_max': 1.2, 'alpha_cl_max': 15.0, 'dat_path': 'airfoils\\symmetric\\NACA0012\\geometry.dat'}
dados_canard = {'name': 'NACA0012', 'cl_max': 1.2, 'alpha_cl_max': 15.0, 'dat_path': 'airfoils\\symmetric\\NACA0012\\geometry.dat'}

aviao2= Prototype( af_root_data=dados_root,
        af_tip_data=dados_tip,
        af_eh_data=dados_eh,
        af_ev_data=dados_ev,
        af_canard_data=dados_canard,cn_b = 1.2, cn_cr = 0.15, cn_ct = 0.9, cn_inc = 0.0, cn_x = -0.5, cn_d = 4.0, cn_z = 0.0, w_bt= 2.274771763125795, w_baf= 0.9, w_cr= 0.46835090245141264, w_ci= 0.776990228187889, w_ct= 0.6638203815384615, w_z= 0.15, w_inc= 2.9744171469230767, w_wo= 1.0977240731062243, w_d= 0.0, eh_b= 0.75, eh_cr= 0.33214639133338325, eh_ct= 0.7, eh_inc= -3.0, ev_b= 0.4, ev_ct= 0.9201353525600001, eh_x= 1.0, eh_z= 0.50, motor_x= -0.15129635916666673,)

# ('cn_b': array([1.14615385]),
#  'cn_cr': array([0.19358974]),
#  'cn_ct': array([0.79358974]),
#  'cn_d': array([9.53846154]),
#  'cn_inc': array([3.92307692]),
#  'cn_x': array([-0.38846154]),
#  'cn_z': array([0.06346154]),
#  'eh_b': array([0.99358974]),
#  'eh_cr': array([0.19166667]),
#  'eh_ct': array([0.85769231]),
#  'eh_inc': array([-0.15384615]),
#  'eh_x': array([0.75641026]),
#  'eh_z': array([0.5924359]),
#  'ev_b': array([0.31794872]),
#  'ev_ct': array([0.86346154]),
#  'motor_x': array([-0.41153846]),
#  'w_baf': array([0.81025641]),
#  'w_bt': array([1.75]),
#  'w_ci': array([0.83461538]),
#  'w_cr': array([0.38269231]),
#  'w_ct': array([0.75]),
#  'w_d': array([2.11538462]),
#  'w_inc': array([-0.61538462]),
# w_wo=-4.91025641,
# w_z = 0.29038462)


aviao2.show_geometry() # Teste para verificar se a geometria está sendo criada corretamente
aviao2.print_geometry_info()
simulation2= Simulator(aviao2)
simulation2.run_a()
simulation2.scorer()
simulation2.print_coeffs()

# a0 = Case(name='a0', alpha=30, X_cg= aviao2.x_cg, Z_cg= aviao2.z_cg)

# session=Session(geometry=aviao2.geometry,cases=[a0])

# session._run_analysis

# results= session.get_results()

# with open('./out.json', 'w') as f:
#         f.write(json.dumps(results))
