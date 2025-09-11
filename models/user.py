from sqlalchemy import Column, Integer, String, Boolean, Enum, BigInteger, DateTime,ForeignKey
from db.session import Base
import enum
import datetime
from sqlalchemy.orm import relationship
import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean,
    ForeignKey, Enum, BigInteger
)
from sqlalchemy.orm import relationship

import uuid
from sqlalchemy.dialects.postgresql import UUID


# ---------- Role Enum ---------- #
class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"


# ---------- User Table ---------- #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(BigInteger, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user,nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Verification fields
    verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    # Permissions (comma separated string or JSON)
    permissions = Column(String, default="")


class WebhookData(Base):
    __tablename__ = "webhook_data"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)  # New UUID column
    stocks = Column(String)            # Comma-separated stock symbols
    trigger_prices = Column(String)    # Comma-separated prices
    triggered_at = Column(String)
    scan_name = Column(String)         # e.g., 'Near 52 Week High' or '200 Weekly MA'
    scan_url = Column(String)
    alert_name = Column(String)
    webhook_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
