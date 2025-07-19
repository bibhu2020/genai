import streamlit as st
import os
from pathlib import Path

import sqlite3
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

st.set_page_config(page_title="SQL Chat", page_icon=":robot_face:")
st.title("LangChain: Chat with SQL Db")

INJECTION_WARNING = """
**Warning:** This app is for educational purposes only. Do not use it with sensitive data.
"""

LOCALDB = "../../_data/student.db"
POSTGRES = "USE_POSTGRES"

# UI
radio_opts = ["Use SQLLite 3 Database - Student.dB", "Connect to Neon Postgres Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opts)
if radio_opts.index(selected_opt) == 1:
    db_uri = POSTGRES
    pg_host = st.sidebar.text_input("Postgres Host", value=os.getenv("PGHOST"))
    pg_port = st.sidebar.text_input("Postgres Port", value="5432")
    pg_user = st.sidebar.text_input("Postgres User", value=os.getenv("PGUSER"))
    pg_password = st.sidebar.text_input("Postgres Password", value=os.getenv("PGPASSWORD"), type="password")
    pg_db = st.sidebar.text_input("Postgres Database", value=os.getenv("PGDATABASE"))
    # pg_host = st.sidebar.text_input("Postgres Host", value="ep-xxx.neon.tech")
    # pg_port = st.sidebar.text_input("Postgres Port", value="5432")
    # pg_user = st.sidebar.text_input("Postgres User", value="your_user")
    # pg_password = st.sidebar.text_input("Postgres Password", type="password")
    # pg_db = st.sidebar.text_input("Postgres Database", value="student_db")
else:
    db_uri = LOCALDB

groq_api_key = st.sidebar.text_input("API Key", type="password", help="Enter your Groq API key to use the LLM.")       

if not db_uri:
    st.info("Please select a database to connect to.")

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.info("Please enter your Groq API key to use the LLM.")

from langchain_groq import ChatGroq
llm = ChatGroq(model="Gemma2-9b-It", max_tokens=512)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, pg_host=None, pg_port=None, pg_user=None, pg_password=None, pg_db=None):
    """
    Configure the database connection based on the selected URI.
    """
    if db_uri == LOCALDB:
        db_path = Path(LOCALDB)
        creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        engine = create_engine(f"sqlite:///", creator=creator)
        db = SQLDatabase(engine, include_tables=["students"])
    elif db_uri == POSTGRES:
        if not all([pg_host, pg_port, pg_user, pg_password, pg_db]):
            st.error("Please provide all Postgres connection details.")
            return None
        # Construct the Postgres connection URI for Neon
        pg_uri = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        engine = create_engine(pg_uri)
        db = SQLDatabase(engine, include_tables=["Employees", "Customers", "Suppliers", "Shippers", "Orders", "Products", "OrderDetails"])
    else:
        st.error("Unsupported database URI.")
        return None
    return db

if db_uri == POSTGRES:
    db = configure_db(db_uri, pg_host, pg_port, pg_user, pg_password, pg_db)
else:
    db = configure_db(db_uri)
if db is None:
    st.error("Failed to connect to the database. Please check your connection details.")
if db:
    # Create the SQL agent
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Streamlit app for user input and displaying results
    st.write(INJECTION_WARNING)

    user_input = st.text_input("Ask a question about the database:")

    # Initialize chat history in session state or reset if button pressed
    reset_clicked = st.sidebar.button("Reset Chat")
    if "messages" not in st.session_state or reset_clicked:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I can help you with questions about the database."}]
        if reset_clicked:
            st.stop()  # Prevents further code execution after rerun

    # Display chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Only process user input if not just reset and input is provided
    if not reset_clicked and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            steamlit_callback = StreamlitCallbackHandler(st.container())
            response = agent.invoke(
                user_input,
                callbacks=[steamlit_callback]
            )
            st.session_state.messages.append({"role": "assistant", "content": response["output"]})
            st.write(response)