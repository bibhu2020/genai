@echo off
:: Usage: setup_zenml_stack.bat <stack_name> <model_deployer_name> <experiment_tracker_name>

:: Validate input
if "%~3"=="" (
    echo Usage: %~nx0 STACK_NAME MODEL_DEPLOYER_NAME TRACKER_NAME
    exit /b 1
)

set STACK_NAME=%1
set MODEL_NAME=%2
set TRACKER_NAME=%3

echo Installing mlflow integration...
zenml integration install mlflow -y

echo Registering experiment tracker: %TRACKER_NAME%
zenml experiment-tracker register %TRACKER_NAME% --flavor=mlflow --tracking_uri=http://localhost:5000 --tracking_token="dummy_token"

echo Registering model deployer: %MODEL_NAME%
zenml model-deployer register %MODEL_NAME% --flavor=mlflow --tracking_uri=http://localhost:5000 --tracking_token="dummy_token"

echo Registering stack: %STACK_NAME%
zenml stack register %STACK_NAME% -a default -o default -d %MODEL_NAME% -e %TRACKER_NAME% --set

echo Updating artifact store for stack: %STACK_NAME%
zenml stack update %STACK_NAME% -a minio_store

echo ✅ ZenML stack '%STACK_NAME%' set up successfully.


