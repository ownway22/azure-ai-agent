# Standard Library Imports
"""
DESCRIPTION:
    This script demonstrates how to connect an Azure AI Agent to a custom MCP server using the Foundry SDK. The agent can call server-side tools via function calling and interact with the user in a chat loop.

USAGE:
    1. Set the required environment variables (see README.md).
    2. Install all dependencies from requirements.txt.
    3. Make sure the MCP server code is available in the mcp-servers directory.
    4. Run the script:
        python 05_ai-agent-mcp-intermediate.py
    5. Enter your prompts as instructed. Type 'quit' to exit the chat.
"""
# Standard Library Imports
import asyncio        # For asynchronous programming
import json           # For working with JSON data
import os             # For interacting with the operating system (e.g., environment variables)
import time           # For time-related functions

# Context Managers
from contextlib import AsyncExitStack # For managing asynchronous contexts

# Third-Party Library Imports
from dotenv import load_dotenv        # For loading environment variables from a .env file

# Azure AI SDK Imports
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ListSortOrder, MessageRole
from azure.identity import DefaultAzureCredential # For Azure authentication

# Local/Project-Specific Imports (e.g., from your 'mcp' project)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



# Clear the console
os.system('cls' if os.name=='nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

async def connect_to_server(exit_stack: AsyncExitStack):
    server_params = StdioServerParameters(
        command="python",
        args=["./mcp-servers/mcp-server.py"],
        env=None
    )

    # Start the MCP server
    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    
    # Create an MCP client session
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))
    await session.initialize()

    # List available tools
    response = await session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools]) 

    return session

async def chat_loop(session):

    # Connect to the agents client
    agents_client = AgentsClient(
     endpoint=project_endpoint,
     credential=DefaultAzureCredential(
         exclude_environment_credential=True,
         exclude_managed_identity_credential=True
     )
    )

    # List tools available on the server
    response = await session.list_tools()
    tools = response.tools
    

    # Build a function for each tool
    def make_tool_func(tool_name):
     async def tool_func(**kwargs):
         result = await session.call_tool(tool_name, kwargs)
         return result
        
     tool_func.__name__ = tool_name
     return tool_func

    functions_dict = {tool.name: make_tool_func(tool.name) for tool in tools}
    mcp_function_tool = FunctionTool(functions=list(functions_dict.values()))
    

    # Create the agent
    agent = agents_client.create_agent(
     model=model_deployment,
     name="05_MSFT agent",
     instructions="""
     You are an expert on Microsoft Information
     """,
     tools=mcp_function_tool.definitions
    )
    

    # Enable auto function calling
    agents_client.enable_auto_function_calls(tools=mcp_function_tool)
    

    # Create a thread for the chat session
    thread = agents_client.threads.create()
    

    while True:
        user_input = input("Enter a prompt for the Microsoft agent. Use 'quit' to exit.\nUSER: ").strip()
        if user_input.lower() == "quit":
            print("Exiting chat.")
            break

        # Invoke the prompt
        message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_input,
        )   
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)


        # Monitor the run status
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
            tool_outputs = []

            if run.status == "requires_action":

                tool_calls = run.required_action.submit_tool_outputs.tool_calls

                for tool_call in tool_calls:

                    # Retrieve the matching function tool
                    function_name = tool_call.function.name
                    args_json = tool_call.function.arguments
                    kwargs = json.loads(args_json)
                    required_function = functions_dict.get(function_name)
                    
                    # Invoke the function
                    output = await required_function(**kwargs)

                    # Append the output text
                    tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output.content[0].text,
                    })
                    
                
                # Submit the tool call output
                agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)
                
        # Check for failure
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Display the response
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                print(f"{message.role}:\n{last_msg.text.value}\n")
                

    # Delete the agent when done
    # print("Cleaning up agents:")
    # agents_client.delete_agent(agent.id)
    # print("Deleted Microsoft agent.")


async def main():
    import sys
    exit_stack = AsyncExitStack()
    try:
        session = await connect_to_server(exit_stack)
        await chat_loop(session)
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
