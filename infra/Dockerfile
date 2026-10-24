FROM python:3.11-slim

WORKDIR /app

# Dépendances d'abord, pour profiter du cache Docker
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY models ./models

EXPOSE 8000
CMD ["uvicorn", "shoppulse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
