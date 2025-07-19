from sklearn.metrics import r2_score, mean_absolute_error
import mlflow

def evaluate_model(model, X_test, y_test):
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)

    mlflow.log_metric("r2_score", r2)
    mlflow.log_metric("mae", mae)

    print(f"R2 Score: {r2}, MAE: {mae}")