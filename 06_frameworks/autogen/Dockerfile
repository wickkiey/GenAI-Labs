FROM python:3.12-slim

WORKDIR /app

# Install base dependencies
RUN pip install --no-cache-dir autogen-agentchat autogen-ext

# Copy application
COPY . /app/

# Use host Ollama
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434/v1

CMD ["python", "01_agent.py"]
