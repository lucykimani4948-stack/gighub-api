from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, create_engine, select
import logging
from datetime import datetime
from typing import List, Optional

from models.product import Product, ProductCreate, ProductUpdate
from models.supplier import Supplier, SupplierCreate, SupplierUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///techvault.db"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI(
    title="TechVault Inventory API",
    description="API for managing TechVault's electronics inventory",
    version="1.0.0"
)

# Create tables
SQLModel.metadata.create_all(engine)

# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent JSON response"""
    logger.warning(f"HTTP Exception: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "errors": None,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed field-level errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) if error["loc"] else "unknown"
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {len(errors)} errors - Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Validation error - please check your input",
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    logger.error(f"Integrity error: {exc} - Path: {request.url.path}")
    
    error_message = "Database constraint violation"
    if "UNIQUE" in str(exc) or "unique" in str(exc):
        error_message = "Duplicate entry - this SKU, email, or name already exists"
    elif "FOREIGN KEY" in str(exc) or "foreign key" in str(exc):
        error_message = "Invalid reference - the supplier_id does not exist"
    
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "status_code": 409,
            "message": error_message,
            "errors": None,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": "An internal server error occurred. Please try again later.",
            "errors": None,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "Welcome to TechVault Inventory API",
        "version": "1.0.0",
        "developer": "LUCY WAMBUI KIMANI - C027-01-0890/2024",
        "endpoints": {
            "products": "/products",
            "product": "/products/{product_id}",
            "suppliers": "/suppliers",
            "search": "/products/search/?name=keyword",
            "bulk_update": "/products/bulk-update/",
            "adjust_stock": "/products/adjust-stock/"
        }
    }

# ============================================================
# PRODUCT ENDPOINTS
# ============================================================

@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product_data: ProductCreate):
    """Create a new product with validation"""
    try:
        with Session(engine) as session:
            # Check if SKU already exists
            existing = session.exec(select(Product).where(Product.sku == product_data.sku)).first()
            if existing:
                raise HTTPException(status_code=409, detail="Product with this SKU already exists")
            
            # Check if supplier exists if supplier_id is provided
            if product_data.supplier_id:
                supplier = session.get(Supplier, product_data.supplier_id)
                if not supplier:
                    raise HTTPException(status_code=404, detail="Supplier not found")
            
            product = Product(**product_data.model_dump())
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.get("/products/", response_model=List[Product])
async def get_products(skip: int = 0, limit: int = 100):
    """Get all products with pagination"""
    try:
        with Session(engine) as session:
            products = session.exec(select(Product).offset(skip).limit(limit)).all()
            return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID"""
    try:
        with Session(engine) as session:
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch product")

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product_data: ProductUpdate):
    """Update a product"""
    try:
        with Session(engine) as session:
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            update_data = product_data.model_dump(exclude_unset=True)
            
            # Check if SKU is being updated and is unique
            if 'sku' in update_data:
                existing = session.exec(
                    select(Product).where(Product.sku == update_data['sku'], Product.id != product_id)
                ).first()
                if existing:
                    raise HTTPException(status_code=409, detail="SKU already taken by another product")
            
            # Check if supplier exists if supplier_id is being updated
            if 'supplier_id' in update_data and update_data['supplier_id']:
                supplier = session.get(Supplier, update_data['supplier_id'])
                if not supplier:
                    raise HTTPException(status_code=404, detail="Supplier not found")
            
            for field, value in update_data.items():
                setattr(product, field, value)
            
            product.updated_at = datetime.utcnow()
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Delete a product"""
    try:
        with Session(engine) as session:
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            session.delete(product)
            session.commit()
            return {"message": "Product deleted successfully", "product_id": product_id}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

@app.get("/products/search/")
async def search_products(name: str = "", brand: str = "", category: str = "", 
                         min_price: float = 0, max_price: float = 500000):
    """Search products by various criteria"""
    try:
        with Session(engine) as session:
            query = select(Product)
            if name:
                query = query.where(Product.name.contains(name))
            if brand:
                query = query.where(Product.brand.ilike(f"%{brand}%"))
            if category:
                query = query.where(Product.category.ilike(f"%{category}%"))
            if min_price:
                query = query.where(Product.price >= min_price)
            if max_price:
                query = query.where(Product.price <= max_price)
            products = session.exec(query).all()
            return products
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to search products")

# ============================================================
# EXERCISE 3: BULK UPDATE ENDPOINT
# ============================================================

class BulkPriceUpdate(SQLModel):
    category: str
    discount_percent: float

@app.patch("/products/bulk-update/")
async def bulk_update_price(update_data: BulkPriceUpdate):
    """
    Apply a discount to all products in a specific category.
    """
    try:
        with Session(engine) as session:
            # Find all products in the category
            products = session.exec(
                select(Product).where(Product.category == update_data.category)
            ).all()
            
            if not products:
                raise HTTPException(
                    status_code=404,
                    detail=f"No products found in category: {update_data.category}"
                )
            
            updated_count = 0
            skipped_count = 0
            errors = []
            
            # Calculate new prices and validate
            for product in products:
                new_price = product.price * (1 - update_data.discount_percent / 100)
                new_price = round(new_price, 2)
                
                # Ensure new price >= 100 KSh
                if new_price < 100:
                    skipped_count += 1
                    errors.append({
                        "product_id": product.id,
                        "name": product.name,
                        "reason": "Price would fall below minimum (100 KSh)",
                        "old_price": product.price,
                        "attempted_price": new_price
                    })
                else:
                    product.price = new_price
                    product.updated_at = datetime.utcnow()
                    updated_count += 1
            
            # Commit changes
            if updated_count > 0:
                session.commit()
            
            # Return summary
            return {
                "success": True,
                "message": f"Bulk price update completed",
                "category": update_data.category,
                "discount_percent": update_data.discount_percent,
                "total_products": len(products),
                "updated_count": updated_count,
                "skipped_count": skipped_count,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk update")

# ============================================================
# EXERCISE 4: STOCK ADJUSTMENT ENDPOINT
# ============================================================

class StockAdjustment(SQLModel):
    product_id: int
    quantity_to_add: int

@app.patch("/products/adjust-stock/")
async def adjust_stock(adjustments: List[StockAdjustment]):
    """
    Adjust stock levels for multiple products.
    """
    try:
        with Session(engine) as session:
            success = []
            failures = []
            
            for adjustment in adjustments:
                # Check if product exists
                product = session.get(Product, adjustment.product_id)
                if not product:
                    failures.append({
                        "product_id": adjustment.product_id,
                        "reason": "Product not found"
                    })
                    continue
                
                # Calculate new stock
                new_stock = product.stock + adjustment.quantity_to_add
                
                # Validate new stock <= 5000
                if new_stock > 5000:
                    failures.append({
                        "product_id": adjustment.product_id,
                        "name": product.name,
                        "reason": "Stock would exceed maximum limit (5000)",
                        "current_stock": product.stock,
                        "requested_add": adjustment.quantity_to_add,
                        "would_be": new_stock
                    })
                    continue
                
                # Update stock
                product.stock = new_stock
                product.updated_at = datetime.utcnow()
                success.append({
                    "product_id": adjustment.product_id,
                    "name": product.name,
                    "old_stock": product.stock - adjustment.quantity_to_add,
                    "added": adjustment.quantity_to_add,
                    "new_stock": product.stock
                })
            
            # Commit changes
            if success:
                session.commit()
            
            # Return summary
            return {
                "success": True,
                "message": f"Stock adjustment completed",
                "total_adjustments": len(adjustments),
                "successful": len(success),
                "failed": len(failures),
                "details": {
                    "success": success,
                    "failures": failures
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error in stock adjustment: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust stock")

# ============================================================
# SUPPLIER ENDPOINTS
# ============================================================

@app.post("/suppliers/", response_model=Supplier, status_code=201)
async def create_supplier(supplier_data: SupplierCreate):
    """Create a new supplier"""
    try:
        with Session(engine) as session:
            # Check if email exists
            existing = session.exec(select(Supplier).where(Supplier.email == supplier_data.email)).first()
            if existing:
                raise HTTPException(status_code=409, detail="Supplier with this email already exists")
            
            # Check if name exists
            existing = session.exec(select(Supplier).where(Supplier.name == supplier_data.name)).first()
            if existing:
                raise HTTPException(status_code=409, detail="Supplier with this name already exists")
            
            supplier = Supplier(**supplier_data.model_dump())
            session.add(supplier)
            session.commit()
            session.refresh(supplier)
            return supplier
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(status_code=500, detail="Failed to create supplier")

@app.get("/suppliers/", response_model=List[Supplier])
async def get_suppliers(skip: int = 0, limit: int = 100):
    """Get all suppliers"""
    try:
        with Session(engine) as session:
            suppliers = session.exec(select(Supplier).offset(skip).limit(limit)).all()
            return suppliers
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch suppliers")

@app.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: int):
    """Get a specific supplier by ID"""
    try:
        with Session(engine) as session:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found")
            return supplier
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching supplier {supplier_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch supplier")

@app.get("/suppliers/{supplier_id}/products/", response_model=List[Product])
async def get_supplier_products(supplier_id: int):
    """Get all products from a specific supplier"""
    try:
        with Session(engine) as session:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found")
            
            products = session.exec(select(Product).where(Product.supplier_id == supplier_id)).all()
            return products
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching supplier products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")