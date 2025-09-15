# application/services/opportunity_summary_service.py
import logging
from typing import Dict, List, Optional
from application.ports.auth_port import AuthPort
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from application.ports.user_repository_port import UserRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail
from domain.models.opportunity_summary import OpportunitySummary

class OpportunitySummaryService:
    def __init__(
            self, 
            opportunity_detail_repository: OpportunityDetailRepositoryPort, 
            opportunity_leads_repository: OpportunityLeadsRepositoryPort,
            auth: AuthPort,
            user_repo: UserRepositoryPort
    ):
        self.opportunity_detail_repository = opportunity_detail_repository
        self.opportunity_leads_repository = opportunity_leads_repository
        self.auth = auth
        self.user_repo = user_repo

    def list_details(self) -> List[OpportunityDetail]:
        return self.repository.get_all()
    
    def get_detail_by_opportunity_id(self, opportunity_id: str) -> Optional[OpportunityDetail]:
        return self.repository.get_by_opportunity_id(opportunity_id)
    
    def list_opportunity_summary_by_agte_id(self, token: str) -> List[OpportunitySummary]:
        
        current_user = self.auth.get_current_user(token)
        email = current_user["email"]
        agte_id = self.user_repo.get_id_agte_by_email(email)

        logging.info(f"Fetching opportunity summaries for agte_id: {agte_id}")

        opportunities_leads = self.opportunity_leads_repository.get_by_agte_id(agte_id)
        logging.info(f"Opportunities leads fetched: {opportunities_leads}")
        logging.info(f"Found {len(opportunities_leads)} opportunity leads for agte_id: {agte_id}")
        summaries = []
        for opportunity_lead in opportunities_leads:
            opportunity_id = opportunity_lead.OpportunityId
            detail = self.opportunity_detail_repository.get_by_opportunity_id(opportunity_id)
            if detail:
                summary = OpportunitySummary(
                    OpportunityId=detail.OpportunityId,
                    Priority=opportunity_lead.Priority,
                    lead_count=len(opportunity_lead.leads),
                    Title=detail.Title,
                    Subtitle=detail.Subtitle,
                    Description=detail.Description,
                    Categories=detail.Categories
                )
                summaries.append(summary)
        return summaries