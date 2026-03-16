# Import packages
import os
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

project = AIProjectClient(
    endpoint=os.getenv("AIPROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

#print(dir(project))
