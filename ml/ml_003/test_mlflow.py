import mlflow

with mlflow.start_run() as run:
    mlflow.log_param("param1", 5)
    mlflow.log_metric("accuracy", 0.87)

    # Create an artifact file
    with open("output.txt", "w") as f:
        f.write("Hello artifact")

    mlflow.log_artifact("output.txt")

    run_id = run.info.run_id
    print(f"Run ID: {run_id}")

    # Construct artifact URL based on your MLflow server config
    artifact_url = f"http://localhost:5000/mlflow-artifacts/0/{run_id}/artifacts/output.txt"
    print(f"Access your artifact here:\n{artifact_url}")
