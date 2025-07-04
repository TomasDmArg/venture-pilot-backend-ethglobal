#!/bin/bash

# Money Mule Multiagent - Repository Initialization Script
echo "🚀 Inicializando repositorio Money Mule Multiagent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado. Por favor instala Git primero."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instala Python 3 primero."
    exit 1
fi

# Initialize git repository
print_status "Inicializando repositorio Git..."
if [ ! -d ".git" ]; then
    git init
    print_success "Repositorio Git inicializado"
else
    print_warning "Repositorio Git ya existe"
fi

# Create .env file from example
print_status "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp env.example .env
    print_success "Archivo .env creado desde env.example"
    print_warning "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu OPENAI_API_KEY"
else
    print_warning "Archivo .env ya existe"
fi

# Create uploads directory
print_status "Creando directorio de uploads..."
mkdir -p uploads
print_success "Directorio uploads creado"

# Create logs directory
print_status "Creando directorio de logs..."
mkdir -p logs
print_success "Directorio logs creado"

# Install Python dependencies
print_status "Instalando dependencias de Python..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_success "Dependencias instaladas"
else
    print_error "Archivo requirements.txt no encontrado"
    exit 1
fi

# Add all files to git
print_status "Agregando archivos al repositorio..."
git add .
print_success "Archivos agregados al staging area"

# Create initial commit
print_status "Creando commit inicial..."
git commit -m "Initial commit: Money Mule Multiagent System

- Sistema multiagente con CrewAI
- API REST con FastAPI
- Integración con OpenAI y GitRoll
- Análisis de proyectos y founders
- Documentación completa"
print_success "Commit inicial creado"

# Create development branch
print_status "Creando rama de desarrollo..."
git checkout -b develop
print_success "Rama develop creada"

# Display next steps
echo ""
echo "🎉 ¡Repositorio inicializado exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env y agrega tu OPENAI_API_KEY"
echo "2. Ejecuta el servidor: python main.py"
echo "3. Prueba la API con Postman usando: postman_collection.json"
echo "4. Ejecuta el ejemplo: python example_usage.py"
echo ""
echo "🔗 URLs importantes:"
echo "- API: http://localhost:8000"
echo "- Documentación: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
echo ""
echo "📚 Recursos:"
echo "- README.md: Documentación completa"
echo "- postman_collection.json: Colección de Postman"
echo "- example_usage.py: Ejemplos de uso"
echo ""

# Check if .env has been configured
if grep -q "your_openai_api_key_here" .env; then
    print_warning "⚠️  Recuerda configurar tu OPENAI_API_KEY en el archivo .env"
fi

print_success "¡Setup completado! 🚀" 