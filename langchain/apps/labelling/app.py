############## PROBLEM STATEMENT
### We are receiving product descriptions and we want to automate the categorization process using LLMs (Hair Care, Skin Care).
### To start, I will manually label a sample data file "../_data/auto-labelling.csv" as a ground truth.
### The goal is to use the sample data to assess if the LLM can label the descriptions with accuracy similar to the manual labels.
### Objective: Find the suitable LLM and prompt technique to automate the process.

############## PROBLEM SOLVING APPROACH
### Step1: Split the data from "../_data/auto-labelling.csv" into example and gold data.
### Step2: Run zero-shot, few-shot, and chain-of-thought (cot) prompting on the gold data, and evaluate the accuracy to determine the best technique.
### Step3: Optionally, test with another LLM to compare accuracy.
### Step4: Perform a comparison between few-shot and cot prompting by running the test multiple times and calculating the standard deviation.

import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tqdm import tqdm
import sys
import os

# Import necessary utilities for LLM interaction
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from langchain.utility.llm_factory import LLMFactory

# Define the prompt message templates for different techniques
user_message_template = """```{product_description}```"""

few_shot_system_message = """
    Classify the following product description into one of the following categories:
    Categories - ['Hair Care', 'Skin Care']
    Product description is delimited by triple backticks.
    Answer only 'Hair Care' or 'Skin Care'. Do not explain your answer.
"""

zero_shot_system_message = """
    Classify the following product description into one of the following categories:
    Categories - ['Hair Care', 'Skin Care']
    Product description is delimited by triple backticks.
    Answer only 'Hair Care' or 'Skin Care'. Nothing Else. Do not explain your answer.
"""

cot_system_message = """
    Given the following product description, determine the appropriate product category by following these steps:

    1. Analyze the product description for keywords and phrases indicating its usage.
    2. Identify if the description mentions keywords related to either Hair Care or Skin Care.
    3. Choose the most strongly emphasized category if both are mentioned.
    4. Output only the category label ('Hair Care' or 'Skin Care'), no explanation.
"""

class PromptEvaluator:
    _client = None  # Static variable for the LLM client

    @staticmethod
    def __initialize():
        client = LLMFactory.get_llm("openai")
        PromptEvaluator._client = client

    @staticmethod
    def get_llm():
        if PromptEvaluator._client is None:
            PromptEvaluator.__initialize()
        return PromptEvaluator._client

    @staticmethod
    def get_chain():
        from langchain_core.output_parsers import StrOutputParser
        parser = StrOutputParser()

        if PromptEvaluator._client is None:
            PromptEvaluator.__initialize()

        return PromptEvaluator._client | parser

    @staticmethod
    def __evaluate_prompt(prompt, gold_examples_data, user_message_template, samples_to_output=1):
        """
        Evaluate accuracy of model predictions on gold examples.
        Args:
            prompt (List): List of messages in the Open AI prompt format.
            gold_examples_data (str): JSON string of gold examples.
            user_message_template (str): Template for product description.
            samples_to_output (int): Number of sample predictions to display.
        Output:
            accuracy (float): Accuracy comparing model predictions to ground truth.
        """
        count = 0
        accuracy = 0
        model_predictions, ground_truths = [], []

        for example in json.loads(gold_examples_data):
            gold_input = example['Product Description']
            user_input = [{'role': 'user', 'content': user_message_template.format(product_description=gold_input)}]

            try:
                prediction = PromptEvaluator.get_chain().invoke(prompt + user_input,
                                                                config={"temperature": 0.5, "max_tokens": 4})

                model_predictions.append(prediction.strip().lower())
                ground_truths.append(example['Category'].strip().lower())

                if count < samples_to_output:
                    count += 1
                    print(f"{count}- Product Description: {example['Product Description']} - Original label: {example['Category']} - Predicted label: {prediction}")

            except Exception as e:
                print(e)
                continue

        accuracy = accuracy_score(ground_truths, model_predictions)
        return accuracy

    @staticmethod
    def __create_examples(dataset, n=4):
        """
        Create a randomized set of examples, ensuring balanced classes.
        Args:
            dataset (DataFrame): A DataFrame with product descriptions and categories.
            n (int): Number of examples to select from each category.
        Output:
            randomized_examples (JSON): JSON string of randomized examples.
        """
        hc_reviews = (dataset.Category == 'Hair Care')
        sc_reviews = (dataset.Category == 'Skin Care')

        cols_to_select = ["Product Description", "Category"]
        hc_examples = dataset.loc[hc_reviews, cols_to_select].sample(n)
        sc_examples = dataset.loc[sc_reviews, cols_to_select].sample(n)

        examples = pd.concat([hc_examples, sc_examples])
        randomized_examples = examples.sample(2 * n, replace=False)

        return randomized_examples.to_json(orient='records')

    @staticmethod
    def __create_prompt(system_message, examples, user_message_template):
        """
        Create a prompt in the expected format for LLMs.
        Args:
            system_message (str): Instructions for the classification task.
            examples (str): JSON string of examples to include.
            user_message_template (str): Template for product descriptions.
        Output:
            few_shot_prompt (List): List of formatted messages for LLM input.
        """
        few_shot_prompt = [{'role': 'system', 'content': system_message}]

        for example in json.loads(examples):
            example_description = example['Product Description']
            example_category = example['Category']

            few_shot_prompt.append({'role': 'user', 'content': user_message_template.format(product_description=example_description)})
            few_shot_prompt.append({'role': 'assistant', 'content': f"{example_category}"})

        return few_shot_prompt

    @staticmethod
    def evaluate_zero_shot_prompt(gold_examples_data):
        zero_shot_prompt = [{'role': 'system', 'content': zero_shot_system_message}]
        token_size = PromptEvaluator.get_llm().num_tokens_from_messages(zero_shot_prompt)
        accuracy = PromptEvaluator.__evaluate_prompt(zero_shot_prompt, gold_examples_data, user_message_template)
        return token_size, accuracy

    @staticmethod
    def evaluate_few_shot_prompt(examples_df, gold_examples_data):
        few_shot_examples = PromptEvaluator.__create_examples(examples_df, 2)
        few_shot_prompt = PromptEvaluator.__create_prompt(few_shot_system_message, few_shot_examples, user_message_template)
        token_size = PromptEvaluator.get_llm().num_tokens_from_messages(few_shot_prompt)
        accuracy = PromptEvaluator.__evaluate_prompt(few_shot_prompt, gold_examples_data, user_message_template)
        return token_size, accuracy

    @staticmethod
    def evaluate_cot_prompt(examples_df, gold_examples_data):
        few_shot_examples = PromptEvaluator.__create_examples(examples_df, 2)
        cot_few_shot_prompt = PromptEvaluator.__create_prompt(cot_system_message, few_shot_examples, user_message_template)
        token_size = PromptEvaluator.get_llm().num_tokens_from_messages(cot_few_shot_prompt)
        accuracy = PromptEvaluator.__evaluate_prompt(cot_few_shot_prompt, gold_examples_data, user_message_template)
        return token_size, accuracy

    @staticmethod
    def compare_few_shot_vs_cot_prompt(examples_df, gold_examples_data):
        num_eval_runs = 5
        few_shot_performance, cot_few_shot_performance = [], []

        for _ in tqdm(range(num_eval_runs)):
            examples = PromptEvaluator.__create_examples(examples_df)
            few_shot_prompt = PromptEvaluator.__create_prompt(few_shot_system_message, examples, user_message_template)
            cot_few_shot_prompt = PromptEvaluator.__create_prompt(cot_system_message, examples, user_message_template)

            few_shot_accuracy = PromptEvaluator.__evaluate_prompt(few_shot_prompt, gold_examples_data, user_message_template)
            cot_few_shot_accuracy = PromptEvaluator.__evaluate_prompt(cot_few_shot_prompt, gold_examples_data, user_message_template)

            few_shot_performance.append(few_shot_accuracy)
            cot_few_shot_performance.append(cot_few_shot_accuracy)

        few_shot_std = np.array(few_shot_performance).mean(), np.array(few_shot_performance).std()
        cot_few_shot_std = np.array(cot_few_shot_performance).mean(), np.array(cot_few_shot_performance).std()

        print(f"Standard deviation in few-shot prompt performance: {few_shot_std}.")
        print(f"Standard deviation in cot prompt performance: {cot_few_shot_std}.")

if __name__ == "__main__":
    # Prepare data for example and testing
    data = pd.read_csv("../../../_data/auto-labelling.csv")
    examples_df, gold_examples_df = train_test_split(data, test_size=0.8, random_state=42, stratify=data['Category'])

    gold_examples_data = gold_examples_df.to_json(orient='records')

    # Example usage (uncomment for testing different prompt techniques)
    # token_size, accuracy = PromptEvaluator.evaluate_zero_shot_prompt(gold_examples_data)
    # print(f"Zero-shot prompt - Token size: {token_size}, Accuracy: {accuracy}")

    # token_size, accuracy = PromptEvaluator.evaluate_few_shot_prompt(examples_df, gold_examples_data)
    # print(f"Few-shot prompt - Token size: {token_size}, Accuracy: {accuracy}")

    # token_size, accuracy = PromptEvaluator.evaluate_cot_prompt(examples_df, gold_examples_data)
    # print(f"Cot prompt - Token size: {token_size}, Accuracy: {accuracy}")

    PromptEvaluator.compare_few_shot_vs_cot_prompt(examples_df, gold_examples_data)
