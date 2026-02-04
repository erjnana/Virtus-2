"""
Variáveis de design e ajustes para a otimizaçao do MDO
Aqui estão todos os dados que são necessários serem ajustados antes de rodar o MDO

"""

# =========================
# IDENTIDADE DO PROJETO
# =========================

PROJECT_NAME = "banana"     # Nome do projeto usado em logs, resultados e relatórios

# =========================
# PONTUAÇÃO ESTIMADA
# =========================

NR_DEFAULT = 110.38         # Nota de relatório estimada
PEE_FACTOR = 25             # Fator de pontuação eficiência estrutural
Nhor_DEFAULT = 2            # Número de superfícies sustentadoras
APRESENTACAO = 30.58        # Nota da apresentação
VIDEOVOO = 30.0             # Nota do vídeo de voo

# ============================================================
# RESTRIÇÕES DE POTENCIA
# ============================================================

pot = 600.0  # Potência máxima do motor em W

# ============================================================
# PERFIS DO AVIÃO
# ============================================================

root_af='random'            # Perfil da raiz da asa (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
tip_af='random'             # Perfil da ponta da asa (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
eh_af='NACA0012'            # Perfil do EH (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)
ev_af ='NACA0012'           # Perfil do EV (insira o nome da pasta do perfil para manter fixo ou "random" para otimizar)

# ============================================================
# RESTRIÇÕES AERODINÂMICAS GLOBAIS
# ============================================================

ALPHA_STALL_MIN_DEG = 13.0      # Ângulo mínimo de estol do AVIÃO COMPLETO [graus]

# =========================
# INPUTS DO INDIVÍDUO
# =========================

INDIVIDUAL_INPUTS = [
    'w_bt',
    'w_baf', 
    'w_cr', 
    'w_ci', 
    'w_ct',
    'w_z', 
    'w_inc', 
    'w_wo', 
    'w_d',
    'eh_b', 
    'eh_cr', 
    'eh_ct', 
    'eh_inc',
    'ev_b', 
    'ev_ct',
    'eh_x', 
    'eh_z',
    'motor_x'
]

# =========================
# VALORES INICIAIS
# =========================

DEFAULT_VALUES = {
    'w_bt': 3.5,        #envergadura
    'w_baf': 0.8,       #região de transição
    'w_cr': 0.4,        #corda da raiz
    'w_ci': 0.70,       #corda da transição
    'w_ct': 0.75,       #corda da ponta
    'w_z': 0.20,        #altura da asa
    'w_inc': 0.0,       #incidência da asa
    'w_wo': 0.0,        #washout da asa
    'w_d': 1.0,         #diedro da asa

    'eh_b': 0.9,        #envergadura
    'eh_cr': 0.25,      #corda da raiz
    'eh_ct': 0.87,      #corda da ponta
    'eh_inc': 0.0,      #incidência

    'ev_b': 0.40,       #envergadura
    'ev_ct': 0.8,       #corda da ponta

    'eh_x': 0.8,        #distância do eh
    'eh_z': 0.4,        #altura do eh

    'motor_x': -0.2,    #distância do motor
}

# =========================
# LIMITES DAS VARIÁVEIS
# =========================

DESIGN_VARIABLES = {
    'w_bt':     {'lower': 3.0,  'upper': 4.0},
    'w_baf':    {'lower': 0.7, 'upper': 0.9},
    'w_cr':     {'lower': 0.25, 'upper': 0.70},
    'w_ci':     {'lower': 0.60, 'upper': 0.85},
    'w_ct':     {'lower': 0.5, 'upper': 0.8},
    'w_z':      {'lower': 0.01, 'upper': 0.5},
    'w_inc':    {'lower': -5,  'upper': 8},
    'w_wo':     {'lower': -5,  'upper': 5},
    'w_d':      {'lower': -2,  'upper': 3},

    'eh_b':     {'lower': 0.8,  'upper': 1.3},
    'eh_cr':    {'lower': 0.15, 'upper': 0.40},
    'eh_ct':    {'lower': 0.7, 'upper': 0.95},
    'eh_inc':   {'lower': -3,  'upper': 3},

    'eh_x':     {'lower': 0.01, 'upper': 1.0},
    'eh_z':     {'lower': 0.01, 'upper': 1.0},

    'ev_b':     {'lower': 0.3, 'upper': 0.60},
    'ev_ct':    {'lower': 0.7, 'upper': 0.95},

    'motor_x':  {'lower': -0.4, 'upper': -0.15},
}