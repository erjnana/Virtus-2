import openmdao.api as om
from prototype import Prototype
from simulator import Simulator
from variables import *
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

        # ======= ASA PRINCIPAL =======
        self.add_input('w_bt', val=3.0)
        self.add_input('w_baf', val=0.2)
        self.add_input('w_cr', val=0.40)
        self.add_input('w_ci', val=0.90)
        self.add_input('w_ct', val=0.87)
        self.add_input('w_z', val=0.21)
        self.add_input('w_inc', val=0.0)
        self.add_input('w_wo', val=0.0)
        self.add_input('w_d', val=1.4)

        # ======= EMPENAGEM (EH / EV) =======
        self.add_input('eh_b', val=0.74)
        self.add_input('eh_cr', val=0.26)
        self.add_input('eh_ct', val=0.90)
        self.add_input('eh_inc', val=-1.19)
        self.add_input('eh_x', val=1.051)
        self.add_input('eh_z', val=0.4)
        
        self.add_input('ev_b', val=0.32)
        self.add_input('ev_ct', val=0.83)

        # ======= CANARD =======
        self.add_input('cn_b', val=0.0)
        self.add_input('cn_cr', val=0.0)
        self.add_input('cn_ct', val=0.0)
        self.add_input('cn_inc', val=0.0)
        self.add_input('cn_x', val=0.0)
        self.add_input('cn_d', val=0.0)
        self.add_input('cn_z', val=0.0)


        # ======= PERFIS  =======
        self.add_input('idx_asa_root', val=0.0)
        self.add_input('idx_asa_tip', val=0.0)
        self.add_input('idx_eh', val=0.0)
        self.add_input('idx_ev', val=0.0)
        self.add_input('idx_cn', val=0.0)

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

        self.add_output('cl_max_3d_wing', val=0.0)
        self.add_output('cl_max_3d_canard', val=0.0)
        self.add_output('stall_safety_margin', val=0.0) # Diferença entre estol do Canard e da Asa

        # ======= RESTRIÇÃO DE STALL =======
        # Margem de stall (deve ser >= 0)
        self.add_output('stall_constraint', val=0.0)

        # Carga propulsiva
        self.add_output('cp', val=0.0)

        self.declare_partials(of='*', wrt='*', method='fd')

    def compute(self, inputs, outputs):
        """
        Executa a simulação de um indivíduo
        """
        global primeira_execucao
        # ======= CONVERSÃO DOS INPUTS =======
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

        cn_b = float(inputs['cn_b'])
        cn_cr = float(inputs['cn_cr'])
        cn_ct = float(inputs['cn_ct'])
        cn_inc = float(inputs['cn_inc'])
        cn_x = float(inputs['cn_x'])
        cn_d = float(inputs['cn_d'])
        cn_z = float(inputs['cn_z'])

        motor_x = float(inputs['motor_x'])

        motor_x = float(inputs['motor_x'])

        def definir_perfil(instrucao, idx_float, lista, database, label):
            if instrucao.lower() == "random":
                i = int(round(float(idx_float)))
                i = max(0, min(i, len(lista) - 1))
                chosen_name = lista[i]
                msg = f"🎲 [OTIMIZANDO] {label}: Selecionado o perfil '{chosen_name}'"
            else:
                chosen_name = instrucao
                if chosen_name not in database:
                    raise KeyError(f"❌ Erro: Perfil '{chosen_name}' não encontrado.")
                msg = f"✅ [FIXO]    {label}: Usando o perfil '{chosen_name}'"
            
            return database[chosen_name], msg # Retorna o dado E a mensagem

        # 2. Carregamos SEMPRE a Asa (pois toda configuração tem asa)
        dados_root, msg_root = definir_perfil(root_af, inputs['idx_asa_root'], LISTA_ASA, airfoils_database_asa, "Raiz da Asa")
        dados_tip, msg_tip = definir_perfil(tip_af, inputs['idx_asa_tip'], LISTA_ASA, airfoils_database_asa, "Ponta da Asa")
        print(msg_root)
        print(msg_tip)

        # 3. Lógica condicional de carregamento e impressão
        # Inicializamos variáveis vazias/None para evitar erros
        dados_eh = dados_ev = dados_canard = None

        if P_CONFIG == "asa_voadora":
            eh_b = ev_b = cn_b = 0.0
            print("🛸 Configuração: ASA VOADORA")
            # Não carrega nem printa EH, EV ou Canard

        elif P_CONFIG == "canard":
            # Carrega e printa tudo
            dados_eh, msg_eh = definir_perfil(eh_af, inputs['idx_eh'], LISTA_EH, airfoils_database_eh, "EH")
            dados_ev, msg_ev = definir_perfil(ev_af, inputs['idx_ev'], LISTA_EV, airfoils_database_ev, "EV")
            dados_canard, msg_cn = definir_perfil(cn_af, inputs['idx_cn'], LISTA_EV, airfoils_database_ev, "Canard")
            print(msg_eh)
            print(msg_ev)
            print(msg_cn)
            print("🦆 Configuração: CANARD")

        else: # CONVENCIONAL
            cn_b = 0.0
            # Carrega e printa apenas EH e EV
            dados_eh, msg_eh = definir_perfil(eh_af, inputs['idx_eh'], LISTA_EH, airfoils_database_eh, "EH")
            dados_ev, msg_ev = definir_perfil(ev_af, inputs['idx_ev'], LISTA_EV, airfoils_database_ev, "EV")
            print(msg_eh)
            print(msg_ev)
            print("🛩️ Configuração: CONVENCIONAL")

        # ======= CONSTRUÇÃO DO AVIÃO =======
        prototype = Prototype(
            w_bt=w_bt, w_baf=w_baf, w_cr=w_cr, w_ci=w_ci, w_ct=w_ct,
            w_z=w_z, w_inc=w_inc, w_wo=w_wo, w_d=w_d,
            eh_b=eh_b, eh_cr=eh_cr, eh_ct=eh_ct, eh_inc=eh_inc,
            eh_x=eh_x, eh_z=eh_z,
            ev_ct=ev_ct, ev_b=ev_b,
            motor_x=motor_x,
            motor_z=0.30,
            af_root_data=dados_root,
            af_tip_data=dados_tip,
            af_eh_data=dados_eh,
            af_ev_data=dados_ev,
            af_canard_data=dados_canard,
            cn_b=cn_b, cn_cr=cn_cr, cn_ct=cn_ct, 
            cn_inc=cn_inc, cn_x=cn_x, cn_d=cn_d, cn_z=cn_z
        )

        # ======= SIMULAÇÃO =======
        simulator = Simulator(prototype)

        # Score global do indivíduo
        score = simulator.scorer()[1]

        # Pegar os Cls máximos encontrados na geometria 3D durante o trim
        # Você deve garantir que seu Simulator tenha acesso a esses valores do AVL
        cl_max_3d_asa    = simulator.get_max_cl_surface("Wing")
        cl_max_3d_canard = simulator.get_max_cl_surface("Canard") if cn_b > 0 else 0.0
        cl_max_3d_eh     = simulator.get_max_cl_surface("Eh") if eh_b > 0 else 0.0

        # Pegar os Cls limites (2D) dos perfis carregados
        cl_limit_asa    = dados_root['cl_max']

        if prototype.cn_b > 0.01 and dados_canard is not None:
            cl_limit_canard = dados_canard['cl_max']
        else:
            cl_limit_canard = 1.0 # Valor genérico que não afetará a lógica se o Canard não existir

        if prototype.eh_b > 0.01 and dados_eh is not None:
            cl_limit_eh = dados_eh['cl_max']
        else:
            cl_limit_eh = 1.0 # Valor genérico que não afetará a lógica se o EH não existir

        # Calcular a "distância" para o estol de cada superfície (Margem de Sustentação)
        # Quanto menor o valor, mais perto do estol a superfície está.
        margem_w = cl_limit_asa - cl_max_3d_asa

        # Margem do Canard (com proteção)
        if cn_b > 0.01 and dados_canard is not None:
            cl_limit_canard = dados_canard['cl_max']
            margem_cn = cl_limit_canard - cl_max_3d_canard
        else:
            margem_cn = 99.0 

        # Margem do EH (com proteção)
        if eh_b > 0.01 and dados_eh is not None:
            cl_limit_eh = dados_eh['cl_max']
            margem_eh = cl_limit_eh - cl_max_3d_eh
        else:
            margem_eh = 99.0

        # ======= LÓGICA DE RESTRIÇÃO (CONSOLIDADA) =======
        if cn_b > 0.01:
            # Canard deve estolar antes da Asa, e Asa antes do EH
            c1 = margem_w - margem_cn   
            c2 = margem_eh - margem_w   
            ordem_estol = min(c1, c2)
            
            # Cálculo da margem de segurança específica para Canard
            margin_wing = prototype.w_root_clmax - cl_max_3d_asa
            margin_canard = dados_canard['cl_max'] - cl_max_3d_canard
            outputs['stall_safety_margin'] = margin_wing - margin_canard
        else:
            # Convencional: Asa deve estolar antes do EH
            ordem_estol = margem_eh - margem_w
            outputs['stall_safety_margin'] = 99.0 # Valor neutro

        # Segurança de Alpha de Trim
        seguranca_trim = ALPHA_STALL_MIN_DEG - simulator.a_trim
        outputs['stall_constraint'] = min(ordem_estol, seguranca_trim)

        # ======= DEMAIS OUTPUTS =======
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
        outputs['cl_max_3d_wing'] = cl_max_3d_asa
        outputs['cl_max_3d_canard'] = cl_max_3d_canard
        outputs['eh_z_const'] = prototype.eh_z_const
        