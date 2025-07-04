# Money Mule Multiagent System

Sistema multiagente para análisis de proyectos y founders utilizando CrewAI, FastAPI y OpenAI.

## Características

- **Análisis de Decks**: Extrae información clave de presentaciones de proyectos
- **Búsqueda de Founders**: Encuentra información de fundadores en LinkedIn, Twitter y GitHub
- **Análisis de GitHub**: Evalúa repositorios y contribuciones técnicas
- **Integración con GitRoll**: Escanea perfiles de GitHub para obtener scores
- **API REST**: Interfaz completa con FastAPI

## Arquitectura

El sistema utiliza un enfoque multiagente con CrewAI:

1. **Deck Analyzer Agent**: Analiza presentaciones de proyectos
2. **Founder Research Agent**: Busca información de fundadores
3. **GitHub Analyzer Agent**: Evalúa repositorios y código

## Instalación

### Prerrequisitos

- Python 3.8+
- OpenAI API Key
- Git

### Configuración

1. Clona el repositorio:
```bash
git clone <repository-url>
cd money-mule-multiagent
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
```bash
cp env.example .env
```

Edita el archivo `.env` y agrega tu API key de OpenAI:
```
OPENAI_API_KEY=tu_api_key_aqui
```

## Uso

### Ejecutar el servidor

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Endpoints de la API

#### 1. Analizar Proyecto
```bash
POST /api/v1/analysis/project
```

Body:
```json
{
  "deck_file": "base64_encoded_deck_content",
  "project_name": "Nombre del Proyecto (opcional)"
}
```

#### 2. Iniciar GitRoll Scan
```bash
POST /api/v1/analysis/gitroll/scan
```

Body:
```json
{
  "user": "github_username"
}
```

#### 3. Verificar Estado de GitRoll Scan
```bash
GET /api/v1/analysis/gitroll/status/{scan_id}
```

### Ejemplo de Uso con curl

```bash
# Analizar un proyecto
curl -X POST "http://localhost:8000/api/v1/analysis/project" \
  -H "Content-Type: application/json" \
  -d '{
    "deck_file": "base64_encoded_content",
    "project_name": "Mi Startup"
  }'

# Iniciar GitRoll scan
curl -X POST "http://localhost:8000/api/v1/analysis/gitroll/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "username"
  }'
```

## Estructura del Proyecto

```
money-mule-multiagent/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analysis_router.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   ├── founder_search_service.py
│   │   └── gitroll_service.py
│   └── __init__.py
├── main.py
├── requirements.txt
├── env.example
└── README.md
```

## Servicios

### AnalysisService
Servicio principal que coordina el análisis multiagente usando CrewAI.

### FounderSearchService
Busca información de fundadores en múltiples plataformas:
- LinkedIn
- Twitter/X
- GitHub

### GitRollService
Integra con la API de GitRoll para escanear perfiles de GitHub.

## Configuración Avanzada

### Variables de Entorno

- `OPENAI_API_KEY`: API key de OpenAI (requerido)
- `GITROLL_API_URL`: URL de la API de GitRoll
- `HOST`: Host del servidor (default: 0.0.0.0)
- `PORT`: Puerto del servidor (default: 8000)
- `DEBUG`: Modo debug (default: True)
- `MAX_FILE_SIZE`: Tamaño máximo de archivo (default: 10MB)

### Personalización de Agentes

Los agentes de CrewAI pueden ser personalizados editando el archivo `app/services/analysis_service.py`:

- Modificar roles y backstories
- Agregar herramientas personalizadas
- Ajustar prompts y tareas

## Desarrollo

### Agregar Nuevos Agentes

1. Crea un nuevo método en `AnalysisService`
2. Define el rol, objetivo y backstory del agente
3. Crea las tareas correspondientes
4. Integra el agente en el crew

### Agregar Nuevas Fuentes de Datos

1. Crea un nuevo servicio en `app/services/`
2. Implementa los métodos de búsqueda
3. Integra con el servicio de análisis

## Troubleshooting

### Error: OpenAI API Key no válida
- Verifica que la API key esté correctamente configurada en `.env`
- Asegúrate de que la key tenga créditos disponibles

### Error: GitRoll API no responde
- Verifica la conectividad a internet
- Revisa que la URL de GitRoll sea correcta

### Error: Análisis falla
- Verifica que el archivo del deck esté correctamente codificado en base64
- Revisa los logs del servidor para más detalles

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. 