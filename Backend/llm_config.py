import os
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

def get_model():
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_endpoint = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    model_name = os.getenv("OPENAPI_MODEL", "openai/gpt-oss-20b")

    # 🔥 Map GROQ → OpenAI env variables
    if groq_api_key:
        os.environ["OPENAI_API_KEY"] = groq_api_key
    else:
        raise ValueError("❌ GROQ_API_KEY not found in .env")

    os.environ["OPENAI_BASE_URL"] = groq_endpoint

    return OpenAIModel(model_name)