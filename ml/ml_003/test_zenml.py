from zenml.client import Client

# Get the active experiment tracker from ZenML
experiment_tracker = Client().active_stack.experiment_tracker

print(f"Using experiment tracker: {experiment_tracker.name}")