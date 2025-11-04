# consola.py — now API-only, no CSV access
import json
import requests
from pathlib import Path
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000"


def register_user(username, password):
    """Registra un nuevo usuario en la base de datos."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('detail', 'No se pudo registrar')}")
            return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def authenticate(username, password):
    """Autentica al usuario usando la API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data  # Devuelve {"status": "success", "user_id": X, "username": Y}
        else:
            return None
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

def save_recommendations(recommendations, username, anime_id):
    """Guarda las recomendaciones asociadas a un usuario específico."""
    data_path = Path(__file__).parent / "data" / username
    data_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recomendaciones_anime_{anime_id}_{timestamp}.json"
    filepath = data_path / filename
    
    # Agregar metadata
    data = {
        "username": username,
        "anime_id": anime_id,
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"\n✓ Recomendaciones guardadas en {filepath}")


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
    # Sistema de Login/Registro
    print("\n" + "=" * 60)
    print("🎌  Bienvenido a AnimeRecomendator  🎌")
    print("=" * 60)
    
    username = None
    user_info = None
    
    # Login o Registro
    while user_info is None:
        print("\n--- MENÚ DE INICIO ---")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")
        
        opcion_inicio = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion_inicio == "1":
            # LOGIN
            print("\n--- LOGIN ---")
            username = input("Usuario: ").strip()
            if username.lower() == 'salir':
                print("¡Hasta luego!")
                return
            
            password = input("Contraseña: ").strip()
            
            user_info = authenticate(username, password)
            if user_info is None:
                print("❌ Usuario o contraseña incorrectos. Intente de nuevo.")
            else:
                print(f"\n✓ Bienvenido de nuevo, {username}!")
        
        elif opcion_inicio == "2":
            # REGISTRO
            print("\n--- REGISTRO ---")
            username = input("Nuevo usuario: ").strip()
            if len(username) < 3:
                print("❌ El nombre de usuario debe tener al menos 3 caracteres.")
                continue
            
            password = input("Nueva contraseña: ").strip()
            if len(password) < 4:
                print("❌ La contraseña debe tener al menos 4 caracteres.")
                continue
            
            confirm_password = input("Confirmar contraseña: ").strip()
            if password != confirm_password:
                print("❌ Las contraseñas no coinciden.")
                continue
            
            result = register_user(username, password)
            if result and result.get("status") == "success":
                print(f"\n✓ Usuario '{username}' registrado exitosamente!")
                print("Ahora puede iniciar sesión.")
            else:
                print("❌ No se pudo completar el registro.")
        
        elif opcion_inicio == "3":
            print("¡Hasta luego!")
            return
        
        else:
            print("❌ Opción no válida.")
    
    # Menú principal
    while True:
        print("\n" + "=" * 60)
        print(f"Usuario: {username}")
        print("=" * 60)
        print("1. Buscar y obtener recomendaciones")
        print("2. Entrenar el modelo")
        print("3. Ver versión del modelo")
        print("4. Salir")

        opcion = input("\nSeleccione una opción (1-4): ")

        if opcion == "1":
            query = input("\nIngrese ID o nombre de anime: ")
            results = search_anime_api(query)
            if not results:
                continue

            display_anime_list(results)
            if len(results) == 1:
                anime_id = results[0]["anime_id"]
                if input("\n¿Ver recomendaciones para este anime? (s/n): ").lower() == "s":
                    recs = get_anime_recommendations(anime_id)
                    if recs:
                        print("\n Animes similares:")
                        for i, r in enumerate(recs, 1):
                            print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', 'N/A')}")
                        save_recommendations(recs, username, anime_id)
            elif len(results) > 1:
                print(f"\n Se encontraron {len(results)} resultados.")
                anime_id_input = input("Ingrese el ID del anime que desea (o Enter para cancelar): ")
                if anime_id_input.isdigit():
                    anime_id = int(anime_id_input)
                    if input("\n¿Ver recomendaciones para este anime? (s/n): ").lower() == "s":
                        recs = get_anime_recommendations(anime_id)
                        if recs:
                            print("\n Animes similares:")
                            for i, r in enumerate(recs, 1):
                                print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', 'N/A')}")
                            save_recommendations(recs, username, anime_id)

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
            print(f"\n ¡Nos vemos pronto ;), {username}!")
            break

        else:
            print(" Opción no válida.")
if __name__ == "__main__":
    try:
        requests.get(f"{API_BASE_URL}/")
        main()
    except requests.RequestException:
        print("Error: No se puede conectar con la API.")
        print("Ejecute primero: python run_api.py")
