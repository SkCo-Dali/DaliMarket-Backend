from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException
from domain.models.dali_lm_interaction import DaliLMInteraction, DaliLMInteractionInput
from application.ports.dali_lm_interaction_repository_port import DaliLMInteractionRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter

class DaliLMInteractionRepository(DaliLMInteractionRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def update_interaction(self, interaction_id: UUID, interaction_data: dict) -> DaliLMInteraction:
        # First, check if the interaction exists
        if not self.db_adapter.execute_query("SELECT 1 FROM dalilm.Interactions WHERE Id = ?", (str(interaction_id),), fetchone=True):
            raise HTTPException(status_code=404, detail="Interacción no encontrada")

        updates = []
        values = []
        for field, value in interaction_data.items():
            updates.append(f"{field} = ?")
            values.append(value)

        values.append(str(interaction_id))

        query = f"UPDATE dalilm.Interactions SET {', '.join(updates)} WHERE Id = ?"
        self.db_adapter.execute_query(query, tuple(values))

        # This is not ideal, as it doesn't return the updated object
        # A better implementation would be to fetch the object again
        return self.get_interaction_by_id(interaction_id) # Assuming this method exists

    def delete_interaction(self, interaction_id: UUID) -> None:
        if not self.get_interaction_by_id(interaction_id):
            raise HTTPException(status_code=404, detail="Interacción no encontrada")

        self.db_adapter.execute_query("DELETE FROM dalilm.Interactions WHERE Id = ?", (str(interaction_id),))

    def get_interaction_by_id(self, interaction_id: UUID) -> Optional[DaliLMInteraction]:
        query = "SELECT Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt FROM dalilm.Interactions WHERE Id = ?"
        row = self.db_adapter.execute_query(query, (str(interaction_id),), fetchone=True)
        if row:
            return DaliLMInteraction(Id=row[0], LeadId=row[1], Type=row[2], Description=row[3], UserId=row[4], Outcome=row[5], Stage=row[6], CreatedAt=row[7])
        return None

    def get_interactions_by_lead(self, lead_id: UUID) -> List[DaliLMInteraction]:
        query = """
            SELECT Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
            FROM dalilm.Interactions
            WHERE LeadId = ?
            ORDER BY CreatedAt DESC
        """
        rows = self.db_adapter.execute_query(query, (str(lead_id),), fetchall=True)
        interactions = []
        for row in rows:
            interaction_dict = {
                "Id": row[0],
                "LeadId": row[1],
                "Type": row[2],
                "Description": row[3],
                "UserId": row[4],
                "Outcome": row[5],
                "Stage": row[6],
                "CreatedAt": row[7],
            }
            interactions.append(DaliLMInteraction(**interaction_dict))
        return interactions

    def create_interaction(self, interaction_data: DaliLMInteractionInput) -> DaliLMInteraction:
        # Validar que el Lead exista
        lead_exists = self.db_adapter.execute_query(
            "SELECT 1 FROM dalilm.Leads WHERE Id = ?",
            (str(interaction_data.LeadId),),
            fetchone=True
        )
        if not lead_exists:
            raise HTTPException(status_code=404, detail="El Lead especificado no existe.")

        # Validar que el usuario exista
        user_exists = self.db_adapter.execute_query(
            "SELECT 1 FROM dalilm.Users WHERE Id = ?",
            (str(interaction_data.UserId),),
            fetchone=True
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="El Usuario especificado no existe.")

        interaction_id = uuid4()
        created_at = datetime.utcnow() # Approximate time, real one is from DB

        query = """
            INSERT INTO dalilm.Interactions (
                Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, GETUTCDATE())
        """
        self.db_adapter.execute_query(
            query,
            (
                str(interaction_id),
                str(interaction_data.LeadId),
                interaction_data.Type,
                interaction_data.Description,
                str(interaction_data.UserId),
                interaction_data.Outcome,
                interaction_data.Stage,
            ),
        )

        return DaliLMInteraction(
            Id=interaction_id,
            CreatedAt=created_at,
            **interaction_data.model_dump()
        )
