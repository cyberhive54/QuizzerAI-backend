from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from utils import get_supabase_client
from supabase import Client
import logging
from pydantic import BaseModel
from uuid import UUID
import time
import requests
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Dependency to get Supabase client
async def get_db():
    return get_supabase_client()

# Get all users
@router.get("/users")
async def get_users(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching users from database")
        response = db.table('users').select('id, user_id, email, username, tier, api_key, created_at, updated_at, is_active').execute()
        logger.info(f"Found {len(response.data)} users")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

# Get all API keys
@router.get("/api-keys")
async def get_api_keys(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching API keys from database")
        response = db.table('user_api_keys').select('user_api_key, user_type, status, user_id').execute()
        logger.info(f"Found {len(response.data)} API keys")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch API keys: {str(e)}")

# Get all OpenRouter API keys
@router.get("/openrouter-keys")
async def get_openrouter_keys(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching OpenRouter API keys from database")
        response = db.table('openrouter_api_keys').select('id, api_key, description, is_default').execute()
        logger.info(f"Found {len(response.data)} OpenRouter API keys")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching OpenRouter API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch OpenRouter API keys: {str(e)}")

# Get all API models
@router.get("/api-models")
async def get_api_models(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching API models from database")
        response = db.table('models').select('id, model_name, description, is_default').execute()
        logger.info(f"Found {len(response.data)} API models")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching API models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch API models: {str(e)}")

# Get all generated quizzes
@router.get("/generated-quizzes")
async def get_generated_quizzes(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching generated quizzes from database")
        response = db.table('generated_quizzes').select('id, user_api_key, generated_at, quiz_content').execute()
        logger.info(f"Found {len(response.data)} generated quizzes")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching generated quizzes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch generated quizzes: {str(e)}")

# Get dashboard statistics
@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching dashboard statistics")
        # Get total users count
        users_response = db.table('users').select('id', count='exact').execute()
        total_users = users_response.count if users_response.count is not None else 0
        logger.info(f"Total users: {total_users}")

        # Get active API keys count
        api_keys_response = db.table('user_api_keys').select('id', count='exact').eq('status', 'active').execute()
        active_api_keys = api_keys_response.count if api_keys_response.count is not None else 0
        logger.info(f"Active API keys: {active_api_keys}")

        # Get total quizzes generated
        quizzes_response = db.table('generated_quizzes').select('id', count='exact').execute()
        total_quizzes = quizzes_response.count if quizzes_response.count is not None else 0
        logger.info(f"Total quizzes: {total_quizzes}")

        # Get total OpenRouter keys
        openrouter_keys_response = db.table('openrouter_api_keys').select('id', count='exact').execute()
        total_openrouter_keys = openrouter_keys_response.count if openrouter_keys_response.count is not None else 0
        logger.info(f"Total OpenRouter keys: {total_openrouter_keys}")

        return {
            "data": {
                "total_users": total_users,
                "active_api_keys": active_api_keys,
                "total_quizzes": total_quizzes,
                "total_openrouter_keys": total_openrouter_keys
            },
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard statistics: {str(e)}")

# Get usage logs
@router.get("/usage-logs")
async def get_usage_logs(
    db: Client = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    try:
        logger.info(f"Fetching usage logs (limit: {limit}, offset: {offset})")
        response = db.table('usage_logs')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        logger.info(f"Found {len(response.data)} usage logs")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching usage logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage logs: {str(e)}")

# Get all usage limits
@router.get("/usage-limits")
async def get_usage_limits(db: Client = Depends(get_db)):
    try:
        logger.info("Fetching usage limits from database")
        response = db.table('usage_limits').select('id, tier_name, max_daily_limit, max_monthly_limit, price, created_at, updated_at').execute()
        logger.info(f"Found {len(response.data)} usage limits")
        return {
            "data": response.data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching usage limits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage limits: {str(e)}")

class UsageLimitCreate(BaseModel):
    tier_name: str
    max_daily_limit: int
    max_monthly_limit: int
    price: float

class UsageLimitUpdate(BaseModel):
    tier_name: str
    max_daily_limit: int
    max_monthly_limit: int
    price: float

# POST: Create a new usage limit
@router.post("/usage-limits")
async def create_usage_limit(limit: UsageLimitCreate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Creating usage limit: {limit.tier_name}")
        response = db.table('usage_limits').insert({
            "tier_name": limit.tier_name,
            "max_daily_limit": limit.max_daily_limit,
            "max_monthly_limit": limit.max_monthly_limit,
            "price": limit.price
        }).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error creating usage limit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create usage limit: {str(e)}")

# PUT: Update a usage limit
@router.put("/usage-limits/{id}")
async def update_usage_limit(id: UUID, limit: UsageLimitUpdate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Updating usage limit {id}")
        response = db.table('usage_limits').update({
            "tier_name": limit.tier_name,
            "max_daily_limit": limit.max_daily_limit,
            "max_monthly_limit": limit.max_monthly_limit,
            "price": limit.price,
            "updated_at": "now()"
        }).eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error updating usage limit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update usage limit: {str(e)}")

# DELETE: Delete a usage limit
@router.delete("/usage-limits/{id}")
async def delete_usage_limit(id: UUID, db: Client = Depends(get_db)):
    try:
        logger.info(f"Deleting usage limit {id}")
        response = db.table('usage_limits').delete().eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error deleting usage limit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete usage limit: {str(e)}")

class ApiModelCreate(BaseModel):
    model_name: str
    description: str
    is_default: Optional[bool] = False

class ApiModelUpdate(BaseModel):
    model_name: str
    description: str
    is_default: Optional[bool] = False

class OpenRouterKeyCreate(BaseModel):
    api_key: str
    description: str
    is_default: Optional[bool] = False

class OpenRouterKeyUpdate(BaseModel):
    api_key: str
    description: str
    is_default: Optional[bool] = False

# CRUD for API Models
@router.post("/api-models")
async def create_api_model(model: ApiModelCreate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Creating API model: {model.model_name}")
        response = db.table('models').insert({
            "model_name": model.model_name,
            "description": model.description,
            "is_default": model.is_default
        }).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error creating API model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create API model: {str(e)}")

@router.put("/api-models/{id}")
async def update_api_model(id: UUID, model: ApiModelUpdate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Updating API model {id}")
        response = db.table('models').update({
            "model_name": model.model_name,
            "description": model.description,
            "is_default": model.is_default
        }).eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error updating API model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update API model: {str(e)}")

@router.delete("/api-models/{id}")
async def delete_api_model(id: UUID, db: Client = Depends(get_db)):
    try:
        logger.info(f"Deleting API model {id}")
        response = db.table('models').delete().eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error deleting API model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete API model: {str(e)}")

# CRUD for OpenRouter API Keys
@router.post("/openrouter-keys")
async def create_openrouter_key(key: OpenRouterKeyCreate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Creating OpenRouter API key: {key.description}")
        response = db.table('openrouter_api_keys').insert({
            "api_key": key.api_key,
            "description": key.description,
            "is_default": key.is_default
        }).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error creating OpenRouter API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create OpenRouter API key: {str(e)}")

@router.put("/openrouter-keys/{id}")
async def update_openrouter_key(id: UUID, key: OpenRouterKeyUpdate, db: Client = Depends(get_db)):
    try:
        logger.info(f"Updating OpenRouter API key {id}")
        response = db.table('openrouter_api_keys').update({
            "api_key": key.api_key,
            "description": key.description,
            "is_default": key.is_default
        }).eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error updating OpenRouter API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update OpenRouter API key: {str(e)}")

@router.delete("/openrouter-keys/{id}")
async def delete_openrouter_key(id: UUID, db: Client = Depends(get_db)):
    try:
        logger.info(f"Deleting OpenRouter API key {id}")
        response = db.table('openrouter_api_keys').delete().eq('id', str(id)).execute()
        return {"data": response.data, "status": "success"}
    except Exception as e:
        logger.error(f"Error deleting OpenRouter API key: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete OpenRouter API key: {str(e)}")

@router.get("/system-health")
async def system_health(db: Client = Depends(get_db)):
    health = {}
    # Database check
    db_start = time.monotonic()
    try:
        db.table('users').select('id').limit(1).execute()
        db_latency = (time.monotonic() - db_start) * 1000
        health['database'] = {'status': 'ok', 'latency_ms': round(db_latency, 2)}
    except Exception as e:
        db_latency = (time.monotonic() - db_start) * 1000
        health['database'] = {'status': 'error', 'latency_ms': round(db_latency, 2), 'error': str(e)}
    # OpenRouter API check
    or_start = time.monotonic()
    try:
        resp = requests.get('https://openrouter.ai/api/v1/models', timeout=5)
        or_latency = (time.monotonic() - or_start) * 1000
        if resp.status_code == 200:
            health['openrouter'] = {'status': 'ok', 'latency_ms': round(or_latency, 2)}
        else:
            health['openrouter'] = {'status': 'error', 'latency_ms': round(or_latency, 2), 'error': f'Status {resp.status_code}'}
    except Exception as e:
        or_latency = (time.monotonic() - or_start) * 1000
        health['openrouter'] = {'status': 'error', 'latency_ms': round(or_latency, 2), 'error': str(e)}
    return {'data': health, 'status': 'success'}

@router.get("/db-tables-health")
async def db_tables_health(db: Client = Depends(get_db)):
    health = []
    # Use a hardcoded list of known table names for safety
    table_names = [
        'users', 'user_api_keys', 'openrouter_api_keys', 'models', 'generated_quizzes', 'usage_limits', 'usage_logs'
    ]
    for table in table_names:
        start = time.monotonic()
        try:
            db.table(table).select('id').limit(1).execute()
            latency = (time.monotonic() - start) * 1000
            health.append({"table": table, "status": "ok", "latency_ms": round(latency, 2)})
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            health.append({"table": table, "status": "error", "latency_ms": round(latency, 2), "error": str(e)})
    return {"data": health, "status": "success"}

@router.get("/openrouter-prompts-health")
async def openrouter_prompts_health(db: Client = Depends(get_db)):
    prompts = {
        "easy": "What is 2+2?",
        "medium": "Explain the process of photosynthesis in a paragraph.",
        "hard": "Write a Python function to compute the nth Fibonacci number recursively and explain its time complexity.",
        "extreme": "Generate a detailed, step-by-step solution to a complex calculus problem involving integration by parts, and provide a LaTeX-formatted answer."
    }
    # Fetch API key from database
    try:
        key_resp = db.table('openrouter_api_keys').select('api_key, is_default').order('is_default', desc=True).limit(1).execute()
        if not key_resp.data or not key_resp.data[0].get('api_key'):
            return {"status": "error", "error": "No OpenRouter API key found in database."}
        api_key = key_resp.data[0]['api_key']
    except Exception as e:
        return {"status": "error", "error": f"Failed to fetch OpenRouter API key: {str(e)}"}
    results = []
    for level, prompt in prompts.items():
        try:
            start = time.monotonic()
            resp = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15
            )
            latency = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                results.append({"level": level, "status": "ok", "latency_ms": round(latency, 2), "prompt": prompt})
            else:
                results.append({"level": level, "status": "error", "latency_ms": round(latency, 2), "prompt": prompt, "error": f"Status {resp.status_code}: {resp.text}"})
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            results.append({"level": level, "status": "error", "latency_ms": round(latency, 2), "prompt": prompt, "error": str(e)})
    return {"data": results, "status": "success"}
