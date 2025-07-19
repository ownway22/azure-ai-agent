"""
DESCRIPTION:
    This script implements an AI assistant using Azure OpenAI services with Model Context Protocol (MCP) servers.
    It integrates PowerPoint and Excel MCP servers to enable the AI assistant to create and manipulate
    PowerPoint presentations and Excel spreadsheets based on user requests. The assistant can interact
    with the filesystem, read files, create and edit PowerPoint presentations, and work with Excel data.

USAGE:
    1. Ensure you have the following environment variables set in a .env file:
       - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
       - AZURE_OPENAI_API_VERSION: API version (e.g., "2023-05-15")
       - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
       - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: Your deployed model name

    2. Install required dependencies:
       - Python packages: openai, python-dotenv, and the agents library
       - Node.js and npx must be installed for MCP servers

    3. Run the script:
       python azure-ai-agent-with-mcp.py

    4. Interact with the assistant through the command line interface
       Type '離開' or 'exit' to end the conversation
"""

# Standard Library Imports
import asyncio   # For asynchronous programming
import logging   # For logging events and debugging
import os        # For interacting with the operating system (e.g., file paths, environment variables)
import shutil    # For high-level file operations (e.g., copying, deleting directories)
import sys       # For system-specific parameters and functions (e.g., exit, path management)
import warnings  # For issuing warning messages

# Third-Party Library Imports
from dotenv import load_dotenv      # For loading environment variables from a .env file
from openai import AsyncAzureOpenAI # For interacting with Azure OpenAI services asynchronously

# Local Application/Project Imports
# These modules are likely part of your 'agents' package within your project.
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerSse, MCPServerStdio



# Suppress ResourceWarning for asyncio event loop closing on Windows
warnings.filterwarnings("ignore", category=ResourceWarning)

# Suppress critical logging from asyncio
if hasattr(asyncio, 'windows_events'):
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Use unraisablehook to ignore specific unhandled exceptions (Python 3.8+)
def ignore_unraisable_hook(unraisable):
    if isinstance(unraisable.exc_value, (RuntimeError, ValueError)):
        return  # Ignore "event loop is closed" and "I/O operation on closed pipe"
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = ignore_unraisable_hook


def get_azure_open_ai_client():
    """
    Creates and returns Azure OpenAI client instance.
    
    Returns:
        AsyncAzureOpenAI: Configured Azure OpenAI client
    """
    load_dotenv()
    
    return AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


async def run(mcp_servers: list[MCPServer]):

    azure_open_ai_client = get_azure_open_ai_client()
    set_tracing_disabled(disabled=True)

    agent = Agent(
        name="AI Assistant",
        instructions="You are a helpful AI assistant. Use the available tools to interact with the filesystem (e.g., read files, list directories), manage PowerPoint presentations (e.g., create presentations, add slides, save files), and create/edit Excel spreadsheets (e.g., create workbooks, read and write data, apply formulas) to assist the user with their requests. Respond to the user based on the information you gather or the actions you perform.",
        model=OpenAIChatCompletionsModel(model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"), 
                                         openai_client=azure_open_ai_client),
        mcp_servers=mcp_servers,
    )

    print("Hello! I'm your AI Assistant, here to help you generate PowerPoint presentations and Excel data tables. You can type '離開' or 'exit' at any time to end our conversation.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["離開", "退出", "exit", "quit"]:
                print("Ending conversation.")
                break

            if not user_input:
                continue

            print(f"\nAI Assistant is processing: {user_input}...")
            result = await Runner.run(starting_agent=agent, input=user_input)
            print(f"\nAI Assistant: {result.final_output}")

        except KeyboardInterrupt:
            print("\nConversation ended due to user interruption.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, decide if the loop should break or continue on other errors


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")

    # PowerPoint MCP Server
    # soucre: https://playbooks.com/mcp/office-powerpoint
    ppt_server = MCPServerStdio(
        name="ppt",
        params={
            "command": "uvx",
            "args": ["--from", "office-powerpoint-mcp-server", "ppt_mcp_server"],
        },
    )

    # Excel MCP Server
    # source: https://playbooks.com/mcp/excel-data-manager
    excel_server = MCPServerStdio(
        name="excel",
        params={
            "command": "uvx",
            "args": ["mcp-excel-server"],
        }
    )

    async with ppt_server, excel_server:
        await run([ppt_server, excel_server])


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it using `npm install -g npx`.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted, gracefully shutting down.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # Windows asyncio bug workaround: Force cleanup of all pending tasks
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()
        except Exception:
            pass  # Loop might already be closed, ignore this error