FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tool_server/tool_server.py .

CMD ["python", "tool_server.py"]

