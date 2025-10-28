import json
from pathlib import Path
import requests
import pandas as pd

# URL base de la API
API_BASE_URL = "http://127.0.0.1:8000"

def save_recommendations(recommendations, filename):
    """Guarda las recomendaciones en un archivo JSON dentro de Front/data"""
    data_path = Path(__file__).parent / 'data'
    data_path.mkdir(exist_ok=True)
    
    filepath = data_path / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=4, ensure_ascii=False)
    print(f"\nRecomendaciones guardadas en {filepath}")

def get_anime_recommendations(anime_id):
    """Obtiene recomendaciones basadas en un anime específico usando la API."""
    try:
        response = requests.get(f"{API_BASE_URL}/recommend/anime/{anime_id}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["recommendations"]
            else:
                print("Error:", data["message"])
                return None
        else:
            print(f"Error al obtener recomendaciones: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        print("¿Está corriendo el servidor API (python run_api.py)?")
        return None

def load_anime_data():
    """Carga los datos de anime desde un archivo CSV local para búsquedas."""
    try:
        return pd.read_csv("Back/Data/anime.csv")
    except Exception as e:
        print(f"Error cargando datos de anime: {e}")
        return None

def search_anime(query, anime_df):
    """Busca un anime por nombre o ID"""
    if anime_df is None:
        print("Error: No se pueden cargar los datos de anime")
        return None

    # Forzar anime_id a int para evitar problemas de tipo
    anime_df = anime_df.copy()
    anime_df['anime_id'] = pd.to_numeric(anime_df['anime_id'], errors='coerce').astype('Int64')

    if query.isdigit():
        anime_id = int(query)
        result = anime_df[anime_df['anime_id'] == anime_id]
    else:
        result = anime_df[anime_df['name'].str.lower().str.contains(query.lower(), na=False)]

    if result.empty:
        print("No se encontró ningún anime con ese criterio de búsqueda")
        return None

    return result[['anime_id', 'name', 'genre', 'rating']]

def display_anime_list(animes):
    """Muestra una lista de animes con sus detalles"""
    for _, row in animes.iterrows():
        print(f"\nID: {row['anime_id']}")
        print(f"Nombre: {row['name']}")
        print(f"Género: {row['genre']}")
        print(f"Rating: {row['rating']}")
        print("-" * 50)

def train_model():
    """Entrena el modelo usando la API"""
    try:
        response = requests.post(f"{API_BASE_URL}/train")
        if response.status_code == 200:
            data = response.json()
            return data["meta"], data["version"]
        else:
            print(f"Error al entrenar el modelo: {response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        print("¿Está corriendo el servidor API (python run_api.py)?")
        return None, None

def get_model_version():
    """Obtiene la versión actual del modelo usando la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/model-version")
        if response.status_code == 200:
            data = response.json()
            return data["current_model_version"]
        else:
            print(f"Error al obtener la versión del modelo: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        print("¿Está corriendo el servidor API (python run_api.py)?")
        return None

def main():
    # Cargar datos de anime para búsquedas locales
    anime_df = load_anime_data()
    if anime_df is None:
        print("Error: No se pueden cargar los datos necesarios.")
        return

    while True:
        print("\n=== Consola de AnimeRecomendator ===")
        print("1. Obtener recomendaciones")
        print("2. Entrenar el algoritmo")
        print("3. Obtener la versión del modelo")
        print("4. Salir")

        opcion = input("\nSeleccione una opción (1-4): ")

        if opcion == "1":
            print("\n-- Obtener recomendaciones de anime similares --")
            print("1. Buscar por Nombre de anime")
            print("2. Buscar por ID de anime")
            print("3. Búsqueda avanzada")
            print("4. Volver")
            sub = input("Seleccione (1-4): ")
            if sub == "1":
                anime_name = input("Ingrese el Nombre del anime: ")
                results = search_anime(anime_name, anime_df)
                if results is not None:
                    display_anime_list(results)
                    if len(results) == 1:
                        anime_id = results.iloc[0]['anime_id']
                        if input("Ver recomendaciones para este anime? (s/n): ").lower() == 's':
                            recs = get_anime_recommendations(anime_id)
                            if recs:
                                print("\nAnimes similares:")
                                for i, r in enumerate(recs, 1):
                                    print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', r.get('score', 'N/A'))}")
                                save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")
                    else:
                        print("\nSeleccione un anime específico usando la opción de búsqueda (3) para ver recomendaciones.")

            elif sub == "2":
                anime_id = input("Ingrese el ID del anime: ")
                try:
                    anime_id = int(anime_id)
                    recs = get_anime_recommendations(anime_id)
                    if recs:
                        print("\nAnimes similares:")
                        for i, r in enumerate(recs, 1):
                            print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', r.get('score', 'N/A'))}")
                        save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")
                except ValueError:
                    print("ID de anime inválido")

            elif sub == "3":
                query = input("Ingrese ID o nombre: ")
                results = search_anime(query, anime_df)
                if results is not None:
                    display_anime_list(results)
                    if len(results) == 1:
                        anime_id = results.iloc[0]['anime_id']
                        if input("Ver recomendaciones para este anime? (s/n): ").lower() == 's':
                            recs = get_anime_recommendations(anime_id)
                            if recs:
                                print("\nAnimes similares:")
                                for i, r in enumerate(recs, 1):
                                    print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', r.get('score', 'N/A'))}")
                                save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")

            else:
                continue

        elif opcion == "2":
            print("Entrenando el modelo (esto puede tardar demasiado :'u)...")
            meta, version = train_model()
            if version:
                print(f"Entrenamiento finalizado. Versión: {version}")

        elif opcion == "3":
            version = get_model_version()
            if version:
                print(f"Versión actual del modelo: {version}")

        elif opcion == "4":
            print("Saliendo nos vemos luego!")
            break

        else:
            print("Opción no válida. Seleccione 1-4.")

if __name__ == "__main__":
    # Verificar si la API está disponible
    try:
        requests.get(f"{API_BASE_URL}/")
        main()
    except requests.RequestException:
        print("Error: No se puede conectar con la API.")
        print("Por favor, asegúrate de que el servidor API está corriendo:")
        print("1. Abre una nueva terminal")
        print("2. Ejecuta: python run_api.py")