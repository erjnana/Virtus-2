from pathlib import Path
import yaml

base_path = "airfoils/assymmetric"
def load_airfoil(name, base_path):
    """
    Carrega os dados de um aerofólio a partir do banco de aerofólios.
    """
    af_dir = Path(base_path) / name

    if not af_dir.exists():
        raise FileNotFoundError(f"Aerofólio '{name}' não encontrado em '{base_path}'")

    info_file = af_dir / "info.yaml"
    if not info_file.exists():
        raise FileNotFoundError(f"Arquivo info.yaml não encontrado para o aerofólio '{name}'")

    with open(info_file, "r") as f:
        info = yaml.safe_load(f)

    if "summary" not in info:
        raise KeyError(f"'summary' ausente no info.yaml do aerofólio '{name}'")

    summary = info["summary"]
    required_fields = ["reynolds", "cl_alpha", "cl_0", "cm_0", "cl_max", "alpha_cl_max"]

    for field in required_fields:
        if field not in summary:
            raise KeyError(f"Campo '{field}' ausente no summary do aerofólio '{name}'")

    dat_file = af_dir / "geometry.dat"
    if not dat_file.exists():
        raise FileNotFoundError(f"Arquivo geometry.dat não encontrado para o aerofólio '{name}'")

    return {
        "cl_max": summary["cl_max"],
        "alpha_cl_max": summary["alpha_cl_max"],
        "dat_path": str(dat_file)
    }

# ============================================================
# LOOP DE CARREGAMENTO
# ============================================================

# Ajustado para a subpasta correta
airfoils_database = {}
base_dir = Path(base_path)

if base_dir.exists() and base_dir.is_dir():
    for folder in base_dir.iterdir():
        if folder.is_dir():
            try:
                airfoil_name = folder.name
                # Passamos o BASE_PATH explicitamente para a função
                data = load_airfoil(airfoil_name, base_path)
                
                # Guardamos no dicionário (usando o nome da pasta como chave)
                airfoils_database[airfoil_name] = data
                
                print(f"Sucesso: {airfoil_name} carregado.")
                
            except (FileNotFoundError, KeyError) as e:
                print(f"Erro ao carregar '{folder.name}': {e}")
else:
    print(f"Erro: O diretório '{base_path}' não foi encontrado.")

print(airfoils_database)