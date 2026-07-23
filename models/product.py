from typing import Optional
from datetime import datetime
import re
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    brand: str = Field(index=True)
    category: str = Field(index=True)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    warranty_months: int = Field(ge=0)
    sku: str = Field(unique=True, index=True)
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")  # Add this line
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
class ProductCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    brand: str
    category: str
    price: float = Field(gt=0, le=1000000)
    stock: int = Field(ge=0, le=10000)
    warranty_months: int = Field(ge=0)
    sku: str
    supplier_id: Optional[int] = None  # Add this line
    # ... rest of the validators stay the same
    @field_validator("name")
    def validate_name(cls, v):
        """Product name must be meaningful."""
        if not v[0].isupper():
            raise ValueError("Name must start with a capital letter")
        if re.search(r'[^a-zA-Z0-9\s\-]', v):
            raise ValueError("Name cannot contain special characters (except spaces and hyphens)")
        if len(v.strip().split()) < 1:
            raise ValueError("Name must contain at least one word")
        return v.strip()

    @field_validator("brand")
    def validate_brand(cls, v):
        """Brand name must be standardized."""
        allowed_brands = ["HP", "Dell", "Lenovo", "Apple", "Samsung", "Intel", 
                         "AMD", "Corsair", "Logitech", "Other"]
        for brand in allowed_brands:
            if v.lower() == brand.lower():
                return brand
        raise ValueError(f"Brand must be one of: {', '.join(allowed_brands)}")

    @field_validator("category")
    def validate_category(cls, v):
        """Category must be one of allowed categories."""
        allowed_categories = ["Laptops", "Monitors", "Storage", "Processors", 
                            "Memory", "Keyboards", "Mice", "Accessories"]
        for category in allowed_categories:
            if v.lower() == category.lower():
                return category
        raise ValueError(f"Category must be one of: {', '.join(allowed_categories)}")

    @field_validator("price")
    def validate_price(cls, v):
        """Price must be practical for the Kenyan market."""
        if len(str(v).split('.')[-1]) > 2:
            raise ValueError("Price cannot have more than 2 decimal places")
        if v < 100:
            raise ValueError("Price must be at least 100 KSh")
        if v > 500000:
            raise ValueError("Price cannot exceed 500,000 KSh")
        return round(v, 2)

    @field_validator("sku")
    def validate_sku(cls, v):
        """SKU must follow the format: CAT-BRAND-XXXX."""
        category_abbr = {
            "Laptops": "LAP", "Monitors": "MON", "Storage": "STO",
            "Processors": "PRO", "Memory": "MEM", "Keyboards": "KEY",
            "Mice": "MOU", "Accessories": "ACC"
        }
        pattern = r'^[A-Z]{3,4}-[A-Z]{2,4}-[0-9]{4}$'
        if not re.match(pattern, v):
            raise ValueError("SKU must follow format: CAT-BRAND-XXXX (e.g., LAP-HP-0001)")
        sku_parts = v.split('-')
        if sku_parts[0] not in category_abbr.values():
            raise ValueError(f"Invalid category abbreviation. Must be one of: {', '.join(category_abbr.values())}")
        return v.upper()

    @field_validator("warranty_months")
    def validate_warranty(cls, v, info):
        """Warranty must be reasonable."""
        if v < 0 or v > 36:
            raise ValueError("Warranty must be between 0 and 36 months")
        if 'price' in info.data and info.data['price'] > 50000 and v < 12:
            raise ValueError("Products priced above 50,000 KSh must have at least 12 months warranty")
        return v

class ProductUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, min_length=10, max_length=500)
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0, le=1000000)
    stock: Optional[int] = Field(default=None, ge=0, le=10000)
    warranty_months: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None