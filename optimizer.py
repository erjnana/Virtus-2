
import openmdao.api as om
from prototype import *
from simulator import *
from individual import *
from performance import *
import os
import sys
from datetime import datetime

from variables import *
from airfoil_loader import LISTA_ASA, LISTA_EH

"""
Programa principal do MDO.

Responsabilidades deste arquivo:
- Criar o problema OpenMDAO
- Definir o driver de otimização
- Registrar variáveis, objetivo e restrições
- Executar o processo de otimização

"""

# =========================
# CRIAÇÃO DO PROBLEMA
# =========================

prob = om.Problem()

# =========================
# SUBSISTEMA PRINCIPAL
# =========================

prob.model.add_subsystem(
    'individual_scorer',
    Individual(),
    promotes_inputs=INDIVIDUAL_INPUTS
)

# =========================
# VALORES INICIAIS
# =========================

# Define os valores iniciais de cada variável de design
# Esses valores são o "primeiro indivíduo" da população
for var_name, default_value in DEFAULT_VALUES.items():
    prob.model.set_input_defaults(var_name, default_value)

# Define os valores dos perfis (FORA do loop)
prob.model.set_input_defaults('individual_scorer.idx_asa_root', 0.0)
prob.model.set_input_defaults('individual_scorer.idx_asa_tip', 0.0)
prob.model.set_input_defaults('individual_scorer.idx_eh', 0.0)
prob.model.set_input_defaults('individual_scorer.idx_ev', 0.0)
prob.model.set_input_defaults('individual_scorer.idx_cn', 0.0)

# =========================
# DRIVER DE OTIMIZAÇÃO
# =========================

# Driver baseado em Algoritmo Genético Diferencial
prob.driver = om.DifferentialEvolutionDriver()

# Mostra no log as variáveis de design a cada geração
prob.driver.options['debug_print'] = ['desvars']

# Tamanho da população
prob.driver.options['pop_size'] = OPTIMIZER_POP_SIZE

# Parâmetros de penalização das restrições
prob.driver.options['penalty_parameter'] = OPTIMIZER_PENALTY_PARAM
prob.driver.options['penalty_exponent'] = OPTIMIZER_PENALTY_EXP

# Execução paralela (MPI)
prob.driver.options['run_parallel'] = False

# Número máximo de gerações
prob.driver.options['max_gen'] = OPTIMIZER_MAX_GEN

# =========================
# RECORDER (LOG DA OTIMIZAÇÃO)
# =========================

# Garante que a pasta de logs exista
log_dir = "log/evolutions"
os.makedirs(log_dir, exist_ok=True)

# Timestamp no formato desejado: AAAA_MM_DD_HHMM
start_time = datetime.now().strftime("%Y_%m_%d_%H%M")

# nomedoprojeto_AAAA_MM_DD_HHMM.db
log_filename = f"{PROJECT_NAME}_{start_time}.db"

log_path = os.path.join(log_dir, log_filename)

prob.driver.add_recorder(
    om.SqliteRecorder(log_path)
)

# Define exatamente o que será salvo
prob.driver.recording_options['includes'] = ['*']
prob.driver.recording_options['record_objectives'] = True
prob.driver.recording_options['record_constraints'] = True
prob.driver.recording_options['record_desvars'] = True

# Arquivo de log em texto
log_filename_txt = f"{PROJECT_NAME}_{start_time}.txt"
log_path_txt = os.path.join(log_dir, log_filename_txt)

# =========================
# VARIÁVEIS DE DESIGN
# =========================

if root_af.lower() == "random":
    prob.model.add_design_var('individual_scorer.idx_asa_root', lower=0, upper=len(LISTA_ASA)-1)

if tip_af.lower() == "random":
    prob.model.add_design_var('individual_scorer.idx_asa_tip', lower=0, upper=len(LISTA_ASA)-1)

if eh_af.lower() == "random":
    prob.model.add_design_var('individual_scorer.idx_eh', lower=0, upper=len(LISTA_EH)-1)

if ev_af.lower() == "random":
    prob.model.add_design_var('individual_scorer.idx_ev', lower=0, upper=len(LISTA_EV)-1)

if cn_af.lower() == "random":
    prob.model.add_design_var('individual_scorer.idx_cn', lower=0, upper=len(LISTA_EV)-1)

for var_name, bounds in DESIGN_VARIABLES.items():
    prob.model.add_design_var(
        var_name,
        lower=bounds['lower'],
        upper=bounds['upper']
    )

# =========================
# FUNÇÃO OBJETIVO
# =========================

# O objetivo é maximizar o score do indivíduo
# OpenMDAO sempre minimiza, então usamos scaler negativo
prob.model.add_objective(
    'individual_scorer.score',
    scaler=-1.0
)

# =========================
# RESTRIÇÕES
# =========================

# Relação de aspecto mínima da asa
prob.model.add_constraint(
    'individual_scorer.ar',
    lower=5.0
)

# Relação de aspecto máxima do estabilizador horizontal
prob.model.add_constraint(
    'individual_scorer.eh_ar',
    upper=4.8
)

# Volume de cauda horizontal
prob.model.add_constraint(
    'individual_scorer.vht',
    lower=vht_min,
    upper=vht_max
)

# Volume de cauda vertical
prob.model.add_constraint(
    'individual_scorer.vvt',
    lower=vvt_min,
    upper=vvt_max
)

# Ângulo de trimagem
# scaler = 0 evita penalização exagerada
prob.model.add_constraint(
    'individual_scorer.a_trim',
    lower=a_trim_min,
    upper=a_trim_max,
    scaler=0.0
)

# Margem estática
prob.model.add_constraint(
    'individual_scorer.me',
    lower=me_min,
    upper=me_max
)

# Centro de gravidade não pode estar muito baixo
prob.model.add_constraint(
    'individual_scorer.low_cg',
    lower=-0.03
)

# Distância mínima da empenagem horizontal ao eixo
prob.model.add_constraint(
    'individual_scorer.eh_z_const',
    lower=0.05
)

# Posição do CG percentual da corda média
prob.model.add_constraint(
    'individual_scorer.x_cg_p',
    lower=0.25,
    upper=0.34,
    scaler=0.0
)

# =========================
# SETUP E EXECUÇÃO
# =========================

# Abre o arquivo de log e redireciona TODA a saída para ele
original_stdout = sys.stdout
log_file = open(log_path_txt, 'w', encoding='utf-8')
sys.stdout = log_file

# Prepara o modelo (checagem de conexões)
print("\n--- INICIANDO SETUP ---")
prob.setup()


print("\n\n===============================================================================================================================================================")
print("\n                                             Simulação Realizada em:", datetime.now().strftime("%d/%m/%Y às %H:%M"))
print("\n===============================================================================================================================================================")
print(r"""                                        ____   ____.__         __                 ________  
                                        \   \ /   /|__|_______/  |_ __ __  ______ \_____  \ 
                                         \   Y   / |  \_  __ \   __\  |  \/  ___/  /  ____/ 
                                          \     /  |  ||  | \/|  | |  |  /\___ \  /       \ 
                                           \___/   |__||__|   |__| |____//______/ \________|""",
      "\n                                             Bem-vindo ao MDO Virtus da Minerva Aerodesign!", 
      "\n                                                        Ver. 2.0 de 22/02/2026", 
      "\n                                            Autores: Ana Luiza S. Duarte e Lucas A. da Rosa")
print("\n===============================================================================================================================================================")
print("\n                                                ==== Configurações de Indivíduo ====",
      "\n\n==== Configuração de projeto:", P_CONFIG,
      "\n\n=== Perfil dos componentes ====\n",
      "\nPerfil da raiz da asa:", root_af,
      "\nPerfil da ponta da asa:", tip_af,
      "\nPerfil do EH:", eh_af,
      "\nPerfil do EV:", ev_af,
      "\nPerfil do canard:", cn_af,
      "\n\n=== Valores iniciais dos parâmetros ====\n",
      "\n==== Parâmetros da asa:",
      "\nEnvergadura (w_bt):", DEFAULT_VALUES['w_bt'], "m",
        "\nRegião de transição (w_baf):", DEFAULT_VALUES['w_baf']*100, "% da envergadura",
        "\nCorda da raiz (w_cr):", DEFAULT_VALUES['w_cr'], "m",
        "\nCorda da transição (w_ci):", DEFAULT_VALUES['w_ci']*100, "% da corda da raiz",
        "\nCorda da ponta (w_ct):", DEFAULT_VALUES['w_ct'], "m",
        "\nPosição z do centro de massa (w_z):", DEFAULT_VALUES['w_z'], "m",
        "\nÂngulo de incidência (w_inc):", DEFAULT_VALUES['w_inc'], "°",
        "\nPosição x do motor (motor_x):", DEFAULT_VALUES['motor_x'], "m",
        "\n\n==== Parâmetros da empenagem horizontal:",
        "\nEnvergadura (eh_b):", DEFAULT_VALUES['eh_b'], "m",
        "\nCorda na raiz (eh_cr):", DEFAULT_VALUES['eh_cr'], "m",
        "\nCorda na ponta (eh_ct):", DEFAULT_VALUES['eh_ct'], "m",
        "\nÂngulo de incidência (eh_inc):", DEFAULT_VALUES['eh_inc'], "°",
        "\nPosição x do EH (eh_x):", DEFAULT_VALUES['eh_x'], "m",
        "\nPosição z do EH (eh_z):", DEFAULT_VALUES['eh_z'], "m",
        "\n\n==== Parâmetros da empenagem vertical:",
        "\nEnvergadura (ev_b):", DEFAULT_VALUES['ev_b'], "m",
        "\nCorda (ev_ct):", DEFAULT_VALUES['ev_ct'], "m",
        "\n\n==== Parâmetros do canard:",
        "\nEnvergadura (cn_b):", DEFAULT_VALUES['cn_b'], "m",
        "\nCorda na raiz (cn_cr):", DEFAULT_VALUES['cn_cr'], "m",
        "\nCorda na ponta (cn_ct):", DEFAULT_VALUES['cn_ct'], "m",
        "\nÂngulo de incidência (cn_inc):", DEFAULT_VALUES['cn_inc'], "°",
        "\nPosição x do canard (cn_x):", DEFAULT_VALUES['cn_x'], "m",
        "\nPosição z do canard (cn_z):", DEFAULT_VALUES['cn_z'], "m",
)
print ("\n\n=== Limites Mínimos e Máximos de Design ====\n",
       "\n==== Parâmetros da asa:",
        "\nEnvergadura (w_bt): mínimo", DESIGN_VARIABLES['w_bt']['lower'], "m - máximo", DESIGN_VARIABLES['w_bt']['upper'], "m",
        "\nRegião de transição (w_baf): mínimo", DESIGN_VARIABLES['w_baf']['lower']*100, "% - máximo", DESIGN_VARIABLES['w_baf']['upper']*100, "% da envergadura",
        "\nCorda da raiz (w_cr): mínimo", DESIGN_VARIABLES['w_cr']['lower'], "m - máximo", DESIGN_VARIABLES['w_cr']['upper'], "m",
        "\nCorda da transição (w_ci): mínimo", DESIGN_VARIABLES['w_ci']['lower']*100, "% - máximo", DESIGN_VARIABLES['w_ci']['upper']*100, "% da corda da raiz",
        "\nCorda da ponta (w_ct): mínimo", DESIGN_VARIABLES['w_ct']['lower'], "m - máximo", DESIGN_VARIABLES['w_ct']['upper'], "m",
        "\nPosição z do centro de massa (w_z): mínimo", DESIGN_VARIABLES['w_z']['lower'], "m - máximo", DESIGN_VARIABLES['w_z']['upper'], "m",
        "\nÂngulo de incidência (w_inc): mínimo", DESIGN_VARIABLES['w_inc']['lower'], "° - máximo", DESIGN_VARIABLES['w_inc']['upper'], "°",
        "\nPosição x do motor (motor_x): mínimo", DESIGN_VARIABLES['motor_x']['lower'], "m - máximo", DESIGN_VARIABLES['motor_x']['upper'], "m",
        "\n\n==== Parâmetros da empenagem horizontal:", 
        "\nEnvergadura (eh_b): mínimo", DESIGN_VARIABLES['eh_b']['lower'], "m - máximo", DESIGN_VARIABLES['eh_b']['upper'], "m", 
        "\nCorda na raiz (eh_cr): mínimo", DESIGN_VARIABLES['eh_cr']['lower'], "m - máximo", DESIGN_VARIABLES['eh_cr']['upper'], "m",
        "\nCorda na ponta (eh_ct): mínimo", DESIGN_VARIABLES['eh_ct']['lower'], "m - máximo", DESIGN_VARIABLES['eh_ct']['upper'], "m",
        "\nÂngulo de incidência (eh_inc): mínimo", DESIGN_VARIABLES['eh_inc']['lower'], "° - máximo", DESIGN_VARIABLES['eh_inc']['upper'], "°",
        "\nPosição x do EH (eh_x): mínimo", DESIGN_VARIABLES['eh_x']['lower'], "m - máximo", DESIGN_VARIABLES['eh_x']['upper'], "m",
        "\nPosição z do EH (eh_z): mínimo", DESIGN_VARIABLES['eh_z']['lower'], "m - máximo", DESIGN_VARIABLES['eh_z']['upper'], "m",
        "\n\n==== Parâmetros da empenagem vertical:",
        "\nEnvergadura (ev_b): mínimo", DESIGN_VARIABLES['ev_b']['lower'], "m - máximo", DESIGN_VARIABLES['ev_b']['upper'], "m",
        "\nCorda (ev_ct): mínimo", DESIGN_VARIABLES['ev_ct']['lower'], "m - máximo", DESIGN_VARIABLES['ev_ct']['upper'], "m",
        "\n\n==== Parâmetros do canard:",
        "\nEnvergadura (cn_b): mínimo", DESIGN_VARIABLES['cn_b']['lower'], "m - máximo", DESIGN_VARIABLES['cn_b']['upper'], "m",
        "\nCorda na raiz (cn_cr): mínimo", DESIGN_VARIABLES['cn_cr']['lower'], "m - máximo", DESIGN_VARIABLES['cn_cr']['upper'], "m",
        "\nCorda na ponta (cn_ct): mínimo", DESIGN_VARIABLES['cn_ct']['lower'], "m - máximo", DESIGN_VARIABLES['cn_ct']['upper'], "m",
        "\nÂngulo de incidência (cn_inc): mínimo", DESIGN_VARIABLES['cn_inc']['lower'], "° - máximo", DESIGN_VARIABLES['cn_inc']['upper'], "°",
        "\nPosição x do canard (cn_x): mínimo", DESIGN_VARIABLES['cn_x']['lower'], "m - máximo", DESIGN_VARIABLES['cn_x']['upper'], "m",
        "\nPosição z do canard (cn_z): mínimo", DESIGN_VARIABLES['cn_z']['lower'], "m - máximo", DESIGN_VARIABLES['cn_z']['upper'], "m",
       )

print("\n\n=== Restrições de Estabilidade ====\n",
      "\n==== Estabilidade longitudinal:",
      "\nVolume de cauda horizontal (vht): mínimo", vht_min, "- máximo", vht_max,
      "\nCm0: mínimo", cm0_min,
      "\nCma: máximo", cma_max,
      "\nÂngulo de trim (a_trim): mínimo", a_trim_min, "° - máximo", a_trim_max, "°",
      "\nMargem estática (me): mínimo", me_min, "- máximo", me_max,
      "\n\n==== Estabilidade direcional:",
      "\nVolume de cauda vertical (vvt): mínimo", vvt_min, "- máximo", vvt_max,
      "\nCnb: mínimo", cnb_min
      )

print("\n===============================================================================================================================================================")
print("\n                                                ==== Configurações do Otimizador ====",
        "\n\n=== Configurações de otimização:",
        "\nTamanho da população:", OPTIMIZER_POP_SIZE,
        "\nNúmero máximo de gerações:", OPTIMIZER_MAX_GEN,
        "\nParâmetro de penalização das restrições:", OPTIMIZER_PENALTY_PARAM,
        "\nExpoente de penalização das restrições:", OPTIMIZER_PENALTY_EXP,
        "\nDriver:", OPTIMIZER_DRIVER
        )
print("\n===============================================================================================================================================================")

# Roda o MDO com log em arquivo txt
print("\n--- SETUP CONCLUÍDO. INICIANDO OTIMIZAÇÃO ---\n")
prob.run_driver()

# Restaura stdout e fecha o arquivo de log
sys.stdout = original_stdout
log_file.close()