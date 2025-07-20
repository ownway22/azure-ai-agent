"""
DESCRIPTION:
    This script demonstrates how to create and interact with an Azure AI Agent for conversational purposes. The agent can chat, tell jokes, and respond to user input in a simple command-line interface.

USAGE:
    1. Set the required environment variables (see README.md).
    2. Install all dependencies from requirements.txt.
    3. Run the script:
        python 02_ai-agent-intermediate.py
    4. Enter your messages as prompted. Type 'exit' or '離開' to end the conversation.
"""
import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    ThreadMessageOptions,
    MessageTextContent,
    ListSortOrder,
)
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    async with project_client:
        agents_client = project_client.agents

        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="02 App agent",
            instructions="You are a helpful assistant that tells jokes and can have a conversation with the user.",
        )
        print(f"Created agent, agent ID: {agent.id}")
        
        # Create a thread for the conversation
        thread_response = await agents_client.threads.create()
        thread_id = thread_response.id
        print(f"Created thread, thread ID: {thread_id}")
        
        print("Chat session started. Type '離開' or 'exit' to end the conversation.")
        print("-" * 50)
        
        # Initial greeting
        await send_message_and_display_response(
            agents_client, 
            agent.id, 
            thread_id, 
            "Hi! I'd like to chat with you."
        )
        
        # Main conversation loop
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["離開", "退出", "exit", "quit"]:
                print("Ending conversation...")
                break

            await send_message_and_display_response(agents_client, agent.id, thread_id, user_input)

        # Clean up
        # await agents_client.delete_agent(agent.id)
        # print(f"Deleted agent {agent.id!r}")


async def send_message_and_display_response(agents_client, agent_id, thread_id, message_content):
    """Send a message to the agent and display its response."""
    # Add the user message to the thread
    await agents_client.messages.create(thread_id=thread_id, role="user", content=message_content)

    # Create and process a run
    run = await agents_client.runs.create(thread_id=thread_id, agent_id=agent_id)

    # Poll until the run completes
    while run.status not in ["completed", "failed", "cancelled"]:
        await asyncio.sleep(1)
        run = await agents_client.runs.get(thread_id=thread_id, run_id=run.id)
    
    if run.status == "failed":
        print(f"Assistant: Run error: {run.last_error}")
        return
    
    # Get the latest assistant message
    messages = agents_client.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING, limit=1)

    async for msg in messages:
        if msg.role == "assistant":
            last_part = msg.content[-1]
            if isinstance(last_part, MessageTextContent):
                print(f"Assistant: {last_part.text.value}")
                break


if __name__ == "__main__":
    asyncio.run(main())