FROM python:3.12-slim

WORKDIR /app

# Install base dependencies
RUN pip install --no-cache-dir crewai crewai-tools pydantic

# Copy application code
COPY . /app/

# Use host Ollama via host.docker.internal
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434/v1

CMD ["python", "01_agent.py"]
