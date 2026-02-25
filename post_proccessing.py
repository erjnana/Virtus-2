
import openmdao.api as om
import os
import sys
from datetime import datetime
from stability import *
from variables import *

# 1. Definição do path do input
db_path = './log/evolutions/banana_canard_2026_02_24_1831.db' #INSIRA NOME DO ARQUIVO A SER ANALISADO AQUI

# 2. Configuração do Nome do Log: post_(nome_do_arquivo).txt
db_filename = os.path.basename(db_path)
partes_do_nome = db_filename.split('_')
P_CONFIG = partes_do_nome[1]

if P_CONFIG == "canard":
    # (O Python buscará os valores de vht_min, etc., que já estão no variables.py)
    print(f">>> Configuração detectada: CANARD")
elif P_CONFIG == "convencional":
    print(f">>> Configuração detectada: CONVENCIONAL")
elif P_CONFIG == "asa_voadora":
    print(f">>> Configuração detectada: ASA VOADORA")

raw_name = os.path.splitext(db_filename)[0] # Remove o '.db'
log_name = f"post_{raw_name}.txt"

log_dir = './log/post_processing/'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_path = os.path.join(log_dir, log_name)

# Classe para duplicar o output (Terminal + Arquivo)
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

# Ativa o redirecionamento
sys.stdout = Logger(log_path)

print("\n\n===============================================================================================================================================================")
print("\n                                        Processamento final Realizado em:", datetime.now().strftime("%d/%m/%Y às %H:%M"))
print("                             Arquivo de otimizacão:", db_path)
print("\n===============================================================================================================================================================")
print(r"""                                        ____   ____.__         __                 ________  
                                        \   \ /   /|__|_______/  |_ __ __  ______ \_____  \ 
                                         \   Y   / |  \_  __ \   __\  |  \/  ___/  /  ____/ 
                                          \     /  |  ||  | \/|  | |  |  /\___ \  /       \ 
                                           \___/   |__||__|   |__| |____//______/ \________|""",
      "\n                                             Bem-vindo ao MDO Virtus da Minerva Aerodesign!", 
      "\n                                                        Ver. 2.0 de 24/02/2026", 
      "\n                                            Autores: Lucas A. da Rosa e Ana Luiza S. Duarte")
print("\n===============================================================================================================================================================")
print("\n                                                ==== Critérios de Validacão de Indivíduo ====")
print(" Ângulo de Trimagem Máximo =", a_trim_max)
print(" Ângulo de Trimagem Mínimo =", a_trim_min)
print(" Posicão horizontal máxima do GC =", x_cg_p_max) 
print(" Posicão horizontal mínima do GC =", x_cg_p_min) 
print(" Margem Estática Máxima =", me_max)
print(" Margem Estática Mínima =", me_min)
print(" AR Mínimo =", ar_min)
print(" Volume horizontal de cauda máximo =", vht_max)
print(" Volume vertical de cauda mínimo =", vvt_min)
print(" Carga Paga Mínima =", cp_min)
print(" Pontuacão de Voo Mínima =", score_min)
print("===============================================================================================================================================================")

# --- Processamento dos Casos ---
np = 1
proc_case = []

# Lógica de leitura (ajustada para usar a variável db_path)
if (np > 1):
    for p in range(np):
        crp = om.CaseReader(db_path + str(p))
        proc_case.append(crp.get_cases())
else:
    crp = om.CaseReader(db_path)
    proc_case.append(crp.get_cases())

for proc_n in range(len(proc_case)):
    # Filtro de população (últimos 19900)
    proc_case[proc_n] = proc_case[proc_n][-19900:]

    for case in proc_case[proc_n]:
        # 'out' busca os valores do case, 'variables' busca os limites do variables.py
        out = case.outputs

        if (
            (out['individual_scorer.a_trim'] <= a_trim_max)
            and (out['individual_scorer.a_trim'] >= a_trim_min)
            and (out['individual_scorer.x_cg_p'] <= x_cg_p_max) 
            and (out['individual_scorer.x_cg_p'] >= x_cg_p_min) 
            and (out['individual_scorer.me'] <= me_max)
            and (out['individual_scorer.me'] >= me_min)
            and (out['individual_scorer.ar'] >= ar_min)
            and (out['individual_scorer.vht'] <= vht_max)
            and (out['individual_scorer.vvt'] >= vvt_min)
            and (out['individual_scorer.cp'] >= cp_min)
            #and (out['individual_scorer.a_stall'] >= a_stall_min)
            #and (out['individual_scorer.g_const'] <= g_const_max)
            #and (out['individual_scorer.g_const'] >= g_const_min)
            and (out['individual_scorer.score'] >= score_min)
            
        ):

            print('-------------- PROTOTIPO:', case.name[-4:]+'-'+str(proc_n)+' --------------\n')
            print(
                ' Variaveis de design: (',
                  'cn_b=' ,float(case.outputs['cn_b'][0]),','
                  'cn_cr=' ,float(case.outputs['cn_cr'][0]),','
                  'cn_ct=' ,float(case.outputs['cn_ct'][0]),','
                  'cn_inc=' ,float(case.outputs['cn_inc'][0]),','
                  'cn_x=' ,float(case.outputs['cn_x'][0]),','
                  'cn_d=' ,float(case.outputs['cn_d'][0]),','
                  'cn_z=' ,float(case.outputs['cn_z'][0]),','
                  ' w_bt= ',float(case.outputs['w_bt'][0]),','
                  ' w_baf= ',float(case.outputs['w_baf'][0]),','
                  ' w_cr= ',float(case.outputs['w_cr'][0]),','
                  ' w_ci= ',float(case.outputs['w_ci'][0]),','
                  ' w_ct= ',float(case.outputs['w_ct'][0]),','
                  ' w_z= ',float(case.outputs['w_z'][0]),','
                  ' w_inc= ',float(case.outputs['w_inc'][0]),','
                  ' w_wo= ',float(case.outputs['w_wo'][0]),','
                  ' w_d= ',float(case.outputs['w_d'][0]),','
                  ' eh_b= ',float(case.outputs['eh_b'][0]),','
                  ' eh_cr= ',float(case.outputs['eh_cr'][0]),','
                  ' eh_ct= ',float(case.outputs['eh_ct'][0]),','
                  ' eh_inc= ',float(case.outputs['eh_inc'][0]),','
                  ' ev_b= ',float(case.outputs['ev_b'][0]),','
                  ' ev_ct= ',float(case.outputs['ev_ct'][0]),','
                  ' eh_x= ',float(case.outputs['eh_x'][0]),','
                  ' eh_z= ',float(case.outputs['eh_z'][0]),','
                  ' motor_x= ',float(case.outputs['motor_x'][0]),','
                  #'pot= ',float(case.outputs['pot']),','
                  ')'
                  , sep=''
                  )
            
            print(
                '\n Objetivos\n',
                  '     Pontuação da competição =', float(case.outputs['individual_scorer.score'][0])
                  )
            
            print(
                '\n Restricoes\n',
                  #'     Altura=', float(case.outputs['individual_scorer.h_const']),'\n',
                  '     Gap do EH=', float(case.outputs['individual_scorer.eh_z_const'][0]),'\n',
                  '     Gap do CG=', float(case.outputs['individual_scorer.low_cg'][0]),'\n',
                  '     VHT=', float(case.outputs['individual_scorer.vht'][0]),'\n',
                  '     VVT=', float(case.outputs['individual_scorer.vvt'][0]),'\n',
                  '     AR=', float(case.outputs['individual_scorer.ar'][0]),'\n',
                  '     AR do EH=', float(case.outputs['individual_scorer.eh_ar'][0]),'\n',
                  #'     Cm0=', float(case.outputs['individual_scorer.cm0']),'\n',
                  '     CG em=', float(case.outputs['individual_scorer.x_cg_p'][0]),'\n',
                  '     Angulo de trimagem=', float(case.outputs['individual_scorer.a_trim'][0]),'\n',
                  '     Margem Estatica=', float(case.outputs['individual_scorer.me'][0]),'\n'
                  #'     Ângulo de Stall', float(case.outputs['individual_scorer.a_stall']),'\n'
                  )

# Finalização limpa
sys.stdout.log.close()
sys.stdout = sys.stdout.terminal 

print(f"\n>>> Log salvo em: {log_path}")