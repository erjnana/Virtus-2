"""
Variáveis de design e ajustes para a otimizaçao do MDO
Aqui estão todos os dados que são necessários serem ajustados antes de rodar o MDO

"""

# =========================
# IDENTIDADE DO PROJETO
# =========================

# Nome do projeto usado em logs, resultados e relatórios
PROJECT_NAME = "banana"

# =========================
# PONTUAÇÃO ESTIMADA
# =========================

NR_DEFAULT = 110.38         # Nota de relatório estimada
PEE_FACTOR = 25             # Fator de pontuação eficiência estrutural
Nhor_DEFAULT = 2            # Número de superfícies sustentadoras
APRESENTACAO = 30.58        # Nota da apresentação
VIDEOVOO = 30.0             # Nota do vídeo de voo

# ============================================================
# RESTRIÇÕES AERODINÂMICAS GLOBAIS
# ============================================================

# Ângulo mínimo de estol do AVIÃO COMPLETO [graus]
ALPHA_STALL_MIN_DEG = 13.0

# =========================
# INPUTS DO INDIVÍDUO
# =========================

INDIVIDUAL_INPUTS = [
    'w_bt', 'w_baf', 'w_cr', 'w_ci', 'w_ct',
    'w_z', 'w_inc', 'w_wo', 'w_d',
    'eh_b', 'eh_cr', 'eh_ct', 'eh_inc',
    'ev_b', 'ev_ct',
    'eh_x', 'eh_z',
    'motor_x'
]

# =========================
# VALORES INICIAIS
# =========================

DEFAULT_VALUES = {
    'w_bt': 2.7,        #envergadura
    'w_baf': 0.5,       #região de transição
    'w_cr': 0.4,        #corda da raiz
    'w_ci': 0.90,       #corda da transição
    'w_ct': 0.87,       #corda da ponta
    'w_z': 0.20,        #altura da asa
    'w_inc': 0.0,       #incidência da asa
    'w_wo': 0.0,        #washout da asa
    'w_d': 1.4,         #diedro da asa

    'eh_b': 0.9,        #envergadura
    'eh_cr': 0.25,      #corda da raiz
    'eh_ct': 0.87,      #corda da ponta
    'eh_inc': 0.0,      #incidência

    'ev_b': 0.40,       #envergadura
    'ev_ct': 0.8,       #corda da ponta

    'eh_x': 1.2,        #distância do eh
    'eh_z': 0.4,        #altura do eh

    'motor_x': -0.2,    #distância do motor
}

# =========================
# LIMITES DAS VARIÁVEIS
# =========================

DESIGN_VARIABLES = {
    'w_bt':     {'lower': 0.1,  'upper': 4.0},
    'w_baf':    {'lower': 0.01, 'upper': 0.99},
    'w_cr':     {'lower': 0.01, 'upper': 1.00},
    'w_ci':     {'lower': 0.01, 'upper': 0.99},
    'w_ct':     {'lower': 0.01, 'upper': 0.99},
    'w_z':      {'lower': 0.01, 'upper': 1.0},
    'w_inc':    {'lower': -10,  'upper': 15},
    'w_wo':     {'lower': -10,  'upper': 15},
    'w_d':      {'lower': 0.0,  'upper': 10.0},

    'eh_b':     {'lower': 0.1,  'upper': 4.0},
    'eh_cr':    {'lower': 0.01, 'upper': 1.0},
    'eh_ct':    {'lower': 0.01, 'upper': 0.99},
    'eh_inc':   {'lower': -10,  'upper': 15},

    'eh_x':     {'lower': 0.01, 'upper': 5.0},
    'eh_z':     {'lower': 0.01, 'upper': 3.0},

    'ev_b':     {'lower': 0.01, 'upper': 0.60},
    'ev_ct':    {'lower': 0.01, 'upper': 0.99},

    'motor_x':  {'lower': -0.4, 'upper': -0.15},
}