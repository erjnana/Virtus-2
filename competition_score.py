"""
Calcula a pontuação da competição de voo automaticamente a partir do Simulator/Prototype.
Fórmula atualizada: PVOO = FPV × FPR × PEE × (0.185N^2 − 0.775N + 1.81) × 1.15^−b
"""
from variables import NR_DEFAULT, PEE_FACTOR, Nhor_DEFAULT, APRESENTACAO, VIDEOVOO

# =======================
# PARÂMETROS FIXOS DA COMPETIÇÃO
# =======================

FPV = 1.1
MAX_WEIGHT = 20

# =======================
# FUNÇÃO DE PONTUAÇÃO
# =======================
def compute_competition_score(pv, cp_max, b, N_horizontal=Nhor_DEFAULT, NR=NR_DEFAULT):
    """
    Calcula a pontuação da aeronave baseado nos resultados do Simulator.
    Argumentos:
        pv: Peso vazio (kg)
        cp_max: Carga paga máxima calculada pelo simulador (kg)
        b: Envergadura total (m)
        N_horizontal: Número de superfícies horizontais
        NR: Número de relatórios
    """

    if pv <= 0:
        raise ValueError("Peso vazio inválido (<=0). Não é possível calcular EE.")

    # 1. Ajuste de carga máxima para não ultrapassar o limite de 20kg (MTOW)
    cp_allowed = min(cp_max, MAX_WEIGHT - pv)
    total_weight_max = pv + cp_allowed

    if pv + cp_max > MAX_WEIGHT:
        print(f"\n⚠️ Aviso: peso total com carga máxima ({pv + cp_max:.2f} kg) excede o limite de {MAX_WEIGHT} kg.")
        print(f"    ⚠️ Calculando PVOO somente até {cp_allowed:.2f} kg de carga paga.")

    # 2. Carga mínima de projeto (conforme regulamento ou estratégia)
    cp_min = 5.0
    if cp_min > cp_allowed:
        cp_min = 0.0

    # 3. Fator de Superfícies Horizontais (Nova Fórmula)
    # (0.185N^2 − 0.775N + 1.81)
    if N_horizontal is None:
        N_horizontal = 1
    horizontal_factor = 0.185 * N_horizontal**2 - 0.775 * N_horizontal + 1.81

    # 4. Fator de Envergadura (Novo Componente)
    # 1.15^-b
    wingspan_factor = 1.15**(-b)

    # 5. Outros Fatores
    FPR = min(1.0, 0.5 + 0.75 * NR / 185)
    
    # 6. Cálculo iterativo para o log (opcional)
    cp_values = []
    PVOO_values = []
    step = (cp_allowed - cp_min) / 5 if cp_allowed > cp_min else 1.0
    
    cp = cp_min
    while cp <= cp_allowed + 1e-6:
        EE = cp / pv
        PEE = PEE_FACTOR * EE
        # PVOO = FPV × FPR × PEE × FatorN × FatorB
        PVOO = FPV * FPR * PEE * horizontal_factor * wingspan_factor
        cp_values.append(cp)
        PVOO_values.append(PVOO)
        cp += step

    # 7. Retorno do PVOO Final (Carga Máxima Permitida)
    final_cp = cp_allowed
    final_EE = final_cp / pv
    final_PEE = PEE_FACTOR * final_EE
    final_PVOO = FPV * FPR * final_PEE * horizontal_factor * wingspan_factor

    print("\n✅ Resultado final (Fórmula Atualizada):")
    print(f"Peso vazio: {pv:.2f} kg | Envergadura: {b:.2f} m")
    print(f"Carga paga máxima: {cp_allowed:.2f} kg")
    print(f"EE máxima: {final_EE:.2f}")
    print(f"Fator N ({N_horizontal} superfícies): {horizontal_factor:.2f}")
    #print(f"Fator Envergadura (b={b:.2f}m): {wingspan_factor:.4f}")
    print(f"PVOO Final: {final_PVOO:.2f}")
    
    print("\n📊 Estimativa de Pontuação Final (PVOO + Relatórios + Vídeo):")
    for cp_val, pvoo_val in zip(cp_values, PVOO_values):
        p_total = pvoo_val + APRESENTACAO + VIDEOVOO + NR_DEFAULT
        print(f"CP: {cp_val:.2f} kg | PVOO: {pvoo_val:.2f} | P_TOTAL: {p_total:.2f}")

    return {"PVOO": final_PVOO}