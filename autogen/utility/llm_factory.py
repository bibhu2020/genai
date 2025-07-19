import os
from typing import Union
from azure.identity import DefaultAzureCredential
from langchain_openai.chat_models import AzureChatOpenAI, ChatOpenAI


class LLMFactory:
    """
    A static utility class to create and return LLM instances based on the input type.
    """

    @staticmethod
    def get_llm(llm_type: str) -> Union[AzureChatOpenAI, ChatOpenAI]:
        """
        Returns an LLM instance based on the specified type.

        Parameters:
            llm_type (str): The type of LLM to return. Valid values are 'azure' or 'openai'.

        Returns:
            Union[AzureChatOpenAI, ChatOpenAI]: The LLM instance.
        """
        if llm_type.lower() == "azure":
            # Get the Azure Credential
            credential = DefaultAzureCredential()
            token=credential.get_token("https://cognitiveservices.azure.com/.default").token

            if not token:
                raise ValueError("Token is required for AzureChatOpenAI.")
            return AzureChatOpenAI(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                azure_deployment=os.environ["AZURE_OPENAI_API_BASE_MODEL"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                api_key=token
            )
        elif llm_type.lower() == "openai":
            return ChatOpenAI(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name="gpt-4"
            )
        else:
            raise ValueError("Invalid llm_type. Use 'azure' or 'openai'.")