# application/services/lead_service.py
from typing import List
from domain.models.opportunity_leads import OpportunityLeads
from domain.models.lead import Lead
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from application.ports.lead_repository_port import LeadRepositoryPort


class LeadService:
    def __init__(
        self,
        opportunity_leads_repo: OpportunityLeadsRepositoryPort,
        lead_repo: LeadRepositoryPort
    ):
        self.opportunity_leads_repo = opportunity_leads_repo
        self.lead_repo = lead_repo

    def create_leads_from_opportunity(self, opportunity_id: int, id_agte: int, created_by: str) -> List[Lead]:
        """
        Dado un opportunity_id y un id_agte, recupera los OpportunityLeads 
        y crea leads en SQL Server.
        """
        # 1. Obtener los opportunity leads desde Cosmos (u otro origen)
        opportunity: OpportunityLeads = self.opportunity_leads_repo.get_by_opportunity_id_and_agte(
            opportunity_id, id_agte
        )

        if not opportunity:
            raise ValueError(f"No se encontró oportunidad con id={opportunity_id} y idAgte={id_agte}")

        created_leads: List[Lead] = []

        # 2. Mapear cada OpportunityLead a LeadInput
        for opp_lead in opportunity.leads:
            lead = Lead(
                CreatedBy=created_by,
                name=f"{opp_lead.nombres} {opp_lead.apellidos}",
                email=opp_lead.emailCliente,
                phone=opp_lead.telefonoCliente or opp_lead.celularCliente,
                documentNumber=opp_lead.nroDocum,
                company=None,  # no viene de OpportunityLead
                source="Oportunidad",  # puedes setear el origen fijo o dinámico
                campaign=None,
                product=None,
                stage="Nuevo",  # estado inicial fijo
                priority="Media",  # prioridad por defecto
                value=0,
                assignedTo=created_by,  # asignado al vendedor
                nextFollowUp=None,
                notes=f"Generado desde oportunidad {opportunity.OpportunityId}",
                tags=None,
                DocumentType=opp_lead.tipoDocum,
                SelectedPortfolios=None,
                CampaignOwnerName=None,
                Age=None,
                Gender=None,
                PreferredContactChannel=None,
                AdditionalInfo=opp_lead.extraDetails
            )

            # 3. Guardar en el repositorio de leads
            self.lead_repo.create_lead(lead)
            created_leads.append(lead)

        return created_leads
