from fastapi import HTTPException, UploadFile
from typing import List, Optional, Any, Tuple
from uuid import UUID
import io
import csv
import json
import pandas as pd
from datetime import datetime

from domain.models.dali_lm_lead import DaliLML_Lead, DaliLML_LeadInput
from application.ports.dali_lm_lead_repository_port import DaliLMLeadRepositoryPort


class DaliLMLeadService:
    def __init__(self, lead_repository: DaliLMLeadRepositoryPort):
        self.lead_repository = lead_repository

    # ... (other methods)

    def _is_nullish(self, v: Any) -> bool:
        if v is None: return True
        try:
            if pd.isna(v): return True
        except Exception: pass
        s = str(v).strip()
        return s == "" or s.lower() in {"", "null", "none", "nan", "na", "<na>", "nat"}

    def _s(self, v: Any) -> Optional[str]:
        if self._is_nullish(v): return None
        return str(v).strip()

    def _fnum(self, v: Any) -> Optional[float]:
        if self._is_nullish(v): return None
        sv = str(v).strip().replace(",", ".")
        try: return float(sv)
        except Exception: return None

    def _iint(self, v: Any) -> Optional[int]:
        if self._is_nullish(v): return None
        sv = str(v).strip().replace(",", ".")
        try: return int(float(sv))
        except Exception: return None

    def _parse_jsonish(self, value: Any) -> Optional[str]:
        if self._is_nullish(value): return None
        if isinstance(value, (dict, list)): return json.dumps(value, ensure_ascii=False)
        svalue = str(value).strip()
        try: return json.dumps(json.loads(svalue), ensure_ascii=False)
        except Exception:
            try:
                s2 = svalue.replace("'", '\"')
                return json.dumps(json.loads(s2), ensure_ascii=False)
            except Exception: return None

    def _to_datetime_or_none(self, v: Any) -> Optional[datetime]:
        if self._is_nullish(v): return None
        try: return pd.to_datetime(v).to_pydatetime()
        except Exception: return None

    def _doc_bigint(self, v: Any) -> Optional[int]:
        if isinstance(v, (list, tuple, set)): v = next((x for x in v if x is not None), None)
        if self._is_nullish(v): return None
        sv = str(v).strip()
        try:
            n = int(float(sv))
            if 0 <= n <= 9223372036854775807: return n
        except Exception: pass
        sv2 = sv.replace(" ", "").replace(",", "").replace(".", "")
        if sv2.isdigit():
            try:
                n2 = int(sv2)
                return n2 if 0 <= n2 <= 9223372036854775807 else None
            except Exception: return None
        return None

    def _row_to_params(self, row: pd.Series, user_uuid: str) -> Tuple[Any, ...]:
        params = (
            user_uuid,
            str(uuid4()),
            (self._s(row.get("Name")) or "Sin Nombre"),
            self._s(row.get("Email")),
            self._s(row.get("Phone")),
            self._doc_bigint(row.get("DocumentNumber")),
            self._s(row.get("Company")),
            self._s(row.get("Source")),
            self._s(row.get("Campaign")),
            self._parse_jsonish(row.get("Product")),
            self._s(row.get("Stage")),
            self._s(row.get("Priority")),
            self._fnum(row.get("Value")) or 0.0,
            user_uuid,
            self._to_datetime_or_none(row.get("NextFollowUp")),
            self._s(row.get("Notes")),
            self._parse_jsonish(row.get("Tags")),
            self._s(row.get("DocumentType")),
            self._parse_jsonish(row.get("SelectedPortfolios")),
            self._s(row.get("CampaignOwnerName")),
            self._iint(row.get("Age")),
            self._s(row.get("Gender")),
            self._s(row.get("PreferredContactChannel")),
        )
        if any(isinstance(x, (list, tuple, set, dict)) for x in params):
            raise HTTPException(status_code=400, detail="Row contains non-scalar value.")
        return params

    def bulk_lead_file(self, file: UploadFile, user_uuid: str, batch_size: int, csv_chunksize: int) -> dict:
        filename = (file.filename or "").lower()
        is_csv = filename.endswith(".csv")
        is_xlsx = filename.endswith((".xls", ".xlsx"))
        if not (is_csv or is_xlsx):
            raise HTTPException(status_code=400, detail="Formato no soportado. Use .csv, .xls o .xlsx")

        total_inserted = 0
        total_failed = 0
        all_errors = []
        base_index = 0

        df_iterator = pd.read_csv(file.file, chunksize=csv_chunksize) if is_csv else [pd.read_excel(file.file)]

        expected_cols = [
            "Name", "Email", "Phone", "DocumentNumber", "Company", "Source", "Campaign",
            "Product", "Stage", "Priority", "Value", "NextFollowUp", "Notes",
            "Tags", "DocumentType", "SelectedPortfolios", "CampaignOwnerName",
            "Age", "Gender", "PreferredContactChannel"
        ]

        for chunk_df in df_iterator:
            for col in expected_cols:
                if col not in chunk_df.columns:
                    chunk_df[col] = pd.NA

            params_buffer = []
            for _, row in chunk_df.iterrows():
                params_buffer.append(self._row_to_params(row, user_uuid))
                if len(params_buffer) >= batch_size:
                    inserted, errs = self.lead_repository.bulk_lead_file(params_buffer)
                    total_inserted += inserted
                    for e in errs:
                        e["row_index"] = base_index + e["row_index"]
                    total_failed += len(params_buffer) - inserted
                    all_errors.extend(errs)
                    base_index += len(params_buffer)
                    params_buffer.clear()

            if params_buffer:
                inserted, errs = self.lead_repository.bulk_lead_file(params_buffer)
                total_inserted += inserted
                for e in errs:
                    e["row_index"] = base_index + e["row_index"]
                total_failed += len(params_buffer) - inserted
                all_errors.extend(errs)
                base_index += len(params_buffer)
                params_buffer.clear()

        if all_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Algunas filas fallaron.",
                    "inserted": total_inserted,
                    "failed": total_failed,
                    "errors": all_errors[:50]
                }
            )

        return {
            "inserted": total_inserted,
            "failed": total_failed,
            "message": f"{total_inserted} leads cargados exitosamente."
        }

    # Keep other methods
    def create_lead(self, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        return self.lead_repository.create_lead(lead_data)

    def get_lead_by_id(self, lead_id: UUID) -> DaliLML_Lead:
        lead = self.lead_repository.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")
        return lead

    def list_leads(self, name: Optional[str], email: Optional[str], phone: Optional[str], source: Optional[str], stage: Optional[str], priority: Optional[str], assigned_to: Optional[str], skip: int, limit: int) -> List[DaliLML_Lead]:
        return self.lead_repository.list_leads(name, email, phone, source, stage, priority, assigned_to, skip, limit)

    def update_lead(self, lead_id: UUID, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        return self.lead_repository.update_lead(lead_id, lead_data)

    def delete_lead(self, lead_id: UUID) -> None:
        self.lead_repository.delete_lead(lead_id)

    def assign_lead(self, lead_id: UUID, user_id: UUID) -> None:
        self.lead_repository.assign_lead(lead_id, user_id)

    def update_lead_stage(self, lead_id: UUID, stage: str) -> None:
        self.lead_repository.update_lead_stage(lead_id, stage)

    def get_duplicate_leads(self) -> List[DaliLML_Lead]:
        return self.lead_repository.get_duplicate_leads()

    def merge_leads(self, lead_ids: List[UUID], primary_lead_id: UUID) -> None:
        if primary_lead_id not in lead_ids:
            raise HTTPException(status_code=400, detail="primaryLeadId debe estar dentro de leadIds")
        self.lead_repository.merge_leads(lead_ids, primary_lead_id)

    def bulk_assign_leads(self, lead_ids: List[UUID], user_id: UUID) -> None:
        if not lead_ids:
            raise HTTPException(status_code=400, detail="La lista de leads no puede estar vacía.")
        self.lead_repository.bulk_assign_leads(lead_ids, user_id)

    def export_leads(self, assigned_to: Optional[UUID], created_by: Optional[UUID], stage: Optional[str], priority: Optional[str]) -> str:
        leads = self.lead_repository.export_leads(assigned_to, created_by, stage, priority)
        if not leads:
            raise HTTPException(status_code=404, detail="No se encontraron leads con esos filtros.")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=leads[0].model_dump().keys())
        writer.writeheader()
        for lead in leads:
            lead_dict = lead.model_dump()
            for key, value in lead_dict.items():
                if isinstance(value, (list, dict)):
                    lead_dict[key] = json.dumps(value)
            writer.writerow(lead_dict)
        return output.getvalue()
