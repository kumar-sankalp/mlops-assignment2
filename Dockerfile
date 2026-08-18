FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and application code
# We copy src as well because app/main.py depends on src/model.py
COPY src/ /app/src/
COPY app/ /app/app/

# Copy model artifact
# In a real setup, we might download this from a model registry
COPY model.pt /app/model.pt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
