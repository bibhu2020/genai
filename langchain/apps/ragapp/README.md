## Overview
This is learning RAG application built using Langchain and Chromadb. The application has 2 major components.

**pdfembedder.py**
This is a backend job that creates embeddings from the input pdf documents (../_data/rag_inputs) and stores in chroma Db (../_vectordbs/ragapp)

**webembedder.py**
This is a backend job that creates embeddings from the input web site contents (https://oauthapp.azurewebsites.net/) and stores in chroma Db (../_vectordbs/ragapp)

**app.py**
This is web app that allows user to query the database. It uses steamlit to construct the webpage.
