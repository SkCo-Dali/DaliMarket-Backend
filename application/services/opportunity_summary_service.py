# application/services/opportunity_summary_service.py
from typing import Dict, List, Optional
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail
from domain.models.opportunity_summary import OpportunitySummary

class OpportunitySummaryService:
    def __init__(self, opportunity_detail_repository: OpportunityDetailRepositoryPort, opportunity_leads_repository: OpportunityLeadsRepositoryPort):
        self.opportunity_detail_repository = opportunity_detail_repository
        self.opportunity_leads_repository = opportunity_leads_repository

    def list_details(self) -> List[OpportunityDetail]:
        return self.repository.get_all()
    
    def get_detail_by_opportunity_id(self, opportunity_id: str) -> Optional[OpportunityDetail]:
        return self.repository.get_by_opportunity_id(opportunity_id)
    
    def list_opportunity_summary_by_agte_id(self, agte_id: str) -> List[OpportunitySummary]:
        opportunities_leads = self.opportunity_leads_repository.get_by_agte_id(agte_id, status=1)
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