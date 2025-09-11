from fastapi import HTTPException
from typing import List
from uuid import UUID
from domain.models.dali_lm_user import DaliLMUser, DaliLMUserInput
from application.ports.dali_lm_user_repository_port import DaliLMUserRepositoryPort
from application.ports.auth_port import AuthPort

class DaliLMUserService:
    def __init__(self, user_repository: DaliLMUserRepositoryPort, auth_adapter: AuthPort):
        self.user_repository = user_repository
        self.auth_adapter = auth_adapter

    def create_user(self, user_data: DaliLMUserInput, token: str) -> DaliLMUser:
        # 1. Authenticate and authorize the requester
        current_user = self.auth_adapter.get_current_user(token)
        requester_email = current_user.get("email")
        if not requester_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el email del token.")

        requester = self.user_repository.get_user_by_email(requester_email)
        if not requester or requester.role.lower() not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para crear usuarios.")

        # 2. Check if user already exists
        if self.user_repository.get_user_by_email(user_data.email):
            raise HTTPException(status_code=409, detail="Ya existe un usuario con este correo.")

        # 3. Create the user
        created_user = self.user_repository.create_user(user_data)
        return created_user

    def list_users(self, name: str, email: str, role: str, is_active: bool, skip: int, limit: int) -> List[DaliLMUser]:
        return self.user_repository.list_users(name, email, role, is_active, skip, limit)

    def get_user_by_id(self, user_id: UUID) -> DaliLMUser:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def delete_user(self, user_id: UUID, token: str) -> None:
        # 1. Authenticate and authorize the requester
        current_user = self.auth_adapter.get_current_user(token)
        requester_email = current_user.get("email")
        if not requester_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el email del token.")

        requester = self.user_repository.get_user_by_email(requester_email)
        if not requester or requester.role.lower() not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios.")

        # 2. Check if user exists
        if not self.user_repository.get_user_by_id(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # 3. Perform soft delete
        self.user_repository.delete_user(user_id)

    def get_user_roles(self) -> List[str]:
        return ['admin', 'seguridad', 'analista', 'supervisor', 'gestor', 'director', 'promotor', 'aliado', 'socio', 'fp']

    def search_users(self, query: str) -> List[DaliLMUser]:
        return self.user_repository.search_users(query)

    def set_user_status(self, user_id: UUID, is_active: bool, token: str) -> None:
        # 1. Authenticate and authorize the requester
        current_user = self.auth_adapter.get_current_user(token)
        requester_email = current_user.get("email")
        if not requester_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el email del token.")

        requester = self.user_repository.get_user_by_email(requester_email)
        if not requester or requester.role.lower() not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para cambiar el estado de usuarios.")

        # 2. Check if user exists
        if not self.user_repository.get_user_by_id(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # 3. Perform status update
        self.user_repository.set_user_status(user_id, is_active)

    def update_user(self, user_id: UUID, user_data: DaliLMUserInput, token: str) -> DaliLMUser:
        # 1. Authenticate and authorize the requester
        current_user = self.auth_adapter.get_current_user(token)
        requester_email = current_user.get("email")
        if not requester_email:
            raise HTTPException(status_code=401, detail="No se pudo obtener el email del token.")

        requester = self.user_repository.get_user_by_email(requester_email)
        if not requester or requester.role.lower() not in ["admin", "seguridad"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para actualizar usuarios.")

        # 2. Check if user exists
        if not self.user_repository.get_user_by_id(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # 3. Check for email conflict
        existing_user = self.user_repository.get_user_by_email(user_data.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="Ya existe otro usuario con este correo.")

        # 4. Update the user
        updated_user = self.user_repository.update_user(user_id, user_data)
        return updated_user
