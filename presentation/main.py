# presentation/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.logging_config import LogLevels, configure_logging
from presentation.routers import opportunity_detail_router, opportunity_leads_router, opportunity_summary_router, lead_router, secure_router

configure_logging(LogLevels.info)

app = FastAPI(
    title="Market DALI",
    description="API for Market DALI",
    version="1.0.0",
)

app.include_router(opportunity_leads_router.router)
app.include_router(opportunity_detail_router.router)
app.include_router(opportunity_summary_router.router)
app.include_router(lead_router.router)
app.include_router(secure_router.router)  # Uncomment this line to include the secure router