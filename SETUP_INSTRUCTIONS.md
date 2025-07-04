# 🚀 Instrucciones de Configuración - Money Mule Multiagent

## 📋 Pasos para Inicializar el Repositorio

### **Opción 1: Script Automático (Recomendado)**

#### En Windows:
```bash
setup_windows.bat
```

#### En Linux/Mac:
```bash
chmod +x init_repo.sh
./init_repo.sh
```

### **Opción 2: Configuración Manual**

1. **Inicializar Git:**
```bash
git init
```

2. **Crear archivo .env:**
```bash
cp env.example .env
```

3. **Editar .env y agregar tu API key:**
```
OPENAI_API_KEY=tu_api_key_aqui
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Crear directorios necesarios:**
```bash
mkdir uploads logs
```

6. **Commit inicial:**
```bash
git add .
git commit -m "Initial commit: Money Mule Multiagent System"
```

## 🔧 Configuración de Postman

### **Importar Colección:**

1. Abre Postman
2. Haz clic en "Import"
3. Selecciona el archivo `postman_collection.json`
4. La colección se importará con todas las variables configuradas

### **Variables de Postman:**

- `base_url`: `http://localhost:8000`
- `deck_base64`: Contenido de ejemplo en base64
- `github_username`: `octocat` (usuario de prueba)
- `scan_id`: ID de ejemplo para GitRoll

### **Endpoints Disponibles:**

#### **Health Checks:**
- `GET /health` - Health check principal
- `GET /api/v1/analysis/health` - Health check del análisis

#### **Análisis de Proyectos:**
- `POST /api/v1/analysis/project` - Analizar proyecto
- `GET /api/v1/analysis/` - Información de endpoints

#### **GitRoll:**
- `POST /api/v1/analysis/gitroll/scan` - Iniciar escaneo
- `GET /api/v1/analysis/gitroll/status/{scan_id}` - Verificar estado

## 🧪 Pruebas del Sistema

### **Ejecutar Tests Automáticos:**
```bash
python test_api.py
```

### **Ejecutar Ejemplo Manual:**
```bash
python example_usage.py
```

### **Verificar Servidor:**
```bash
python main.py
```

## 🔗 URLs Importantes

- **API Base:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **ReDoc:** http://localhost:8000/redoc

## 📁 Estructura de Archivos

```
money-mule-multiagent/
├── 📄 main.py                    # Punto de entrada
├── 📄 requirements.txt           # Dependencias
├── 📄 env.example               # Variables de entorno
├── 📄 .env                      # Configuración (crear)
├── 📄 .gitignore                # Archivos ignorados
├── 📄 README.md                 # Documentación
├── 📄 postman_collection.json   # Colección Postman
├── 📄 example_usage.py          # Ejemplos de uso
├── 📄 test_api.py               # Tests automáticos
├── 📄 init_repo.sh              # Script Linux/Mac
├── 📄 setup_windows.bat         # Script Windows
├── 📄 SETUP_INSTRUCTIONS.md     # Este archivo
├── 📁 app/                      # Código de la aplicación
│   ├── 📁 core/                 # Configuración
│   ├── 📁 models/               # Modelos de datos
│   ├── 📁 routers/              # Endpoints API
│   └── 📁 services/             # Lógica de negocio
├── 📁 uploads/                  # Archivos subidos
└── 📁 logs/                     # Logs del sistema
```

## ⚠️ Notas Importantes

### **Requisitos:**
- Python 3.8+
- OpenAI API Key
- Git

### **Variables de Entorno Requeridas:**
- `OPENAI_API_KEY` - **OBLIGATORIO** para el funcionamiento

### **Puertos:**
- Puerto 8000 (configurable en .env)

### **Tamaño de Archivos:**
- Máximo 10MB por archivo (configurable)

## 🐛 Troubleshooting

### **Error: OpenAI API Key no válida**
```bash
# Verificar que .env existe y tiene la key
cat .env
```

### **Error: Puerto en uso**
```bash
# Cambiar puerto en .env
PORT=8001
```

### **Error: Dependencias no instaladas**
```bash
pip install -r requirements.txt
```

### **Error: Git no inicializado**
```bash
git init
git add .
git commit -m "Initial commit"
```

## 🎯 Próximos Pasos

1. ✅ Configurar API key de OpenAI
2. ✅ Ejecutar servidor: `python main.py`
3. ✅ Importar colección de Postman
4. ✅ Probar endpoints con Postman
5. ✅ Ejecutar tests: `python test_api.py`
6. ✅ Revisar documentación en `/docs`

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la consola
2. Verifica que todas las dependencias estén instaladas
3. Confirma que la API key de OpenAI sea válida
4. Ejecuta `python test_api.py` para diagnóstico

¡Listo para usar! 🚀 