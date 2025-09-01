# infrastructure/adapters/sqlserver_lead_repository.py
import pyodbc
import json
from application.ports.lead_repository_port import LeadRepositoryPort
from domain.models.lead import Lead


class LeadRepository(LeadRepositoryPort):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def create_lead(self, lead: Lead) -> None:
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()

        product_json = json.dumps(lead.product) if lead.product else None
        tags_json = json.dumps(lead.tags) if lead.tags else None
        portfolios_json = json.dumps(lead.SelectedPortfolios) if lead.SelectedPortfolios else None
        additional_info_json = json.dumps(lead.AdditionalInfo) if lead.AdditionalInfo else None

        cursor.execute("""
            INSERT INTO dalilm.Leads (
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                PreferredContactChannel, AdditionalInfo
            )
            VALUES (?, NEWID(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(),
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, lead.CreatedBy, lead.name, lead.email, lead.phone, lead.documentNumber, lead.company,
             lead.source, lead.campaign, product_json, lead.stage, lead.priority, lead.value,
             lead.assignedTo, lead.nextFollowUp, lead.notes, tags_json, lead.DocumentType,
             portfolios_json, lead.CampaignOwnerName, lead.Age, lead.Gender,
             lead.PreferredContactChannel, additional_info_json)

        conn.commit()
        cursor.close()
        conn.close()
