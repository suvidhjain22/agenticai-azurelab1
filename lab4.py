import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchToolDefinition, AzureAISearchToolResource, AISearchIndexResource, ToogitlResources, AgentThreadCreationOptions

load_dotenv()

project = AIProjectClient(
    endpoint=os.getenv("AIPROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

index_name="healthdata-index"
print(index_name)


# Iterate through the connections in your project and get the connection ID of the Azure AI Search connection.
conn_id = None
for conn in project.connections.list():
    if getattr(conn, "type", None) == "CognitiveSearch":
        conn_id = conn.id
        break

if not conn_id:
    raise ValueError("No Azure Cognitive Search connection found in this project.")

# Define the Azure AI Search tool and its resources using the latest SDK classes, and connect to your AI Search index
ai_search_tool = AzureAISearchToolDefinition()
ai_search_resource = AzureAISearchToolResource(
    index_list=[
        AISearchIndexResource(
            index_connection_id=conn_id,
            index_name=index_name # Be sure to set your index name above
        )
    ]
)

# The tool resources are used to define the tools available to the agent
tool_resources = ToolResources(azure_ai_search=ai_search_resource)

search_agent = project.agents.create_agent(
    model=os.environ["CHAT_MODEL"],
    name="search-agent",
    instructions="You are a helpful agent that is an expert at searching health plan documents.",
    tools=[ai_search_tool],
    tool_resources=tool_resources
)

# The name of the health plan we want to search for
plan_name = 'Northwind Standard'

# Create thread options with initial user message and tool resources (use dict for message)
thread_options = AgentThreadCreationOptions(
    messages=[
        {
            "role": "user",
            "content": f"Tell me about the {plan_name} plan."
        }
    ],
    tool_resources=tool_resources
)

# Use create_thread_and_process_run to create the thread, message, and run in one step
run = project.agents.create_thread_and_process_run(
    agent_id=search_agent.id,
    thread=thread_options
)

# Wait for the run to complete
import time
max_wait = 60  # seconds
waited = 0
while run.status not in ["completed", "failed"] and waited < max_wait:
    time.sleep(2)
    waited += 2
    run = project.agents.get_run(run.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    # Fetch all the messages from the thread
    messages = project.agents.messages.list(thread_id=run.thread_id)
    # Print the last assistant/agent message's text, if any
    last_msg = None
    for msg in reversed(list(messages)):
        role = getattr(msg, "role", None)
        if role and ("agent" in role.lower() or "assistant" in role.lower()):
            last_msg = msg
            break
    if last_msg and getattr(last_msg, "content", None) and isinstance(last_msg.content, list):
        for part in last_msg.content:
            if part.get("type") == "text" and "text" in part and "value" in part["text"]:
                print('Agent:', part["text"]["value"])
                break

# Delete the agent when it's done running
project.agents.delete_agent(search_agent.id)