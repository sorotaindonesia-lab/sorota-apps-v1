from enum import Enum


class CustomerStatus(str, Enum):
    REGISTERED = "registered"
    INVITED = "invited"
    PROFILING = "profiling"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    INVALID = "invalid"


class BusinessCategory(str, Enum):
    KULINER = "kuliner"
    RETAIL = "retail"
    FASHION = "fashion"
    LAUNDRY = "laundry"
    WARUNG = "warung"
    TOKO_KELONTONG = "toko_kelontong"
    COFFEE_SHOP = "coffee_shop"
    RESELLER = "reseller"
    JASA = "jasa"
    LAINNYA = "lainnya"


class ConversationState(str, Enum):
    NEW = "NEW"
    ASK_BUSINESS_NAME = "ASK_BUSINESS_NAME"
    ASK_BUSINESS_CATEGORY = "ASK_BUSINESS_CATEGORY"
    ASK_LOCATION = "ASK_LOCATION"
    ASK_MAIN_PRODUCTS = "ASK_MAIN_PRODUCTS"
    ASK_PRICE_DATA = "ASK_PRICE_DATA"
    ACTIVE = "ACTIVE"


class EarlyWarningStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    SENT = "sent"
    SKIPPED = "skipped"
    FAILED = "failed"
