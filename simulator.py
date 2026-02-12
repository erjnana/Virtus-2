import json
from avlwrapper import *
from prototype import *
from performance import *
from stability import *
import numpy as np
import pandas as pd
import time
from competition_score import compute_competition_score


class Simulator():
    """
    Classe responsável por criar os casos e realizar simulações no AVL.
    Cada indivíduo corresponde a uma aeronave completa, incluindo:
    - Simulação com e sem efeito solo
    - Coleta de coeficientes aerodinâmicos (CL, CD, CM)
    - Estimativa de ângulo de estol, trimagem e margem estática
    - Cálculo de MTOW, carga paga e pontuação de voo da competição
    """

    def __init__(self, prototype, p=905.5, t=25, v=10, mach=0.0):
        self.prototype = prototype
        self.p = p
        self.t = t
        self.v = v
        self.mach = mach
        self.rho = rho(p=p, t=t)
        self.deflex = {}
        self.cl = {}
        self.cd = {}
        self.cm = {}
        self.cma = {}
        self.cnb = {}
        self.cl_ge = {}
        self.cd_ge = {}
        self.a_trim = -20
        self.me = -0.2
        self.score = 0
        self.cp = 0
        self.stall_constraint = None
        self.competition_score = 0

    ###########################################################################
    # MÉTODOS DE CHECAGEM DE ESTOL
    ###########################################################################
    def check_stall(self, results):
        limits = {
            'Wing': self.prototype.w_root_clmax,
            'Eh': self.prototype.af_eh_data['cl_max'] if hasattr(self.prototype, 'af_eh_data') else 1.2,
            'Canard': self.prototype.af_canard_data['cl_max'] if hasattr(self.prototype, 'af_canard_data') else 1.2
        }

        for surf_name, cl_limit in limits.items():
            if surf_name in results['a']['StripForces']:
                cls = results['a']['StripForces'][surf_name]['cl']
                max_cl_3d = max(cls)
                if max_cl_3d >= cl_limit:
                    # Encontra a posição y do estol para o print do run_a
                    idx = np.argmax(cls)
                    y_stall = results['a']['StripForces'][surf_name]['Yle'][idx]
                    return True, y_stall 

        return False, 0.0

    ###########################################################################
    # MÉTODOS DE SIMULAÇÃO
    ###########################################################################
    def run_a(self, a=0):
        a_case = Case(
            name='a',
            alpha=a,
            density=self.rho,
            Mach=self.mach,
            velocity=self.v,
            X_cg=self.prototype.x_cg,
            Z_cg=self.prototype.z_cg,
            elevator=Parameter(name='elevator', constraint='Cm', value=0.0)
        )
        session = Session(geometry=self.prototype.geometry, cases=[a_case])
        a_results = session.get_results()
        self.last_results = a_results

        try:
            stall, b_stall = self.check_stall(a_results) # <--- Recebe o b_stall
            if not stall:
                self.deflex[a] = a_results['a']['Totals']['elevator']
                self.cl[a] = a_results['a']['Totals']['CLtot']
                print(f"    ✈️ CL Voo Livre (alpha={a}): {self.cl[a]:.4f}")
                self.cd[a] = a_results['a']['Totals']['CDtot']
                self.cm[a] = a_results['a']['Totals']['Cmtot']
                self.cma[a] = a_results['a']['StabilityDerivatives']['Cma']
                self.cnb[a] = a_results['a']['StabilityDerivatives']['Cnb']
            else:
                raise RuntimeError(f"\nEstol detectado em alfa={a}")
            return a_results
        except Exception as e:
            stall, b_stall = self.check_stall(a_results)
            print(f'    ⚠️Estol em {b_stall*100:.1f}% da envergadura')
            raise e

    def run_ge(self):
        print('⌛Calculando coeficientes em efeito solo')
        ge_geometry = self.prototype.get_geometry(ground_effect=True)
        a_case = Case(
            name='a',
            alpha=0,
            density=self.rho,
            Mach=self.mach,
            velocity=self.v,
            X_cg=self.prototype.x_cg,
            Z_cg=self.prototype.z_cg
        )
        session = Session(geometry=ge_geometry, cases=[a_case])
        a_results = session.get_results()
        
        self.cl_ge[0] = a_results['a']['Totals']['CLtot']
        print(f"    🛫 CL Efeito Solo: {self.cl_ge[0]:.4f}")
        self.cd_ge[0] = a_results['a']['Totals']['CDtot']
        return a_results

    def run_stall(self):
        for a in np.arange(5, 12, 2):
            try:
                self.run_a(a)
            except:
                self.a_stall = a - 1
                self.clmax = self.cl[a - 1]
                print(f'    ⚠️ Ângulo de estol entre {a-1} e {a} graus')
                break
        for a in np.arange(12, 31, 1):
            try:
                self.run_a(a)
            except:
                self.a_stall = a - 1
                self.clmax = self.cl[a - 1]
                print(f'    ⚠️ Ângulo de estol entre {a-1} e {a} graus')
                break
        self.prototype.ALPHA_STALL_MIN_DEGREE = self.a_stall
        self.stall_constraint = self.prototype.ALPHA_STALL_MIN_DEGREE

    def run_trim(self):
        trimmed = Case(
            name='trimmed',
            alpha=Parameter(name='alpha', constraint='Cm', value=0.0),
            X_cg=self.prototype.x_cg,
            Z_cg=self.prototype.z_cg
        )
        session = Session(geometry=self.prototype.geometry, cases=[trimmed])
        trim_results = session.get_results()
        
        # --- ADICIONE ESTA LINHA ---
        self.last_results = trim_results 
        # ---------------------------

        self.a_trim = trim_results['trimmed']['Totals']['Alpha']
        self.xnp = trim_results['trimmed']['StabilityDerivatives']['Xnp']
        self.me = me(self.xnp, self.prototype.x_cg, self.prototype.mac)

    def get_max_cl_surface(self, surface_name):
        """
        Extrai o Cl máximo de uma superfície específica.
        """
        if not hasattr(self, 'last_results'):
            return 0.0
            
        # Tenta encontrar os dados de força no caso 'trimmed' ou no caso 'a'
        case_name = 'trimmed' if 'trimmed' in self.last_results else 'a'
        
        try:
            forces = self.last_results[case_name]['StripForces']
            if surface_name in forces:
                cls = forces[surface_name]['cl']
                return max(cls) if len(cls) > 0 else 0.0
        except KeyError:
            pass
            
        return 0.0
    
    def print_coeffs(self):
        aero_coeffs = pd.DataFrame(
            [self.cl, self.cd, self.cm, self.deflex],
            index=['CL', 'CD', 'CM', 'Prof']
        ).T

        print('--------------OUTPUTS-----------------\n')
        print('--------------Aerodinâmica-----------------')
        print('CL em corrida=', self.cl_ge.get(0, 'N/A'))
        print('CD em corrida=', self.cd_ge.get(0, 'N/A'))

        print('Transição=', round(self.prototype.w_baf / self.prototype.w_bt, 3) * 100, '% da envergadura')
        print('Altura do EH com relação à asa=', round(self.prototype.eh_z_const, 3), 'm')
        print('Área alar=', round(self.prototype.s_ref, 3), 'm^2')
        print('AR=', round(self.prototype.ar, 2))
        print('AR do EH=', round(self.prototype.eh_ar, 2))
        print('M.A.C.=', round(self.prototype.mac, 3), 'm')

        print('\n--------------Controle e Estabilidade-----------------')
        print('VHT=', round(self.prototype.vht, 4))
        print('VVT=', round(self.prototype.vvt, 4))
        print('X_CG=', round(self.prototype.x_cg_p, 3), '% da corda da asa')
        print('Z_CG=', round(self.prototype.z_cg, 3), 'm do chão')
        print('CG=', round(self.prototype.low_cg, 3), 'm abaixo da asa')
        print('Ângulo de trimagem=', round(self.a_trim, 2), 'graus')
        print('Margem Estática=', round(self.me, 3))

    ###########################################################################
    # MÉTODO PRINCIPAL DE PONTUAÇÃO
    ###########################################################################
    def scorer(self):
        try:
            self.run_a(0)
            print('✅CASO ALFA 0 CONCLUIDO')
        except:
            print('❌FALHA NA SIMULAÇÃO DE ALFA 0')
            self.score = 0

        try:
            self.run_ge()
            print('✅CASO EFEITO SOLO CONCLUIDO')
        except:
            print('❌FALHA NA SIMULAÇÃO EM EFEITO SOLO')
            self.score = 0

        try:
            self.run_stall()
            print('✅CASO ESTOL CONCLUIDO')
        except:
            print('❌FALHA NA SIMULAÇÃO ATÉ O ESTOL')
            self.score = 0

        try:
            self.run_trim()
            print('✅CASO TRIMADO CONCLUIDO')
        except:
            print('❌FALHA NA SIMULAÇÃO DE TRIMAGEM')
            self.score = 0
            self.a_trim = 0

        # MTOW e carga paga
        try:
            self.mtow = mtow(
                self.p, self.t, self.v, self.prototype.pv, self.prototype.s_ref,
                self.cl_ge[0], self.clmax, self.cd_ge[0], self.cd[0],
                self.prototype.pot, g=9.81, mu=0.03, n=1.2, gamma=0
            )
            self.prototype.m = self.mtow
            self.cp = self.mtow - self.prototype.pv
            self.score = self.cp
        except Exception as e:
            print('FALHA NA SIMULAÇÃO DE MTOW')
            print(f"    ⚠️Erro: {e}")
            self.score = 0
            self.cp = 0

        # PONTUAÇÃO DA COMPETIÇÃO
        try:
            comp_score_dict = compute_competition_score(self.prototype.pv, self.cp, self.prototype.w_bt)
            self.competition_score = comp_score_dict["PVOO"]
            print(f"\n🏆 Pontuação de voo final (PVOO): {self.competition_score:.3f}\n")
        except Exception as e:
            print("\n⚠️ Erro ao calcular a pontuação da competição:\n", e)
            self.competition_score = 0

        # Penalidades
        a_trim_pen = 0
        x_cg_p_pen = 0
        if self.a_trim > a_trim_max:
            a_trim_pen = 2 + 10 * (self.a_trim - a_trim_max)
        if self.a_trim < a_trim_min:
            a_trim_pen = 2 + 10 * (a_trim_min - self.a_trim)
        if self.prototype.x_cg_p > 0.35:
            x_cg_p_pen = 2 + 10 * (self.prototype.x_cg_p - 0.35)
        if self.prototype.x_cg_p < 0.25:
            x_cg_p_pen = 2 + 10 * (0.25 - self.prototype.x_cg_p)

        pen = a_trim_pen + x_cg_p_pen
        self.score -= pen

        self.print_coeffs()

        return self.score, self.competition_score

    ###########################################################################
    # MÉTODO PARA PRINTAR COEFICIENTES E INFO
    ###########################################################################
    # def print_coeffs(self):
    #     aero_coeffs = pd.DataFrame(
    #         [self.cl, self.cd, self.cm, self.deflex],
    #         index=['CL', 'CD', 'CM', 'Prof']
    #     ).T

    #     print('--------------OUTPUTS-----------------\n')
    #     print('--------------Aerodinâmica-----------------')
    #     print('Coeficientes aerodinâmicos:\n', aero_coeffs, sep='')
    #     print('CL em corrida=', self.cl_ge.get(0, 'N/A'))
    #     print('CD em corrida=', self.cd_ge.get(0, 'N/A'))

    #     print('\nEnvergadura=', round(self.prototype.w_bt, 3), 'm')
    #     print('Transição=', round(self.prototype.w_baf / self.prototype.w_bt, 3) * 100, '% da envergadura')
    #     print('Altura do EH com relação à asa=', round(self.prototype.eh_z_const, 3), 'm')
    #     print('Área alar=', round(self.prototype.s_ref, 3), 'm^2')
    #     print('AR=', round(self.prototype.ar, 2))
    #     print('AR do EH=', round(self.prototype.eh_ar, 2))
    #     print('M.A.C.=', round(self.prototype.mac, 3), 'm')

    #     print('\n--------------Controle e Estabilidade-----------------')
    #     print('VHT=', round(self.prototype.vht, 4))
    #     print('VVT=', round(self.prototype.vvt, 4))
    #     print('X_CG=', round(self.prototype.x_cg_p, 3), '% da corda da asa')
    #     print('Z_CG=', round(self.prototype.z_cg, 3), 'm do chão')
    #     print('CG=', round(self.prototype.low_cg, 3), 'm abaixo da asa')
    #     print('Ângulo de trimagem=', round(self.a_trim, 2), 'graus')
    #     print('Margem Estática=', round(self.me, 3))

        # print('--------------Perfis e Estol-----------------')
        # self.prototype.print_geometry_info()

# if __name__ == '__main__':
#     banana = Prototype( w_bt= 3.2321286257332065, w_baf= 0.9, w_cr= 0.45, w_ci= 0.8547042296684797, w_ct= 0.8, w_z= 0.18, w_inc= -0.3960870755918585, w_wo= 0.0, w_d= 2.1132179687299235, eh_b= 0.6197954432211882, eh_cr= 0.24309488336263088, eh_ct= 0.8, eh_inc= -2.0, ev_b= 0.4, ev_ct= 0.7900185499329802, eh_x= 1.3699514929079597, eh_z= 0.3, motor_x= -0.4,)
#     banana_ge = Prototype( w_bt= 3.2321286257332065, w_baf= 0.9, w_cr= 0.45, w_ci= 0.8547042296684797, w_ct= 0.8, w_z= 0.18, w_inc= -0.3960870755918585, w_wo= 0.0, w_d= 2.1132179687299235, eh_b= 0.6197954432211882, eh_cr= 0.24309488336263088, eh_ct= 0.8, eh_inc= -2.0, ev_b= 0.4, ev_ct= 0.7900185499329802, eh_x= 1.3699514929079597, eh_z= 0.3, motor_x= -0.4, ge=True)
#     banana2= Simulator(banana,banana_ge)
#     banana2.scorer()
#     banana2.print_coeffs()

