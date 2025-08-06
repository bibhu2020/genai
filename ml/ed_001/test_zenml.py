from zenml.client import Client

try:
    experiment_tracker = Client().active_stack.experiment_tracker
    if not experiment_tracker:
        raise ValueError("No experiment tracker found in active stack.")
except Exception as e:
    print(f"Experiment tracker not found or misconfigured: {e}")
