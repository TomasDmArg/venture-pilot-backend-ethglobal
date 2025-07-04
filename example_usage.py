#!/usr/bin/env python3
"""
Ejemplo de uso del sistema Money Mule Multiagent
"""

import asyncio
import base64
import json
import requests
from typing import Dict, Any

# Configuración
API_BASE_URL = "http://localhost:8000/api/v1"

def encode_file_to_base64(file_path: str) -> str:
    """
    Codifica un archivo a base64
    """
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            return base64.b64encode(file_content).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""
    except Exception as e:
        print(f"Error codificando archivo: {e}")
        return ""

async def analyze_project_example():
    """
    Ejemplo de análisis de proyecto
    """
    print("=== Ejemplo de Análisis de Proyecto ===\n")
    
    # Crear contenido de ejemplo (en lugar de un archivo real)
    example_deck_content = """
    PROYECTO: TechStart
    
    DESCRIPCIÓN:
    TechStart es una plataforma SaaS que conecta startups con inversores ángeles.
    
    PROBLEMA:
    Las startups tienen dificultades para encontrar inversores, y los inversores
    tienen problemas para evaluar oportunidades de inversión.
    
    SOLUCIÓN:
    Plataforma de matching inteligente que utiliza IA para conectar startups
    con inversores basándose en criterios de inversión y necesidades de financiamiento.
    
    MERCADO OBJETIVO:
    Startups en etapa seed y series A, inversores ángeles y fondos de inversión.
    
    MODELO DE NEGOCIO:
    Comisión del 5% sobre inversiones exitosas + suscripción mensual para startups.
    
    EQUIPO:
    - Juan Pérez (CEO) - Ex Google, Stanford MBA
    - María García (CTO) - Ex Facebook, PhD Computer Science
    - Carlos López (CPO) - Ex Uber, Product Manager
    """
    
    # Codificar contenido a base64
    deck_base64 = base64.b64encode(example_deck_content.encode('utf-8')).decode('utf-8')
    
    # Preparar request
    payload = {
        "deck_file": deck_base64,
        "project_name": "TechStart"
    }
    
    try:
        print("Enviando request de análisis...")
        response = requests.post(f"{API_BASE_URL}/analysis/project", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis completado exitosamente!")
            print(f"Mensaje: {result['message']}")
            
            if result.get('data'):
                data = result['data']
                print(f"\n📊 Resumen del Proyecto:")
                print(f"Nombre: {data.get('project_name', 'N/A')}")
                print(f"Descripción: {data.get('description', 'N/A')}")
                print(f"Problema: {data.get('problem_statement', 'N/A')}")
                print(f"Solución: {data.get('solution', 'N/A')}")
                print(f"Mercado: {data.get('target_market', 'N/A')}")
                print(f"Modelo: {data.get('business_model', 'N/A')}")
                
                print(f"\n👥 Equipo ({len(data.get('team_info', []))} miembros):")
                for member in data.get('team_info', []):
                    print(f"  - {member.get('name', 'N/A')}")
                    if member.get('github_username'):
                        print(f"    GitHub: {member.get('github_username')}")
                    if member.get('linkedin_url'):
                        print(f"    LinkedIn: {member.get('linkedin_url')}")
                
                print(f"\n📁 Repositorios GitHub ({len(data.get('github_repos', []))}):")
                for repo in data.get('github_repos', []):
                    print(f"  - {repo}")
                
                print(f"\n🔍 GitRoll Scans ({len(data.get('gitroll_scans', []))}):")
                for scan in data.get('gitroll_scans', []):
                    print(f"  - {scan.get('username', 'N/A')}: {scan.get('status', 'N/A')}")
                    if scan.get('profile_url'):
                        print(f"    URL: {scan.get('profile_url')}")
        else:
            print(f"❌ Error en el análisis: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

async def gitroll_scan_example():
    """
    Ejemplo de GitRoll scan
    """
    print("\n=== Ejemplo de GitRoll Scan ===\n")
    
    # Usuario de ejemplo (reemplazar con un usuario real)
    test_username = "octocat"  # Usuario de ejemplo de GitHub
    
    payload = {
        "user": test_username
    }
    
    try:
        print(f"Iniciando GitRoll scan para usuario: {test_username}")
        response = requests.post(f"{API_BASE_URL}/analysis/gitroll/scan", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ GitRoll scan iniciado exitosamente!")
            print(f"Mensaje: {result['message']}")
            
            if result.get('scan_id'):
                print(f"Scan ID: {result['scan_id']}")
                print(f"Profile URL: {result.get('profile_url', 'N/A')}")
                
                # Verificar estado del scan
                print("\nVerificando estado del scan...")
                await asyncio.sleep(2)  # Esperar un poco
                
                status_response = requests.get(f"{API_BASE_URL}/analysis/gitroll/status/{result['scan_id']}")
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"Estado: {status_result.get('status', 'N/A')}")
                    if status_result.get('score'):
                        print(f"Score: {status_result.get('score')}")
                    if status_result.get('og_image_score'):
                        print(f"OG Image Score: {status_result.get('og_image_score')}")
                else:
                    print(f"Error verificando estado: {status_response.status_code}")
            else:
                print("No se recibió scan_id en la respuesta")
        else:
            print(f"❌ Error en GitRoll scan: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

async def health_check():
    """
    Verificar salud del sistema
    """
    print("=== Health Check ===\n")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sistema saludable: {result}")
        else:
            print(f"❌ Sistema no saludable: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

async def main():
    """
    Función principal
    """
    print("🚀 Money Mule Multiagent System - Ejemplo de Uso\n")
    
    # Verificar que el servidor esté corriendo
    await health_check()
    
    # Ejecutar ejemplos
    await analyze_project_example()
    await gitroll_scan_example()
    
    print("\n✨ Ejemplos completados!")

if __name__ == "__main__":
    # Ejecutar ejemplos
    asyncio.run(main()) 