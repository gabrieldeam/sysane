from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum
import uuid

# Enums para o cadastro
class CompanySize(enum.Enum):
    SOLE_PROPRIETOR = "Somente eu"
    STARTUP = "Empresa iniciante"
    SMALL = "2-10"
    MEDIUM = "11-50"
    LARGE = "51-200"
    XLARGE = "201-500"
    XXLARGE = "501-1000"
    HUGE = "1001-5000"
    MASSIVE = "5001-10000"
    ENTERPRISE = "10001 ou mais"

class WorkArea(enum.Enum):
    IT = "TI"
    BUSINESS = "Negócios"

class Department(enum.Enum):
    PURCHASING = "Compras"
    HR = "RH"
    IT = "TI"
    FINANCE = "Financeiro"
    SHARED_SERVICES = "Serviços Compartilhados"
    OPERATIONS = "Operações de Negócios"
    SUPPORT = "CS/Suporte"
    LEGAL = "Jurídico"
    SALES = "Vendas"
    MARKETING = "Marketing"
    PRODUCT_DEVELOPMENT = "Desenvolvimento de Produtos"
    SUPPLY = "Supply"
    FACILITIES = "Facilities"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    company_size = Column(Enum(CompanySize), nullable=True)
    work_area = Column(Enum(WorkArea), nullable=False)
    department = Column(Enum(Department), nullable=False)
    accepted_privacy_policy = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
