# presentation/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.logging_config import LogLevels, configure_logging
from presentation.routers import opportunity_leads, opportunity_detail

configure_logging(LogLevels.info)

app = FastAPI(
    title="Market DALI",
    description="API for Market DALI",
    version="1.0.0",
)

app.include_router(opportunity_leads.router)
app.include_router(opportunity_detail.router)