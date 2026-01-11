FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_b/agent_b.py .

CMD ["python", "agent_b.py"]

