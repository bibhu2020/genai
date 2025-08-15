import requests

# response = requests.post(
#     "http://localhost:8000/query_postgres",
#     json={"query": 'SELECT "ContactName" FROM "Customers";'}
# )

# response = requests.post(
#     "https://srepoc-mcp-server-python-b5cydkbnamgafyab.b01.azurefd.net/query_postgres",
#     json={"query": 'SELECT "ContactName" FROM "Customers";'}
# )

response = requests.post(
    "http://localhost:8000/query_log_analytics",
    json={"query": 'Heartbeat | summarize count() by Computer'}
)


print(response.json())