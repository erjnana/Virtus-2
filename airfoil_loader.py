from pathlib import Path
import yaml
import random

def load_airfoil(name):
    """
    Carrega os dados de um aerofólio procurando nas subpastas 
    symmetric, assymmetric e inverted.
    """
    base_dir = Path("airfoils")
    subfolders = ["symmetric", "assymmetric", "inverted"]
    af_dir = None

    # Procura em qual subpasta o aerofólio está
    for sub in subfolders:
        potential_path = base_dir / sub / name
        if potential_path.exists():
            af_dir = potential_path
            break

    if not af_dir:
        raise FileNotFoundError(f"Aerofólio '{name}' não encontrado nas subpastas de '{base_path}'")

    info_file = af_dir / "info.yaml"
    if not info_file.exists():
        raise FileNotFoundError(f"Arquivo info.yaml não encontrado em '{af_dir}'")

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
        raise FileNotFoundError(f"Arquivo geometry.dat não encontrado em '{af_dir}'")

    return {
        "cl_max": summary["cl_max"],
        "alpha_cl_max": summary["alpha_cl_max"],
        "dat_path": str(dat_file)
    }

# ============================================================
# LOOP DE CARREGAMENTO ORGANIZADO POR CATEGORIA
# ============================================================

airfoils_database_asa = {} # Apenas assymmetric
airfoils_database_eh = {}  # symmetric e inverted
airfoils_database_ev = {}  # Apenas symmetric

base_path = "airfoils"
base_dir = Path(base_path)

if base_dir.exists() and base_dir.is_dir():
    # Mapeamento de pastas para seus respectivos dicionários alvo
    # Pasta -> Lista de dicionários onde deve ser incluído
    mapping = {
        "assymmetric": [airfoils_database_asa],
        "symmetric": [airfoils_database_eh, airfoils_database_ev],
        "inverted": [airfoils_database_eh]
    }

    for subfolder_name, targets in mapping.items():
        subfolder_path = base_dir / subfolder_name
        
        if subfolder_path.exists() and subfolder_path.is_dir():
            for folder in subfolder_path.iterdir():
                if folder.is_dir():
                    try:
                        airfoil_name = folder.name
                        data = load_airfoil(airfoil_name)
                        
                        # Adiciona o perfil nos dicionários correspondentes
                        for target_dict in targets:
                            target_dict[airfoil_name] = data
                        
                        print(f"Sucesso: {airfoil_name} carregado em sua categoria ({subfolder_name}).")
                        
                    except (FileNotFoundError, KeyError) as e:
                        print(f"⚠️ Erro ao carregar '{folder.name}': {e}")
else:
    print(f"⚠️ Erro: O diretório base '{base_path}' não foi encontrado.")

def select_airfoil(name_or_random, database, label="Componente"):
    """
    Seleciona o perfil e imprime a escolha no terminal.
    """
    if not database:
        raise ValueError(f"O banco de dados para {label} está vazio.")

    if name_or_random.lower() == "random":
        chosen_name = random.choice(list(database.keys()))
        print(f"🎲 [RANDOM] {label}: Selecionado o perfil '{chosen_name}'")
    else:
        chosen_name = name_or_random
        if chosen_name not in database:
            raise KeyError(f"❌ Erro: Perfil '{chosen_name}' não encontrado para {label}.")
        print(f"✅ [FIXO]   {label}: Usando o perfil '{chosen_name}'")

    return database[chosen_name]

LISTA_ASA = sorted(list(airfoils_database_asa.keys()))
LISTA_EH  = sorted(list(airfoils_database_eh.keys()))
LISTA_EV  = sorted(list(airfoils_database_ev.keys()))

print(f"📦 Catálogo carregado: {len(LISTA_ASA)} perfis de asa, {len(LISTA_EH)} de EH, {len(LISTA_EV)} de EV.")

# print(airfoils_database_asa)
# print(airfoils_database_eh)
# print(airfoils_database_ev)