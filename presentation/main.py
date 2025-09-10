# presentation/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.logging_config import LogLevels, configure_logging
from presentation.routers import opportunity_detail_router, opportunity_leads_router, opportunity_summary_router, lead_router, dali_lm_lead_router, dali_lm_user_router, dali_lm_interaction_router, dali_lm_lead_assignment_router, dali_lm_email_router, dali_lm_profiling_router, dali_lm_whatsapp_router

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
app.include_router(dali_lm_lead_router.router)
app.include_router(dali_lm_user_router.router)
app.include_router(dali_lm_interaction_router.router)
app.include_router(dali_lm_lead_assignment_router.router)
app.include_router(dali_lm_email_router.router)
app.include_router(dali_lm_profiling_router.router)
app.include_router(dali_lm_whatsapp_router.router)