import json
from pathlib import Path
import pandas as pd
import sys
import os
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

from Back.Recommendator.recommender import get_user_recommendations as get_user_recs
from Back.Recommendator.recommender import get_similar_anime, anime, load_current_model
from Back.Trainer.trainer import train_model, get_current_model_version

def save_recommendations(recommendations, filename):
    """Guarda las recomendaciones en un archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=4, ensure_ascii=False)
    print(f"\nRecomendaciones guardadas en {filename}")

def get_anime_recommendations(anime_id):
    """Obtiene recomendaciones basadas en un anime específico.

    Propaga FileNotFoundError si el modelo no existe.
    """
    try:
        recommendations = get_similar_anime(anime_id)
    except FileNotFoundError:
        raise
    except Exception as e:
        print("Error obteniendo recomendaciones por anime:", str(e))
        return None

    if recommendations is not None and not recommendations.empty:
        return recommendations.to_dict(orient="records")
    else:
        print("Error: No se encontraron animes similares")
        return None


def search_anime(query):
    """Busca un anime por nombre o ID"""
    if query.isdigit():
        anime_id = int(query)
        result = anime[anime['anime_id'] == anime_id]
    else:
        result = anime[anime['name'].str.lower().str.contains(query.lower(), na=False)]

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


def main():
    while True:
        print("\n=== Consola de AnimeRecomendator ===")
        print("1. Obtener recomendaciones")
        print("2. Entrenar el algoritmo")
        print("3. Obtener la versión del modelo")
        print("4. Testear el algoritmo (cargar modelo)")
        print("5. Salir")

        opcion = input("\nSeleccione una opción (1-5): ")

        if opcion == "1":
            print("\n-- Obtener recomendaciones de anime similares --")
            print("1. Buscar por Nombre de anime")
            print("2. Buscar por ID de anime")
            print("3. Búsqueda avanzada")
            print("4. Volver")
            sub = input("Seleccione (1-4): ")
            if sub == "1":
                anime_name = input("Ingrese el Nombre del anime: ")
                results = search_anime(anime_name)
                if results is not None:
                    display_anime_list(results)
                    if len(results) == 1:
                        anime_id = results.iloc[0]['anime_id']
                        if input("Ver recomendaciones para este anime? (s/n): ").lower() == 's':
                            try:
                                recs = get_anime_recommendations(anime_id)
                            except FileNotFoundError as e:
                                print(f"Error: {e}")
                                if input("¿Desea entrenar el modelo ahora? (s/n): ").lower() == 's':
                                    train_model()
                                    recs = get_anime_recommendations(anime_id)
                                else:
                                    recs = None
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
                    try:
                        recs = get_anime_recommendations(anime_id)
                    except FileNotFoundError as e:
                        print(f"Error: {e}")
                        resp = input("¿Desea entrenar el modelo ahora? (s/n): ")
                        if resp.lower() == 's':
                            train_model()
                            recs = get_anime_recommendations(anime_id)
                        else:
                            recs = None
                    if recs:
                        print("\nAnimes similares:")
                        for i, r in enumerate(recs, 1):
                            print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', r.get('score', 'N/A'))}")
                        save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")
                except ValueError:
                    print("ID de anime inválido")

            elif sub == "3":
                query = input("Ingrese ID o nombre: ")
                results = search_anime(query)
                if results is not None:
                    display_anime_list(results)
                    if len(results) == 1:
                        anime_id = results.iloc[0]['anime_id']
                        if input("Ver recomendaciones para este anime? (s/n): ").lower() == 's':
                            try:
                                recs = get_anime_recommendations(anime_id)
                            except FileNotFoundError as e:
                                print(f"Error: {e}")
                                if input("¿Desea entrenar el modelo ahora? (s/n): ").lower() == 's':
                                    train_model()
                                    recs = get_anime_recommendations(anime_id)
                                else:
                                    recs = None
                            if recs:
                                for i, r in enumerate(recs, 1):
                                    print(f"{i}. {r.get('name', 'Sin nombre')} - Score: {r.get('final_score', r.get('score', 'N/A'))}")
                                save_recommendations(recs, f"recomendaciones_anime_{anime_id}.json")

            else:
                # volver
                continue

        elif opcion == "2":
            print("Entrenando el modelo (esto puede tardar demasiado :'u)...")
            meta, version = train_model()
            print(f"Entrenamiento finalizado. Versión: {version}")

        elif opcion == "3":
            version = get_current_model_version()
            print(f"Versión actual del modelo: {version}")

        elif opcion == "4":
            print("Probando carga del modelo...")
            try:
                model = load_current_model()
                print(f"Modelo cargado, tamaño: {model.shape}")
                # mostrar algunas columnas de ejemplo
                cols = list(model.columns)[:5]
                print("Columnas de ejemplo:", cols)
            except FileNotFoundError as e:
                print(f"Error: {e}")
                if input("¿Desea entrenar el modelo ahora? (s/n): ").lower() == 's':
                    train_model()
                    try:
                        model = load_current_model()
                        print(f"Modelo entrenado y cargado, tamaño: {model.shape}")
                    except Exception as e2:
                        print("Error al cargar el modelo después de entrenar:", e2)

        elif opcion == "5":
            print("Saliendo...")
            break

        else:
            print("Opción no válida. Seleccione 1-5.")


if __name__ == "__main__":
    main()
