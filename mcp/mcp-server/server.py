import os
import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from azure.identity import ManagedIdentityCredential, AzureCliCredential
from azure.mgmt.loganalytics import LogAnalyticsManagementClient

load_dotenv()  # loads PG_HOST, PG_USER, PG_PASS, PG_DB

# FastAPI instance
app = FastAPI()

# PostgreSQL query function
def query_postgres_tool(query: str):
    """
    Function to query data from PostgreSQL.
    """
    try:
        print(f"Executing query: {query}")
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DATABASE")
        )
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        print(f"Error querying PostgreSQL with query: {query}")
        print(f"Error: {str(e)}")
        raise


# Function to insert data into PostgreSQL
def insert_postgres_tool(table: str, data: dict):
    """
    Insert data into the specified PostgreSQL table.
    """
    try:
        columns = ', '.join(data.keys())
        values = ', '.join([f"%s" for _ in data.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        print(f"Insert Query: {query}")
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DATABASE")
        )
        
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                print(f"Inserted data into {table} successfully")
    except Exception as e:
        print(f"Error inserting data into {table} with query: {query}")
        print(f"Error: {str(e)}")
        raise


# Function to update data in PostgreSQL
def update_postgres_tool(table: str, data: dict, condition: dict):
    """
    Update data in the specified PostgreSQL table.
    """
    try:
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        where_clause = ' AND '.join([f"{col} = %s" for col in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        print(f"Update Query: {query}")
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DATABASE")
        )
        
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(data.values()) + tuple(condition.values()))
                conn.commit()
                print(f"Updated data in {table} successfully")
    except Exception as e:
        print(f"Error updating data in {table} with query: {query}")
        print(f"Error: {str(e)}")
        raise


# Function to delete data from PostgreSQL
def delete_postgres_tool(table: str, condition: dict):
    """
    Delete data from the specified PostgreSQL table.
    """
    try:
        where_clause = ' AND '.join([f"{col} = %s" for col in condition.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"

        print(f"Delete Query: {query}")
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DATABASE")
        )
        
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, tuple(condition.values()))
                conn.commit()
                print(f"Deleted data from {table} successfully")
    except Exception as e:
        print(f"Error deleting data from {table} with query: {query}")
        print(f"Error: {str(e)}")
        raise


# Function to get Azure Log Analytics token using Managed Identity
def get_azure_token_managed_identity():
    """
    Uses Managed Identity (FIC) to get an Azure Access Token for querying Log Analytics.
    """
    try:
        print("Initializing ManagedIdentityCredential with client_id:", os.getenv("MANAGED_IDENTITY_CLIENT_ID"))
        credential = ManagedIdentityCredential(client_id=os.getenv("MANAGED_IDENTITY_CLIENT_ID"))
        
        # Set the Log Analytics resource endpoint for Azure
        log_analytics_resource = "https://api.loganalytics.io/.default"
        
        # Use the credential to get the token for Log Analytics
        print(f"Requesting token for resource: {log_analytics_resource}")
        token = credential.get_token(log_analytics_resource)
        print(f"Token retrieved successfully: {token.token[:10]}...")  # Log part of the token for debugging (for security, not log the full token)
        return token.token
    except Exception as e:
        print(f"Error obtaining Azure token: {str(e)}")
        raise


# Function to query Azure Log Analytics using KQL
def query_log_analytics(kql_query: str):
    log_analytics_url = os.getenv("AZURE_LOG_ANALYTICS_API_URL")
    print(f"Using Log Analytics API URL: {log_analytics_url}")
    
    try:
        token = get_azure_token_managed_identity()  # Fetch token from Managed Identity
    except Exception as e:
        print(f"Error fetching token: {str(e)}")
        raise
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query_payload = {
        "query": kql_query
    }
    
    # Log the query for debugging purposes
    print(f"Sending query to Log Analytics: {kql_query}")

    # Send the request to Log Analytics API
    response = requests.post(log_analytics_url, json=query_payload, headers=headers)
    
    # Log the response for debugging
    print(f"Received response status code: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to query Log Analytics with query: {kql_query}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to query Log Analytics: {response.text}")


# Postgres query endpoint
@app.post("/query_postgres")
async def query_postgres_endpoint(request: Request):
    """
    Expects JSON of the form {"query": "..."}.
    Returns {"rows": [...]} with all non‑JSON types converted.
    """
    body = await request.json()
    sql = body.get("query")
    if not sql:
        return JSONResponse(status_code=400, content={"error": "Missing 'query' in request body."})

    try:
        rows = query_postgres_tool(sql)
    except Exception as e:
        print(f"Error executing query: {sql}")
        print(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": f"Error executing query: {e}"})

    # Use jsonable_encoder to handle dates, decimals, etc.
    payload = {"rows": rows}
    return JSONResponse(content=jsonable_encoder(payload))


# Insert Postgres data endpoint
@app.post("/insert_postgres")
async def insert_postgres_endpoint(request: Request):
    """
    Expects JSON of the form {"table": "...", "data": {...}}.
    Returns success or failure message.
    """
    body = await request.json()
    table = body.get("table")
    data = body.get("data")

    if not table or not data:
        return JSONResponse(status_code=400, content={"error": "Missing 'table' or 'data' in request body."})

    try:
        insert_postgres_tool(table, data)
        return JSONResponse(status_code=200, content={"status": "success", "message": f"Inserted data into {table}"})
    except Exception as e:
        print(f"Error during insert with data: {data}")
        return JSONResponse(status_code=500, content={"error": f"Error during insert: {str(e)}"})


# Update Postgres data endpoint
@app.put("/update_postgres")
async def update_postgres_endpoint(request: Request):
    """
    Expects JSON of the form {"table": "...", "data": {...}, "condition": {...}}.
    Returns success or failure message.
    """
    body = await request.json()
    table = body.get("table")
    data = body.get("data")
    condition = body.get("condition")

    if not table or not data or not condition:
        return JSONResponse(status_code=400, content={"error": "Missing 'table', 'data' or 'condition' in request body."})

    try:
        update_postgres_tool(table, data, condition)
        return JSONResponse(status_code=200, content={"status": "success", "message": f"Updated data in {table}"})
    except Exception as e:
        print(f"Error during update with query: {data} WHERE {condition}")
        return JSONResponse(status_code=500, content={"error": f"Error during update: {str(e)}"})


# Delete Postgres data endpoint
@app.delete("/delete_postgres")
async def delete_postgres_endpoint(request: Request):
    """
    Expects JSON of the form {"table": "...", "condition": {...}}.
    Returns success or failure message.
    """
    body = await request.json()
    table = body.get("table")
    condition = body.get("condition")

    if not table or not condition:
        return JSONResponse(status_code=400, content={"error": "Missing 'table' or 'condition' in request body."})

    try:
        delete_postgres_tool(table, condition)
        return JSONResponse(status_code=200, content={"status": "success", "message": f"Deleted data from {table}"})
    except Exception as e:
        print(f"Error during delete with query: DELETE FROM {table} WHERE {condition}")
        return JSONResponse(status_code=500, content={"error": f"Error during delete: {str(e)}"})


# Log Analytics query endpoint
@app.post("/query_log_analytics")
async def query_log_analytics_endpoint(request: Request):
    """
    Expects JSON of the form {"query": "<KQL query>"}.
    Returns the query result from Azure Log Analytics.
    """
    body = await request.json()
    kql_query = body.get("query")
    
    if not kql_query:
        return JSONResponse(status_code=400, content={"error": "Missing 'query' in request body."})

    try:
        result = query_log_analytics(kql_query)
        return JSONResponse(content={"result": result})
    except Exception as e:
        print(f"Error querying Log Analytics with query: {kql_query}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# Health check endpoint to check if the server is running
@app.get("/healthz")
async def health_check():
    """
    A health check endpoint that verifies if the server is up and the database connection is working.
    """
    try:
        # Test the PostgreSQL connection by running a simple query
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DATABASE")
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                if result:
                    return JSONResponse(status_code=200, content={"status": "ok", "database": "connected"})
                else:
                    return JSONResponse(status_code=500, content={"status": "error", "message": "Database query failed"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# Main entry point for running the app
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
