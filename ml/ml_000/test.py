import mlflow
import os

# Define experiment name
experiment_name = "genai-clean"

# Point to your MLflow tracking server running in Docker
mlflow.set_tracking_uri("http://localhost:5000")
print("Tracking URI:", mlflow.get_tracking_uri())

# Let the server create the experiment if it doesn't exist
mlflow.set_experiment(experiment_name)

# Verify where artifacts will go (on the server side)
exp = mlflow.get_experiment_by_name(experiment_name)
print("Artifact location (server-managed):", exp.artifact_location)

# Create a small dummy file to log as an artifact
with open("README.md", "w") as f:
    f.write("This is a test artifact for MLflow.\n")

# Start the run and log data
with mlflow.start_run() as run:
    mlflow.log_param("param1", 42)
    mlflow.log_artifact("README.md")
    print("✅ Successfully logged to run:", run.info.run_id)

# URLs to verify in browser
print(f"🔗 Run: http://localhost:5000/#/experiments/{exp.experiment_id}/runs/{run.info.run_id}")
print(f"📁 Artifact path (on server): {exp.artifact_location}/{run.info.run_id}/artifacts")
