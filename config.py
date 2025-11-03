import os
import io
from dotenv import load_dotenv
from google.cloud import secretmanager

def load_secrets():
    """
    Loads secrets from Google Secret Manager if in a GCP environment,
    otherwise falls back to a local .env file.
    """
    # Check if running in a GCP environment by looking for the PROJECT_ID env var
    # which is automatically set in Cloud Run.
    project_id = os.environ.get("PROJECT_ID")

    if project_id:
        # GCP environment: Fetch the single secret containing all env vars
        try:
            client = secretmanager.SecretManagerServiceClient()
            secret_name = "workout-tracker-env"
            version = "latest"
            
            # Full resource name of the secret version
            name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
            
            # Access the secret version
            response = client.access_secret_version(name=name)
            
            # Decode the payload and treat it as a file-in-memory
            payload = response.payload.data.decode("UTF-8")
            string_io = io.StringIO(payload)
            
            # Load the environment variables from the in-memory "file"
            load_dotenv(stream=string_io)
            print("Successfully loaded secrets from Secret Manager.")

        except Exception as e:
            # If fetching from Secret Manager fails, the app might not start.
            # You might want to handle this more gracefully depending on your needs.
            raise Exception(f"Could not load secrets from Secret Manager: {str(e)}")
            
    else:
        # Local environment: Load from a .env file
        load_dotenv()
        print("Loaded secrets from local .env file.")

# --- Load all secrets once at the start ---
load_secrets()


# --- Your Config class is now much simpler ---
# It will read from the environment variables populated by load_secrets()
class Config:
    # --- General Config ---
    APP_ENV = os.getenv("APP_ENV", "local")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8080))
    PROJECT_ID = os.getenv("PROJECT_ID")

    # --- Database Config ---
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_CONNECTION_STRING = os.getenv("DATABASE_URL")

    # --- Auth & API Keys ---
    SECRET_KEY = os.getenv("SECRET_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # --- Redis ---
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")