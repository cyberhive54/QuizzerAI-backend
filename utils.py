from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

async def verify_api_key(api_key: str):
    supabase: Client = get_supabase_client()
    # Query the 'user_api_keys' table
    response = supabase.table('user_api_keys').select('user_type, status').eq('user_api_key', api_key).execute()

    if not response.data:
        return None # API key not found

    user_data = response.data[0]
    if user_data['status'] == 'inactive':
        return 'inactive' # API key is inactive

    return user_data['user_type'] # Return user type (free, silver, gold)

async def fetch_api_config():
    supabase: Client = get_supabase_client()
    # Query the 'models' table for the default model
    model_response = supabase.table('models').select('model_name').eq('is_default', True).single().execute()
    model = model_response.data['model_name'] if model_response.data else 'gpt-3.5-turbo' # Default model if none found

    # Query the 'openrouter_api_keys' table for the default API key
    api_key_response = supabase.table('openrouter_api_keys').select('api_key').eq('is_default', True).limit(1).execute()
    openrouter_api_key = api_key_response.data[0]['api_key'] if api_key_response.data else None

    if not openrouter_api_key:
        print("No default OpenRouter API key found in database.")
        # In a real application, you'd raise an error or handle this appropriately
        # For now, returning None will cause the API call to fail gracefully
        pass

    return model, openrouter_api_key

async def save_generated_quiz(user_api_key: str, quiz_content: dict):
    supabase: Client = get_supabase_client()
    # Insert the generated quiz into the 'generated_quizzes' table
    data, count = supabase.table('generated_quizzes').insert({
        'user_api_key': user_api_key,
        'quiz_content': quiz_content
    }).execute()
    if count is None:
        print(f"Error saving quiz for user {user_api_key}")

import requests

async def call_openrouter_api(prompt: str, model: str, api_key: str):
    if not api_key:
        print("OpenRouter API key is missing.")
        return None # Or raise an exception

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return None # Or raise an exception