from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Dict, Any
from .mock_data import SAMPLE_VENDORS, SAMPLE_CATEGORIES
from ..services.excel_service import generate_rfq_excel
from ..services.email_service import send_rfq_email
from loguru import logger

router = APIRouter()

@router.get("/categories")
async def get_categories():
    return SAMPLE_CATEGORIES

@router.get("/vendors")
async def get_vendors(category: str):
    vendors = [v for v in SAMPLE_VENDORS if v["category"] == category]
    return vendors

import base64

@router.post("/send-rfq")
async def send_rfq(
    category: str, 
    vendor_ids: List[int], 
    project_name: str = "General Project",
    materials: List[Dict[str, Any]] = Body(...),
    email_body: str = Query(None),
    original_file_base64: str = Body(None),
    original_filename: str = Body(None)
):
    try:
        # 1. Determine spreadsheet content
        if original_file_base64:
            excel_content = base64.b64decode(original_file_base64)
            filename = original_filename
        else:
            if not materials:
                raise HTTPException(status_code=400, detail="No materials provided for RFQ.")
            excel_content = generate_rfq_excel(materials)
            filename = None # Service will generate default

        # 2. Fetch Selected Vendors from sample data
        vendors = [v for v in SAMPLE_VENDORS if v["id"] in vendor_ids]

        # 3. Send Emails
        success_count = 0
        for vendor in vendors:
            success = send_rfq_email(
                vendor_name=vendor["name"],
                vendor_email=vendor["email"],
                category=category,
                project_name=project_name,
                excel_content=excel_content,
                custom_body=email_body,
                filename=filename
            )
            if success:
                success_count += 1

        return {
            "status": "success", 
            "emails_sent": success_count, 
            "total_vendors": len(vendors),
            "materials_count": len(materials)
        }

    except Exception as e:
        logger.exception("RFQ sending failed")
        raise HTTPException(status_code=500, detail=str(e))
