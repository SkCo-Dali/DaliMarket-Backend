from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from application.services.dali_lm_user_service import DaliLMUserService
from domain.models.dali_lm_user import DaliLMUser, DaliLMUserInput
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.adapters.azure_auth_adapter import AzureAuthAdapter
from infrastructure.repositories.dali_lm_user_repository import DaliLMUserRepository
from application.ports.auth_port import AuthPort

router = APIRouter(prefix="/dalilm/users", tags=["DaliLM Users"])
security = HTTPBearer()

def get_dali_lm_user_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMUserService:
    user_repo = DaliLMUserRepository(sql)
    auth_adapter = AzureAuthAdapter()
    return DaliLMUserService(user_repo, auth_adapter)

from fastapi import Query
from typing import Optional

@router.get("/", response_model=List[DaliLMUser])
def list_users(
    name: Optional[str] = Query(None, description="Filtrar por nombre"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    role: Optional[str] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a devolver"),
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
):
    """
    Lists users with filtering and pagination.
    """
    try:
        users = service.list_users(name, email, role, is_active, skip, limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from uuid import UUID

@router.get("/{user_id}", response_model=DaliLMUser)
def get_user_by_id(
    user_id: UUID,
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
):
    """
    Gets a specific user by their ID.
    """
    try:
        user = service.get_user_by_id(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import status

@router.get("/search/", response_model=List[DaliLMUser])
def search_users(
    query: str = Query(..., description="Texto a buscar en nombre o email"),
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
):
    """
    Searches for users by name or email.
    """
    return service.search_users(query)

@router.get("/roles/", response_model=List[str])
def get_user_roles(
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
):
    """
    Gets the list of available user roles.
    """
    return service.get_user_roles()

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Deletes a user (soft delete). Requires authentication and authorization.
    """
    try:
        token = credentials.credentials
        service.delete_user(user_id, token)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class UserStatusInput(BaseModel):
    is_active: bool

@router.put("/{user_id}/status", status_code=status.HTTP_204_NO_CONTENT)
def set_user_status(
    user_id: UUID,
    status_data: UserStatusInput,
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Sets a user's active status. Requires authentication and authorization.
    """
    try:
        token = credentials.credentials
        service.set_user_status(user_id, status_data.is_active, token)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=DaliLMUser)
def update_user(
    user_id: UUID,
    user_data: DaliLMUserInput,
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Updates a user. Requires authentication and authorization.
    """
    try:
        token = credentials.credentials
        updated_user = service.update_user(user_id, user_data, token)
        return updated_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=DaliLMUser)
def create_user(
    user_data: DaliLMUserInput,
    service: DaliLMUserService = Depends(get_dali_lm_user_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Creates a new user in the system based on the DaliLM logic.
    Requires authentication and authorization.
    """
    try:
        token = credentials.credentials
        created_user = service.create_user(user_data, token)
        return created_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
