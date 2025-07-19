############## PROBLEM STATEMENT
# We have received 1000s of user queries at the customer support center.
# Our objective is to classify the problem into 3 major categories so that we can address them on priority.

############## PROBLEM SOLVING APPROACH
# Step 1: Take a sample from the queries received (`../_data/customer_intent_raw.csv`) and ask the LLM to find 3 top categories for you. 
# Do multiple runs to find the most frequent ones.
#
# Step 2: Take another sample of data, label them manually using the 3 categories you found, label others where there is no match.
#
# Step 3: Use the labeled sample data to evaluate which prompt technique you should use to categorize the query. 
# This will involve evaluating different prompt techniques.

import json
import os
import sys
import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from utility.llm_factory import LLMFactory
from langchain_core.output_parsers import StrOutputParser

# Define Classification class for processing queries and finding categories
class Classification:
    @staticmethod
    def find_top_5_category():
        # Load dataset containing user queries
        dataset = pd.read_csv("../../../_data/customer_intent_raw.csv")
        raw_intent = dataset['description'].str.cat(sep=' || ')

        # Create a prompt to extract problems and find the top 5 categories
        prompt = f"""Extract the list of problems faced by the user from the following customer queries, separated by " || ". 
                     A problem category should be a two word label. List out 10 unique problems.
                     Then, identify the top 5 most frequent problems encountered by the user.

                     Customer queries:
                     {raw_intent}"""

        # Create message for LLM
        messages = [{'role':'user','content':prompt}]

        # Get response from the LLM
        response = PropmtEvaluator.get_chain().invoke(messages, config={"temperature": 0, "seed": 49})
        print(response)

# Define PropmtEvaluator class for evaluating and selecting the best prompt techniques
class PropmtEvaluator:
    _client = None  # Static variable for the LLM client
    _user_message_template = """```{description}```"""

    _few_shot_system_message = """Classify the following product desciption presented in the input into one of the following categories.
        Categories - ['change order', 'track order', 'payment issue']
        Product description will be delimited by triple backticks in the input.
        Answer only 'change order', or 'track order', or 'payment issue'. Nothing Else. Do not explain your answer.
    """
    _zero_shot_system_message = """Classify the following product desciption presented in the input into one of the following categories.
        Categories - ['change order', 'track order', 'payment issue', 'others']
        Product description will be delimited by triple backticks in the input.
        Answer only 'change order',
        or 'track order', or 'payment issue',or 'others'. Nothing Else. Do not explain your answer.
    """

    @staticmethod
    def __initialize():
        """ Initialize the LLM client """
        client = LLMFactory.get_llm("groq")
        PropmtEvaluator._client = client

    @staticmethod
    def get_llm():
        """ Retrieve the LLM client """
        if PropmtEvaluator._client is None:
            PropmtEvaluator.__initialize()
        return PropmtEvaluator._client

    @staticmethod
    def get_chain():
        parser = StrOutputParser()
        """ Retrieve the LLM pipeline chain """
        if PropmtEvaluator._client is None:
            PropmtEvaluator.__initialize()
        chain = PropmtEvaluator._client | parser 
        return chain

    @staticmethod
    def __evaluate_prompt(prompt, gold_examples, user_message_template, samples_to_output=5):
        """
        Evaluate a given prompt based on its accuracy using the gold examples.
        """
        count = 0
        model_predictions, ground_truths = [], []

        # Iterate over the gold examples and make predictions
        for example in json.loads(gold_examples):
            gold_input = example['description']
            user_input = [{'role':'user', 'content': user_message_template.format(description=gold_input)}]

            try:
                prediction = PropmtEvaluator.get_chain().invoke(prompt + user_input, config={"temperature": 0, "max_tokens": 4})
                
                while count < samples_to_output:
                    count += 1
                    print(f"{count}-Original label: {example['task']} - Predicted label: {prediction}")

                model_predictions.append(prediction.strip().lower())  # Remove whitespace and lowercase output
                ground_truths.append(example['task'].strip().lower())
            except Exception as e:
                print(e)
                continue

        # Calculate accuracy for each category
        df = pd.DataFrame({'Predictions': model_predictions, 'Ground Truth': ground_truths})
        labels = df['Ground Truth'].unique()

        accuracy_df = pd.DataFrame(columns=labels)
        for label in labels:
            subset = df[df['Ground Truth'] == label]
            accuracy = accuracy_score(subset['Ground Truth'], subset['Predictions'])
            accuracy_df.loc[0, label] = accuracy

        print("\n\n", accuracy_df)
        print("====================================================")

        # Overall accuracy
        accuracy = accuracy_score(ground_truths, model_predictions)
        return accuracy

    @staticmethod
    def __create_examples(examples_df, n=4):
        """
        Create randomized examples from each class.
        """
        task1 = (examples_df.task == 'change order')
        task2 = (examples_df.task == 'track order')
        task3 = (examples_df.task == 'payment issue')
        task4 = (examples_df.task == 'others')

        t1_examples = examples_df.loc[task1, :].sample(n)
        t2_examples = examples_df.loc[task2, :].sample(n)
        t3_examples = examples_df.loc[task3, :].sample(n)
        t4_examples = examples_df.loc[task4, :].sample(n)
        examples = pd.concat([t1_examples, t2_examples, t3_examples, t4_examples])
        randomized_examples = examples.sample(4*n, replace=False)

        return randomized_examples.to_json(orient='records')

    @staticmethod
    def __create_prompt(system_message, examples, user_message_template):
        """
        Create a few-shot prompt for the classification task.
        """
        few_shot_prompt = [{'role':'system', 'content': system_message}]
        for example in json.loads(examples):
            few_shot_prompt.append({'role': 'user', 'content': user_message_template.format(description=example['description'])})
            few_shot_prompt.append({'role': 'assistant', 'content': f"{example['task']}"})

        return few_shot_prompt

    @staticmethod
    def evaluate_zero_shot_promt(gold_examples):
        """
        Evaluate zero-shot prompt on gold examples.
        """
        zero_shot_prompt = [{'role':'system', 'content': PropmtEvaluator._zero_shot_system_message}]
        token_size = LLMFactory.num_tokens_from_messages(zero_shot_prompt)
        accuracy = PropmtEvaluator.__evaluate_prompt(zero_shot_prompt, gold_examples, PropmtEvaluator._user_message_template)
        return token_size, accuracy

    @staticmethod
    def evaluate_few_shot_promt(examples_df, gold_examples):
        """
        Evaluate few-shot prompt on gold examples.
        """
        few_shot_examples = PropmtEvaluator.__create_examples(examples_df, 2)
        few_shot_prompt = PropmtEvaluator.__create_prompt(PropmtEvaluator._few_shot_system_message, few_shot_examples, PropmtEvaluator._user_message_template)
        token_size = LLMFactory.num_tokens_from_messages(few_shot_prompt)
        accuracy = PropmtEvaluator.__evaluate_prompt(few_shot_prompt, gold_examples, PropmtEvaluator._user_message_template)
        return token_size, accuracy

# Main execution
if __name__ == "__main__":
    # Step 1: Find the top 3 categories
    # Classification.find_top_5_category()

    # Step 2: Label data manually using top 3 categories found earlier.

    # Step 3: Evaluate prompt techniques for labeling
    dataset_df = pd.read_csv("../../../_data/customer_intent_labeled.csv")
    examples_df, gold_examples_df = train_test_split(dataset_df, test_size=0.6, random_state=42)

    num_eval_runs = 1
    few_shot_performance = []

    # Perform evaluation multiple times with random data splits
    for _ in tqdm(range(num_eval_runs)):
        gold_examples = (gold_examples_df.sample(100, random_state=42).to_json(orient='records'))
        token_size, few_shot_accuracy = PropmtEvaluator.evaluate_few_shot_promt(examples_df, gold_examples)
        few_shot_performance.append(few_shot_accuracy)

    # Print evaluation results
    print(f"Few-shot performance: {few_shot_performance}")
