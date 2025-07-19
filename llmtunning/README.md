# RAG vs Fine Tunning

## LLM Challenges
LLMs are very generalisistic, and not trained on real-time or domain specific data. 
Hence, it may hallucinate for specific tasks. And that's where RAG and Fine-tunning come to rescue.

E.g.
On asking, "who own 2024 Eurocup?", LLM may fail to answer the question.

## RAG
    - RAG combines two components: a retrieval system (usually based on a vector database or search engine) and a generative model (such as GPT).

    - The model retrieves relevant documents or passages from a large corpus and then generates an answer using this information. This method allows the model to pull in **external knowledge in real time**, enabling it to handle knowledge gaps that may not be encoded in the model itself.

    - RAG is particularly useful for tasks that require up-to-date information or knowledge that is too vast to be encoded within the model's training data.

    - Extra-layer of vector query on LLM slows the performance, but it is cost-effective solution.

    - Use Case: RAG is ideal for applications like knowledge retrieval, document-based question answering, or chatbots needing real-time updates (e.g., customer service bots accessing product documentation).

![Image Alt Text](./images/RAG2.png)

## RAG Challenges
    - In RAG "Retrival" phase you query your embedding dB, pull-in the simllarities and send them as context to the llm. Basically, you "Agument" the llm with additional information. LLM uses the context to "Generate" a response.
    - The challenge here is that larger the context (or simllarities match from dB), larger is the latency. Also larger the context is larger is the no of tokens sent to llm resulting into more cost.
    - This is where fine-tunning comes to rescue.


## Fine Tunning
    - Fine-tuning refers to customizing a pre-trained LLM with additional training on a specific task of new dataset for enhanced performance and accuracy.

![Image Alt Text](./images/FINETUNNING.png)

### Why fine tune?

**Better performance**:  Fine-tune the model to specific domain data, improving performance on specialized tasks (e.g., legal, medical, etc.).

**Cheaper and Faster Models**:  You may want to fine-tune a smaller model for specific task, instead of using an expensive general-purpose model like gpt4 or gpt4o.

**Differentiation**:  Fine tunning with proprietary data provides a competative advantage. Commonly used in applications like legal document review, medical diagnosis assistance, specialized creative writing, or any domain-specific language task where the model needs to understand specialized terminology or context.

### Challenges?

**Data**: Finding large volume of good quality data. 

**Computational Horsepower**: Fine-tunning requires a lot of computation resources.

**Expertise Needed**: Need skilled resources.

Putting all the points together makes it an expensive affair.

## Fine Tunning vs Not Fine Tunning

    - By "Not Fine Tunning" means, adding more data to the prompt. This can be done by prompt engineering technique or building a RAG.
    
    - In prompt engineering technique used is called "few shot examples" where you pass some examples in the prompt for LLM to respond you in the input pattern. 

    - In RAG, you retrieve simllarities from vector search, and then send them to LLM along with the prompt for LLM to find you the best match.

    - By "Fine Tunning" means, you customize the LLM or add skill to the LLM. It is also a low-latency solution.


## RAFT (Retrieval Agumented Fine Tunning)
https://www.youtube.com/watch?v=JJ1tSdsYXQ8 
It's about fine-tunning a model for RAG based solution. It's a hybrid of RAG and Fine-tunning.


## Azure Open AI - Fine Tunning
Azure Open AI provides supervised fine-tunning using LORA (Low Rank Approximation). It optimizes a sub-set of internal model weights with your particular dataset. 

Fine tunning is always in your private workspace that secures your model, and dataset. 








