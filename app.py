from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from utils import verify_api_key
from prompt_selector import select_and_customize_prompt
from utils import fetch_api_config, call_openrouter_api, save_generated_quiz
from admin_crud import router as admin_router

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
origins = [
    "*" # Allow all origins for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for admin
app.mount("/admin", StaticFiles(directory="admin"), name="admin")

# Models
class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5
    model_name: str = None
    model_config = {
        "protected_namespaces": ()
    }

class QuizResponse(BaseModel):
    quiz_id: str
    questions: list
    model_used: str
    model_config = {
        "protected_namespaces": ()
    }

class ErrorResponse(BaseModel):
    error: str
    model_config = {
        "protected_namespaces": ()
    }

# Include the admin router
app.include_router(admin_router)

@app.post("/generate-quiz")
async def generate_quiz(request: Request):
    # Extract user API key from headers or query params (as per frontend implementation)
    # Assuming API key is in 'X-User-API-Key' header for now
    user_api_key = request.headers.get('X-User-API-Key')
    if not user_api_key:
        raise HTTPException(status_code=401, detail="User API key missing")

    # Verify API key
    user_status = await verify_api_key(user_api_key)
    if user_status is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if user_status == 'inactive':
        raise HTTPException(status_code=403, detail="API key is inactive")

    user_type = user_status # Now user_type holds 'free', 'silver', or 'gold'
    # TODO: Implement rate limiting based on user_type (e.g., using a rate limiter library and storage)
    # Example placeholder:
    # if not check_rate_limit(user_api_key, user_type):
    #     raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Parse request body for quiz parameters
    try:
        params = await request.json()
        print(f"Received parameters: {params}") # Add this line to inspect parameters
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Select and customize prompt
    final_prompt = select_and_customize_prompt(params)

    # Fetch API config from DB
    model, openrouter_api_key = await fetch_api_config()

    # Call OpenRouter API
    api_response = await call_openrouter_api(final_prompt, model, openrouter_api_key)

    # Process and return the quiz data from the API response
    if api_response and api_response.get("choices"):
        # Assuming the generated quiz content is in the first message's content
        quiz_content = api_response["choices"][0]["message"]["content"]
        
        # Attempt to parse quiz_content as JSON, if it's a JSON string
        try:
            quiz_json = json.loads(quiz_content)
        except json.JSONDecodeError:
            # If not JSON, store as a simple dictionary or string
            quiz_json = {"content": quiz_content}

        # Save the generated quiz to the database
        await save_generated_quiz(user_api_key, quiz_json)

        return {"quiz_content": quiz_content}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate quiz from API")

# To run the app, use: uvicorn app:app --reload
