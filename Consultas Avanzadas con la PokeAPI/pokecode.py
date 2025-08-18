import requests
import json
from tqdm import tqdm

BASE_URL = "https://pokeapi.co/api/v2"

def get_json(url):
    """Realiza una petición HTTP y devuelve JSON con manejo de errores"""
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None

def get_pokemon_by_type(tipo):
    """Devuelve lista de pokémon de un tipo específico"""
    data = get_json(f"{BASE_URL}/type/{tipo}")
    return [p['pokemon']['name'] for p in data['pokemon']] if data else []

def get_pokemon_info(name_or_id):
    """Obtiene detalles de un pokémon por nombre o id"""
    return get_json(f"{BASE_URL}/pokemon/{name_or_id}")

def get_species_info(name_or_id):
    """Obtiene detalles de species (hábitat, evolución, etc.)"""
    return get_json(f"{BASE_URL}/pokemon-species/{name_or_id}")

def get_evolution_chain(chain_url):
    """Obtiene la cadena evolutiva a partir de species"""
    return get_json(chain_url)

# ------------------------------
# 🔹 Clasificación por Tipos
# ------------------------------

def fuego_kanto():
    """a) ¿Cuántos Pokémon de tipo fuego existen en Kanto?"""
    pokes = get_pokemon_by_type("fire")
    kanto = []
    for p in tqdm(pokes, desc="Revisando Kanto"):
        info = get_pokemon_info(p)
        if info and info['id'] <= 151:  # Kanto son #1 a #151
            kanto.append(info['name'])
    return kanto

def agua_altos():
    """b) Pokémon tipo agua con altura > 10"""
    pokes = get_pokemon_by_type("water")
    grandes = []
    for p in tqdm(pokes, desc="Buscando Pokémon altos"):
        info = get_pokemon_info(p)
        if info and info['height'] > 10:
            grandes.append((info['name'], info['height']))
    return grandes

# ------------------------------
# 🔹 Evoluciones
# ------------------------------

def cadena_evolutiva(pokemon):
    """a) Cadena evolutiva completa de un pokémon inicial"""
    species = get_species_info(pokemon)
    if not species: return []
    evo_chain = get_evolution_chain(species['evolution_chain']['url'])
    chain = []

    def recorrer(evo):
        chain.append(evo['species']['name'])
        for e in evo['evolves_to']:
            recorrer(e)

    recorrer(evo_chain['chain'])
    return chain

def electricos_sin_evo():
    """b) Pokémon eléctricos que no tienen evoluciones"""
    pokes = get_pokemon_by_type("electric")
    solitarios = []
    for p in tqdm(pokes, desc="Buscando eléctricos sin evolución"):
        species = get_species_info(p)
        if species and species['evolves_from_species'] is None:
            evo_chain = get_evolution_chain(species['evolution_chain']['url'])
            if evo_chain and len(evo_chain['chain']['evolves_to']) == 0:
                solitarios.append(species['name'])
    return solitarios

# ------------------------------
# 🔹 Estadísticas de Batalla
# ------------------------------

def max_attack_johto():
    """a) Pokémon con mayor ataque base en Johto (#152-#251)"""
    max_atk = ("", 0)
    for i in tqdm(range(152, 252), desc="Johto Pokémon"):
        info = get_pokemon_info(i)
        if info:
            atk = next(stat['base_stat'] for stat in info['stats'] if stat['stat']['name'] == 'attack')
            if atk > max_atk[1]:
                max_atk = (info['name'], atk)
    return max_atk

def fastest_non_legendary(limit=1025):
    """b) Pokémon con mayor velocidad que no sea legendario"""
    max_speed = ("", 0)
    for i in tqdm(range(1, limit), desc="Buscando velocistas"):
        species = get_species_info(i)
        if not species: continue
        if species['is_legendary'] or species['is_mythical']:
            continue
        info = get_pokemon_info(i)
        if info:
            speed = next(stat['base_stat'] for stat in info['stats'] if stat['stat']['name'] == 'speed')
            if speed > max_speed[1]:
                max_speed = (info['name'], speed)
    return max_speed

# ------------------------------
# 🔹 Extras
# ------------------------------

def habitat_planta():
    """a) Hábitat más común entre Pokémon planta"""
    pokes = get_pokemon_by_type("grass")
    habitats = {}
    for p in tqdm(pokes, desc="Analizando hábitats planta"):
        species = get_species_info(p)
        if species and species['habitat']:
            hab = species['habitat']['name']
            habitats[hab] = habitats.get(hab, 0) + 1
    return max(habitats.items(), key=lambda x: x[1])

def menor_peso(limit=1025):
    """b) Pokémon con menor peso en toda la API"""
    min_peso = ("", 999999)
    for i in tqdm(range(1, limit), desc="Buscando Pokémon liviano"):
        info = get_pokemon_info(i)
        if info and info['weight'] < min_peso[1]:
            min_peso = (info['name'], info['weight'])
    return min_peso

# ------------------------------
# 🚀 Pruebas
# ------------------------------
if __name__ == "__main__":
    print("🔥 Fuego en Kanto:", fuego_kanto())
    print("💧 Agua altura > 10:", agua_altos())
    print("🌱 Cadena evolutiva de bulbasaur:", cadena_evolutiva("bulbasaur"))
    print("⚡ Eléctricos sin evolución:", electricos_sin_evo())
    print("🛡️ Mayor ataque en Johto:", max_attack_johto())
    print("💨 Más veloz no legendario:", fastest_non_legendary(500))  # limitado por rapidez
    print("🌍 Hábitat común planta:", habitat_planta())
    print("⚖️ Pokémon más liviano:", menor_peso(500))  # limitado por rapidez
