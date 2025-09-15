import logging
from uuid import uuid4
from application.ports.auth_port import AuthPort
from application.ports.lead_repository_port import LeadRepositoryPort
from application.ports.log_repository_port import LogRepositoryPort
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from application.ports.user_repository_port import UserRepositoryPort
from domain.models.lead import Lead
from domain.models.log import Log


class LeadService:
    def __init__(
            self, 
            lead_repo: LeadRepositoryPort, 
            opportunity_leads_repo: OpportunityLeadsRepositoryPort, 
            user_repo: UserRepositoryPort,
            log_repo: LogRepositoryPort,
            auth: AuthPort
    ):
        self.lead_repo = lead_repo
        self.opportunity_leads_repo = opportunity_leads_repo
        self.user_repo = user_repo
        self.log_repo = log_repo
        self.auth = auth

    def create_leads_from_opportunity(self, opportunity_id: int, token: str):
        current_user = self.auth.get_current_user(token)
        email = current_user["email"]
        user = self.user_repo.get_user_by_email(email)

        opportunity = self.opportunity_leads_repo.get_by_opportunity_id_and_agte(
            opportunity_id, user.id_agte
        )

        created_by = user.id

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

        # Guardar log
        log_entry = Log(
            id=str(uuid4()),
            user_id=user.id,
            user_email=email,
            opportunity_id=opportunity_id
        )
        self.log_repo.save(log_entry)

        return leads_created
