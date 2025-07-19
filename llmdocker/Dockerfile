#FROM ubuntu:22.04 #Commented this line to remediate 1es warnings

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    libgomp1 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Add Ollama to PATH
ENV PATH="/root/.ollama/bin:${PATH}"

# Create working directory
WORKDIR /app

# Copy app code (if any) and entrypoint script
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies (customize as needed)
RUN pip3 install --upgrade pip
RUN pip3 install torch transformers

# Expose Ollama API port
EXPOSE 11434

# Use entrypoint script to run everything
ENTRYPOINT ["/entrypoint.sh"]
