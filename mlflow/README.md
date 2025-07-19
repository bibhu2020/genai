# 🚀 MLflow: End-to-End Machine Learning Lifecycle Platform

**MLflow** is an open-source platform that helps manage the complete machine learning lifecycle — from experimentation and reproducibility to model deployment and registry.

https://www.youtube.com/watch?v=bwhcEi3fryM&list=PLQqR_3C2fhUUkoXAcomOxcvfPwRn90U-g&index=3

---

## 🔧 Key Components of MLflow

| Component        | Description |
|------------------|-------------|
| **Tracking**     | Log experiments, parameters, metrics, and artifacts. Enables comparison across different runs. |
| **Projects**     | Package ML code in a reusable and reproducible format using conda, Docker, or MLproject files. |
| **Models**       | A standard format for packaging and sharing models across different ML libraries. |
| **Model Registry** | Centralized repository to manage model versions, transitions (e.g., staging → production), and annotations. |

---

## 📚 Why Use MLflow?

- ✅ **Track** and visualize experiments across teams
- ✅ **Compare** model performance easily
- ✅ **Reproduce** results reliably
- ✅ **Package and deploy** models seamlessly
- ✅ Works with many frameworks: `scikit-learn`, `TensorFlow`, `PyTorch`, `XGBoost`, etc.

---

## 🧪 Example: Logging a Model with MLflow

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Start MLflow run
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)

    # Log parameters, metrics, and model
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", acc)
    mlflow.sklearn.log_model(model, "rf_model")
```

## Model Registry Example
Use the MLflow UI or API to:

- Register a model
- Transition it between stages (e.g., Staging → Production)
- Track model versions

## 📝 Summary Table

| Feature              | Purpose                                                             |
|----------------------|---------------------------------------------------------------------|
| **Experiment Tracking** | Log and compare model runs (metrics, parameters, artifacts)         |
| **Model Packaging**     | Save models in a reusable, portable format                         |
| **Model Registry**      | Version control and stage transitions for production models        |
| **Deployment**          | Serve models via REST API or deploy to cloud platforms             |


## Useful Commands
```bash
# Run MLflow UI locally
mlflow ui

# Serve a registered model
mlflow models serve -m models:/YourModelName/Production

```

# References
- Official Site: https://mlflow.org

- GitHub: https://github.com/mlflow/mlflow


# mlflow serve
```bash
mlflow models serve \
  --model-uri runs:/428c4eee148d4a878279793b5ade420e/custom_model \
  --no-conda \
  --port 8080

```