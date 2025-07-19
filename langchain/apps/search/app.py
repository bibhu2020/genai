import streamlit as st
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, Tool
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor

class ToolFactory:
    """
    Factory class for creating various search and retrieval tools
    used by the SearchAgentApp.
    """

    @staticmethod
    def create_arxiv_tool():
        """
        Create a tool for querying Arxiv papers.

        Returns:
            ArxivQueryRun: Tool for querying Arxiv.
        """
        api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=1, doc_dcontent_chars_max=250)
        return ArxivQueryRun(api_wrapper=api_wrapper_arxiv)

    @staticmethod
    def create_wiki_tool():
        """
        Create a tool for querying Wikipedia articles.

        Returns:
            WikipediaQueryRun: Tool for querying Wikipedia.
        """
        api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_dcontent_chars_max=1000)
        return WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

    @staticmethod
    def create_rag_tool(embedding_model):
        """
        Create a Retrieval-Augmented Generation (RAG) tool using a custom
        vector store built from LangChain documentation.

        Args:
            embedding_model: The embedding model to use for vectorization.

        Returns:
            Tool: A tool for similarity search over LangChain docs.
        """
        loader = WebBaseLoader(
            web_paths=("https://docs.smith.langchain.com/",)
        )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        document_chunks = text_splitter.split_documents(docs)
        vector_store_db = Chroma.from_documents(
            document_chunks,
            embedding_model,
            collection_name="search_app_collection",
            persist_directory="../../_data/chroma_db"
        )
        retriever = vector_store_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 1}
        )
        return Tool(
            name="rag_tool",
            func=retriever.invoke,
            description="Search any information about langsmith."
        )

class SearchAgentApp:
    """
    Main application class for the Streamlit-based LangChain agent
    with integrated search tools.
    """

    def __init__(self):
        """
        Initialize the SearchAgentApp with embedding model, LLM, tools, and agent executor.
        """
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
        self.llm_groq = ChatGroq(model="Gemma2-9b-It", max_tokens=512)
        self.tools = self._init_tools()
        self.agent_executor = self._init_agent_executor()

    def _init_tools(self):
        """
        Initialize all tools (Arxiv, Wikipedia, RAG).

        Returns:
            list: List of initialized tools.
        """
        arxiv_tool = ToolFactory.create_arxiv_tool()
        wiki_tool = ToolFactory.create_wiki_tool()
        rag_tool = ToolFactory.create_rag_tool(self.embedding_model)
        return [arxiv_tool, wiki_tool, rag_tool]

    def _init_agent_executor(self):
        """
        Initialize the agent executor with the tools and prompt.

        Returns:
            AgentExecutor: Configured agent executor.
        """
        prompt = hub.pull("hwchase17/openai-functions-agent")
        agent = create_openai_tools_agent(
            llm=self.llm_groq,
            tools=self.tools,
            prompt=prompt
        )
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True
        )

    def run(self):
        """
        Run the Streamlit app, handling user input and displaying results.
        """
        st.title("LangChain Search Engine (using Agents and Tools)")
        user_input = st.text_input("Ask a question:")
        if user_input:
            with st.spinner("Thinking..."):
                response = self.agent_executor.invoke({"input": user_input})
                st.write(response["output"])

# streamlit run app.py
if __name__ == "__main__":
    app = SearchAgentApp()
    app.run()