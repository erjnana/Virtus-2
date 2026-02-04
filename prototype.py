from avlwrapper import *
from mass import *
from support import *
from math import *
from airfoil_loader import *
from variables import *

def h_const(ev_z,ev_b): #mantido
    '''
    Função que calcula o valor relacionado à restrição geométrica

    w_bt[m],ev_z[m],ev_b[m] -> g_const[m]
    '''
    return ev_z+ev_b

def s_ref(w_cr, w_ci, w_baf,w_ct,w_bt): #alterado
    '''
    Função que calcula a área alar de uma asa com dois afilamentos
    
    Se atentar a calculos futuros em simulações simétricas (meia aeronave)

    w_cr[m], w_ci[m], w_baf[m],w_ct[m],w_bt[m] -> s_ref[m^2]

    '''
    return (((w_cr+w_ci)*w_baf/2) + ((w_ci+w_ct)/2)*(w_bt-w_baf))

def c_med(s_ref,w_bt): #mantido
    '''
    Função que calcula a corda média de uma asa trapezoidal

    s_ref[m],w_bt[m] -> c_med[m]
    '''
    return s_ref/w_bt

def z_d(w_b,w_d): 
    '''
    Função que calcula a altura de uma secção de uma superfície sustentadora em uma determinada envergadura dado o seu ângulo de diedro. Quando o mesmo se inicia da raíz

    w_b[m],w_d[m] -> w_z[m]
    '''
    w_z= w_b*tan(radians(w_d))
    
    return w_z

def ref_span(w_baf,mac,w_cr,w_bt): #mantido (precisa alterar na presente versão)
    '''
    Função que calcula a distância entre as cordas médias, envergadura de referência para uma asa mista reto-trapezoidal

    '''
    return w_baf+(mac/w_cr)*(w_bt-w_baf)

def lvt(ev_x, ev_cr, x_cg): #alterado (mas confirmar)
    '''
    Função que calcula a distância entre o EV e o CG em uma empenagem convencional
    
    Considera o centro aerodinâmico do perfil em 25% da corda
    '''
    # Entra a distância em y também
    return (ev_x + (ev_cr/4))-x_cg

def svt(ev_cr, ev_ct, ev_b): #alterado
    '''
    Função que calcula a área de um EV trapezoidal
    '''
    return (ev_cr+ev_ct)*ev_b/2

def vvt(lvt,svt,w_bt,s_ref): #mantido
    '''
    Função que calcula o volume de cauda vertical de uma empenagem em convencional com EV trapezoidal
    '''
    return ((lvt*svt)/(w_bt*s_ref))

def sht(eh_b,eh_cr, eh_ct): #alterado
    '''
    Função que calcula a área de um EH trapezoidal
    '''
    return eh_b*(eh_cr+eh_ct)/2

def lht(eh_x, eh_cr, x_cg): #alterado
    '''
    Função que calcula a distância entre o EH e o CG
    '''
    return (eh_x + (eh_cr/4))-x_cg

def vht(lht,sht,mac,s_ref): #mantido
    '''
    Função que calcula o volume de cauda horizontal de uma empenagem com EH retangular
    '''
    return (lht*sht)/(mac*s_ref)

def ar(b,s): #mantido
    '''
    Função que calcula a razão de aspecto de uma superfície utilizando a envergadura e área
    '''
    return (b**2)/s

def l_boom(fus_l, eh_x): #mantido 
    '''
    Função que calcula o comprimento do tailboom em função do comprimento da fuselagem, posição do eh e corda da raíz. Assumindo o início do boom na metade da fuselagem
    '''

    return eh_x-fus_l*0.8   # Boom começando no meio da fuselagem (possível ponto pra discussão)


class Prototype:
    """
    Constrói a geometria completa da aeronave no AVL.

    Convenções:
    - w_* : asa
    - eh_* : estabilizador horizontal
    - ev_* : estabilizador vertical
    """

    def __init__(
        self,
        # ---------------- ASA ----------------
        w_bt, w_baf, w_cr, w_ci, w_ct,
        w_z, w_inc, w_wo, w_d,

        # ---------------- EH ----------------
        eh_b, eh_cr, eh_ct, eh_inc, eh_x, eh_z,

        # ---------------- EV ----------------
        ev_b, ev_ct,

        # ---------------- MOTOR ----------------
        motor_x, motor_z=0.30,

        # ---------------- OPÇÕES ----------------
        ge=False
    ):
                #w_ci, w_ct, eh_ct, ev_ct são frações (0 a 1) de outra quantidade. Para facilitar a restrição na otimização

        # ====================================================
        # CONVERSÃO DE VARIÁVEIS ADIMENSIONAIS
        # ====================================================
        w_ci= w_ci*w_cr             # O input de w_ci é porcentagem da corda da raíz (w_cr), convertendo para [m]
        w_ct= w_ct*w_ci             # O input de w_ct é porcentagem da corda intermediária (w_ci), convertendo para [m]
        w_baf= w_baf*w_bt           # O input de w_baf é porcentagem do ponto de transição (w_bt), convertendo para [m

        # ====================================================
        # PERFIS
        # ====================================================


        # ====================================================
        # ARMAZENAMENTO DA ASA
        # ====================================================
        self.w_baf= w_baf           # Ponto de transição da envergadura
        self.w_bt= w_bt             # Envergadura total
        self.w_cr= w_cr             # Corda da raíz
        self.w_ci= w_ci             # Corda intermediária
        self.w_ct= w_ct             # Corda da ponta
        self.w_inc= w_inc           # Ângulo de incidência da asa
        self.w_wo= w_wo             # Washout na ponta da asa
        self.w_z= w_z               # Altura da asa em relação ao chão
        self.w_d= w_d               # Ângulo de diedro

        # ====================================================
        # EMPENAGEM HORIZONTAL
        # ====================================================
        eh_ct= eh_ct*eh_cr          # O input de eh_ct é porcentagem da corda da raíz (eh_cr), convertendo para [m]
        
        self.eh_b= eh_b             # Envergadura do EH
        self.eh_cr= eh_cr           # Corda da raíz do EH
        self.eh_ct= eh_ct           # Corda da ponta do EH
        self.eh_inc= eh_inc         # Ângulo de incidência do EH
        self.eh_x= eh_x             # Distância horizontal do bordo de atque do EH, em relação ao bordo de ataque da asa
        self.eh_z= eh_z             # Distância vertical do bordo de atque do EH, em relação ao solo

        # ====================================================
        # EMPENAGEM VERTICAL
        # ====================================================

        ev_cr= eh_cr                # Na configuração de empenagem convencional a corda do ev é igual à do eh
        ev_ct= ev_ct*ev_cr          # O input de ev_ct é porcentagem da corda da raíz (ev_cr), convertendo para [m]
        ev_x= eh_x                  # EV fixado com o EH
        ev_y= 0                     # Fixando ev_y no centro
        ev_z= eh_z                  # Ajuste da altura do EV, para ficar sobre o tailboom

        self.ev_b= ev_b             # Envergadura do EV
        self.ev_cr= ev_cr           # Corda da raíz EV
        self.ev_ct= ev_ct           # Corda da ponta EV
        self.ev_x= ev_x             # Distância horizontal do bordo de atque dos EV's, em relação ao bordo de ataque da asa
        self.ev_y= ev_y             # Distância no eixo Y dos EV's até o plano de simetria do avião
        self.ev_z= ev_z             # Distância vertical do bordo de atque dos EV's, em relação ao bordo de ataque da asa

        # ====================================================
        # MOTOR
        # ====================================================
        self.motor_x= motor_x       # Posição horizontal do motor. Vai ser negativa em uma configuração convencional
        self.motor_z= motor_z       # Posição vertical do motor
        self.pot= pot             # Potência do motor em W

        # ====================================================
        # FUSELAGEM E BOOM
        # ====================================================
        fus_h= self.w_cr*0.12                      # Modelando as placas da fuselagem como retângulos de altura = 12% da corda da raíz
        fus_l= 1.25*self.w_cr
        fus_z= self.w_z - fus_h*0.5

        self.fus_z= fus_z                          # Posicionando o centro da fuselagem coincidente com a asa
        if fus_l < 0.5:                            # Definindo a fuselagem igual a 125% da corda da raiz da asa, mas não menor que 50 cm.
            self.fus_l = 0.5
        else:
            self.fus_l= fus_l
        self.fus_h= fus_h                          # Altura da fuselagem
        #self.x0_boom= self.fus_l-self.motor_x
        self.boom_l= l_boom(self.fus_l, self.eh_x)

        # ====================================================
        # GRANDEZAS DE REFERÊNCIA
        # ====================================================
        self.s_ref = s_ref(w_cr, w_ci, w_baf, w_ct, w_bt)
        self.c_med = c_med(self.s_ref, w_bt)
        self.mac = mac(0, w_bt, w_baf, w_cr, w_ct)
        self.ref_span = ref_span(w_baf, self.mac, w_cr, w_bt)

        self.svt = svt(self.ev_cr, self.ev_ct, ev_b)
        self.sht = sht(eh_b, eh_cr, eh_ct)

        self.ar = ar(w_bt, self.s_ref)
        self.eh_ar = ar(eh_b, self.sht)

        # ====================================================
        # MASSA E CG
        # ====================================================
        self.eh_z_const= self.eh_z - self.w_z # Restrição geométrica para eh acima da asa
        self.pv= total_m(self.s_ref, self.sht, self.svt, self.fus_h, self.fus_l, self.boom_l)
        self.x_cg= cg(self.s_ref, self.w_z, self.w_cr, self.sht, self.eh_x, self.eh_z, self.eh_cr, self.svt, self.ev_x, self.ev_z, self.ev_cr, self.fus_z, self.fus_h, self.fus_l, self.boom_l, self.motor_x, self.motor_z)[0]
        self.z_cg= cg(self.s_ref, self.w_z, self.w_cr, self.sht, self.eh_x, self.eh_z, self.eh_cr, self.svt, self.ev_x, self.ev_z, self.ev_cr, self.fus_z, self.fus_h, self.fus_l, self.boom_l, self.motor_x, self.motor_z)[1]
        self.x_cg_p= self.x_cg/self.w_cr    # Posição do CG como fração da corda

        self.lvt= lvt(self.ev_x, self.ev_cr, self.x_cg)
        self.vvt= vvt(self.lvt,self.svt,self.w_bt,self.s_ref)

        self.lht= lht(self.eh_x, self.eh_cr, self.x_cg)
        self.vht= vht(self.lht,self.sht,self.mac,self.s_ref)

        self.low_cg= self.w_z - self.z_cg   # Restrição do CG abaixo da asa

        # ====================================================
        # PERFIS – CARREGADOS DO BANCO
        # ====================================================

        self.root_af = select_airfoil(root_af, airfoils_database_asa, label="Raiz da Asa")
        self.tip_af  = select_airfoil(tip_af, airfoils_database_asa, label="Ponta da Asa")
        self.eh_af   = select_airfoil(eh_af, airfoils_database_eh, label="EH")
        self.ev_af   = select_airfoil(ev_af, airfoils_database_ev, label="EV")

        # ====================================================
        # CL_MAX DOS PERFIS
        # ====================================================
        self.w_root_clmax = self.root_af['cl_max']
        self.w_tip_clmax = self.tip_af['cl_max']
        self.w_eh_clmax = self.eh_af['cl_max']
        self.w_ev_clmax = self.ev_af['cl_max']

        # ====================================================
        # SEÇÕES – ASA
        # ====================================================
        self.w_root_section = Section(leading_edge_point=Point(0, 0, w_z),
                                    chord=w_cr,
                                    airfoil=FileAirfoil(self.root_af["dat_path"])
                                    )
        
        self.w_trans_section = Section(leading_edge_point=Point((w_cr-w_ci)/4, self.w_baf, w_z + z_d(self.w_baf,w_d)),
                                    chord=w_ci,
                                    airfoil=FileAirfoil(self.root_af["dat_path"])
                                    )
        
        self.w_tip_section = Section(leading_edge_point=Point(((w_cr-w_ci)/4) + ((w_ci-w_ct)/4) , self.w_bt, w_z + z_d(self.w_bt,w_d)), #necessário incluir função para transformar o ângulo do diedro em altura do perfil
                                    chord=w_ct,
                                    airfoil=FileAirfoil(self.tip_af["dat_path"]),
                                    angle= self.w_wo
                                    )

        self.wing_surface = Surface(name="Wing",
                                    n_chordwise=12,
                                    chord_spacing=Spacing.cosine,
                                    n_spanwise=22,
                                    span_spacing=Spacing.neg_sine,
                                    y_duplicate=0.0,
                                    sections=[self.w_root_section,self.w_trans_section, self.w_tip_section],
                                    angle= self.w_inc
                                    )

        # ====================================================
        # SEÇÕES – EMPENAGEM
        # ====================================================

        self.elevator = Control(name="elevator",
                                gain=1.0,
                                x_hinge=0.4,
                                duplicate_sign=1.0)

        self.eh_root_section = Section(leading_edge_point=Point(eh_x, 0, eh_z),
                                        chord=eh_cr,
                                        airfoil= FileAirfoil(self.eh_af["dat_path"]),
                                        controls= [self.elevator]
                                        )
        
        self.eh_tip_section = Section(leading_edge_point=Point(eh_x + (eh_cr-eh_ct)/4, self.eh_b, eh_z),
                                        chord=eh_ct,
                                        airfoil= FileAirfoil(self.eh_af["dat_path"]),
                                        controls= [self.elevator]
                                        )
        
        self.ev_root_section = Section(leading_edge_point=Point(ev_x, 0, ev_z),
                                        chord=eh_cr,
                                        airfoil= FileAirfoil(self.eh_af["dat_path"])
                                        )
        
        self.ev_tip_section = Section(leading_edge_point=Point(ev_x + (ev_cr - ev_ct)/4, 0, ev_z+ev_b),
                                        chord=ev_ct,
                                        airfoil= FileAirfoil(self.eh_af["dat_path"])
                                        )
        
        self.eh_surface = Surface(name="Horizontal_Stabilizer",
                                    n_chordwise=8,
                                    chord_spacing=Spacing.cosine,
                                    n_spanwise=10,
                                    span_spacing=Spacing.equal,
                                    y_duplicate=0.0,
                                    sections=[self.eh_root_section, self.eh_tip_section],
                                    angle= self.eh_inc
                                    )
        
        self.ev_surface = Surface(name="Vertical_Stabilizer",
                                    n_chordwise=8,
                                    chord_spacing=Spacing.cosine,
                                    n_spanwise=8,
                                    span_spacing=Spacing.equal,
                                    #y_duplicate=0.0,
                                    sections=[self.ev_root_section, self.ev_tip_section]
                                    )

############################################# Definição da geometria com e sem o efeito solo (método das imagens) #############################################

        if ge:
            #Todas as dimensões de referência são calculadas diretamente, mas podem ser implementadas funções mais acima
            self.geometry = Geometry(name="Prototype",
                                    reference_area= self.s_ref,
                                    reference_chord= self.mac,
                                    reference_span= self.ref_span,
                                    reference_point=Point(self.x_cg, 0, self.z_cg),
                                    surfaces=[self.wing_surface, self.eh_surface, self.ev_surface],
                                    #y_symmetry=Symmetry.symmetric,
                                    z_symmetry=Symmetry.symmetric,
                                    z_symmetry_plane= 0.00
                                    )

        else:

            self.geometry = Geometry(name="Prototype",
                                    reference_area= self.s_ref,
                                    reference_chord= self.mac,
                                    reference_span= self.ref_span,
                                    reference_point= Point(self.x_cg, 0, self.z_cg),
                                    surfaces=[self.wing_surface, self.eh_surface, self.ev_surface],
                                    #y_symmetry=Symmetry.symmetric
                                    )

        

    #Método utilizado para mostrar em interface gráfica a geometria do protótipo
    def show_geometry(self):

        geometry_session= Session(geometry= self.geometry, cases=[])
        geometry_session.show_geometry()


    # ====================================================
    # MÉTODO DE PRINT DA GEOMETRIA E PERFIS
    # ====================================================
    def print_geometry_info(self):
        print("\n--- Perfis escolhidos ---")
        print(f"Perfil da Raiz: {self.root_af['name']}  |  Alpha CLmax: {self.root_af['alpha_cl_max']}°")
        print(f"Perfil da Ponta: {self.tip_af['name']}  |  Alpha CLmax: {self.tip_af['alpha_cl_max']}°")
        print(f"Perfil do EH: {self.eh_af['name']}  |  Alpha CLmax: {self.eh_af['alpha_cl_max']}°\n")
        print(f"Perfil do EV: {self.ev_af['name']}  |  Alpha CLmax: {self.ev_af['alpha_cl_max']}°\n")



# if __name__ == '__main__':
#     banana = Prototype( w_bt= 3.2321286257332065, w_baf= 0.9, w_cr= 0.45, w_ci= 0.8547042296684797, w_ct= 0.8, w_z= 0.18, w_inc= -0.3960870755918585, w_wo= 0.0, w_d= 2.1132179687299235, eh_b= 0.6197954432211882, eh_cr= 0.24309488336263088, eh_ct= 0.8, eh_inc= -2.0, ev_b= 0.4, ev_ct= 0.7900185499329802, eh_x= 1.3699514929079597, eh_z= 0.3, motor_x= -0.4, ge=False)
#     banana_ge = Prototype( w_bt= 3.2321286257332065, w_baf= 0.9, w_cr= 0.45, w_ci= 0.8547042296684797, w_ct= 0.8, w_z= 0.18, w_inc= -0.3960870755918585, w_wo= 0.0, w_d= 2.1132179687299235, eh_b= 0.6197954432211882, eh_cr= 0.24309488336263088, eh_ct= 0.8, eh_inc= -2.0, ev_b= 0.4, ev_ct= 0.7900185499329802, eh_x= 1.3699514929079597, eh_z= 0.3, motor_x= -0.4, ge=True)
#     banana.print_geometry_info()