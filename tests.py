from prototype import *
from simulator import *
from performance import *
import matplotlib.pyplot as plt
import time

"""
Este arquivo contém alguns testes que foram úteis para debugging durante o desenvolvimento do código.
"""
# Aviao 1: Primeiro após trocas para perfis de 2024
aviao1= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_c= 0.2794223867605712, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502,pot= 680.0, ge= False)
aviao1_ge= Prototype ( w_cr= 0.57, w_ct= 0.40975013961162043, w_z= 0.18220990045077817, w_inc= 0.1923063435461832, eh_b= 0.8735965804721229, eh_c= 0.2794223867605712, eh_inc= 2.9476393667342435, ev_b= 0.22514748539953888, eh_x= 1.002904353165168, eh_z= 0.3437012200770051, motor_x= -0.2247097169299502,pot= 680.0, ge= True)
aviao2= Prototype ( w_cr= 0.5699220096512, w_ct= 0.33, w_z= 0.18, w_inc= -0.6927216185942724, eh_b= 1.1455366975233654, eh_c= 0.2832457949890901, eh_inc= 0.11748405385738692, ev_b= 0.2330642307232967, eh_x= 1.038698074462542, eh_z= 0.25, motor_x= -0.19707875106896672,pot= 680.0, ge= False)
aviao2_ge= Prototype ( w_cr= 0.5699220096512, w_ct= 0.33, w_z= 0.18, w_inc= -0.6927216185942724, eh_b= 1.1455366975233654, eh_c= 0.2832457949890901, eh_inc= 0.11748405385738692, ev_b= 0.2330642307232967, eh_x= 1.038698074462542, eh_z= 0.25, motor_x= -0.19707875106896672,pot= 680.0, ge= True)

print('Peso vazio:', aviao1.pv, 
      'X_cg:',aviao1.x_cg, 
      'Z_cg:',aviao1.z_cg)

print('Comprimento do boom:', aviao1.boom_l)


simulation1= Simulator(aviao1,aviao1_ge)

simulation1.scorer()

#simulation1.run_a()
#simulation1.run_a_fus(19)
#simulation1.run_stall()
#simulation1.run_ge()
#print('CL=',simulation1.cl)
#print('CD=',simulation1.cd)
#print('CLmax=', simulation1.clmax)
#print('CL_GE=',simulation1.cl_ge)
#print('CD_GE=',simulation1.cd_ge)

alpha_cases=[]

for a in range(0,25):
    a_case= Case(name='a'+str(a), alpha=a, X_cg= aviao1.x_cg, Z_cg= aviao1.z_cg)
    alpha_cases.append(a_case)


a0 = Case(name='a0', alpha=30, X_cg= aviao1.x_cg, Z_cg= aviao1.z_cg)
a_trim = Case(name='a10', alpha=0, X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg,  elevator=Parameter(name='elevator', constraint='Cm', value=0))
beta= Case(name='dutch_roll', beta=5, bank=5, X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg)
#trimmed = Case(name='Trimmed', alpha=10, elevator=Parameter(name='elevator', constraint='Cm', value=0.0))
aviao1.show_geometry()

trimmed= Case(name='trimmed', X_cg=aviao1.x_cg, Z_cg=aviao1.z_cg, alpha=Parameter(name='a', constraint='Cm',value=0.0))

session=Session(geometry=aviao1.geometry,cases=[a0])

session._run_analysis


results= session.get_results()

with open('./logs/out8.json', 'w') as f:
        f.write(json.dumps(results))
#time.sleep(1000)

#mass= mtow(simulation1.p, simulation1.t, simulation1.v, simulation1.prototype.m, simulation1.prototype.s, simulation1.cl_ge[0], simulation1.clmax, simulation1.cd_ge[0], simulation1.cd[0], g= 9.81, mu= 0.03, n= 1.2, gamma= 0)
#print(mass)


'''
fig, ax = plt.subplots(figsize=(10,6))
x = np.linspace(0,20, 200)
y= np.zeros(200)
for e in range(len(x)):
    i= x[e]
    y[e]= f_d_sol(i, simulation1.p, simulation1.t, simulation1.prototype.m, simulation1.prototype.s, simulation1.cl_ge[0], simulation1.clmax, simulation1.cd_ge[0])
ax.plot(x, y, 'r-', linewidth=2, alpha=0.6) 
plt.grid()
ax.set_xlabel('v') 
ax.set_ylabel('distsol')
#ax.set_xticks(np.arange(0, 21, 5))
#ax.set_yticks(np.arange(0, 2.5, 0.2))
plt.axhline(color='k', lw=0.8)
plt.axvline(color='k', lw=0.8)
ax.set_title('dist_sol x v')
plt.show()
'''