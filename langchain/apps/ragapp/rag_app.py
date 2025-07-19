import os
import sys
from pathlib import Path
# Import necessary utilities for LLM interaction
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from utility.rag import RAG


if __name__ == "__main__":
    # Create the vectod embeddings
    pdf_folder = "../../../_data/rag_input/cloud/"
    db_path = "../../../_data/db/cloud_rag_db"

    rag = RAG(pdf_folder=pdf_folder, db_path=db_path)
    
    user_question = "How is the company integrating AI across their various business units?"
    pdf_path = pdf_folder + "google-10-k-2023.pdf"
    source_document = str(Path(pdf_path).resolve())

    answer = rag.question_and_answer(user_question, source_document)

    print(answer)

