# infrastructure/repositories/lead_repository.py
import json
from domain.models.lead_ import Lead
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter
from fastapi import HTTPException


class LeadRepository:
    def __init__(self, adapter: SqlServerAdapter):
        self.adapter = adapter

    def create_lead(self, lead: Lead, lead_id: str):
        """
        Inserta un lead en SQL Server en las tablas Leads y LeadsRaw.
        """
        try:
            # Serializar campos JSON
            product_json = json.dumps(lead.product) if lead.product else None
            tags_json = json.dumps(lead.tags) if lead.tags else None
            portfolios_json = json.dumps(lead.SelectedPortfolios) if lead.SelectedPortfolios else None
            additional_info_json = json.dumps(lead.AdditionalInfo) if lead.AdditionalInfo else None

            # Verificar si el usuario asignado existe
            user_exists = self.adapter.execute_query(
                "SELECT 1 FROM dalilm.Users WHERE Id = ?",
                (lead.assignedTo,),
                fetchone=True
            )
            if not user_exists:
                raise HTTPException(status_code=404, detail="El usuario asignado no existe.")

            # Insertar en Leads
            insert_lead_query = """
                INSERT INTO dalilm.Leads (
                    CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                    Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                    NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                    PreferredContactChannel, AdditionalInfo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(),
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.adapter.execute_query(
                insert_lead_query,
                (
                    lead.CreatedBy, lead_id, lead.name, lead.email, lead.phone, lead.documentNumber,
                    lead.company, lead.source, lead.campaign, product_json, lead.stage, lead.priority,
                    lead.value, lead.assignedTo, lead.nextFollowUp, lead.notes, tags_json,
                    lead.DocumentType, portfolios_json, lead.CampaignOwnerName, lead.Age,
                    lead.Gender, lead.PreferredContactChannel, additional_info_json
                )
            )

            # Insertar copia en LeadsRaw
            insert_raw_query = """
                INSERT INTO dalilm.LeadsRaw (
                    CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                    Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                    NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                    PreferredContactChannel, AdditionalInfo
                )
                SELECT 
                    CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                    Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                    NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                    PreferredContactChannel, AdditionalInfo
                FROM dalilm.Leads
                WHERE Id = ?
            """
            self.adapter.execute_query(insert_raw_query, (lead_id,))

        except HTTPException:
            # Se relanza si ya fue manejado (ej: usuario no existe)
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al crear lead: {str(e)}")
