from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Abstract Base Class for Missing Values Analysis
# -----------------------------------------------
# This class defines a template for missing values analysis.
# Subclasses must implement the methods to identify and visualize missing values.
class MissingValuesAnalysisTemplate(ABC):
    def analyze(self, df: pd.DataFrame):
        """
        Performs a complete missing values analysis by identifying and visualizing missing values.

        Parameters:
        df (pd.DataFrame): The dataframe to be analyzed.

        Returns:
        None: This method performs the analysis and visualizes missing values.
        """
        self.identify_missing_values(df)
        self.visualize_missing_values(df)

    @abstractmethod
    def identify_missing_values(self, df: pd.DataFrame):
        """
        Identifies missing values in the dataframe.

        Parameters:
        df (pd.DataFrame): The dataframe to be analyzed.

        Returns:
        None: This method should print the count of missing values for each column.
        """
        pass

    @abstractmethod
    def visualize_missing_values(self, df: pd.DataFrame):
        """
        Visualizes missing values in the dataframe.

        Parameters:
        df (pd.DataFrame): The dataframe to be visualized.

        Returns:
        None: This method should create a visualization (e.g., heatmap) of missing values.
        """
        pass


# Concrete Class for Missing Values Identification
# -------------------------------------------------
# This class implements methods to identify and visualize missing values in the dataframe.
class SimpleMissingValuesAnalysis(MissingValuesAnalysisTemplate):
    def identify_missing_values(self, df: pd.DataFrame):
        """
        Prints the count of missing values for each column in the dataframe.

        Parameters:
        df (pd.DataFrame): The dataframe to be analyzed.

        Returns:
        None: Prints the missing values count to the console.
        """
        # 📋 Count missing values per column
        missing_per_column = df.isnull().sum()

        # 🎯 Filter only columns with missing values
        missing_columns = missing_per_column[missing_per_column > 0]

        # 🧮 Count how many columns have missing values
        num_missing_columns = missing_columns.shape[0]

        # 📊 Print only missing columns and their missing counts
        print("📌 Columns with missing values and their counts:")
        print(missing_columns)

        # 🧾 Print number of columns with missing data
        print(f"\n🧮 Total columns with missing values: {num_missing_columns}")

        # 📈 (Optional) Add percentage of missing values
        total_rows = len(df)
        missing_summary = missing_columns.to_frame(name="Missing Count")
        missing_summary["% Missing"] = (missing_summary["Missing Count"] / total_rows * 100).round(2)

        print("\n📈 Missing Values Summary (with %):")
        print(missing_summary)

    def visualize_missing_values(self, df: pd.DataFrame):
        """
        Creates a heatmap to visualize the missing values in the dataframe.

        Parameters:
        df (pd.DataFrame): The dataframe to be visualized.

        Returns:
        None: Displays a heatmap of missing values.
        """
        print("\nVisualizing Missing Values...")
        plt.figure(figsize=(20, 20))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
        plt.title("Missing Values Heatmap")
        plt.xlabel("Columns")
        plt.show()


# Example usage
if __name__ == "__main__":
    # Example usage of the SimpleMissingValuesAnalysis class.

    # Load the data
    # df = pd.read_csv('../extracted-data/your_data_file.csv')

    # Perform Missing Values Analysis
    # missing_values_analyzer = SimpleMissingValuesAnalysis()
    # missing_values_analyzer.analyze(df)
    pass
