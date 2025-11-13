"""
Database Schemas for Oil & Gas B2B Supplier Site

Each Pydantic model corresponds to a MongoDB collection whose name is the lowercase of the class name.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Certification(BaseModel):
    name: str = Field(..., description="Certification or standard name e.g., ISO 9001, API 6D")
    pdf_url: HttpUrl = Field(..., description="Link to the certification PDF")
    standard: Optional[str] = Field(None, description="Standard code or brief description")


class Product(BaseModel):
    slug: str = Field(..., description="URL-friendly unique identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Category e.g., Valves, Pumps, Sensors")
    description: str = Field(..., description="Detailed description")
    image_url: HttpUrl = Field(..., description="High-res product image URL")
    spec_pdf_url: HttpUrl = Field(..., description="Technical spec sheet PDF URL")
    certifications: List[Certification] = Field(default_factory=list, description="List of certifications")
    tags: List[str] = Field(default_factory=list, description="Search tags")


class IndustrySolution(BaseModel):
    slug: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Solution title")
    segment: str = Field(..., description="upstream | midstream | downstream")
    problem: str = Field(..., description="The core operational challenge")
    solution: str = Field(..., description="How our product/approach solves it")
    related_products: List[str] = Field(default_factory=list, description="List of related product slugs")
    content: Optional[str] = Field(None, description="Long-form content or notes")


class CaseStudy(BaseModel):
    slug: str = Field(...)
    title: str = Field(...)
    client: str = Field(...)
    location: Optional[str] = None
    challenge: str = Field(...)
    solution: str = Field(...)
    outcome: str = Field(...)
    products_used: List[str] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None


class RFQ(BaseModel):
    company_name: str = Field(...)
    contact_name: str = Field(...)
    email: str = Field(...)
    phone: Optional[str] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    specifications: Optional[str] = None
    product_slugs: List[str] = Field(default_factory=list)
    quantity: Optional[int] = Field(None, ge=1)
    timeline: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
