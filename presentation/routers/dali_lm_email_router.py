from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from application.services.dali_lm_email_service import DaliLMEmailService
from domain.models.dali_lm_email import DaliLMEmailInput
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.dali_lm_email_log_repository import DaliLMEmailLogRepository
from infrastructure.repositories.dali_lm_user_repository import DaliLMUserRepository
from infrastructure.adapters.graph_api_adapter import GraphApiAdapter
from infrastructure.adapters.azure_auth_adapter import AzureAuthAdapter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/dalilm/emails", tags=["DaliLM Emails"])
security = HTTPBearer()

def get_dali_lm_email_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMEmailService:
    email_log_repo = DaliLMEmailLogRepository(sql)
    user_repo = DaliLMUserRepository(sql)
    graph_adapter = GraphApiAdapter()
    auth_adapter = AzureAuthAdapter()
    return DaliLMEmailService(email_log_repo, user_repo, graph_adapter, auth_adapter)

@router.post("/send", response_model=dict)
def send_emails(
    data: DaliLMEmailInput,
    request: Request,
    service: DaliLMEmailService = Depends(get_dali_lm_email_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Sends emails using Microsoft Graph API and logs the results.
    Requires an API token in 'Authorization' header and a Graph API token in 'X-Graph-Token' header.
    """
    graph_token = request.headers.get("X-Graph-Token")
    if not graph_token:
        raise HTTPException(status_code=400, detail="Falta header X-Graph-Token.")

    api_token = credentials.credentials

    try:
        results = service.send_emails(data, api_token, graph_token)
        return {"message": "Proceso completado", "results": results}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
