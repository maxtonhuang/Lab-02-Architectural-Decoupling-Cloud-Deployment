import os
import sys
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Global runtime configuration flags
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
DB_NAME = os.getenv("DB_NAME")

# Safety gate: explicitly halt processing if the API key is missing
if OPENAI_API_KEY is None:
    print(
        "Configuration Error: OPENAI_API_KEY is missing. Please set it in your .env file.",
        file=sys.stderr,
    )
    sys.exit(1)