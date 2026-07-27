from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    # Get tenant_id from authenticated user - must not be None for data isolation
    if isinstance(current_user, dict):
        tenant_id = current_user.get("tenant_id")
    else:
        tenant_id = getattr(current_user, "tenant_id", None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User tenant_id not found - cannot proceed with data isolation"
        )
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # Keep total as string to preserve Decimal precision for financial calculations
    total_revenue_str = revenue_data['total']
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_str,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
