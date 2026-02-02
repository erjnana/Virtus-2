from pathlib import Path
import yaml

def load_airfoil(name, base_path="airfoils"):
    """
    Carrega os dados de um aerofólio a partir do banco de aerofólios.

    Este loader NÃO cria objetos do AVL.
    Ele apenas lê, valida e organiza os dados aerodinâmicos,
    deixando a decisão de como usar esses dados para o Prototype.

    Estrutura esperada do banco:

    airfoils/
      └── E421/
          ├── E421.dat
          └── info.yaml
    """

    # ============================================================
    # 1. Localização da pasta do aerofólio
    # ============================================================
    # Ex: airfoils/E421
    af_dir = Path(base_path) / name

    # Se a pasta não existir, o banco está inconsistente
    if not af_dir.exists():
        raise FileNotFoundError(
            f"Aerofólio '{name}' não encontrado em '{base_path}'"
        )

    # ============================================================
    # 2. Leitura do info.yaml
    # ============================================================
    info_file = af_dir / "info.yaml"

    # O info.yaml é obrigatório
    if not info_file.exists():
        raise FileNotFoundError(
            f"Arquivo info.yaml não encontrado para o aerofólio '{name}'"
        )

    # Carrega o YAML como dicionário Python
    with open(info_file, "r") as f:
        info = yaml.safe_load(f)

    # ============================================================
    # 3. Validação da estrutura mínima do YAML
    # ============================================================
    # Todo aerofólio PRECISA ter um bloco summary
    if "summary" not in info:
        raise KeyError(
            f"'summary' ausente no info.yaml do aerofólio '{name}'"
        )

    summary = info["summary"]

    # Campos obrigatórios para o MDO funcionar corretamente
    # Se faltar qualquer um desses, a otimização fica inválida
    required_fields = [
        "reynolds",        # Reynolds de referência
        "cl_alpha",        # dCl/dα [1/rad]
        "cl_0",            # Cl em alpha = 0
        "cm_0",            # Cm em alpha = 0
        "cl_max",          # Cl máximo (estol)
        "alpha_cl_max"     # Ângulo de estol [graus]
    ]

    # Verificação explícita campo a campo
    for field in required_fields:
        if field not in summary:
            raise KeyError(
                f"Campo '{field}' ausente no summary do aerofólio '{name}'"
            )

    # ============================================================
    # 4. Localização do arquivo de geometria
    # ============================================================
    dat_file = af_dir / "geometry.dat"
    if not dat_file.exists():
        raise FileNotFoundError(
            f"Arquivo geometry.dat não encontrado para o aerofólio '{name}'"
        )

    # ============================================================
    # 5. Retorno organizado dos dados
    # ============================================================
    # Retornamos apenas DADOS.
    # Nada de objetos do AVL aqui — isso é responsabilidade do Prototype.
    return {
        # -------------------------
        # Identificação
        # -------------------------
        "name": info["name"],
        "family": info.get("family", "unknown"),

        # -------------------------
        # Reynolds de referência
        # -------------------------
        # Esse é o Reynolds no qual o summary foi extraído.
        # Futuramente pode ser usado para interpolação.
        "reynolds_ref": summary["reynolds"],

        # -------------------------
        # Aerodinâmica linear
        # -------------------------
        # IMPORTANTE: cl_alpha deve estar em 1/rad
        "cl_alpha": summary["cl_alpha"],
        "cl_0": summary["cl_0"],
        "cm_0": summary["cm_0"],

        # -------------------------
        # Limites aerodinâmicos
        # -------------------------
        "cl_max": summary["cl_max"],
        "alpha_cl_max": summary["alpha_cl_max"],

        # -------------------------
        # Geometria do perfil
        # -------------------------
        # Retornamos como string para garantir compatibilidade
        # com FileAirfoil do avlwrapper
        "dat_path": str(dat_file)
    }
