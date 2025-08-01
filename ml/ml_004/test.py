# from zenml.client import Client

# client = Client()
# pipeline_runs = client.list_pipeline_runs(name="train_pipeline")

# if not pipeline_runs:
#     print("❌ No pipeline runs found for 'continuous_deployment_pipeline'")
# else:
#     latest_run = pipeline_runs[0]
#     print(f"✅ Found run: {latest_run.name}")


from zenml.client import Client
print(Client().active_stack.artifact_store.path)
