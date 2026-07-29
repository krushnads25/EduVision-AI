from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.importers.base import BaseImporter, DataImportError
from app.models.college import College
from app.models.district import District


class CollegeImporter(BaseImporter):
    entity_name = "college"
    required_columns = ("name",)
    alias_map = {
        "college_name": "name",
        "name": "name",
        "district": "district_name",
        "district_name": "district_name",
        "district_code": "district_code",
        "address": "address",
    }

    def process_row(self, row: Dict[str, Any]) -> Optional[str]:
        name = self.clean_text(row.get("name"))
        if not name:
            raise DataImportError("College name is required")

        existing = self.db.query(College).filter(College.name == name).one_or_none()
        if existing:
            return "duplicate"

        district_name = self.clean_text(row.get("district_name"))
        district_code = self.clean_text(row.get("district_code"))
        address = self.clean_text(row.get("address"))

        district = self._get_or_create_district(district_name, district_code)

        college = College(name=name, address=address, district=district)
        self.db.add(college)
        return None

    def _get_or_create_district(self, district_name: Optional[str], district_code: Optional[str]) -> Optional[District]:
        if not district_name and not district_code:
            return None

        query = self.db.query(District)
        if district_name:
            query = query.filter(District.name == district_name)
        if district_code:
            query = query.filter(District.code == district_code)

        district = query.one_or_none()
        if district:
            return district

        if not district_name:
            district_name = district_code

        district = District(name=district_name, code=district_code)
        self.db.add(district)
        self.db.flush()
        return district
