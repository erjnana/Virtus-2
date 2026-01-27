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

    def __init__(self, prototype, prototype_ge, p=905.5, t=25, v=10, mach=0.0):
        self.prototype = prototype
        self.prototype_ge = prototype_ge
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
        stall = False
        b_stall = 0

        for panel_n in range(int(len(results['a']['StripForces']['Wing']['Yle']))):
            y_pos = results['a']['StripForces']['Wing']['Yle'][panel_n]
            cl = results['a']['StripForces']['Wing']['cl'][panel_n]

            if y_pos <= self.prototype.w_baf / 2:
                clmax = self.prototype.w_root_clmax
            else:
                af_len = (self.prototype.w_bt - self.prototype.w_baf) / 2
                af_len_perc = (y_pos - self.prototype.w_baf / 2) / af_len
                clmax = af_len_perc * self.prototype.w_tip_clmax + (1 - af_len_perc) * self.prototype.w_root_clmax

            if cl >= clmax:
                stall = True
                b_stall = y_pos / (self.prototype.w_bt / 2)
                return stall, b_stall

        return stall, b_stall

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

        try:
            stall, _ = self.check_stall(a_results)
            if not stall:
                self.deflex[a] = a_results['a']['Totals']['elevator']
                self.cl[a] = a_results['a']['Totals']['CLtot']
                self.cd[a] = a_results['a']['Totals']['CDtot']
                self.cm[a] = a_results['a']['Totals']['Cmtot']
                self.cma[a] = a_results['a']['StabilityDerivatives']['Cma']
                self.cnb[a] = a_results['a']['StabilityDerivatives']['Cnb']
            else:
                raise RuntimeError(f"Estol detectado em alfa={a}")
            return a_results
        except Exception as e:
            stall, b_stall = self.check_stall(a_results)
            print(f'Estol em {b_stall*100:.1f}% da envergadura')
            raise e

    def run_ge(self):
        print('Calculando coeficientes em efeito solo')
        a_case = Case(
            name='a',
            alpha=0,
            density=self.rho,
            Mach=self.mach,
            velocity=self.v,
            X_cg=self.prototype.x_cg,
            Z_cg=self.prototype.z_cg
        )
        session = Session(geometry=self.prototype_ge.geometry, cases=[a_case])
        a_results = session.get_results()
        self.cl_ge[0] = a_results['a']['Totals']['CLtot']
        self.cd_ge[0] = a_results['a']['Totals']['CDtot']
        return a_results

    def run_stall(self):
        for a in np.arange(5, 12, 2):
            try:
                self.run_a(a)
            except:
                self.a_stall = a - 1
                self.clmax = self.cl[a - 1]
                print(f'Ângulo de estol entre {a-1} e {a} graus')
                break
        for a in np.arange(12, 31, 1):
            try:
                self.run_a(a)
            except:
                self.a_stall = a - 1
                self.clmax = self.cl[a - 1]
                print(f'Ângulo de estol entre {a-1} e {a} graus')
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
        self.a_trim = trim_results['trimmed']['Totals']['Alpha']
        self.xnp = trim_results['trimmed']['StabilityDerivatives']['Xnp']
        self.me = me(self.xnp, self.prototype.x_cg, self.prototype.mac)

    ###########################################################################
    # MÉTODO PRINCIPAL DE PONTUAÇÃO
    ###########################################################################
    def scorer(self):
        try:
            self.run_a(0)
            print('CASO ALFA 0 CONCLUIDO')
        except:
            print('FALHA NA SIMULAÇÃO DE ALFA 0')
            self.score = 0

        try:
            self.run_ge()
            print('CASO EFEITO SOLO CONCLUIDO')
        except:
            print('FALHA NA SIMULAÇÃO EM EFEITO SOLO')
            self.score = 0

        try:
            self.run_stall()
            print('CASO ESTOL CONCLUIDO')
        except:
            print('FALHA NA SIMULAÇÃO ATÉ O ESTOL')
            self.score = 0

        try:
            self.run_trim()
            print('CASO TRIMADO CONCLUIDO')
        except:
            print('FALHA NA SIMULAÇÃO DE TRIMAGEM')
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
        except:
            print('FALHA NA SIMULAÇÃO DE MTOW')
            self.score = 0
            self.cp = 0

        # PONTUAÇÃO DA COMPETIÇÃO
        try:
            comp_score_dict = compute_competition_score(
                simulator=self,
                N_horizontal=1
            )
            self.competition_score = comp_score_dict["PVOO"]
            print(f"🏆 Pontuação de voo final (PVOO): {self.competition_score:.3f}")
        except Exception as e:
            print("⚠️ Erro ao calcular a pontuação da competição:", e)
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

        return self.score, self.competition_score

    ###########################################################################
    # MÉTODO PARA PRINTAR COEFICIENTES E INFO
    ###########################################################################
    def print_coeffs(self):
        aero_coeffs = pd.DataFrame(
            [self.cl, self.cd, self.cm, self.deflex],
            index=['CL', 'CD', 'CM', 'Prof']
        ).T

        print('--------------OUTPUTS-----------------\n')
        print('--------------Aerodinâmica-----------------')
        print('Coeficientes aerodinâmicos:\n', aero_coeffs, sep='')
        print('CL em corrida=', self.cl_ge.get(0, 'N/A'))
        print('CD em corrida=', self.cd_ge.get(0, 'N/A'))

        print('Envergadura=', round(self.prototype.w_bt, 3), 'm')
        print('Transição=', round(self.prototype.w_baf / self.prototype.w_bt, 3) * 100, '% da envergadura')
        print('Área alar=', round(self.prototype.s_ref, 3), 'm^2')
        print('AR=', round(self.prototype.ar, 2))
        print('AR do EH=', round(self.prototype.eh_ar, 2))
        print('M.A.C.=', round(self.prototype.mac, 3), 'm')

        print('--------------Controle e Estabilidade-----------------')
        print('VHT=', round(self.prototype.vht, 4))
        print('VVT=', round(self.prototype.vvt, 4))
        print('X_CG=', round(self.prototype.x_cg_p, 3), '% da corda da asa')
        print('Z_CG=', round(self.prototype.z_cg, 3), 'm do chão')
        print('CG=', round(self.prototype.low_cg, 3), 'm abaixo da asa')
        print('Ângulo de trimagem=', round(self.a_trim, 2), 'graus')
        print('Margem Estática=', round(self.me, 3))

        print('--------------Restrições-----------------')
        print('Altura do EH com relação à asa=', round(self.prototype.eh_z_const, 3), 'm')

        print('--------------Estruturas-----------------')
        print('Peso Vazio=', round(self.prototype.pv, 3), 'kg')

        print('--------------Perfis e Estol-----------------')
        self.prototype.print_geometry_info()

