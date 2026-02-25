"""
Variáveis de design e ajustes para a otimizaçao do MDO
Aqui estão todos os dados que são necessários serem ajustados antes de rodar o MDO

"""
# =========================
# CONFIGURAÇÃO DO PROJETO
# =========================

# Opções: "convencional", "canard", "asa_voadora"
P_CONFIG = "canard"

# =========================
# IDENTIDADE DO PROJETO
# =========================

NAME = "banana"     # Nome do projeto usado em logs, resultados e relatórios
PROJECT_NAME = f"{NAME}_{P_CONFIG}"

# ============================================================
# CONFIGURAÇÕES DO OTIMIZADOR
# ============================================================

OPTIMIZER_POP_SIZE = 35             # Tamanho da população
OPTIMIZER_MAX_GEN = 120             # Número máximo de gerações
OPTIMIZER_PENALTY_PARAM = 20.0      # Parâmetro de penalização das restrições
OPTIMIZER_PENALTY_EXP = 1.0         # Expoente de penalização das restrições
OPTIMIZER_DRIVER = "Differential Evolution Driver"  # Tipo de driver

# =========================
# PONTUAÇÃO ESTIMADA
# =========================

NR_DEFAULT = 130.00         # Nota de relatório estimada
PEE_FACTOR = 50             # Fator de pontuação eficiência estrutural
APRESENTACAO = 32.00        # Nota da apresentação
VIDEOVOO = 30.0             # Nota do vídeo de voo

# ============================================================
# RESTRIÇÕES DE DESEMPENHO
# ============================================================

c_pista= 55     # Comprimento da pista de decolagem (m)
h_decol= 0.9    # Altura do obstãculo (m)
pot = 600.0     # Potência máxima do motor (W)

# ============================================================
# PERFIS DO AVIÃO
# ============================================================

root_af='random'            # Perfil da raiz da asa (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
tip_af='random'             # Perfil da ponta da asa (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
eh_af='random'            # Perfil do EH (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
ev_af ='random'           # Perfil do EV (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
cn_af = 'random'          # Perfil do canard (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)

# =========================
# INPUTS DO INDIVÍDUO
# =========================

INDIVIDUAL_INPUTS = [
    # Geral
    'w_bt',
    'w_baf', 
    'w_cr', 
    'w_ci', 
    'w_ct',
    'w_z', 
    'w_inc', 
    'w_wo', 
    'w_d',
    # Empenagem
    'eh_b', 
    'eh_cr', 
    'eh_ct', 
    'eh_inc',
    'ev_b', 
    'ev_ct',
    'eh_x', 
    'eh_z',
    # Motor
    'motor_x',
    # Canard
    'cn_b',
    'cn_cr',
    'cn_ct',
    'cn_inc',
    'cn_x', 
    'cn_d',
    'cn_z',
    
]

# ========================= ========================= ========================= =========================
# RESTRICÒES PARA AERONAVE CONVENCIONAL
# ========================= ========================= ========================= =========================

if P_CONFIG == "convencional":
    Nhor_DEFAULT = 2            # Asa + EH

    # =========================
    # VALORES INICIAIS
    # =========================

    DEFAULT_VALUES = {
        'w_bt': 2.0,        #envergadura
        'w_baf': 0.8,       #região de transição (% da envergadura)
        'w_cr': 0.4,        #corda da raiz
        'w_ci': 0.70,       #corda da transição (% da raiz)
        'w_ct': 0.75,       #corda da ponta (% da transição)
        'w_z': 0.20,        #altura da asa
        'w_inc': 0.0,       #incidência da asa
        'w_wo': 0.0,        #washout da asa
        'w_d': 1.0,         #diedro da asa

        'eh_b': 0.9,        #envergadura
        'eh_cr': 0.25,      #corda da raiz
        'eh_ct': 0.87,      #corda da ponta (% da raiz)
        'eh_inc': 0.0,      #incidência

        'ev_b': 0.40,       #envergadura
        'ev_ct': 0.8,       #corda da ponta (% da raiz)

        'eh_x': 0.8,        #distância do eh
        'eh_z': 0.4,        #altura do eh

        'motor_x': -0.4,    #distância do motor

        'cn_b': 0.0,          #envergadura do canard
        'cn_cr': 0.0,       #corda da raiz do canard
        'cn_ct': 0.0,      #corda da ponta do canard (% da raiz)
        'cn_inc': 0.0,      #incidência do canard
        'cn_x': 0.0,       #distância do canard (em relação à asa)
        'cn_d': 0.0,        #diedro do canard
        'cn_z': 0.0,        #altura do canard (em relação à asa)
    }

    # =========================
    # LIMITES DAS VARIÁVEIS
    # =========================

    DESIGN_VARIABLES = {
        'w_bt':     {'lower': 1.5,  'upper': 2.8},
        'w_baf':    {'lower': 0.6, 'upper': 0.9},
        'w_cr':     {'lower': 0.25, 'upper': 0.60},
        'w_ci':     {'lower': 0.60, 'upper': 0.90},
        'w_ct':     {'lower': 0.5, 'upper': 0.9},
        'w_z':      {'lower': 0.15, 'upper': 0.3},
        'w_inc':    {'lower': -2.0,  'upper': 2.0},
        'w_wo':     {'lower': -2.0,  'upper': 2.0},
        'w_d':      {'lower': 0.0,  'upper': 5.0},

        'eh_b':     {'lower': 0.4,  'upper': 1.0},
        'eh_cr':    {'lower': 0.15, 'upper': 0.35},
        'eh_ct':    {'lower': 0.6, 'upper': 1.0},
        'eh_inc':   {'lower': -3,  'upper': 3},

        'eh_x':     {'lower': 0.50, 'upper': 1.3},
        'eh_z':     {'lower': 0.18, 'upper': 0.6},

        'ev_b':     {'lower': 0.3, 'upper': 0.5},
        'ev_ct':    {'lower': 0.7, 'upper': 0.95},

        'motor_x':  {'lower': -0.6, 'upper': -0.30},

        'cn_b': {'lower': 0.0,  'upper': 0.0},
        'cn_cr': {'lower': 0.0,  'upper': 0.0},
        'cn_ct': {'lower': 0.0,  'upper': 0.0},
        'cn_inc': {'lower': 0.0,  'upper': 0.0},
        'cn_x': {'lower': 0.0,  'upper': 0.0},
        'cn_d': {'lower': 0.0,  'upper': 0.0},
        'cn_z': {'lower': 0.0,  'upper': 0.0},
    }

    # ============================================================
    # RESTRIÇÕES DE ESTABILIDADE
    # ============================================================

    vht_min= 0.3        #Volume de cauda horizontal mínimo
    vht_max= 0.7        #Volume de cauda horizontal máximo
    cm0_min= 0          #Cm0 mínimo
    cma_max= 0          #Cma máximo
    a_trim_min= 2       #Ângulo de trimagem mínimo
    a_trim_max= 6       #Ângulo de trimagem máximo
    me_min= 0.05        #Margem estática mínima (normalizada com relação à corda da raíz)
    me_max= 0.15        #Margem estática máxima (normalizada com relação à corda da raíz)

    vvt_min= 0.02       #Volume de cauda vertical mínimo
    vvt_max=0.05        #Volume de cauda vertical máximo
    cnb_min= 0          #Cnb mínimo

    # =================================================
    # REQUISITOS PARA INDIVÍDUOS VÁLIDOS (POST PROCESSING)
    # =================================================

    a_trim_max = 5.0
    a_trim_min = -1.0
    x_cg_p_max = 0.40
    x_cg_p_min = 0.25
    me_max = 0.15
    me_min = 0.05
    ar_min = 4.8
    vht_max = 0.8
    vvt_min = 0.04
    cp_min = 5.0
    g_const_max = 2.9
    g_const_min = 2.8
    score_min = 100.00

# ========================= ========================= ========================= =========================
# RESTRICÒES PARA AERONAVE CANARD
# ========================= ========================= ========================= =========================

elif P_CONFIG == "canard":
    Nhor_DEFAULT = 3            # Asa + EH + Canard

    # =========================
    # VALORES INICIAIS
    # =========================

    DEFAULT_VALUES = {
        'w_bt': 2.0,        #envergadura
        'w_baf': 0.8,       #região de transição (% da envergadura)
        'w_cr': 0.4,        #corda da raiz
        'w_ci': 0.70,       #corda da transição (% da raiz)
        'w_ct': 0.75,       #corda da ponta (% da transição)
        'w_z': 0.20,        #altura da asa
        'w_inc': 0.0,       #incidência da asa
        'w_wo': 0.0,        #washout da asa
        'w_d': 1.0,         #diedro da asa

        'eh_b': 0.9,        #envergadura
        'eh_cr': 0.25,      #corda da raiz
        'eh_ct': 0.87,      #corda da ponta (% da raiz)
        'eh_inc': 0.0,      #incidência

        'ev_b': 0.40,       #envergadura
        'ev_ct': 0.8,       #corda da ponta (% da raiz)

        'eh_x': 0.8,        #distância do eh
        'eh_z': 0.4,        #altura do eh

        'motor_x': -0.4,    #distância do motor

        'cn_b': 1.0,          #envergadura do canard
        'cn_cr': 0.2,       #corda da raiz do canard
        'cn_ct': 0.8,      #corda da ponta do canard (% da raiz)
        'cn_inc': 3.0,      #incidência do canard
        'cn_x': -0.3,       #distância do canard (em relação à asa)
        'cn_d': 1.0,        #diedro do canard
        'cn_z': 0.2,        #altura do canard (em relação à asa)
    }

    # =========================
    # LIMITES DAS VARIÁVEIS
    # =========================

    DESIGN_VARIABLES = {
        'w_bt':     {'lower': 1.5,  'upper': 2.8},
        'w_baf':    {'lower': 0.6, 'upper': 0.9},
        'w_cr':     {'lower': 0.25, 'upper': 0.60},
        'w_ci':     {'lower': 0.60, 'upper': 0.90},
        'w_ct':     {'lower': 0.5, 'upper': 0.9},
        'w_z':      {'lower': 0.15, 'upper': 0.3},
        'w_inc':    {'lower': -2.0,  'upper': 2.0},
        'w_wo':     {'lower': -2.0,  'upper': 2.0},
        'w_d':      {'lower': 0.0,  'upper': 5.0},

        'eh_b':     {'lower': 0.4,  'upper': 1.0},
        'eh_cr':    {'lower': 0.15, 'upper': 0.35},
        'eh_ct':    {'lower': 0.6, 'upper': 1.0},
        'eh_inc':   {'lower': -3,  'upper': 3},

        'eh_x':     {'lower': 0.50, 'upper': 1.3},
        'eh_z':     {'lower': 0.18, 'upper': 0.6},

        'ev_b':     {'lower': 0.3, 'upper': 0.5},
        'ev_ct':    {'lower': 0.7, 'upper': 0.95},

        'motor_x':  {'lower': -0.8, 'upper': -0.45},

        'cn_b': {'lower': 0.5, 'upper': 1.3},
        'cn_cr': {'lower': 0.15, 'upper': 0.35},
        'cn_ct': {'lower': 0.4, 'upper': 1.0},
        'cn_inc': {'lower': 0.0, 'upper': 6.0},
        'cn_x': {'lower': -0.5, 'upper': -0.20},
        'cn_d': {'lower': -2.0, 'upper': 10.0},
        'cn_z': {'lower': 0.05, 'upper': 0.4},
    }

    # ============================================================
    # RESTRIÇÕES DE ESTABILIDADE
    # ============================================================

    vht_min= 0.3        #Volume de cauda horizontal mínimo
    vht_max= 0.7        #Volume de cauda horizontal máximo
    cm0_min= 0          #Cm0 mínimo
    cma_max= 0          #Cma máximo
    a_trim_min= 2       #Ângulo de trimagem mínimo
    a_trim_max= 6       #Ângulo de trimagem máximo
    me_min= 0.05        #Margem estática mínima (normalizada com relação à corda da raíz)
    me_max= 0.15        #Margem estática máxima (normalizada com relação à corda da raíz)

    vvt_min= 0.02       #Volume de cauda vertical mínimo
    vvt_max=0.05        #Volume de cauda vertical máximo
    cnb_min= 0          #Cnb mínimo

    # =================================================
    # REQUISITOS PARA INDIVÍDUOS VÁLIDOS (POST PROCESSING)
    # =================================================

    a_trim_max = 5.0
    a_trim_min = -1.0
    x_cg_p_max = 0.60
    x_cg_p_min = 0.10
    me_max = 0.15
    me_min = 0.05
    ar_min = 4.8
    vht_max = 0.8
    vvt_min = 0.04
    cp_min = 5.0
    g_const_max = 2.9
    g_const_min = 2.8
    score_min = 100.00

# ========================= ========================= ========================= =========================
# RESTRICÒES PARA AERONAVE ASA VOADORA
# ========================= ========================= ========================= =========================

elif P_CONFIG == "asa_voadora":
    Nhor_DEFAULT = 1            # Asa

    # =========================
    # VALORES INICIAIS
    # =========================

    DEFAULT_VALUES = {
        'w_bt': 2.0,        #envergadura
        'w_baf': 0.8,       #região de transição (% da envergadura)
        'w_cr': 0.4,        #corda da raiz
        'w_ci': 0.70,       #corda da transição (% da raiz)
        'w_ct': 0.75,       #corda da ponta (% da transição)
        'w_z': 0.20,        #altura da asa
        'w_inc': 0.0,       #incidência da asa
        'w_wo': 0.0,        #washout da asa
        'w_d': 1.0,         #diedro da asa

        'eh_b': 0.0,        #envergadura
        'eh_cr': 0.0,      #corda da raiz
        'eh_ct': 0.0,      #corda da ponta (% da raiz)
        'eh_inc': 0.0,      #incidência

        'ev_b': 0.0,       #envergadura
        'ev_ct': 0.0,       #corda da ponta (% da raiz)

        'eh_x': 0.0,        #distância do eh
        'eh_z': 0.0,        #altura do eh

        'motor_x': -0.4,    #distância do motor

        'cn_b': 0.0,          #envergadura do canard
        'cn_cr': 0.0,       #corda da raiz do canard
        'cn_ct': 0.0,      #corda da ponta do canard (% da raiz)
        'cn_inc': 0.0,      #incidência do canard
        'cn_x': 0.0,       #distância do canard (em relação à asa)
        'cn_d': 0.0,        #diedro do canard
        'cn_z': 0.0,        #altura do canard (em relação à asa)
    }

    # =========================
    # LIMITES DAS VARIÁVEIS
    # =========================

    DESIGN_VARIABLES = {
        'w_bt':     {'lower': 1.5,  'upper': 2.8},
        'w_baf':    {'lower': 0.7, 'upper': 0.9},
        'w_cr':     {'lower': 0.25, 'upper': 0.70},
        'w_ci':     {'lower': 0.60, 'upper': 0.90},
        'w_ct':     {'lower': 0.5, 'upper': 0.8},
        'w_z':      {'lower': 0.15, 'upper': 0.3},
        'w_inc':    {'lower': -2.0,  'upper': 3.0},
        'w_wo':     {'lower': -5.0,  'upper': 7.0},
        'w_d':      {'lower': 0,  'upper': 3},

        'eh_b':     {'lower': 0.0,  'upper': 0.0},
        'eh_cr':    {'lower': 0.0,  'upper': 0.0},
        'eh_ct':    {'lower': 0.0,  'upper': 0.0},
        'eh_inc':   {'lower': 0.0,  'upper': 0.0},

        'eh_x':     {'lower': 0.0,  'upper': 0.0},
        'eh_z':     {'lower': 0.0,  'upper': 0.0},

        'ev_b':     {'lower': 0.0,  'upper': 0.0},
        'ev_ct':    {'lower': 0.0,  'upper': 0.0},

        'motor_x':  {'lower': -0.6, 'upper': -0.30},

        'cn_b': {'lower': 0.0,  'upper': 0.0},
        'cn_cr': {'lower': 0.0,  'upper': 0.0},
        'cn_ct': {'lower': 0.0,  'upper': 0.0},
        'cn_inc': {'lower': 0.0,  'upper': 0.0},
        'cn_x': {'lower': 0.0,  'upper': 0.0},
        'cn_d': {'lower': 0.0,  'upper': 0.0},
        'cn_z': {'lower': 0.0,  'upper': 0.0},
    }

    # ============================================================
    # RESTRIÇÕES DE ESTABILIDADE
    # ============================================================

    vht_min= 0.3        #Volume de cauda horizontal mínimo
    vht_max= 0.6        #Volume de cauda horizontal máximo
    cm0_min= 0          #Cm0 mínimo
    cma_max= 0          #Cma máximo
    a_trim_min= 2       #Ângulo de trimagem mínimo
    a_trim_max= 6       #Ângulo de trimagem máximo
    me_min= 0.05        #Margem estática mínima (normalizada com relação à corda da raíz)
    me_max= 0.15        #Margem estática máxima (normalizada com relação à corda da raíz)

    vvt_min= 0.02       #Volume de cauda vertical mínimo
    vvt_max=0.05        #Volume de cauda vertical máximo
    cnb_min= 0          #Cnb mínimo

    # =================================================
    # REQUISITOS PARA INDIVÍDUOS VÁLIDOS (POST PROCESSING)
    # =================================================

    a_trim_max = 5.0
    a_trim_min = -1.0
    x_cg_p_max = 0.40
    x_cg_p_min = 0.25
    me_max = 0.15
    me_min = 0.05
    ar_min = 4.8
    vht_max = 0.8
    vvt_min = 0.04
    cp_min = 5.0
    g_const_max = 2.9
    g_const_min = 2.8
    score_min = 125.00

# ============================================================

else: 
    print("⚠️ Configuração não definida.")