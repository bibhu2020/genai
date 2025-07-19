import mlflow

if __name__ == "__main__":
    # start an MLflow run
    mlflow.start_run()

    # machine learning code goes here
    mlflow.log_param("param1", 5)

    # end the mlflow run
    mlflow.end_run()
    
    print("MLflow run completed successfully.")
