FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer — cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run uvicorn with --reload so code changes are picked up without rebuilding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
