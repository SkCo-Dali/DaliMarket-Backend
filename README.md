# 📊 Market DALI - API de Oportunidades y Leads

## 🚀 Introducción

Este proyecto es una **API construida con FastAPI** para gestionar **oportunidades y leads comerciales**, utilizando **Azure Cosmos DB** como base de datos. La arquitectura sigue los principios de **Clean Architecture**, separando las responsabilidades en cuatro capas principales: `domain`, `application`, `infrastructure` y `presentation`. Este enfoque promueve un código más limpio, mantenible y fácil de escalar.

---

## 🛠️ Primeros Pasos

### Requisitos Previos

- **Python 3.11+**
- **pip** (gestor de paquetes de Python)
- Un entorno virtual (recomendado para aislar dependencias)
- Credenciales de acceso a una cuenta de **Azure Cosmos DB**.

### Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/tu-repo.git
    cd tu-repo
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate   # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura las variables de entorno:**
    Crea un archivo `.env` a partir del archivo `.env.template` y añade tus credenciales de **Azure Cosmos DB**.

---

## ▶️ Ejecución

Para iniciar la API en un entorno de desarrollo local, ejecuta el siguiente comando:

```bash
uvicorn presentation.main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`.

### Documentación Interactiva de la API

FastAPI genera automáticamente la documentación interactiva, la cual puedes usar para explorar y probar los endpoints:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📂 Estructura del Proyecto

El proyecto está organizado siguiendo los principios de Clean Architecture:

```
/
│
├── core/                  # Módulos transversales (configuración, excepciones, etc.)
│   ├── settings.py        # Carga de variables de entorno
│   ├── exceptions.py      # Excepciones personalizadas de la aplicación
│   └── logging_config.py  # Configuración del sistema de logs
│
├── domain/                # Contiene las entidades y reglas de negocio principales
│   └── models/
│       ├── Lead.py
│       ├── opportunity_detail.py
│       ├── opportunity_leads.py
│       └── opportunity_summary.py
│
├── application/           # Orquesta los casos de uso y la lógica de la aplicación
│   ├── ports/             # Interfaces (puertos) para los repositorios
│   │   ├── opportunity_detail_repository_port.py
│   │   └── opportunity_leads_repository_port.py
│   └── services/          # Implementación de los casos de uso
│       ├── opportunity_detail_service.py
│       ├── opportunity_leads_service.py
│       └── opportunity_summary_service.py
│
├── infrastructure/        # Implementaciones concretas de la tecnología
│   └── adapters/
│       ├── cosmos.py                                    # Conexión a Cosmos DB
│       ├── opportunity_detail_repository_adapter.py     # Adaptador para detalles de oportunidad
│       └── opportunity_leads_repository_adapter.py      # Adaptador para leads de oportunidad
│
├── presentation/          # Capa de entrada (API con FastAPI)
│   ├── routers/
│   │   ├── opportunity_detail_router.py
│   │   ├── opportunity_leads_router.py
│   │   └── opportunity_summary_router.py
│   └── main.py            # Punto de entrada de la aplicación FastAPI
│
├── tests/                 # Pruebas unitarias y de integración
│
├── .env.template          # Plantilla para variables de entorno
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Esta documentación
```

---

## Endpoints de la API

La API expone los siguientes recursos principales:

-   **`GET /opportunity-leads`**: Obtiene una lista de todas las oportunidades con sus leads asociados.
-   **`GET /opportunity-leads/{agte_id}`**: Obtiene las oportunidades con leads para un agente específico.
-   **`GET /opportunity-detail`**: Obtiene los detalles de todas las oportunidades (título, descripción, etc.).
-   **`GET /opportunity-detail/{opportunity_id}`**: Obtiene el detalle de una oportunidad específica.
-   **`GET /opportunity-summary/{agte_id}`**: Genera un resumen de las oportunidades para un agente, combinando detalles y el conteo de leads.

---

## ✅ Pruebas

Para ejecutar el conjunto de pruebas, utiliza `pytest`:

```bash
pytest
```

---

## 🤝 Contribuciones

Las contribuciones son siempre bienvenidas. Si deseas contribuir:

1.  Realiza un **fork** de este repositorio.
2.  Crea una nueva rama para tu funcionalidad (`git checkout -b feature/nombre-feature`).
3.  Realiza tus cambios y haz commit.
4.  Asegúrate de que todas las pruebas pasen.
5.  Envía un **Pull Request** con una descripción clara de tus cambios.

---

## 📚 Referencias

-   [Documentación de FastAPI](https://fastapi.tiangolo.com/)
-   [Azure Cosmos DB Python SDK](https://learn.microsoft.com/es-es/azure/cosmos-db/nosql/sdk-python)
-   [The Clean Architecture (artículo de Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
