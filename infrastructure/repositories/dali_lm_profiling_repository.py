from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from fastapi import HTTPException
import pyodbc
from domain.models.dali_lm_profiling import *
from application.ports.dali_lm_profiling_repository_port import DaliLMProfilingRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter

class DaliLMProfilingRepository(DaliLMProfilingRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

    def check_client_profile(self, email: Optional[str], id_number: Optional[str]) -> Optional[Tuple[UUID, bool]]:
        query = "SELECT TOP (1) ProfileId, IsCompleted FROM dalilm.ClientProfiles WHERE (ClientEmail = ? OR ClientIdentificationNumber = ?) ORDER BY CreatedAt DESC"
        row = self.db_adapter.execute_query(query, (email, id_number), fetchone=True)
        return (row[0], row[1]) if row else None

    def start_profiling(self, request: DaliLMStartProfilingRequest, user_id: Optional[UUID], user_email: str) -> UUID:
        query = "INSERT INTO dalilm.ClientProfiles (ClientEmail, ClientIdentificationNumber, ClientName, CreatedByUserId, CreatedByEmail) OUTPUT inserted.ProfileId VALUES (?, ?, ?, ?, ?)"
        try:
            row = self.db_adapter.execute_query(query, (request.clientEmail, request.clientIdentificationNumber, request.clientName, user_id, user_email), fetchone=True)
            self.db_adapter.commit()
            return row[0]
        except pyodbc.IntegrityError:
            self.db_adapter.rollback()
            raise HTTPException(status_code=409, detail="Ya existe un perfil para este cliente.")
        except Exception:
            self.db_adapter.rollback()
            raise

    def save_response(self, request: DaliLMSaveResponseRequest) -> int:
        profile_query = "SELECT IsCompleted FROM dalilm.ClientProfiles WHERE ProfileId = ?"
        profile_row = self.db_adapter.execute_query(profile_query, (str(request.profileId),), fetchone=True)
        if not profile_row: raise HTTPException(status_code=404, detail="Perfil no encontrado")
        if profile_row[0]: raise HTTPException(status_code=400, detail="El perfil ya está finalizado")

        order_query = "SELECT ISNULL(MAX(ResponseOrder), 0) + 1 FROM dalilm.ProfilingResponses WHERE ProfileId = ?"
        order = self.db_adapter.execute_query(order_query, (str(request.profileId),), fetchone=True)[0]

        insert_query = "INSERT INTO dalilm.ProfilingResponses (ProfileId, FlowStep, QuestionId, SelectedAnswer, AdditionalNotes, ResponseOrder) VALUES (?, ?, ?, ?, ?, ?)"
        self.db_adapter.execute_query(insert_query, (str(request.profileId), request.flowStep, request.questionId, request.selectedAnswer, request.additionalNotes, order))
        self.db_adapter.commit()
        return order

    def get_profiling_responses(self, profile_id: UUID) -> List[Tuple[str, str]]:
        query = "SELECT QuestionId, SelectedAnswer FROM dalilm.ProfilingResponses WHERE ProfileId = ? ORDER BY ResponseOrder ASC"
        rows = self.db_adapter.execute_query(query, (str(profile_id),), fetchall=True)
        return [(row[0], row[1]) for row in rows]

    def complete_profiling(self, profile_id: UUID, final_type: str, recommended: str, risk: str, strategy: str, result_json: str) -> None:
        try:
            results_query = "INSERT INTO dalilm.ProfilingResults (ProfileId, FinalProfileType, RecommendedProducts, RiskLevel, InvestmentStrategy, ResultData) VALUES (?, ?, ?, ?, ?, ?)"
            self.db_adapter.execute_query(results_query, (str(profile_id), final_type, recommended, risk, strategy, result_json))

            update_profile_query = "UPDATE dalilm.ClientProfiles SET ProfileType = ?, IsCompleted = 1 WHERE ProfileId = ?"
            self.db_adapter.execute_query(update_profile_query, (final_type, str(profile_id)))

            self.db_adapter.commit()
        except pyodbc.IntegrityError:
            self.db_adapter.rollback()
            raise HTTPException(status_code=409, detail="Este perfil ya tiene resultados guardados")
        except Exception:
            self.db_adapter.rollback()
            raise

    def get_profiling_result(self, profile_id: UUID) -> Optional[DaliLMProfilingResult]:
        query = "SELECT ProfileId, FinalProfileType, RecommendedProducts, RiskLevel, InvestmentStrategy, ResultData, CreatedAt FROM dalilm.ProfilingResults WHERE ProfileId = ?"
        row = self.db_adapter.execute_query(query, (str(profile_id),), fetchone=True)
        if row:
            return DaliLMProfilingResult(profileId=row[0], finalProfileType=row[1], recommendedProducts=row[2], riskLevel=row[3], investmentStrategy=row[4], resultData=row[5], createdAt=row[6].isoformat())
        return None
