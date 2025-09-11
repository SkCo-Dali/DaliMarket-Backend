from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from application.services.dali_lm_profiling_service import DaliLMProfilingService
from domain.models.dali_lm_profiling import *
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.dali_lm_profiling_repository import DaliLMProfilingRepository
from infrastructure.repositories.dali_lm_user_repository import DaliLMUserRepository
from infrastructure.adapters.azure_auth_adapter import AzureAuthAdapter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/dalilm/profiling", tags=["DaliLM Profiling"])
security = HTTPBearer()

def get_dali_lm_profiling_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMProfilingService:
    repo = DaliLMProfilingRepository(sql)
    auth_adapter = AzureAuthAdapter()
    user_repo = DaliLMUserRepository(sql)
    return DaliLMProfilingService(repo, auth_adapter, user_repo)

@router.post('/check-client', response_model=dict)
def check_client(
    payload: DaliLMCheckClientRequest,
    service: DaliLMProfilingService = Depends(get_dali_lm_profiling_service),
):
    return service.check_client(payload)

@router.post('/start', status_code=status.HTTP_201_CREATED, response_model=dict)
def start_profiling(
    payload: DaliLMStartProfilingRequest,
    service: DaliLMProfilingService = Depends(get_dali_lm_profiling_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return service.start_profiling(payload, credentials.credentials)

@router.post('/save-response', status_code=status.HTTP_201_CREATED, response_model=dict)
def save_response(
    payload: DaliLMSaveResponseRequest,
    service: DaliLMProfilingService = Depends(get_dali_lm_profiling_service),
):
    return service.save_response(payload)

@router.post('/complete', response_model=dict)
def complete_profiling(
    payload: DaliLMCompleteProfilingRequest,
    service: DaliLMProfilingService = Depends(get_dali_lm_profiling_service),
):
    return service.complete_profiling(payload)

@router.get('/results/{profile_id}', response_model=DaliLMProfilingResult)
def get_results(
    profile_id: UUID,
    service: DaliLMProfilingService = Depends(get_dali_lm_profiling_service),
):
    return service.get_results(profile_id)
