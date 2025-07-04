@echo off
chcp 65001 >nul
echo 🚀 Inicializando repositorio Money Mule Multiagent...

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no está instalado. Por favor instala Git primero.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado. Por favor instala Python primero.
    pause
    exit /b 1
)

REM Initialize git repository
echo [INFO] Inicializando repositorio Git...
if not exist ".git" (
    git init
    echo [SUCCESS] Repositorio Git inicializado
) else (
    echo [WARNING] Repositorio Git ya existe
)

REM Create .env file from example
echo [INFO] Configurando variables de entorno...
if not exist ".env" (
    copy env.example .env
    echo [SUCCESS] Archivo .env creado desde env.example
    echo [WARNING] ⚠️  IMPORTANTE: Edita el archivo .env y agrega tu OPENAI_API_KEY
) else (
    echo [WARNING] Archivo .env ya existe
)

REM Create uploads directory
echo [INFO] Creando directorio de uploads...
if not exist "uploads" mkdir uploads
echo [SUCCESS] Directorio uploads creado

REM Create logs directory
echo [INFO] Creando directorio de logs...
if not exist "logs" mkdir logs
echo [SUCCESS] Directorio logs creado

REM Install Python dependencies
echo [INFO] Instalando dependencias de Python...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [SUCCESS] Dependencias instaladas
) else (
    echo [ERROR] Archivo requirements.txt no encontrado
    pause
    exit /b 1
)

REM Add all files to git
echo [INFO] Agregando archivos al repositorio...
git add .
echo [SUCCESS] Archivos agregados al staging area

REM Create initial commit
echo [INFO] Creando commit inicial...
git commit -m "Initial commit: Money Mule Multiagent System

- Sistema multiagente con CrewAI
- API REST con FastAPI
- Integración con OpenAI y GitRoll
- Análisis de proyectos y founders
- Documentación completa"
echo [SUCCESS] Commit inicial creado

REM Create development branch
echo [INFO] Creando rama de desarrollo...
git checkout -b develop
echo [SUCCESS] Rama develop creada

REM Display next steps
echo.
echo 🎉 ¡Repositorio inicializado exitosamente!
echo.
echo 📋 Próximos pasos:
echo 1. Edita el archivo .env y agrega tu OPENAI_API_KEY
echo 2. Ejecuta el servidor: python main.py
echo 3. Prueba la API con Postman usando: postman_collection.json
echo 4. Ejecuta el ejemplo: python example_usage.py
echo.
echo 🔗 URLs importantes:
echo - API: http://localhost:8000
echo - Documentación: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo.
echo 📚 Recursos:
echo - README.md: Documentación completa
echo - postman_collection.json: Colección de Postman
echo - example_usage.py: Ejemplos de uso
echo.

REM Check if .env has been configured
findstr "your_openai_api_key_here" .env >nul
if not errorlevel 1 (
    echo [WARNING] ⚠️  Recuerda configurar tu OPENAI_API_KEY en el archivo .env
)

echo [SUCCESS] ¡Setup completado! 🚀
pause 