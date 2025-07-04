#!/usr/bin/env python3
"""
Script de pruebas para la API Money Mule Multiagent
"""

import requests
import base64
import json
import time
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"

def test_health_check():
    """Prueba el health check principal"""
    print("🔍 Probando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check OK")
            return True
        else:
            print(f"❌ Health Check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en Health Check: {e}")
        return False

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    print("🔍 Probando Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root Endpoint OK")
            return True
        else:
            print(f"❌ Root Endpoint falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en Root Endpoint: {e}")
        return False

def test_analysis_health():
    """Prueba el health check del análisis"""
    print("🔍 Probando Analysis Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/health")
        if response.status_code == 200:
            print("✅ Analysis Health OK")
            return True
        else:
            print(f"❌ Analysis Health falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en Analysis Health: {e}")
        return False

def test_analysis_root():
    """Prueba el endpoint raíz del análisis"""
    print("🔍 Probando Analysis Root...")
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/")
        if response.status_code == 200:
            print("✅ Analysis Root OK")
            return True
        else:
            print(f"❌ Analysis Root falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en Analysis Root: {e}")
        return False

def test_project_analysis():
    """Prueba el análisis de proyecto"""
    print("🔍 Probando Project Analysis...")
    
    # Contenido de ejemplo del deck
    example_deck = """
    PROYECTO: TestStartup
    
    DESCRIPCIÓN:
    Plataforma de prueba para testing de APIs.
    
    PROBLEMA:
    Necesitamos probar el sistema multiagente.
    
    SOLUCIÓN:
    Crear un proyecto de ejemplo para testing.
    
    MERCADO OBJETIVO:
    Desarrolladores y testers.
    
    MODELO DE NEGOCIO:
    Freemium con características premium.
    
    EQUIPO:
    - Test User (CEO)
    - Demo Developer (CTO)
    """
    
    # Codificar a base64
    deck_base64 = base64.b64encode(example_deck.encode('utf-8')).decode('utf-8')
    
    payload = {
        "deck_file": deck_base64,
        "project_name": "TestStartup"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/analysis/project", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Project Analysis OK")
            print(f"   Mensaje: {result.get('message', 'N/A')}")
            if result.get('data'):
                data = result['data']
                print(f"   Proyecto: {data.get('project_name', 'N/A')}")
                print(f"   Equipo: {len(data.get('team_info', []))} miembros")
                print(f"   Repos: {len(data.get('github_repos', []))} repositorios")
            return True
        else:
            print(f"❌ Project Analysis falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en Project Analysis: {e}")
        return False

def test_gitroll_scan():
    """Prueba el GitRoll scan"""
    print("🔍 Probando GitRoll Scan...")
    
    payload = {
        "user": "octocat"  # Usuario de ejemplo de GitHub
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/analysis/gitroll/scan", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ GitRoll Scan OK")
            print(f"   Mensaje: {result.get('message', 'N/A')}")
            if result.get('scan_id'):
                print(f"   Scan ID: {result['scan_id']}")
                return result['scan_id']
            return None
        else:
            print(f"❌ GitRoll Scan falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en GitRoll Scan: {e}")
        return None

def test_gitroll_status(scan_id: str):
    """Prueba el estado del GitRoll scan"""
    if not scan_id:
        print("⚠️  Saltando GitRoll Status (no hay scan_id)")
        return True
    
    print("🔍 Probando GitRoll Status...")
    try:
        response = requests.get(f"{API_BASE_URL}/analysis/gitroll/status/{scan_id}")
        if response.status_code == 200:
            result = response.json()
            print("✅ GitRoll Status OK")
            print(f"   Estado: {result.get('status', 'N/A')}")
            if result.get('score'):
                print(f"   Score: {result['score']}")
            return True
        else:
            print(f"❌ GitRoll Status falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en GitRoll Status: {e}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de la API Money Mule Multiagent\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Analysis Health", test_analysis_health),
        ("Analysis Root", test_analysis_root),
        ("Project Analysis", test_project_analysis),
        ("GitRoll Scan", test_gitroll_scan),
    ]
    
    results = []
    scan_id = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        if test_name == "GitRoll Scan":
            scan_id = test_func()
            results.append((test_name, scan_id is not None))
        else:
            result = test_func()
            results.append((test_name, result))
        
        time.sleep(1)  # Pausa entre pruebas
    
    # Probar GitRoll Status si tenemos scan_id
    if scan_id:
        print(f"\n{'='*50}")
        print("🧪 GitRoll Status")
        print('='*50)
        result = test_gitroll_status(scan_id)
        results.append(("GitRoll Status", result))
    
    # Resumen de resultados
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE PRUEBAS")
    print('='*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La API está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs para más detalles.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 