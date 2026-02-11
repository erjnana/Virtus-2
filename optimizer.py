
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

# =========================
# DRIVER DE OTIMIZAÇÃO
# =========================

# Driver baseado em Algoritmo Genético Diferencial
prob.driver = om.DifferentialEvolutionDriver()

# Mostra no log as variáveis de design a cada geração
prob.driver.options['debug_print'] = ['desvars']

# Tamanho da população
prob.driver.options['pop_size'] = 40

# Parâmetros de penalização das restrições
prob.driver.options['penalty_parameter'] = 20.0
prob.driver.options['penalty_exponent'] = 1.0

# Execução paralela (MPI)
prob.driver.options['run_parallel'] = False

# Número máximo de gerações
prob.driver.options['max_gen'] = 999

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

# Aqui o MDO fica sabendo:
# - quais variáveis ele pode mexer
# - quais os limites físicos de cada uma
# Os limites vêm TODOS do variables.py
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

# Ângulo mínimo de stall
prob.model.add_constraint(
    'individual_scorer.stall_constraint',
    lower=0.0
)

# Garante que o Canard estole antes da asa (Segurança Canard)
# Se stall_safety_margin > 0, o canard atinge o Cl_max dele primeiro.
prob.model.add_constraint(
    'individual_scorer.stall_safety_margin',
    lower=0.02 # Margem de segurança de 2% de Cl
)

# Otimização de Sustentação: Garante que a asa não opere acima do Cl_max real
# Isso substitui ou complementa o stall_constraint antigo
prob.model.add_constraint(
    'individual_scorer.cl_max_3d_wing',
    upper=1.5 # Substitua pelo Cl_max do seu perfil de asa
)

# =========================
# SETUP E EXECUÇÃO
# =========================

# Prepara o modelo (checagem de conexões)
print("\n--- INICIANDO SETUP ---")
prob.setup()

# Roda o MDO com log em arquivo txt
print("\n--- SETUP CONCLUÍDO. INICIANDO OTIMIZAÇÃO ---\n")
original_stdout = sys.stdout
with open(log_path_txt, 'w', encoding='utf-8') as f:
    sys.stdout = f
    prob.run_driver()
sys.stdout = original_stdout