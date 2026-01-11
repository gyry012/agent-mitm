FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_a/agent_a.py .

CMD ["python", "agent_a.py"]

