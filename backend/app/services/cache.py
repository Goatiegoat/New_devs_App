import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
import os

# Initialize Redis client
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Fetches revenue summary, utilizing tenant-scoped caching to prevent cross-tenant data leaks.
    """
    # Tenant-scoped cache key prevents collisions when property_ids match across tenants
    cache_key = f"revenue:{tenant_id}:{property_id}"
    
    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Revenue calculation is delegated to the reservation service.
    from app.services.reservations import calculate_total_revenue
    
    # Calculate revenue
    result = await calculate_total_revenue(property_id, tenant_id)
    
    # Cache the result for 5 minutes (300 seconds)
    await redis_client.setex(cache_key, 300, json.dumps(result))
    
    return result

async def invalidate_property_revenue_cache(property_id: str, tenant_id: str) -> None:
    """
    Utility to explicitly clear the revenue cache entry for a given property and tenant.
    Call this when reservations or revenue data change.
    """
    cache_key = f"revenue:{tenant_id}:{property_id}"
    await redis_client.delete(cache_key)
