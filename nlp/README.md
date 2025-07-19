# Machine Learning
- Supervised
    - Classification
    - Regression
- Unsupervised

In supervised learning, we have input/independent features and output/dependent features.

We use the input to train a model so that it can predict.

Example: (let's say we are training a model to detect span and not span email.)
    - Input Features
        - Email_Subject (e.g. Billionaire!!)
        - Email_Body (e.g. "You own a lottery of billions $$$")
        - Email_sender
    - Output Features
        - Spam or Ham

In this example, the input feature is TEXT which is not easy for MODEL to understand. 
- Raw text data is not directly understandable by machine learning models because they work with numerical representations.
- Embeddings convert text into meaningful numerical vectors so that models can process and understand relationships between words, sentences, or documents
- NLP (Natural Language Processing) performs embedding. Hence, NLP is needed in this context. But, NLP is broader field. It is capable of text preprocessing, embedding generation, and understanding textual data.

# Roadmap of NLP / Agenda
 - [x] python
 - [ ] Step1: text pre-processing (cleaning up input data)
    - [ ] Tokenization
    - [ ] Lemmatization
    - [ ] Stemming
 - [ ] Step2: text pre-processing (create embeddings/vectors)
    - [ ] Bow
    - [ ] IFIDF
    - [ ] Unigram
    - [ ] Bigram
 - [ ] Step3: text pre-processing (create embeddings/vectors)
    - [ ] Word2Vec
    - [ ] Average2Vec
 - [ ] Step4: Deep Learning Techniques (used for classification)
    - [ ] RNN
    - [ ] LSTM RNN
    - [ ] GRU RNN
 - [ ] Step5: Deep Learning Techniques
    - [ ] Word Embeddings
 - [ ] Step6: Deep Learning Techniques
    - [ ] Transformer
    - [ ] BERT

above list tells you the accuracy of text-processing as you go from top to bottom.

**Machine Learning Libraries** are NLTK and spacy

**Deep Learning Libraries** are Tensorflow (from Google) or Pytorch (from Meta)

## Tokenization and Basic Terminologies
**Corpus**: Paragraph is called corpus.

**Document**: Sentense is called Document.

**Vocabulary**: Unique word

**Words**: all words prsent in the corpus

### Tokenization (process to convert a paragraph into tokens)
**Corpus** --> """
I like to drink apple juice.my friend likes mango juice.
"""

**Documents** -->
- I like to drink apple juice.

- my friend likes to drink mango juice.

**Vocabulary** --> (unique words)
I,like,to,drink,apple,juice,my,friend,mango

**Words** --> (all words)
I,like,to,drink,apple,juice,my,friend,like,to,drink,mango,juice.



