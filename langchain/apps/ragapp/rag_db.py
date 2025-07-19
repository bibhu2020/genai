import os
import sys
from pathlib import Path
# Import necessary utilities for LLM interaction
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..'))
from utility.rag import RAG


if __name__ == "__main__":
    pdf_folder = "../../../_data/rag_input/cloud/"
    db_path = "../../../_data/db/cloud_rag_db"

    rag = RAG(pdf_folder=pdf_folder, db_path=db_path)
    #rag.build_vector_db()

    ##Now that the dB is build. let's make query and test it.
    query = "How is the company integrating AI across their various business units" 
    pdf_path = pdf_folder + "Meta-10-k-2023.pdf"

    source_document = str(Path(pdf_path).resolve())

    docs = rag.test_query(query, source_document)
    print(docs)

    # Print the retrieved docs, their source and the page number
    # (page number can be accessed using doc.metadata['page'] )
    for i, doc in enumerate(docs):
        print(f"Retrieved chunk {i+1}: \n")
        print(doc)
        print(doc.page_content.replace('\t', ' '))
        print("Source: ", doc.metadata['source'],"\n ")
        print("Page Number: ",doc.metadata['page'],"\n===================================================== \n")
        print('\n')