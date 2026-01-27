import openmdao.api as om

# Importa os módulos principais do MDO
from prototype import Prototype
from simulator import Simulator

# Importa variáveis globais do projeto (restrições, configs, etc.)
from variables import ALPHA_STALL_MIN_DEG


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

        # ======= PROPULSÃO =======
        self.add_input('motor_x', val=-0.218)

        # ======= OUTPUTS =======
        self.add_output('score', val=0.0)

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

        ALPHA_STALL_MIN_DEG = prototype.compute_stall_angle() 
        outputs['stall_constraint'] = ALPHA_STALL_MIN_DEG - simulator.a_trim

        # ======= CONSTRUÇÃO DO AVIÃO =======
        prototype = Prototype(
            w_bt, w_baf, w_cr, w_ci, w_ct,
            w_z, w_inc, w_wo, w_d,
            eh_b, eh_cr, eh_ct, eh_inc,
            eh_x, eh_z,
            ev_ct, ev_b,
            motor_x,
            motor_z=0.30,
            ge=False
        )

        prototype_ge = Prototype(
            w_bt, w_baf, w_cr, w_ci, w_ct,
            w_z, w_inc, w_wo, w_d,
            eh_b, eh_cr, eh_ct, eh_inc,
            eh_x, eh_z,
            ev_ct, ev_b,
            motor_x,
            motor_z=0.30,
            ge=True
        )

        # ======= SIMULAÇÃO =======
        simulator = Simulator(prototype, prototype_ge)

        # Score global do indivíduo
        score = simulator.scorer()

        # ======= OUTPUTS =======
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

