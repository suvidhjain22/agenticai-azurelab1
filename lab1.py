from base_file import *

project = AIProjectClient(
    endpoint=os.getenv("AIPROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

chat = project.inference.get_chat_completions_client()
response = chat.complete(
    model=os.getenv("CHAT_MODEL"), # gpt-4o model from your project
    messages=[
        {
            "role": "system",
            "content": "You are an AI assistant that tells jokes for toddlers.",
        },
        {"role": "user", "content": "Hey, can you tell a joke about teddy bear?"},
    ],
)

print(response.choices[0].message.content)