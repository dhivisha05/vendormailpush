from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    city = Column(String)
    category = Column(String, index=True)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    specification = Column(String, nullable=True)
    quantity = Column(Float)
    unit = Column(String)
    category = Column(String, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class RFQ(Base):
    __tablename__ = "rfqs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    category = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Sent")

class RFQItem(Base):
    __tablename__ = "rfq_items"
    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
