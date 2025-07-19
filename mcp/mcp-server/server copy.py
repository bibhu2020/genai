# mcp_server/server.py
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn

load_dotenv()  # loads PG_HOST, PG_USER, PG_PASS, PG_DB

app = FastAPI()

def query_postgres_tool(query: str):
    print(os.getenv("PG_USER"))
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        dbname=os.getenv("PG_DATABASE")
    )
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()
    

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
        print(f"Error executing query: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Use jsonable_encoder to handle dates, decimals, etc.
    payload = {"rows": rows}
    return JSONResponse(content=jsonable_encoder(payload))

@app.get("/")
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

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)