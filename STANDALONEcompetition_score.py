# =======================
# PARÂMETROS FIXOS DA COMPETIÇÃO
# =======================
FPV = 0.9               # Fator de previsão de voo
NR_DEFAULT = 110.38        # Nota de relatório estimada
MAX_WEIGHT = 20.0       # kg
PEE_FACTOR = 25         # Fator de pontuação eficiência estrutural
Nhor_DEFAULT = 2        #Número de superfícies sustentadoras
pv = 5
cp_max = 13

# =======================
# FUNÇÃO DE PONTUAÇÃO
# =======================
def compute_competition_score(N_horizontal=Nhor_DEFAULT , NR=NR_DEFAULT):
    """
    Calcula a pontuação da aeronave baseado nos resultados do Simulator.
    Mostra PVOO para cargas pagas que gerem EE ≥ 1.5 até a carga máxima possível respeitando o limite de 20 kg.
    """


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

    cp_values = []
    PVOO_values = []
    step = (cp_allowed - cp_min) / 10 if cp_allowed > cp_min else 1.0  # divide em 10 passos
    cp = cp_min
    while cp <= cp_allowed + 1e-6:
        EE = cp / pv
        PEE = PEE_FACTOR * EE
        PVOO = FPV_factor * FPR * PEE * horizontal_factor
        cp_values.append(cp)
        PVOO_values.append(PVOO)
        cp += step

    # Retorna o PVOO final considerando carga máxima permitida
    final_cp = cp_allowed
    final_EE = final_cp / pv
    final_PEE = PEE_FACTOR * final_EE
    final_PVOO = FPV_factor * FPR * final_PEE * horizontal_factor

    print("\n✅ Resultado final:")
    print(f"peso_vazio: {pv}")
    print(f"carga_paga_max: {cp_allowed}")
    print(f"total_peso_max: {total_weight_max}")
    print(f"EE_max: {final_EE:.2f}")
    print(f"PEE_max: {final_PEE:.2f}")
    print(f"FPV: {FPV_factor}")
    print(f"FPR: {FPR:.2f}")
    print(f"horizontal_factor: {horizontal_factor:.2f}")
    print(f"PVOO_final: {final_PVOO:.2f}")
    print("\n📊 Intervalo de PVOO para diferentes cargas pagas (EE ≥ 1.5 até carga máxima permitida):")
    for cp_val, pvoo_val in zip(cp_values, PVOO_values):
        print(f"Carga paga: {cp_val:.2f} kg | PVOO: {pvoo_val:.2f}")

compute_competition_score()