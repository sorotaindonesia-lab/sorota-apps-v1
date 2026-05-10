from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Business, Customer
from app.schemas.customer import (
    BusinessRead,
    CustomerCreate,
    CustomerCreateResponse,
    CustomerDetail,
    CustomerListItem,
    CustomerListResponse,
    CustomerUpdate,
)
from app.services.customer_service import (
    CustomerAlreadyExistsError,
    create_customer,
    get_customer,
    list_customers,
    update_customer,
)

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _primary_business(customer: Customer) -> Business | None:
    return customer.businesses[0] if customer.businesses else None


def _to_list_item(customer: Customer) -> CustomerListItem:
    business = _primary_business(customer)
    return CustomerListItem(
        id=customer.id,
        name=customer.name,
        phone_number=customer.phone_number,
        status=customer.status,
        business_name=business.business_name if business else None,
        business_category=business.business_category if business else None,
        location=business.location if business else None,
        last_active_at=customer.last_active_at,
    )


def _to_detail(customer: Customer) -> CustomerDetail:
    business = _primary_business(customer)
    return CustomerDetail(
        id=customer.id,
        name=customer.name,
        phone_number=customer.phone_number,
        status=customer.status,
        last_active_at=customer.last_active_at,
        business=BusinessRead.model_validate(business) if business else None,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.post("", response_model=CustomerCreateResponse, status_code=status.HTTP_201_CREATED)
def create_customer_endpoint(payload: CustomerCreate, db: Session = Depends(get_db)) -> CustomerCreateResponse:
    try:
        customer = create_customer(db, payload)
    except CustomerAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CustomerCreateResponse(id=customer.id, status=customer.status)


@router.get("", response_model=CustomerListResponse)
def list_customers_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    business_category: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    customers = list_customers(
        db,
        status=status_filter,
        business_category=business_category,
        limit=limit,
        offset=offset,
    )
    return CustomerListResponse(items=[_to_list_item(customer) for customer in customers])


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer_endpoint(customer_id: UUID, db: Session = Depends(get_db)) -> CustomerDetail:
    customer = get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="customer not found")
    return _to_detail(customer)


@router.patch("/{customer_id}", response_model=CustomerDetail)
def update_customer_endpoint(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
) -> CustomerDetail:
    customer = get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="customer not found")
    return _to_detail(update_customer(db, customer, payload))
