# consola.py — now API-only, no CSV access
import json
import requests
from pathlib import Path

API_BASE_URL = "http://127.0.0.1:8000"


def save_recommendations(recommendations, filename):
    data_path = Path(__file__).parent / "data"
    data_path.mkdir(exist_ok=True)
    filepath = data_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=4, ensure_ascii=False)
    print(f"\nRecomendaciones guardadas en {filepath}")


def search_anime_api(query):
    """Search anime by name or ID via API."""
    try:
        response = requests.get(f"{API_BASE_URL}/anime/search", params={"query": query})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print("No se encontró ningún anime con ese criterio de búsqueda")
            return None
        else:
            print(f"Error al buscar anime: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def get_anime_recommendations(anime_id):
    try:
        response = requests.get(f"{API_BASE_URL}/recommend/anime/{anime_id}")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["recommendations"]
            print("Error:", data.get("message", "Error desconocido"))
            return None
        print(f"Error al obtener recomendaciones: {response.status_code}")
        return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def train_model():
    try:
        response = requests.post(f"{API_BASE_URL}/train")
        if response.status_code == 200:
            data = response.json()
            return data["meta"], data["version"]
        print(f"Error al entrenar el modelo: {response.status_code}")
        return None, None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None, None


def get_model_version():
    try:
        response = requests.get(f"{API_BASE_URL}/model-version")
        if response.status_code == 200:
            data = response.json()
            return data["current_model_version"]
        print(f"Error al obtener la versión del modelo: {response.status_code}")
        return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def display_anime_list(animes):
    for anime in animes:
        print(f"\nID: {anime.get('anime_id')}")
        print(f"Nombre: {anime.get('name')}")
        print(f"Género: {anime.get('genre')}")
        print(f"Rating: {anime.get('rating')}")
        print("-" * 50)


def main():
    while True:
        print("\n=== Consola de AnimeRecomendator ===")
        print("1. Buscar y obtener recomendaciones")
        print("2. Entrenar el modelo")
        print("3. Ver versión del modelo")
        print("4. Salir")

        opcion = input("Seleccione una opción (1-4): ")

        if opcion == "1":
            query = input("\nIngrese ID o nombre de anime: ")
            results = search_anime_api(query)
            if not results:
                continue

            display_anime_list(results)
            if len(results) == 1:
                anime_id = results[0]["anime_id"]
                if input("¿Ver recomendaciones para este anime? (s/n): ").lower() == "s":
                    recs = get_anime_recommendations(anime_id)
                    if recs:
                        print("\nAnimes similares:")
                        for i, r in enumerate(recs, 1):
                            print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', 'N/A')}")
                        save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")

        elif opcion == "2":
            print("Entrenando el modelo... puede tardar un poco.")
            meta, version = train_model()
            if version:
                print(f"Entrenamiento finalizado. Versión: {version}")

        elif opcion == "3":
            version = get_model_version()
            if version:
                print(f"Versión actual del modelo: {version}")

        elif opcion == "4":
            print("Saliendo... ¡Nos vemos pronto!")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    try:
        requests.get(f"{API_BASE_URL}/")
        main()
    except requests.RequestException:
        print("Error: No se puede conectar con la API.")
        print("Ejecute primero: python run_api.py")
