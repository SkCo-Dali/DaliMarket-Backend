from fastapi import HTTPException
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime
import json
from domain.models.dali_lm_profiling import *
from application.ports.dali_lm_profiling_repository_port import DaliLMProfilingRepositoryPort
from application.ports.auth_port import AuthPort
from application.ports.dali_lm_user_repository_port import DaliLMUserRepositoryPort

class DaliLMProfilingService:
    def __init__(self, repository: DaliLMProfilingRepositoryPort, auth_adapter: AuthPort, user_repository: DaliLMUserRepositoryPort):
        self.repository = repository
        self.auth_adapter = auth_adapter
        self.user_repository = user_repository

    def check_client(self, request: DaliLMCheckClientRequest) -> dict:
        if not request.email and not request.identificationNumber:
            raise HTTPException(status_code=400, detail="Debes enviar email o identificationNumber")
        result = self.repository.check_client_profile(request.email, request.identificationNumber)
        if result:
            return {"hasProfile": True, "profileId": str(result[0]), "isCompleted": bool(result[1])}
        return {"hasProfile": False, "profileId": None}

    def start_profiling(self, request: DaliLMStartProfilingRequest, token: str) -> dict:
        if not request.clientEmail and not request.clientIdentificationNumber:
            raise HTTPException(status_code=400, detail="Debes enviar clientEmail o clientIdentificationNumber")

        current_user = self.auth_adapter.get_current_user(token)
        user_email = current_user.get("email")
        user = self.user_repository.get_user_by_email(user_email)
        user_id = user.id if user else None

        # This logic for reusing an active profile should be in the service
        existing = self.repository.check_client_profile(request.clientEmail, request.clientIdentificationNumber)
        if existing and not existing[1]: # if profile exists and is not completed
            return {"profileId": str(existing[0]), "reused": True}

        new_id = self.repository.start_profiling(request, user_id, user_email)
        return {"profileId": str(new_id), "reused": False}

    def save_response(self, request: DaliLMSaveResponseRequest) -> dict:
        order = self.repository.save_response(request)
        return {"saved": True, "order": order}

    def complete_profiling(self, request: DaliLMCompleteProfilingRequest) -> dict:
        rows = self.repository.get_profiling_responses(request.profileId)
        if not rows:
            raise HTTPException(status_code=400, detail="No hay respuestas registradas para este perfil")

        categories = ['inmediatista', 'planificador', 'familiar', 'maduro']
        counts = {c: 0 for c in categories}
        for q_id, ans in rows:
            ans_lower = (ans or '').strip().lower()
            if ans_lower in counts:
                counts[ans_lower] += 1

        final_type = max(counts.items(), key=lambda kv: kv[1])[0]
        # Tie-breaking logic
        if len({v for v in counts.values() if v == counts[final_type]}) > 1:
            for q_id, ans in reversed(rows):
                ans_lower = (ans or '').strip().lower()
                if ans_lower in categories:
                    final_type = ans_lower
                    break

        product_map = {'inmediatista': 'Fondos de liquidez...', 'planificador': 'Fondos balanceados...', 'familiar': 'Seguros de vida...', 'maduro': 'Rentas vitalicias...'}
        risk_map = {'inmediatista': 'Bajo', 'familiar': 'Bajo a Medio', 'planificador': 'Medio', 'maduro': 'Bajo'}
        strategy_map = {'inmediatista': 'Liquidez...', 'planificador': 'Disciplina...', 'familiar': 'Protección...', 'maduro': 'Ingreso...'}

        recommended = product_map.get(final_type, '')
        risk = risk_map.get(final_type, 'Medio')
        strategy = strategy_map.get(final_type, '')

        result_json = json.dumps({
            "counts": counts, "answers": [{"q": q, "a": a} for q, a in rows],
            "finalData": request.finalData, "computedAt": datetime.utcnow().isoformat() + 'Z'
        })

        self.repository.complete_profiling(request.profileId, final_type, recommended, risk, strategy, result_json)

        return {"profileId": str(request.profileId), "finalProfileType": final_type, "riskLevel": risk, "recommendedProducts": recommended, "investmentStrategy": strategy}

    def get_results(self, profile_id: UUID) -> DaliLMProfilingResult:
        result = self.repository.get_profiling_result(profile_id)
        if not result:
            raise HTTPException(status_code=404, detail="Resultados no encontrados para este perfil")
        return result
