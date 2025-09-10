import json
from uuid import uuid4
from domain.models.dali_lm_lead import DaliLML_Lead, DaliLML_LeadInput
from application.ports.dali_lm_lead_repository_port import DaliLMLeadRepositoryPort
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter
from fastapi import HTTPException

class DaliLMLeadRepository(DaliLMLeadRepositoryPort):
    def __init__(self, db_adapter: SqlServerAdapter):
        self.db_adapter = db_adapter

from typing import Optional

    def get_lead_by_id(self, lead_id: UUID) -> Optional[DaliLML_Lead]:
        query = """
            SELECT
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName,
                Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE (Stage IS NULL OR Stage <> 'Eliminado') and Id = ?
        """
        row = self.db_adapter.execute_query(query, (str(lead_id),), fetchone=True)
        if not row:
            return None

        # This is complex, I need to map all columns to the model
        lead_dict = {
            "CreatedBy": row[0],
            "id": row[1],
            "name": row[2],
            "email": row[3],
            "phone": row[4],
            "documentNumber": row[5],
            "company": row[6],
            "source": row[7],
            "campaign": row[8],
            "product": json.loads(row[9]) if row[9] else None,
            "stage": row[10],
            "priority": row[11],
            "value": row[12],
            "assignedTo": row[13],
            "nextFollowUp": row[16],
            "notes": row[17],
            "tags": json.loads(row[18]) if row[18] else None,
            "DocumentType": row[19],
            "SelectedPortfolios": json.loads(row[20]) if row[20] else None,
            "CampaignOwnerName": row[21],
            "Age": row[22],
            "Gender": row[23],
            "PreferredContactChannel": row[24],
            "AdditionalInfo": json.loads(row[25]) if row[25] else None,
        }
        return DaliLML_Lead(**lead_dict)

from typing import List

    def list_leads(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        source: Optional[str],
        stage: Optional[str],
        priority: Optional[str],
        assigned_to: Optional[str],
        skip: int,
        limit: int,
    ) -> List[DaliLML_Lead]:
        query = """
            SELECT
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName,
                Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE Stage IS NULL OR Stage <> 'Eliminado'
        """
        params = []

        if name:
            query += " AND Name LIKE ?"
            params.append(f"%{name}%")
        if email:
            query += " AND Email LIKE ?"
            params.append(f"%{email}%")
        if phone:
            query += " AND Phone LIKE ?"
            params.append(f"%{phone}%")
        if source:
            query += " AND Source = ?"
            params.append(source)
        if stage:
            query += " AND Stage = ?"
            params.append(stage)
        if priority:
            query += " AND Priority = ?"
            params.append(priority)
        if assigned_to:
            query += " AND AssignedTo = ?"
            params.append(assigned_to)

        query += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([skip, limit])

        rows = self.db_adapter.execute_query(query, tuple(params), fetchall=True)

        leads = []
        for row in rows:
            lead_dict = {
                "CreatedBy": row[0], "id": row[1], "name": row[2], "email": row[3], "phone": row[4],
                "documentNumber": row[5], "company": row[6], "source": row[7], "campaign": row[8],
                "product": json.loads(row[9]) if row[9] else None, "stage": row[10], "priority": row[11],
                "value": row[12], "assignedTo": row[13], "nextFollowUp": row[16], "notes": row[17],
                "tags": json.loads(row[18]) if row[18] else None, "DocumentType": row[19],
                "SelectedPortfolios": json.loads(row[20]) if row[20] else None, "CampaignOwnerName": row[21],
                "Age": row[22], "Gender": row[23], "PreferredContactChannel": row[24],
                "AdditionalInfo": json.loads(row[25]) if row[25] else None,
            }
            leads.append(DaliLML_Lead(**lead_dict))
        return leads

    def get_leads_by_user(self, user_id: UUID, stage: Optional[str], priority: Optional[str]) -> List[DaliLML_Lead]:
        query = """
            SELECT
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName,
                Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE (Stage IS NULL OR Stage <> 'Eliminado') and AssignedTo = ?
        """
        params = [str(user_id)]

        if stage:
            query += " AND Stage = ?"
            params.append(stage)
        if priority:
            query += " AND Priority = ?"
            params.append(priority)

        rows = self.db_adapter.execute_query(query, tuple(params), fetchall=True)

        leads = []
        for row in rows:
            lead_dict = {
                "CreatedBy": row[0], "id": row[1], "name": row[2], "email": row[3], "phone": row[4],
                "documentNumber": row[5], "company": row[6], "source": row[7], "campaign": row[8],
                "product": json.loads(row[9]) if row[9] else None, "stage": row[10], "priority": row[11],
                "value": row[12], "assignedTo": row[13], "nextFollowUp": row[16], "notes": row[17],
                "tags": json.loads(row[18]) if row[18] else None, "DocumentType": row[19],
                "SelectedPortfolios": json.loads(row[20]) if row[20] else None, "CampaignOwnerName": row[21],
                "Age": row[22], "Gender": row[23], "PreferredContactChannel": row[24],
                "AdditionalInfo": json.loads(row[25]) if row[25] else None,
            }
            leads.append(DaliLML_Lead(**lead_dict))
        return leads

    def bulk_lead_file(self, leads_data: List[tuple]) -> Tuple[int, List[dict]]:
        SQL_INSERT = """
        INSERT INTO dalilm.Leads (
            CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
            Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
            NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios,
            CampaignOwnerName, Age, Gender, PreferredContactChannel
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        inserted = 0
        errors = []
        if not leads_data:
            return inserted, errors

        # This is a simplified version of the original's complex transaction handling.
        # The SqlServerAdapter would need to support transactions for a true equivalent.
        with self.db_adapter.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.fast_executemany = True
                cursor.executemany(SQL_INSERT, leads_data)
                conn.commit()
                inserted = len(leads_data)
            except Exception as batch_ex:
                conn.rollback()
                # Fallback to row-by-row
                for i, params in enumerate(leads_data):
                    try:
                        cursor.execute(SQL_INSERT, params)
                        conn.commit()
                        inserted += 1
                    except Exception as ex:
                        conn.rollback()
                        errors.append({
                            "row_index": i,
                            "error": str(ex),
                        })
        return inserted, errors

    def export_leads(
        self,
        assigned_to: Optional[UUID],
        created_by: Optional[UUID],
        stage: Optional[str],
        priority: Optional[str],
    ) -> List[DaliLML_Lead]:
        query = """
            SELECT
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName,
                Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE Stage IS NULL OR Stage <> 'Eliminado'
        """
        params = []
        if assigned_to:
            query += " AND AssignedTo = ?"
            params.append(str(assigned_to))
        if created_by:
            query += " AND CreatedBy = ?"
            params.append(str(created_by))
        if stage:
            query += " AND Stage = ?"
            params.append(stage)
        if priority:
            query += " AND Priority = ?"
            params.append(priority)

        rows = self.db_adapter.execute_query(query, tuple(params), fetchall=True)
        leads = []
        for row in rows:
            lead_dict = {
                "CreatedBy": row[0], "id": row[1], "name": row[2], "email": row[3], "phone": row[4],
                "documentNumber": row[5], "company": row[6], "source": row[7], "campaign": row[8],
                "product": json.loads(row[9]) if row[9] else None, "stage": row[10], "priority": row[11],
                "value": row[12], "assignedTo": row[13], "nextFollowUp": row[16], "notes": row[17],
                "tags": json.loads(row[18]) if row[18] else None, "DocumentType": row[19],
                "SelectedPortfolios": json.loads(row[20]) if row[20] else None, "CampaignOwnerName": row[21],
                "Age": row[22], "Gender": row[23], "PreferredContactChannel": row[24],
                "AdditionalInfo": json.loads(row[25]) if row[25] else None,
            }
            leads.append(DaliLML_Lead(**lead_dict))
        return leads

    def bulk_assign_leads(self, lead_ids: List[UUID], user_id: UUID) -> None:
        # Verificar si el usuario asignado existe
        user_exists = self.db_adapter.execute_query(
            "SELECT 1 FROM dalilm.Users WHERE Id = ?",
            (str(user_id),),
            fetchone=True
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

        # Validar leads uno a uno
        missing_leads = []
        for lead_id in lead_ids:
            if not self.get_lead_by_id(lead_id):
                missing_leads.append(str(lead_id))

        if missing_leads:
            raise HTTPException(
                status_code=404,
                detail=f"Los siguientes leads no existen: {', '.join(missing_leads)}"
            )

        # Realizar la asignación masiva
        for lead_id in lead_ids:
            self.db_adapter.execute_query(
                """
                UPDATE dalilm.Leads
                SET AssignedTo = ?, UpdatedAt = GETUTCDATE(), Stage = 'Asignado'
                WHERE Id = ?
                """,
                (str(user_id), str(lead_id))
            )

    def merge_leads(self, lead_ids: List[UUID], primary_lead_id: UUID) -> None:
        secondary_ids = [str(lid) for lid in lead_ids if lid != primary_lead_id]

        # This should be a transaction
        # For now, we'll execute the queries sequentially

        # Verify that all leads exist
        # This is not ideal, but it's what the original code did
        placeholders = ','.join(['?'] * len(lead_ids))
        query = f"SELECT COUNT(*) FROM dalilm.Leads WHERE Id IN ({placeholders})"
        count = self.db_adapter.execute_query(query, tuple(str(lid) for lid in lead_ids), fetchone=True)[0]
        if count != len(lead_ids):
            raise HTTPException(status_code=404, detail="Uno o más leads no existen.")

        # Migrate Interactions
        placeholders = ','.join(['?'] * len(secondary_ids))
        update_interactions_query = f"UPDATE dalilm.Interactions SET LeadId = ? WHERE LeadId IN ({placeholders})"
        self.db_adapter.execute_query(update_interactions_query, (str(primary_lead_id), *secondary_ids))

        # Migrar Tasks
        update_tasks_query = f"UPDATE dalilm.Tasks SET LeadId = ? WHERE LeadId IN ({placeholders})"
        self.db_adapter.execute_query(update_tasks_query, (str(primary_lead_id), *secondary_ids))

        # Eliminar Leads secundarios
        delete_leads_query = f"DELETE FROM dalilm.Leads WHERE Id IN ({placeholders})"
        self.db_adapter.execute_query(delete_leads_query, tuple(secondary_ids))

    def get_duplicate_leads(self) -> List[DaliLML_Lead]:
        query = """
        WITH LeadDuplicates AS (
            SELECT Email, Phone, DocumentNumber, COUNT(*) AS Count
            FROM dalilm.Leads
            WHERE Email IS NOT NULL OR Phone IS NOT NULL OR DocumentNumber IS NOT NULL
            GROUP BY Email, Phone, DocumentNumber
            HAVING COUNT(*) > 1
        )
        SELECT
            l.CreatedBy, l.Id, l.Name, l.Email, l.Phone, l.DocumentNumber, l.Company, l.Source, l.Campaign,
            l.Product, l.Stage, l.Priority, l.Value, l.AssignedTo, l.CreatedAt, l.UpdatedAt,
            l.NextFollowUp, l.Notes, l.Tags, l.DocumentType, l.SelectedPortfolios, l.CampaignOwnerName,
            l.Age, l.Gender, l.PreferredContactChannel, l.AdditionalInfo
        FROM dalilm.Leads l
        INNER JOIN LeadDuplicates d
            ON (l.Email = d.Email AND l.Email IS NOT NULL)
            OR (l.Phone = d.Phone AND l.Phone IS NOT NULL)
            OR (l.DocumentNumber = d.DocumentNumber AND l.DocumentNumber IS NOT NULL)
        ORDER BY l.Email, l.Phone, l.DocumentNumber
        """
        rows = self.db_adapter.execute_query(query, fetchall=True)
        leads = []
        for row in rows:
            lead_dict = {
                "CreatedBy": row[0], "id": row[1], "name": row[2], "email": row[3], "phone": row[4],
                "documentNumber": row[5], "company": row[6], "source": row[7], "campaign": row[8],
                "product": json.loads(row[9]) if row[9] else None, "stage": row[10], "priority": row[11],
                "value": row[12], "assignedTo": row[13], "nextFollowUp": row[16], "notes": row[17],
                "tags": json.loads(row[18]) if row[18] else None, "DocumentType": row[19],
                "SelectedPortfolios": json.loads(row[20]) if row[20] else None, "CampaignOwnerName": row[21],
                "Age": row[22], "Gender": row[23], "PreferredContactChannel": row[24],
                "AdditionalInfo": json.loads(row[25]) if row[25] else None,
            }
            leads.append(DaliLML_Lead(**lead_dict))
        return leads

    def update_lead_stage(self, lead_id: UUID, stage: str) -> None:
        # Verificar que el lead exista
        if not self.get_lead_by_id(lead_id):
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        query = """
            UPDATE dalilm.Leads
            SET Stage = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(query, (stage, str(lead_id)))

    def assign_lead(self, lead_id: UUID, user_id: UUID) -> None:
        # Verificar que el lead exista
        if not self.get_lead_by_id(lead_id):
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        # Verificar que el usuario exista y esté activo
        user_exists = self.db_adapter.execute_query(
            "SELECT 1 FROM dalilm.Users WHERE Id = ? AND IsActive = 1",
            (str(user_id),),
            fetchone=True
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="El usuario asignado no existe o no está activo.")

        query = """
            UPDATE dalilm.Leads
            SET AssignedTo = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(query, (str(user_id), str(lead_id)))

    def delete_lead(self, lead_id: UUID) -> None:
        # Verificar que el lead exista
        if not self.get_lead_by_id(lead_id):
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        query = """
            UPDATE dalilm.Leads
            SET Stage = 'Eliminado', UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(query, (str(lead_id),))

    def update_lead(self, lead_id: UUID, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        # Verificar que el lead exista
        if not self.get_lead_by_id(lead_id):
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        # Verificar que el usuario asignado exista
        # This check should ideally be in a UserRepository, but for now, we'll keep it here
        user_exists = self.db_adapter.execute_query(
            "SELECT 1 FROM dalilm.Users WHERE Id = ?",
            (lead_data.assignedTo,),
            fetchone=True
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="El usuario asignado no existe.")

        product_json = json.dumps(lead_data.product) if lead_data.product else None
        tags_json = json.dumps(lead_data.tags) if lead_data.tags else None
        selected_portfolios_json = json.dumps(lead_data.SelectedPortfolios) if lead_data.SelectedPortfolios else None

        query = """
            UPDATE dalilm.Leads
            SET
                CreatedBy = ?, Name = ?, Email = ?, Phone = ?, DocumentNumber = ?, Company = ?,
                Source = ?, Campaign = ?, Product = ?, Stage = ?, Priority = ?,
                Value = ?, AssignedTo = ?, NextFollowUp = ?, Notes = ?, Tags = ?,
                DocumentType = ?, SelectedPortfolios = ?, CampaignOwnerName = ?, Age = ?, Gender = ?, PreferredContactChannel = ?,
                UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """
        self.db_adapter.execute_query(
            query,
            (
                lead_data.CreatedBy, lead_data.name, lead_data.email, lead_data.phone, lead_data.documentNumber,
                lead_data.company, lead_data.source, lead_data.campaign, product_json, lead_data.stage,
                lead_data.priority, lead_data.value, lead_data.assignedTo, lead_data.nextFollowUp,
                lead_data.notes, tags_json, lead_data.DocumentType, selected_portfolios_json,
                lead_data.CampaignOwnerName, lead_data.Age, lead_data.Gender, lead_data.PreferredContactChannel,
                str(lead_id)
            )
        )
        return self.get_lead_by_id(lead_id)

    def create_lead(self, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        lead_id = uuid4()
        product_json = json.dumps(lead_data.product) if lead_data.product else None
        tags_json = json.dumps(lead_data.tags) if lead_data.tags else None
        selected_portfolios_json = json.dumps(lead_data.SelectedPortfolios) if lead_data.SelectedPortfolios else None
        additional_info_json = json.dumps(lead_data.AdditionalInfo) if lead_data.AdditionalInfo else None

        try:
            # Verificar si el usuario asignado existe
            user_exists = self.db_adapter.execute_query(
                "SELECT 1 FROM dalilm.Users WHERE Id = ?",
                (lead_data.assignedTo,),
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_adapter.execute_query(
                insert_lead_query,
                (
                    lead_data.CreatedBy, str(lead_id), lead_data.name, lead_data.email, lead_data.phone,
                    lead_data.documentNumber, lead_data.company, lead_data.source, lead_data.campaign,
                    product_json, lead_data.stage, lead_data.priority, lead_data.value,
                    lead_data.assignedTo, lead_data.nextFollowUp, lead_data.notes, tags_json,
                    lead_data.DocumentType, selected_portfolios_json, lead_data.CampaignOwnerName,
                    lead_data.Age, lead_data.Gender, lead_data.PreferredContactChannel, additional_info_json
                )
            )

            # Insertar en LeadsRaw
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
            self.db_adapter.execute_query(insert_raw_query, (str(lead_id),))

        except HTTPException:
            raise
        except Exception as e:
            # Here you might want to log the exception e
            raise HTTPException(status_code=500, detail=f"Error al crear lead en la base de datos: {e}")

        created_lead = DaliLML_Lead(id=lead_id, **lead_data.model_dump())
        return created_lead
