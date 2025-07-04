import requests
import os

def test_file_upload():
    """
    Test the new file upload endpoint
    """
    url = "http://localhost:8000/api/v1/analysis/project/upload"
    
    # Create a sample project deck content
    sample_content = """
    PROYECTO: MoneyMule MultiAgent
    
    DESCRIPCIÓN:
    MoneyMule MultiAgent es una plataforma de análisis de startups que utiliza inteligencia artificial 
    para evaluar proyectos, encontrar fundadores y analizar repositorios de GitHub.
    
    PROBLEMA:
    Los inversores y analistas necesitan una forma rápida y eficiente de evaluar startups, 
    encontrar información sobre fundadores y analizar el código técnico de los proyectos.
    
    SOLUCIÓN:
    Una plataforma multiagente que combina análisis de documentos, búsqueda de fundadores 
    y análisis de repositorios GitHub para proporcionar evaluaciones completas.
    
    MERCADO OBJETIVO:
    - Inversores de capital de riesgo
    - Analistas de startups
    - Aceleradoras e incubadoras
    - Empresas de consultoría
    
    MODELO DE NEGOCIO:
    - Suscripción mensual para acceso a la plataforma
    - Análisis por proyecto con tarifa fija
    - API para integración con otras herramientas
    - Consultoría personalizada
    
    EQUIPO:
    - CEO: Experto en IA y análisis de startups
    - CTO: Desarrollador senior con experiencia en multiagentes
    - Head of Product: Especialista en UX/UI para herramientas B2B
    """
    
    # Create a temporary file
    with open("sample_deck.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    try:
        # Test file upload
        with open("sample_deck.txt", "rb") as f:
            files = {"file": ("sample_deck.txt", f, "text/plain")}
            data = {"project_name": "MoneyMule MultiAgent"}
            
            response = requests.post(url, files=files, data=data)
            
            print("Status Code:", response.status_code)
            print("Response:", response.json())
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        if os.path.exists("sample_deck.txt"):
            os.remove("sample_deck.txt")

if __name__ == "__main__":
    test_file_upload() 