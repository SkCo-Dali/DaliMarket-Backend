from typing import List, Optional
from uuid import UUID, uuid4
from domain.models.dali_lm_user import DaliLMUser, DaliLMUserInput
from application.ports.dali_lm_user_repository_port import DaliLMUserRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter

class DaliLMUserRepository(DaliLMUserRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def get_user_by_email(self, email: str) -> Optional[DaliLMUser]:
        query = "SELECT Id, Name, Email, Role, IsActive FROM dalilm.Users WHERE Email = ?"
        row = self.db_adapter.execute_query(query, (email,), fetchone=True)
        if row:
            return DaliLMUser(
                id=row[0],
                name=row[1],
                email=row[2],
                role=row[3],
                isActive=row[4]
            )
        return None

    def create_user(self, user_data: DaliLMUserInput) -> DaliLMUser:
        user_id = uuid4()

        insert_query = """
            INSERT INTO dalilm.Users (Id, Name, Email, Role, IsActive, CreatedAt, UpdatedAt)
            VALUES (?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())
        """
        self.db_adapter.execute_query(
            insert_query,
            (str(user_id), user_data.name, user_data.email, user_data.role, int(user_data.isActive))
        )

        # Call the stored procedure
        sp_query = "EXEC dalilm.SP_Actualiza_Usuario ?"
        self.db_adapter.execute_query(sp_query, (user_data.email,))

        return DaliLMUser(id=user_id, **user_data.model_dump())

    def list_users(self, name: Optional[str], email: Optional[str], role: Optional[str], is_active: Optional[bool], skip: int, limit: int) -> List[DaliLMUser]:
        base_query = "SELECT Id, Name, Email, Role, IsActive FROM dalilm.Users WHERE 1=1"
        params = []

        if name:
            base_query += " AND Name LIKE ?"
            params.append(f"%{name}%")
        if email:
            base_query += " AND Email LIKE ?"
            params.append(f"%{email}%")
        if role:
            base_query += " AND Role = ?"
            params.append(role)
        if is_active is not None:
            base_query += " AND IsActive = ?"
            params.append(1 if is_active else 0)

        base_query += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([skip, limit])

        rows = self.db_adapter.execute_query(base_query, tuple(params), fetchall=True)

        return [DaliLMUser(id=row[0], name=row[1], email=row[2], role=row[3], isActive=row[4]) for row in rows]

    def get_user_by_id(self, user_id: UUID) -> Optional[DaliLMUser]:
        query = "SELECT Id, Name, Email, Role, IsActive FROM dalilm.Users WHERE Id = ?"
        row = self.db_adapter.execute_query(query, (str(user_id),), fetchone=True)
        if row:
            return DaliLMUser(
                id=row[0],
                name=row[1],
                email=row[2],
                role=row[3],
                isActive=row[4]
            )
        return None

    def update_user(self, user_id: UUID, user_data: DaliLMUserInput) -> DaliLMUser:
        query = """
            UPDATE dalilm.Users
            SET Name = ?, Email = ?, Role = ?, IsActive = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(
            query,
            (user_data.name, user_data.email, user_data.role, int(user_data.isActive), str(user_id))
        )
        return DaliLMUser(id=user_id, **user_data.model_dump())

    def delete_user(self, user_id: UUID) -> None:
        query = """
            UPDATE dalilm.Users
            SET IsActive = 0, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(query, (str(user_id),))

    def search_users(self, query: str) -> List[DaliLMUser]:
        sql_query = """
            SELECT Id, Name, Email, Role, IsActive
            FROM dalilm.Users
            WHERE Name LIKE ? OR Email LIKE ?
            ORDER BY CreatedAt DESC
        """
        search_param = f"%{query}%"
        rows = self.db_adapter.execute_query(sql_query, (search_param, search_param), fetchall=True)
        return [DaliLMUser(id=row[0], name=row[1], email=row[2], role=row[3], isActive=row[4]) for row in rows]

    def set_user_status(self, user_id: UUID, is_active: bool) -> None:
        query = """
            UPDATE dalilm.Users
            SET IsActive = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(query, (int(is_active), str(user_id)))

    # I will implement the other methods later
    def get_user_roles(self) -> List[str]:
        pass
