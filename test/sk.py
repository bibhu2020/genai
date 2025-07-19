from semantic_kernel import Kernel
from semantic_kernel.skill_definition import sk_function
from semantic_kernel.planning.basic_planner import BasicPlanner
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.identity import DefaultAzureCredential

# ---------------------------
# Step 1: Define a Plugin
# ---------------------------

class MathPlugin:
    @sk_function(name="Add", description="Add two numbers")
    def add(self, a: str, b: str) -> str:
        return str(float(a) + float(b))

    @sk_function(name="Multiply", description="Multiply two numbers")
    def multiply(self, a: str, b: str) -> str:
        return str(float(a) * float(b))

# ---------------------------
# Step 2: Setup Kernel
# ---------------------------

kernel = Kernel()

# Replace with your actual deployment name and endpoint
deployment_name = "gpt-4o"
endpoint = "https://srepoc-ai-services.openai.azure.com"
# endpoint = "https://srepoc-ai-services.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
credential=DefaultAzureCredential()
token=credential.get_token("https://cognitiveservices.azure.com/.default").token

print(f"Token: {token}")


# Azure OpenAI authentication using CLI credential
kernel.add_chat_service(
    service_id="azure-openai",
    service=AzureChatCompletion(
        deployment_name=deployment_name,
        endpoint=endpoint,
        ad_token=token
    )
)

# Register the plugin
math_plugin = MathPlugin()
kernel.import_skill(math_plugin, skill_name="MathPlugin")

# ---------------------------
# Step 3: Use Basic Planner
# ---------------------------

planner = BasicPlanner(kernel)

goal = "Please add 4 and 6 and then multiply the result by 10"

# Generate plan
plan = planner.create_plan(goal)
print("\n🧠 Plan created:\n", plan)

# Execute plan
result = plan.invoke()
print("\n✅ Final Result:\n", result.result)
