# Install conda python on ubuntu
## Update packages
sudo apt update

## Download Miniconda (change the URL for a different Python version if needed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sha256sum Miniconda3-latest-Linux-x86_64.sh

## Run Installer
bash Miniconda3-latest-Linux-x86_64.sh

## Initialize Conda
~/miniconda3/bin/conda init

## Restart
shutdown
wsl

## check version
conda --version

# Create python environment & install additional packages for machine learning
conda create --name .autogen python=3.11.4
conda activate .autogen
conda install numpy pandas scikit-learn

conda create --name .langchain python=3.11.4
conda activate .langchain
conda install numpy pandas scikit-learn

conda deactivate

# install autogen
**The core framework provided by Microsoft AutoGen. It includes basic tools and infrastructure for creating LLM-powered agents, focusing on individual task execution.**
pip install -qU autogen
**autogen-agentchat an specialized submodule of Microsoft AutoGen designed for multi-agent collaboration and communication. It focuses on enabling agents to interact dynamically and collaboratively. GroupChat, CoverstableAgent, etc....**
pip install -qU autogen-agentchat~=0.2
**pyautoagent another library for creating agent-based systems, likely unrelated to Microsoft AutoGen but with similar naming. It’s often more general-purpose and less integrated with multi-agent systems or AutoGen-specific tools.**
#pip install -qU pyautogen
pip install -qU ipython 
pip install -qU azure-identity
pip install -qU azure-core
pip install -qU agentops 
pip install -qU 'flaml[automl]'
pip install -qqq matplotlib numpy
pip install 'autogen-agentchat[jupyter-executor]~=0.2'
pip install -qU apify-client
pip install -qU azure.devops

# install langchain
pip uninstall langchain-openai langchain langchain-community langchain-core langchain-text-splitters -y
pip install azure-identity
pip install -qU langchain-openai #openai and azure openai
pip install -qU langchain-chroma #this is for chroma vector db
pip install -qU langgraph #needed for agent building
pip install -qU langchain-community #travily search
#pip install -qU pytube #youtube video access
#pip install git+https://github.com/openai/whisper.git #whisper creates transcripts from audio
#pip install pip install -U openai-whisper
#pip install pypdf



