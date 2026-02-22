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

        #self.add_output('cl_max_3d_wing', val=0.0)
        #self.add_output('cl_max_3d_canard', val=0.0)
        #self.add_output('stall_safety_margin', val=0.0) # Diferença entre estol do Canard e da Asa

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
        w_bt = float(inputs['w_bt'][0])
        w_baf = float(inputs['w_baf'][0])
        w_cr = float(inputs['w_cr'][0])
        w_ci = float(inputs['w_ci'][0])
        w_ct = float(inputs['w_ct'][0])
        w_z = float(inputs['w_z'][0])
        w_inc = float(inputs['w_inc'][0])
        w_wo = float(inputs['w_wo'][0])
        w_d = float(inputs['w_d'][0])

        eh_b = float(inputs['eh_b'][0])
        eh_cr = float(inputs['eh_cr'][0])
        eh_ct = float(inputs['eh_ct'][0])
        eh_inc = float(inputs['eh_inc'][0])
        eh_x = float(inputs['eh_x'][0])
        eh_z = float(inputs['eh_z'][0])

        ev_b = float(inputs['ev_b'][0])
        ev_ct = float(inputs['ev_ct'][0])

        cn_b = float(inputs['cn_b'][0])
        cn_cr = float(inputs['cn_cr'][0])
        cn_ct = float(inputs['cn_ct'][0])
        cn_inc = float(inputs['cn_inc'][0])
        cn_x = float(inputs['cn_x'][0])
        cn_d = float(inputs['cn_d'][0])
        cn_z = float(inputs['cn_z'][0])

        motor_x = float(inputs['motor_x'][0])

        def definir_perfil(instrucao, idx_float, lista, database, label):
            if instrucao.lower() == "random":
                i = int(round(float(idx_float[0])))
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
        #outputs['cl_max_3d_wing'] = cl_max_3d_asa
        #outputs['cl_max_3d_canard'] = cl_max_3d_canard
        outputs['eh_z_const'] = prototype.eh_z_const
        