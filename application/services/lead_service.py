import logging
from uuid import uuid4
from domain.models.lead import Lead

class LeadService:
    def __init__(self, lead_repo, opportunity_leads_repo):
        self.lead_repo = lead_repo
        self.opportunity_leads_repo = opportunity_leads_repo

    def create_leads_from_opportunity(self, opportunity_id: int, id_agte: int, created_by: str):
        opportunity = self.opportunity_leads_repo.get_by_opportunity_id_and_agte(opportunity_id, id_agte)

        leads_created = []

        for opp_lead in opportunity.leads:
            lead = Lead(
                CreatedBy=created_by,
                name=f"{opp_lead.nombres} {opp_lead.apellidos}",
                email=opp_lead.emailCliente,
                phone=opp_lead.celularCliente or opp_lead.telefonoCliente,
                documentNumber=opp_lead.nroDocum,
                company=None,
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
                Age=None,
                Gender=None,
                PreferredContactChannel=None,
                AdditionalInfo=opp_lead.extraDetails,
            )

            lead_id = str(uuid4())

            self.lead_repo.create_lead(lead, lead_id)

            logging.info(f"Lead created with ID: {lead_id}")

        return leads_created
