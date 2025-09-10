from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_lead_assignment import DaliLMLeadAssignment
from application.ports.dali_lm_lead_assignment_repository_port import DaliLMLeadAssignmentRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter

class DaliLMLeadAssignmentRepository(DaliLMLeadAssignmentRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def get_current_assignments_by_user(self, user_id: UUID) -> List[DaliLMLeadAssignment]:
        query = """
        SELECT
            l.Id AS LeadId, l.Name AS LeadName, l.Email, l.Phone, l.Stage,
            l.Priority, l.Value, l.Source, l.Campaign, l.CreatedAt, lah.AssignedAt
        FROM dalilm.LeadAssignmentHistory lah
        INNER JOIN dalilm.Leads l ON lah.LeadId = l.Id
        WHERE lah.ToUserId = ? AND lah.IsActive = 1
        ORDER BY lah.AssignedAt DESC
        """
        rows = self.db_adapter.execute_query(query, (str(user_id),), fetchall=True)
        assignments = []
        for row in rows:
            assignment_dict = {
                "LeadId": row[0], "LeadName": row[1], "Email": row[2], "Phone": row[3],
                "Stage": row[4], "Priority": row[5], "Value": row[6], "Source": row[7],
                "Campaign": row[8], "CreatedAt": row[9], "AssignedAt": row[10]
            }
            assignments.append(DaliLMLeadAssignment(**assignment_dict))
        return assignments
