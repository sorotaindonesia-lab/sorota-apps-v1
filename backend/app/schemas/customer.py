from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import BusinessCategory, CustomerStatus


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_name: str | None = None
    business_category: str | None = None
    business_subcategory: str | None = None
    location: str | None = None
    business_stage: str | None = None
    target_margin_percent: float | None = None
    notes: str | None = None


class CustomerCreate(BaseModel):
    name: str | None = None
    phone_number: str = Field(min_length=8, max_length=32)
    business_name: str | None = None
    business_category: BusinessCategory | None = None
    location: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    status: CustomerStatus | None = None
    business_name: str | None = None
    business_category: BusinessCategory | None = None
    location: str | None = None


class CustomerCreateResponse(BaseModel):
    id: UUID
    status: str


class CustomerListItem(BaseModel):
    id: UUID
    name: str | None = None
    phone_number: str
    status: str
    conversation_state: str | None = None
    business_name: str | None = None
    business_category: str | None = None
    location: str | None = None
    last_active_at: datetime | None = None


class CustomerListResponse(BaseModel):
    items: list[CustomerListItem]


class CustomerDetail(BaseModel):
    id: UUID
    name: str | None = None
    phone_number: str
    status: str
    conversation_state: str
    last_active_at: datetime | None = None
    business: BusinessRead | None = None
    created_at: datetime
    updated_at: datetime
