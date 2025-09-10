import logging
from uuid import uuid4
from application.ports.auth_port import AuthPort
from application.ports.lead_repository_port import LeadRepositoryPort
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from application.ports.user_repository_port import UserRepositoryPort
from domain.models.lead import Lead


class LeadService:
    def __init__(
            self, 
            lead_repo: LeadRepositoryPort, 
            opportunity_leads_repo: OpportunityLeadsRepositoryPort, 
            user_repo: UserRepositoryPort, 
            auth: AuthPort
    ):
        self.lead_repo = lead_repo
        self.opportunity_leads_repo = opportunity_leads_repo
        self.user_repo = user_repo
        self.auth = auth

    def create_leads_from_opportunity(
            self, opportunity_id: int, 
            id_agte: int,
            token: str
    ):
        opportunity = self.opportunity_leads_repo.get_by_opportunity_id_and_agte(
            opportunity_id, id_agte)
        
        if not opportunity:
            logging.warning(f"Opportunity with ID {opportunity_id} and AGTE {id_agte} not found.")
            return []

        current_user = self.auth.get_current_user(token)
        email = current_user["email"]

        created_by = self.user_repo.get_id_by_email(email)

        leads_created = []

        for opp_lead in opportunity.leads:
            logging.info(f"Processing lead: {opp_lead}")
            lead = Lead(
                CreatedBy=created_by,
                name=f"{opp_lead.nombres} {opp_lead.apellidos}",
                email=opp_lead.emailCliente,
                phone=opp_lead.celularCliente or opp_lead.telefonoCliente,
                documentNumber=opp_lead.nroDocum,
                company=opp_lead.empleadorCliente,
                source="Market Dali",
                campaign=None,
                product=[],
                stage="Nuevo",
                priority="Media",
                value=0,
                assignedTo=created_by,
                nextFollowUp=None,
                notes=None,
                tags=[],
                DocumentType=opp_lead.tipoDocum,
                SelectedPortfolios=[],
                CampaignOwnerName=None,
                Age=int(opp_lead.edad),
                Gender=opp_lead.sexo,
                PreferredContactChannel=None,
                AdditionalInfo=opp_lead.extraDetails,
            )

            logging.info(f"Creating lead in database: {lead}")

            lead_id = str(uuid4())

            self.lead_repo.create_lead(lead, lead_id)

            logging.info(f"Lead created with ID: {lead_id}")

            leads_created.append(lead)

        opportunity.Status = 0
        self.opportunity_leads_repo.update(opportunity)

        return leads_created
