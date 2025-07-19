import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.identity import AzureCliCredential

async def main():
    kernel = Kernel()

    # Replace with your Azure OpenAI details
    # deployment_name = "gpt-35-turbo"
    # endpoint = "https://<your-resource-name>.openai.azure.com/"  # ← your Azure OpenAI endpoint
    deployment_name = "gpt-4o"
    endpoint = "https://srepoc-ai-services.openai.azure.com/"

    # Use Azure CLI credential to authenticate
    chat_service = AzureChatCompletion(
        deployment_name=deployment_name,
        endpoint=endpoint,
        credential=AzureCliCredential()
    )

    # Register the chat service with the kernel
    kernel.add_chat_service("azure-openai", chat_service)

    # Use the chat service
    chat = kernel.get_service("azure-openai")
    result = await chat.complete("What's the capital of France?")
    print("🔹 Response:", result)

asyncio.run(main())
