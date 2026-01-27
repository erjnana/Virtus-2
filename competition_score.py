#ESTÁ STANDALONE, PRECISA CONECTAR AO SIMULATOR

"""
Calcula a pontuação da competição de voo automaticamente a partir do Simulator/Prototype.
"""
from variables import NR_DEFAULT, PEE_FACTOR, Nhor_DEFAULT, APRESENTACAO, VIDEOVOO

# =======================
# PARÂMETROS FIXOS DA COMPETIÇÃO
# =======================

FPV = 1.1
pv = 2.0
cp_max = 10.495
MAX_WEIGHT = 20

# =======================
# FUNÇÃO DE PONTUAÇÃO
# =======================
def compute_competition_score(
        #simulator, 
        N_horizontal=Nhor_DEFAULT, 
        NR=NR_DEFAULT):
    """
    Calcula a pontuação da aeronave baseado nos resultados do Simulator.
    Mostra PVOO para cargas pagas que gerem EE ≥ 1.5 até a carga máxima possível respeitando o limite de 20 kg.
    """

    #pv = simulator.prototype.pv
    #cp_max = simulator.cp  # carga paga máxima teórica

    if pv <= 0:
        raise ValueError("Peso vazio inválido (<=0). Não é possível calcular EE.")

    # Ajuste de carga máxima para não ultrapassar o limite de 20kg
    cp_allowed = min(cp_max, MAX_WEIGHT - pv)
    total_weight_max = pv + cp_allowed

    if pv + cp_max > MAX_WEIGHT:
        print(f"⚠️ Aviso: peso total com carga máxima ({pv + cp_max:.2f} kg) excede o limite de {MAX_WEIGHT} kg.")
        print(f"    ⚠️ Calculando PVOO somente até {cp_allowed:.2f} kg de carga paga (peso total = {total_weight_max:.2f} kg).")

    # Determina carga mínima que gera EE = 1.5
    cp_min = max(0.0, 1.5 * pv)
    if cp_min > cp_allowed:
        print(f"⚠️ Atenção: não é possível atingir EE=1.5 sem ultrapassar 20kg. Usando carga mínima = 0.")
        cp_min = 0.0

    # Número de superfícies horizontais
    if N_horizontal is None:
        N_horizontal = 1
    horizontal_factor = 0.163 * N_horizontal**2 - 0.663 * N_horizontal + 1.6739

    FPR = min(1.0, 0.5 + 0.75 * NR / 185)
    FPV_factor = FPV

    print("📊 Intervalo de PVOO para diferentes cargas pagas (EE ≥ 1.5 até carga máxima permitida):")
    cp_values = []
    PVOO_values = []
    step = (cp_allowed - cp_min) / 10 if cp_allowed > cp_min else 1.0  # divide em 10 passos
    cp = cp_min
    while cp <= cp_allowed + 1e-6:
        EE = cp / pv
        PEE = PEE_FACTOR * EE
        PVOO = FPV_factor * FPR * PEE * horizontal_factor
        print(f"  Carga paga: {cp:.2f} kg | EE: {EE:.2f} | PVOO: {PVOO:.2f}")
        cp_values.append(cp)
        PVOO_values.append(PVOO)
        cp += step

    # Retorna o PVOO final considerando carga máxima permitida
    final_cp = cp_allowed
    final_EE = final_cp / pv
    final_PEE = PEE_FACTOR * final_EE
    final_PVOO = FPV_factor * FPR * final_PEE * horizontal_factor

    print("\n✅ Resultado final:")
    print(f"Peso vazio: {pv} kg")
    print(f"Carga paga máxima: {cp_allowed} kg")
    print(f"MTOW: {total_weight_max} kg")
    print(f"EE máxima: {final_EE:.2f}")
    print(f"PEE máxima: {final_PEE:.2f}")
    print(f"FPV: {FPV_factor}")
    print(f"FPR: {FPR:.2f}")
    print(f"Fator Horizontal: {horizontal_factor:.2f}")
    print(f"PVOO máxima: {final_PVOO:.2f}")
    print("\n📊 Intervalo de PVOO para diferentes cargas pagas (EE ≥ 1.5 até carga máxima permitida):")
    for cp_val, pvoo_val in zip(cp_values, PVOO_values):
        print(f"Carga paga: {cp_val:.2f} kg | PVOO: {pvoo_val:.2f} | PFINAL: {pvoo_val + APRESENTACAO + VIDEOVOO + NR_DEFAULT:.2f}")

compute_competition_score() 