from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import Business, Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.enums import CustomerStatus


class CustomerAlreadyExistsError(ValueError):
    pass


def get_customer(db: Session, customer_id: UUID) -> Customer | None:
    stmt = (
        select(Customer)
        .where(Customer.id == customer_id)
        .options(selectinload(Customer.businesses))
    )
    return db.scalars(stmt).first()


def get_customer_by_phone(db: Session, phone_number: str) -> Customer | None:
    stmt = (
        select(Customer)
        .where(Customer.phone_number == phone_number)
        .options(selectinload(Customer.businesses))
    )
    return db.scalars(stmt).first()


def list_customers(
    db: Session,
    status: str | None = None,
    business_category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Customer]:
    stmt = select(Customer).options(selectinload(Customer.businesses))

    if business_category:
        stmt = stmt.join(Business).where(Business.business_category == business_category)

    if status:
        stmt = stmt.where(Customer.status == status)

    stmt = stmt.order_by(Customer.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).unique().all())


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    existing = get_customer_by_phone(db, payload.phone_number)
    if existing:
        raise CustomerAlreadyExistsError("customer phone number already exists")

    customer = Customer(
        name=payload.name,
        phone_number=payload.phone_number,
        status=CustomerStatus.REGISTERED.value,
    )
    db.add(customer)
    db.flush()

    if payload.business_name or payload.business_category or payload.location:
        db.add(
            Business(
                customer_id=customer.id,
                business_name=payload.business_name,
                business_category=payload.business_category.value if payload.business_category else None,
                location=payload.location,
            )
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CustomerAlreadyExistsError("customer phone number already exists") from exc

    return get_customer(db, customer.id) or customer


def update_customer(db: Session, customer: Customer, payload: CustomerUpdate) -> Customer:
    updates = payload.model_dump(exclude_unset=True, mode="json")

    if "name" in updates:
        customer.name = updates["name"]
    if "status" in updates:
        customer.status = updates["status"]

    business_update_keys = {"business_name", "business_category", "location"}
    business_updates = {key: updates[key] for key in business_update_keys if key in updates}
    if business_updates:
        business = customer.businesses[0] if customer.businesses else Business(customer_id=customer.id)
        for key, value in business_updates.items():
            setattr(business, key, value)
        db.add(business)

    db.add(customer)
    db.commit()
    return get_customer(db, customer.id) or customer
