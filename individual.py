import openmdao.api as om
from prototype import Prototype
from simulator import Simulator
from variables import *
# IMPORTANTE: importar as listas e bases
from airfoil_loader import (LISTA_ASA, LISTA_EH, LISTA_EV, airfoils_database_asa, airfoils_database_eh, airfoils_database_ev)

class Individual(om.ExplicitComponent):
    """
    Componente OpenMDAO que representa UM indivíduo do MDO.

    - Recebe variáveis de design (inputs)
    - Constrói o avião (Prototype)
    - Simula seu desempenho (Simulator)
    - Retorna score e métricas para otimização
    """

    def setup(self):
        """
        Definição das entradas (variáveis de design)
        Essas variáveis serão manipuladas pelo otimizador
        """

        # ======= ASA =======
        self.add_input('w_bt', val=3.0)     # envergadura total
        self.add_input('w_baf', val=0.2)    # fração da asa afilada
        self.add_input('w_cr', val=0.40)    # corda raiz
        self.add_input('w_ci', val=0.90)    # corda intermediária
        self.add_input('w_ct', val=0.87)    # corda ponta
        self.add_input('w_z', val=0.21)     # posição vertical
        self.add_input('w_inc', val=0.0)    # incidência
        self.add_input('w_wo', val=0.0)     # washout
        self.add_input('w_d', val=1.4)      # diedro

        # ======= EMPENAGEM HORIZONTAL =======
        self.add_input('eh_b', val=0.74)
        self.add_input('eh_cr', val=0.26)
        self.add_input('eh_ct', val=0.90)
        self.add_input('eh_inc', val=-1.19)
        self.add_input('eh_x', val=1.051)
        self.add_input('eh_z', val=0.4)
        

        # ======= EMPENAGEM VERTICAL =======
        self.add_input('ev_b', val=0.32)
        self.add_input('ev_ct', val=0.83)

        # ======= PERFIS =======
        self.add_input('idx_asa_root', val=0.0)
        self.add_input('idx_asa_tip', val=0.0)
        self.add_input('idx_eh', val=0.0)
        self.add_input('idx_ev', val=0.0)

        # ======= PROPULSÃO =======
        self.add_input('motor_x', val=-0.218)

        # ======= OUTPUTS =======
        self.add_output('score', val=0.0)
        self.add_output('eh_z_const', val= 0.06)

        # Métricas aerodinâmicas / geométricas
        self.add_output('vht', val=0.0)
        self.add_output('vvt', val=0.0)
        self.add_output('ar', val=0.0)
        self.add_output('eh_ar', val=0.0)

        # Estabilidade / trim
        self.add_output('a_trim', val=0.0)
        self.add_output('me', val=0.0)

        # Centro de gravidade
        self.add_output('low_cg', val=0.0)
        self.add_output('x_cg_p', val=0.0)

        # ======= RESTRIÇÃO DE STALL =======
        # Margem de stall (deve ser >= 0)
        self.add_output('stall_constraint', val=0.0)

        # Carga propulsiva
        self.add_output('cp', val=0.0)

    def compute(self, inputs, outputs):
        """
        Executa a simulação de um indivíduo
        """
        global primeira_execucao
        # ======= CONVERSÃO DOS INPUTS =======
        # OpenMDAO trabalha com arrays → converter para float
        w_bt = float(inputs['w_bt'])
        w_baf = float(inputs['w_baf'])
        w_cr = float(inputs['w_cr'])
        w_ci = float(inputs['w_ci'])
        w_ct = float(inputs['w_ct'])
        w_z = float(inputs['w_z'])
        w_inc = float(inputs['w_inc'])
        w_wo = float(inputs['w_wo'])
        w_d = float(inputs['w_d'])

        eh_b = float(inputs['eh_b'])
        eh_cr = float(inputs['eh_cr'])
        eh_ct = float(inputs['eh_ct'])
        eh_inc = float(inputs['eh_inc'])
        eh_x = float(inputs['eh_x'])
        eh_z = float(inputs['eh_z'])

        ev_b = float(inputs['ev_b'])
        ev_ct = float(inputs['ev_ct'])

        motor_x = float(inputs['motor_x'])

        def definir_perfil(instrucao, idx_float, lista, database, label):
            if instrucao.lower() == "random":
                # Traduz o índice do otimizador para um nome da lista
                i = int(round(float(idx_float)))
                i = max(0, min(i, len(lista) - 1))
                chosen_name = lista[i]
                print(f"🎲 [OTIMIZANDO] {label}: Selecionado o perfil '{chosen_name}'")
            else:
                chosen_name = instrucao
                if chosen_name not in database:
                    raise KeyError(f"❌ Erro: Perfil '{chosen_name}' não encontrado para {label}.")
                print(f"✅ [FIXO]   {label}: Usando o perfil '{chosen_name}'")
            
            return database[chosen_name]

        # Resgatando os perfis com base na regra
        dados_root = definir_perfil(root_af, inputs['idx_asa_root'], LISTA_ASA, airfoils_database_asa, "Raiz da Asa")
        dados_tip  = definir_perfil(tip_af,  inputs['idx_asa_tip'],  LISTA_ASA, airfoils_database_asa, "Ponta da Asa")
        dados_eh   = definir_perfil(eh_af,   inputs['idx_eh'],       LISTA_EH,  airfoils_database_eh,  "EH")
        dados_ev   = definir_perfil(ev_af,   inputs['idx_ev'],       LISTA_EV,  airfoils_database_ev,  "EV")

        # ======= CONSTRUÇÃO DO AVIÃO =======
        prototype = Prototype(
            w_bt, w_baf, w_cr, w_ci, w_ct,
            w_z, w_inc, w_wo, w_d,
            eh_b, eh_cr, eh_ct, eh_inc,
            eh_x, eh_z,
            ev_ct, ev_b,
            motor_x,
            motor_z=0.30,
            af_root_data=dados_root,
            af_tip_data=dados_tip,
            af_eh_data=dados_eh,
            af_ev_data=dados_ev
        )

        # ======= SIMULAÇÃO =======
        simulator = Simulator(prototype)

        # Score global do indivíduo
        score = simulator.scorer()[1]

        # ======= OUTPUTS =======
        outputs['stall_constraint'] = ALPHA_STALL_MIN_DEG - simulator.a_trim
        outputs['score'] = score

        outputs['vht'] = prototype.vht
        outputs['vvt'] = prototype.vvt
        outputs['ar'] = prototype.ar
        outputs['eh_ar'] = prototype.eh_ar

        outputs['a_trim'] = simulator.a_trim
        outputs['me'] = simulator.me

        outputs['low_cg'] = prototype.low_cg
        outputs['x_cg_p'] = prototype.x_cg_p

        outputs['cp'] = simulator.cp

        # ======= RESTRIÇÃO DE STALL DO AVIÃO =======
        # Margem positiva → seguro
        # Margem negativa → stall
        outputs['stall_constraint'] = ALPHA_STALL_MIN_DEG - simulator.a_trim

