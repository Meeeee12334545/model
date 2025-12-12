from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    location: str | None = None
    owner: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class SiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    pipe_material: str | None = None
    pipe_diameter_mm: float | None = None


class SiteCreate(SiteBase):
    project_id: int


class SiteResponse(SiteBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime
    parameter: str
    value: float | None
    unit: str | None = None
    qc_flag: str | None = None


class UploadSummary(BaseModel):
    site_id: int
    records_imported: int
    time_range: list[str]
    parameters: dict[str, dict]
