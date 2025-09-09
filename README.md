# 📊 Oportunidades y Leads API

## 🚀 Introducción

Este proyecto es una **API construida con FastAPI** para gestionar **oportunidades y leads comerciales**, almacenados en **Azure Cosmos DB**.  
La arquitectura sigue principios de **Clean Architecture**, separando dominio, aplicación, infraestructura y presentación, lo que facilita la escalabilidad y el mantenimiento.

---

## 🛠️ Empezando

### Requisitos Previos

- **Python 3.11+**
- **pip** (gestor de dependencias)
- **Entorno virtual** (opcional pero recomendado)
- Acceso a **Azure Cosmos DB**

### Instalación

Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

Crea y activa un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Configura las variables de entorno:  
Crea un archivo `.env` basado en `.env.template` y completa tus credenciales de **Cosmos DB**.

---

## 📂 Estructura del Proyecto

```
project/
│
├── core/                  # Configuración y utilidades comunes
│   ├── settings.py        # Variables de entorno
│   ├── exceptions.py      # Excepciones custom
│   └── logging.py         # Configuración de logs
│
├── domain/                # Entidades del dominio
│   ├── opportunity.py
│   └── lead.py
│
├── application/           # Casos de uso y contratos
│   ├── ports/             # Interfaces de repositorios
│   │   ├── opportunity_repository.py
│   │   └── lead_repository.py
│   ├── services/          # Casos de uso / lógica de aplicación
│   │   ├── opportunity_service.py
│   │   └── lead_service.py
│   └── dtos/              # Modelos DTO
│
├── infrastructure/        # Implementaciones técnicas
│   ├── repositories/      
│   │   ├── opportunity_repository.py
│   │   └── lead_repository.py
│   └── adapters/          
│       └── cosmos_session.py  # Conexión a Cosmos DB
│
├── presentation/          # Capa de entrada (FastAPI)
│   ├── routers/           
│   │   ├── opportunities.py
│   │   └── leads.py
│   └── main.py            # Inicializa FastAPI y routers
│
├── tests/                 # Pruebas unitarias e integración
│   ├── unit/
│   └── integration/
│
└── .env                   # Variables de entorno
```

---

## ▶️ Ejecución

Para correr la API localmente:

```bash
uvicorn presentation.main:app --reload
```

Por defecto se expone en:  
👉 [http://localhost:8000](http://localhost:8000)

Documentación interactiva:  
- [Swagger UI](http://localhost:8000/docs)  
- [ReDoc](http://localhost:8000/redoc)

---

## ✅ Pruebas

Ejecuta las pruebas con:

```bash
pytest tests/
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas.  
Pasos para contribuir:

1. Haz un **fork** del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios.
4. Asegúrate de que las pruebas pasen.
5. Envía un **Pull Request** 🚀

---

## 📚 Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)  
- [Azure Cosmos DB Python SDK](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/sdk-python)  
- [Clean Architecture](https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html)  
